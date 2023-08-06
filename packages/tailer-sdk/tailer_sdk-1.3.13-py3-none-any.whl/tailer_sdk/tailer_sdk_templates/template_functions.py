

def process_status_details(
        status,
        failed_task_critical,
        failed_task_warning,
        failed_task_transparent,
        failed_task_break,
        failed_task_stop):

    logging.info("Processing status details")

    status_details = {}
    status_details["sub_status"] = "SUCCESS"
    status_details["failed_critical_tasks"] = failed_task_critical
    status_details["failed_warning_tasks"] = failed_task_warning
    status_details["failed_transparent_tasks"] = failed_task_transparent
    status_details["failed_break_tasks"] = failed_task_break
    status_details["failed_stop_tasks"] = failed_task_stop

    if status.strip() == "FAILED":
        status_details["sub_status"] = "FAILED"

    elif (failed_task_stop is not None) and (len(failed_task_stop) > 0):
        status_details["sub_status"] = "STOP"

    elif (failed_task_break is not None) and (len(failed_task_break) > 0):
        status_details["sub_status"] = "BREAK"

    elif (failed_task_warning is not None) and (len(failed_task_warning) > 0):
        status_details["sub_status"] = "WARNING"

    return status_details


def process_bigquery_record(payload, convert_type_to_string=False, caller_task_id_for_logging=None):

    logging.info("{} Processing RECORD type ...".format(caller_task_id_for_logging))

    # Check for field description
    #
    field_description = None
    try:
        field_description = payload['description']
    except Exception:
        field_description = None

    # Check for field MODE
    #
    mode = None
    try:
        mode = payload['mode']
    except Exception:
        mode = "NULLABLE"

    # Check for field FIELDS
    #
    fields = ()
    try:
        fields_list = payload['fields']
        logging.info("{} {}".format(caller_task_id_for_logging, str(payload['fields'])))
        list_tuples = []

        for field in fields_list:

            # Field, NAME
            field_name = None
            try:
                field_name = field['name']
            except KeyError:
                # error
                continue

            # Field, TYPE
            field_type = None
            try:
                field_type = field['type'].strip()
            except KeyError:
                # error
                continue

            logging.info("{} Field name : {} || Field type : {}".format(
                caller_task_id_for_logging, field_name, field_type))

            # Check if field type is RECORD
            #
            if field_type == "RECORD":
                logging.info("{} Going to process sub Record.".format(caller_task_id_for_logging))
                processed_record = process_bigquery_record(field, caller_task_id_for_logging=caller_task_id_for_logging)
                logging.info("{} Sub Record processed : \n{}".format(caller_task_id_for_logging, processed_record))
                list_tuples.append(processed_record)

            else:

                # Field, MODE
                field_mode = None
                try:
                    field_mode = field['mode']
                except KeyError:
                    field_mode = "NULLABLE"

                # Field, DESCRIPTION
                field_desc = None
                try:
                    field_desc = field['description']
                except KeyError:
                    field_desc = None

                # Convert FIELD TYPE to STRING
                #
                if convert_type_to_string is True:
                    field_type = "STRING"

                list_tuples.append(bigquery.SchemaField(name=field_name,
                                                        field_type=field_type,
                                                        mode=field_mode,
                                                        description=field_desc))

        fields = tuple(list_tuples)

    except Exception:
        fields = ()

    # Must return a bigquery.SchemaField
    #
    logging.info("{} Creating SchemaField : name : {} || type : {} || desc. : {} || mode : {} || fields : {}".format(
        caller_task_id_for_logging, payload['name'], payload['type'], field_description, mode, fields))
    return bigquery.SchemaField(payload['name'], payload['type'], description=field_description, mode=mode, fields=fields)


def get_firestore_data(collection, doc_id, item, credentials=None):

    # Read the configuration is stored in Firestore
    #
    if credentials is None:
        db = firestore.Client()

    else:
        info = json.loads(credentials)
        credentials = service_account.Credentials.from_service_account_info(info)
        db = firestore.Client(credentials=credentials)

    collection = collection

    return (db.collection(collection).document(doc_id).get()).to_dict()[item]


def set_firestore_data(collection, doc_id, item, value, credentials=None):

    # Read the configuration is stored in Firestore
    #
    if credentials is None:
        db = firestore.Client()

    else:
        info = json.loads(credentials)
        credentials = service_account.Credentials.from_service_account_info(info)
        db = firestore.Client(credentials=credentials)

    collection = collection

    date_now = datetime.datetime.now().isoformat('T')
    data = {item : value, "last_updated":date_now}

    db.collection(collection).document(doc_id).set(data, merge=True)


def execute_bq_copy_table(  
        source_gcp_project_id,
        source_bq_dataset,
        source_bq_table,
        destination_gcp_project_id,
        destination_bq_dataset,
        destination_bq_table,
        destination_bq_table_date_suffix,
        destination_bq_table_date_suffix_format,
        firestore_com_id=None,
        task_id=None):

    try:

        # Caller function processing for logging
        #
        caller_task_id_for_logging = "[task_id=" + task_id + "]"


        logging.info("{} source_gcp_project_id : {}".format(caller_task_id_for_logging, source_gcp_project_id))
        logging.info("{} source_bq_dataset : {}".format(caller_task_id_for_logging, source_bq_dataset))
        logging.info("{} source_bq_table : {}".format(caller_task_id_for_logging, source_bq_table))
        logging.info("{} destination_gcp_project_id : {}".format(caller_task_id_for_logging, destination_gcp_project_id))
        logging.info("{} destination_bq_dataset : {}".format(caller_task_id_for_logging, destination_bq_dataset))
        logging.info("{} destination_bq_table : {}".format(caller_task_id_for_logging, destination_bq_table))
        logging.info("{} destination_bq_table_date_suffix : {}".format(caller_task_id_for_logging, str(destination_bq_table_date_suffix)))
        logging.info("{} destination_bq_table_date_suffix_format : {}".format(caller_task_id_for_logging, destination_bq_table_date_suffix_format))

        # Create Bigquery client
        #
        gbq_client = bigquery.Client(project="fd-jarvis-datalake")
        db = firestore.Client()

        # Set this task as RUNNING
        #
        logging.info("{} Setting task status : running".format(caller_task_id_for_logging))
        task_infos = {}
        task_infos[task_id] = "running"
        status_doc_id = firestore_com_id

        time.sleep(1)
        db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

        # Source data
        #
        source_dataset = gbq_client.dataset(source_bq_dataset, project=source_gcp_project_id)
        source_table_ref = source_dataset.table(source_bq_table)

        # Destination
        #
        if destination_bq_table_date_suffix is True:
            today = datetime.datetime.now().strftime(destination_bq_table_date_suffix_format)
            logging.info("{} Today : {}".format(caller_task_id_for_logging, today))
            destination_bq_table += "_" + today
            logging.info("{} Destination table : {}".format(caller_task_id_for_logging, destination_bq_table))

        dest_table_ref = gbq_client.dataset(destination_bq_dataset, project=destination_gcp_project_id).table(destination_bq_table)

        job_config = bigquery.CopyJobConfig()
        job_config.write_disposition = "WRITE_TRUNCATE"

        job = gbq_client.copy_table(
            source_table_ref,
            dest_table_ref,
            location="EU",
            job_config = job_config
        )

        job.result()  # Waits for job to complete.
        assert job.state == "DONE"

        # TEST
        #
        try:
            for referenced_table in job.referenced_tables:
                logging.info(referenced_table.table_id)
                logging.info(referenced_table.dataset_id)
                logging.info(referenced_table.project_id)

        except Exception as ex:
            logging.info("ERROR TEST : {}".format(str(ex)))

        # Set this task as SUCCESS
        #
        logging.info("{} Setting task status : success".format(caller_task_id_for_logging))
        task_infos = {}
        task_infos[task_id] = "success"
        status_doc_id = firestore_com_id

        time.sleep(1)
        db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

    except Exception as ex:

        logging.info("Exception during execute_bq_copy_table.")
        logging.info("Type      : {}".format(type(ex)))
        logging.info("Exception : {}".format(ex))
        raise ex


def execute_bq_create_table(gcp_project_id,
                            force_delete,
                            bq_dataset,
                            bq_table,
                            bq_table_description,
                            bq_table_schema,
                            bq_table_clustering_fields,
                            bq_table_timepartitioning_type,
                            bq_table_timepartitioning_field,
                            bq_table_timepartitioning_expiration_ms,
                            bq_table_timepartitioning_require_partition_filter,
                            firestore_com_id=None,
                            sql_execution_date=None,
                            task_id=None,
                            sql_parameters=None):


    # Caller function processing for logging
    #
    caller_task_id_for_logging = "[task_id=" + task_id + "]"


    logging.info("{} gcp_project_id : {}".format(caller_task_id_for_logging, gcp_project_id))
    logging.info("{} bq_dataset : {}".format(caller_task_id_for_logging, bq_dataset))
    logging.info("{} bq_table : {}".format(caller_task_id_for_logging, bq_table))

    # Create Bigquery client and Firestore client
    #
    gbq_client = bigquery.Client(project=gcp_project_id)
    db = firestore.Client()

    # Set this task as RUNNING
    #
    logging.info("{} Setting task status : running".format(caller_task_id_for_logging))
    task_infos = {}
    task_infos[task_id] = "running"
    status_doc_id = firestore_com_id

    time.sleep(1)
    db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

    # Instantiate a table object
    #
    dataset_ref = gbq_client.dataset(bq_dataset, project=gcp_project_id)
    table_ref = dataset_ref.table(bq_table)
    table = bigquery.Table(table_ref)

    # Check wether the table already exist or not
    #
    try:
        table_tmp = gbq_client.get_table(table_ref)
        logging.info("{} Table {} exists.".format(caller_task_id_for_logging, gcp_project_id + "." + bq_dataset + "." + bq_table))

        if force_delete is True:
            logging.info("{} Table {} is flagged to be deleted.".format(caller_task_id_for_logging, gcp_project_id + "." + bq_dataset + "." + bq_table))
            gbq_client.delete_table(gcp_project_id + "." + bq_dataset + "." + bq_table)

        else:

            # Is the table partitioned
            #
            time_partitioning = table_tmp.partitioning_type

            # Let's delete the current date partition
            #
            if time_partitioning is not None:

                sql_execution_date = sql_execution_date.replace("-", "")

                table_name_with_partition = gcp_project_id + "." + bq_dataset + "." + bq_table + "$" + sql_execution_date
                logging.info("{} Delete partition : {}".format(caller_task_id_for_logging, table_name_with_partition))
                gbq_client.delete_table(table_name_with_partition)

            # Set this task as SUCCESS
            #
            logging.info("{} Setting task status : success".format(caller_task_id_for_logging))
            task_infos = {}
            task_infos[task_id] = "success"
            status_doc_id = firestore_com_id
            time.sleep(1)
            db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

            return

    except exceptions.NotFound:
        logging.info("{} Table {} does not exist. Let's create it.".format(caller_task_id_for_logging, gcp_project_id + ":" + bq_dataset + "." + bq_table))

    except ValueError as error:
        logging.info("{} {}".format(caller_task_id_for_logging, str(error)))
        logging.info("{} Table {} exists and is not time partitioned.".format(caller_task_id_for_logging, gcp_project_id + ":" + bq_dataset + "." + bq_table))

        # Set this task as SUCCESS
        #
        logging.info("{} Setting task status : success".format(caller_task_id_for_logging))
        task_infos = {}
        task_infos[task_id] = "success"
        status_doc_id = firestore_com_id

        time.sleep(1)
        db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

        return


    # Get a new REF
    #
    table = bigquery.Table(table_ref)

    # Set table description
    #
    table.description = bq_table_description

    # Processing the table schema
    #
    table_schema_in = bq_table_schema
    table_schema_out = []

    logging.info("{} Table Schema :".format(caller_task_id_for_logging))

    for item in table_schema_in:

        # Field, NAME
        field_name = None
        try:
            field_name = item['name'].strip()
        except KeyError:
            # error
            logging.info("{} ERROR : field does note have NAME".format(caller_task_id_for_logging))
            continue

        # Field, TYPE
        field_type = None
        try:
            field_type = item['type'].strip()
        except KeyError:
            # error
            logging.info("{} ERROR : field does note have TYPE".format(caller_task_id_for_logging))
            continue

        logging.info("{} Field name : {} || Field type : {}".format(caller_task_id_for_logging, field_name, field_type))

        # Check for field description
        field_description = None
        try:
            field_description = item['description']
        except Exception:
            field_description = None

        # Check for field MODE
        mode = None
        try:
            mode = item['mode']
        except Exception:
            mode = "NULLABLE"

        # Process RECORD type
        #
        if field_type == "RECORD":

            schemafield_to_add = process_bigquery_record(item, caller_task_id_for_logging=caller_task_id_for_logging)
            logging.info("{} Record processed : \n{}".format(caller_task_id_for_logging, schemafield_to_add))

        else:
            schemafield_to_add = bigquery.SchemaField(field_name, field_type, description=field_description, mode=mode)

        table_schema_out.append(schemafield_to_add)
        logging.info("{} SchemaField added : {}".format(caller_task_id_for_logging, schemafield_to_add))

    # Some infos
    #
    logging.info("{} {}".format(caller_task_id_for_logging, str(table_schema_out)))


    # Processing clustering fields
    #
    if (bq_table_clustering_fields is not None) and (len(bq_table_clustering_fields) > 0):

        table.clustering_fields = bq_table_clustering_fields
        logging.info("{} Clustering fields : {}".format(caller_task_id_for_logging, str(bq_table_clustering_fields)))

        # Clustering fields option needs time_partition enabled
        #
        table.time_partitioning = bigquery.table.TimePartitioning()

    else:
        logging.info("{} No clustering fields option to process.".format(caller_task_id_for_logging))

    # Processing time partitioning options
    #
    if (bq_table_timepartitioning_field is not None) or (bq_table_timepartitioning_expiration_ms is not None) or (bq_table_timepartitioning_require_partition_filter is not None):

        logging.info("{} Time Partitioning TYPE                     : {}".format(caller_task_id_for_logging, bq_table_timepartitioning_type))
        logging.info("{} Time Partitioning FIELD                    : {}".format(caller_task_id_for_logging, bq_table_timepartitioning_field))
        logging.info("{} Time Partitioning EXPIRATION MS            : {}".format(caller_task_id_for_logging, bq_table_timepartitioning_expiration_ms))
        logging.info("{} Time Partitioning REQUIRE PARTITION FILTER : {}".format(caller_task_id_for_logging, bq_table_timepartitioning_require_partition_filter))

        if bq_table_timepartitioning_type == "HOUR":
            bqTableTimePartitioningType = bigquery.TimePartitioningType.HOUR
        elif bq_table_timepartitioning_type == "MONTH":
            bqTableTimePartitioningType = bigquery.TimePartitioningType.MONTH
        elif bq_table_timepartitioning_type == "YEAR":
            bqTableTimePartitioningType = bigquery.TimePartitioningType.YEAR
        else:
            bqTableTimePartitioningType = bigquery.TimePartitioningType.DAY

        table.time_partitioning = \
            bigquery.table.TimePartitioning(
                type_=bqTableTimePartitioningType,
                field=bq_table_timepartitioning_field,
                expiration_ms=bq_table_timepartitioning_expiration_ms)

        table.require_partition_filter = bq_table_timepartitioning_require_partition_filter

    # Schema
    #
    table.schema = table_schema_out

    for item in table.schema:
        logging.info("{} {}".format(caller_task_id_for_logging, str(item)))

    # Create table
    #
    job = gbq_client.create_table(table)

    # Set this task as SUCCESS
    #
    logging.info("{} Setting task status : success".format(caller_task_id_for_logging))
    task_infos = {}
    task_infos[task_id] = "success"
    status_doc_id = firestore_com_id

    time.sleep(1)
    db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)


def get_gcs_file(bucket, filename):

    client = storage.Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.get_blob(filename)
    return blob.download_as_string()


def read_from_firestore(collection_id, document_id, sub_collection=None, sub_doc_id=None):

    retry = 3
    message = None

    while retry > 0:

        try:
            db = firestore.Client()
            if (sub_collection is not None) and (sub_doc_id is not None):
                return_payload = db.collection(collection_id).document(document_id).collection(sub_collection).document(sub_doc_id).get().to_dict()
            else:
                return_payload = db.collection(collection_id).document(document_id).get().to_dict()

            return (return_payload, message)

        except Exception as ex:

            message = str(ex)
            time.sleep(5)
            retry -= 1

    time.sleep(2)

    return (None, message)


def write_to_firestore(collection_id, document_id, payload, sub_collection=None, sub_doc_id=None, merge=False):

    retry = 3
    message = None

    payload["last_updated"] = datetime.datetime.now().isoformat('T')

    while retry > 0:

        try:
            db = firestore.Client()
            if (sub_collection is not None) and (sub_doc_id is not None):
                db.collection(collection_id).document(document_id).collection(sub_collection).document(sub_doc_id).set(payload, merge=merge)
            else:
                db.collection(collection_id).document(document_id).set(payload, merge=merge)

            return (True, message)

        except Exception as ex:

            message = str(ex)
            time.sleep(5)
            retry -= 1

    time.sleep(2)

    return (False, message)


def publish_dag_info_to_firestore(dag_name, dag_run_id, task_id, payload):

    # Set task status
    #
    task_infos = {}
    task_infos[task_id] = "running"
    doc_id = dag_name + "_" + dag_run_id
    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format(task_id, doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))

    # Process payload
    #

    copy_payload = copy.deepcopy(payload)

    # Add timestamp
    #
    pst = pytz.timezone("UTC")
    status_updated = str(datetime.datetime.now(pst).isoformat("T"))
    copy_payload["status_updated"] = status_updated

    # We need to resolve the configuration context if present
    #
    task_infos[task_id] = "success"

    if "configuration_context" in copy_payload.keys():

        conf_context_document, message = \
            read_from_firestore(
                copy_payload["configuration_context"]["collection"],
                copy_payload["configuration_context"]["doc_id"])

        if conf_context_document is None:
            logging.error("Error while processing configuration context : \n{}".format(message))
            task_infos[task_id] = "failed"

        else:
            copy_payload["configuration_context"] = \
                conf_context_document[copy_payload["configuration_context"]["item"]]

    # Update the DAG status
    #
    feedback, message = write_to_firestore(_dag_type + "-runs", doc_id, copy_payload, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format(_dag_name, doc_id))
    else:
        logging.error("Error while processing DAG Status : \n{}".format(message))
        task_infos[task_id] = "failed"


    # Update task status
    #
    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format(task_id, doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))


def check_dag_concurrency(
        dag_run_id,
        max_active_runs,
        firestore_com_id,
        lock_manager="redis"):

    retry = 0
    retry_redis_timeout = 0

    while ( (retry < 3) and (retry_redis_timeout < 3) ):

        try:
            # Create the Secret Manager client.
            secret_manager_client = secretmanager.SecretManagerServiceClient()

            # Build the resource name of the secret version.
            #
            if lock_manager == "redis":
                secret_id = "tailer-redis-infos"
            else:
                raise Exception("Lock manager {} is not valid.".format(lock_manager))

            secret_name = "projects/{}/secrets/{}/versions/latest".format(os.environ["PROJECT_ID"], secret_id)

            # Access the secret version.
            #
            secret_response = secret_manager_client.access_secret_version(request={"name": secret_name})
            secret_payload = json.loads(secret_response.payload.data.decode('UTF-8'))

            # Get Lock Manager information
            #
            if lock_manager == "redis":
                lock_manager_host_address = secret_payload["redis_host"]
                lock_manager_host_port = int(secret_payload["redis_port"])
                lock_manager_user = ""
                lock_manager_secret = secret_payload["redis_secret"]

            logging.info("Connecting to {} : {}:{}".format(lock_manager, lock_manager_host_address, str(lock_manager_host_port)))

            # Instantiate Firestore client
            #
            fs_db = firestore.Client()
            collection = _dag_type + "-runs"
            doc_id = firestore_com_id

            # Socket option for Redis Client
            #
            socket_option = {
                socket.SO_KEEPALIVE: 60,
                socket.TCP_KEEPCNT: 10}


            while True:

                # Kill switch
                #
                dag_run_doc = None
                while dag_run_doc is None:

                    dag_run_doc = (fs_db.collection(collection).document(doc_id).get()).to_dict()
                    # dag_run_doc, message = read_from_firestore(collection, doc_id)

                    # if dag_run_doc is None:
                    #     logging.info("Error while retrieving DAG run status.")

                    if (dag_run_doc is not None) and ("killswitch" in dag_run_doc.keys()) and (dag_run_doc["killswitch"] is True):
                        raise Exception("Killed.")
                    else:
                        time.sleep(2)

                # Instantiation lock manager client
                #
                if lock_manager == "redis":

                    lock_manager_instance = \
                        redis.Redis(
                            host=lock_manager_host_address,
                            port=lock_manager_host_port,
                            db=0,
                            password=lock_manager_secret,
                            socket_keepalive=True,
                            socket_keepalive_options=socket_option,
                            socket_connect_timeout=300)

                    # Test if Redis is responding
                    #
                    lock_manager_instance.set(_dag_name, "test")

                    # Remove a retry for retry_redis_timeout
                    #
                    if retry_redis_timeout > 0:
                        retry_redis_timeout -= 1

                    # Lock
                    # TTL 15 seconds
                    #
                    lock_instance = Redlock(
                                        key=_dag_name,
                                        masters={lock_manager_instance},
                                        auto_release_time=15)

                if lock_instance.acquire(timeout=2):

                    logging.info("DAG {} with run ID {} has acquired the lock.".format(_dag_name, dag_run_id))

                    # Now, we need to check how many running instances are there
                    #
                    # TODO
                    # work on the type
                    #

                    logging.info("Trying to retrieve DAG status. Doc ID: {}".format(doc_id))

                    # with firestore.Client() as fs_db:
                    fs_query_result = \
                        fs_db.collection(collection)\
                        .where("dag_id", "==", _dag_name)\
                        .where("status", "==", "RUNNING")\
                        .order_by("dag_execution_date", direction=firestore.Query.DESCENDING)\
                        .limit(int(max_active_runs))

                    counter = 0
                    for instance in fs_query_result.stream():
                        counter += 1

                    logging.info("Count of running instances : {}".format(str(counter)))

                    if counter >= int(max_active_runs):

                        # we cannot launch an new instance
                        #

                        # Release the lock:
                        #
                        lock_instance.release()
                        time.sleep(5)
                        continue

                    else:

                        # OK, we're good to go
                        #
                        # we need to modify the status of the run to RUNNING
                        #

                        logging.info("We have available slots to run instance ...")

                        dag_run_doc = (fs_db.collection(collection).document(doc_id).get()).to_dict()
                        # dag_run_doc, message = read_from_firestore(collection, doc_id)

                        # if dag_run_doc is None:
                        #     raise Exception("Cannot retrieve DAG run status.")

                        logging.info("DAG status : {}".format(dag_run_doc))

                        dag_run_doc["status"] = "RUNNING"
                        fs_db.collection(collection).document(doc_id).set(dag_run_doc)

                        # ret_value, message = write_to_firestore(collection, doc_id, dag_run_doc)

                        # if ret_value is False:
                        #     raise Exception(message)

                        # Release the lock:
                        #
                        lock_instance.release()

                        return

                else:

                    logging.info("DAG {} with run ID {} is waiting to get the lock.".format(_dag_name, dag_run_id))
                    time.sleep(5)

        except TypeError as ex:

            logging.info("Exception type : {}".format(type(ex)))
            logging.info("Exception      : {}".format(str(ex)))

            if str(ex).find("retry_state") != -1:
                logging.info("Known error, no problem ...")
            else:
                retry += 1

            time.sleep(5)

        except redis.exceptions.ConnectionError as ex:

            # Process connection timeout
            #
            if "Error 110" in str(ex):

                logging.info("Exception type : {}".format(type(ex)))
                logging.info("Exception      : {}".format(str(ex)))
                time.sleep(5)
                retry_redis_timeout += 1
            
            else:
                logging.info("Exception type : {}".format(type(ex)))
                logging.info("Exception      : {}".format(str(ex)))
                time.sleep(5)
                retry += 1

        except Exception as ex:

            logging.info("Exception type : {}".format(type(ex)))
            logging.info("Exception      : {}".format(str(ex)))
            time.sleep(5)
            retry += 1

    raise Exception("Error during initialization step.")


def initialize(dag_run_id, firestore_com_id):

    # Read the configuration is stored in Firestore
    #
    collection           = "gbq-to-gbq-conf"
    conf_doc_id          = _dag_name
    task_statuses_doc_id = firestore_com_id

    # Set this task as RUNNING
    #
    task_infos = {}
    task_infos["initialize"] = "running"
    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, task_statuses_doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format("initialize", task_statuses_doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))
        raise

    # Check if there is a Run already associated to this ID
    # We are looking for the following attribute : attempt_number
    #
    logging.info("Attempting to retrieve a potential RUN : {}".format(firestore_com_id))
    data_read, message = read_from_firestore("gbq-to-gbq-runs", firestore_com_id)

    if data_read is not None:
        if "attempt_number" in data_read.keys():

            # Check the status
            #
            try:
                if data_read["status"].strip() == "SUCCESS":
                    return None, None, None, DAG_INIT_STATUS_DUPLICATE_SUCCESS
                    
            except Exception:
                pass

            return None, None, None, DAG_INIT_STATUS_FORCE_FAILED

        else:
            # Add "attempt_number" attribute
            #
            data_read["attempt_number"] = 1
            feedback, message = write_to_firestore("gbq-to-gbq-runs", firestore_com_id, data_read, merge=True)

            if feedback is not True:
                logging.error("Error while processing RUN Status : \n{}".format(message))
                raise
    else:
        logging.error("Error while retrieving RUNS information : \n{}".format(message))
        raise

    # Retrieve configuration
    #
    dag_configuration, message = read_from_firestore(collection, conf_doc_id)

    if dag_configuration is None:
        logging.error("Error while retrieving configuration : \n{}".format(message))
        raise

    dag_configuration['sql'] = {}

    # retrieve maximum active runs
    #
    try:
        max_active_runs = dag_configuration["configuration"]["max_active_runs"]
    except Exception:
        max_active_runs = 1

    # Push configuration context
    #
    conf_context = {}
    conf_context["configuration_context"] = dag_configuration
    feedback, message = write_to_firestore(AIRFLOW_COM_FIRESTORE_COLLECTION, task_statuses_doc_id, conf_context, merge=False)

    if feedback is False:
        logging.error("Error while writing configuration context to Firestore : \n{}".format(message))
        raise

    # Do we need to run this DAG
    # let's check the 'activated' flag
    #
    try:
        dag_activated = dag_configuration["activated"]
    except KeyError:
        print("No activated attribute found in DAGs config. Setting to default : True")
        dag_activated = True

    if dag_activated is True:

        # Forcing lock manager to REDIS
        #
        print("Forcing lock manager, setting default : redis")
        lock_manager = "redis"

        # Allright, we are going to execute this DAG.
        # First of all, we need to check that we are above the DAG concurrency threshold.
        #
        try:

            check_dag_concurrency(
                dag_run_id=dag_run_id,
                max_active_runs=max_active_runs,
                firestore_com_id=firestore_com_id,
                lock_manager=lock_manager)

        except Exception as ex:

            logging.error("Error while checking DAG concurrency.")
            logging.error("Exception type : {}".format(str(type(ex))))
            logging.error("Exception      : {}".format(str(ex)))
            return None, None, None, None

    # Set this task as SUCCESS
    #
    task_infos = {}
    task_infos["initialize"] = "success"
    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, task_statuses_doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format("initialize", task_statuses_doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))
        raise

    # Return these values
    # dag activated : boolean
    # account : string
    # environment : string
    # force_failed = Global value
    #
    return dag_activated, dag_configuration["account"], dag_configuration["environment"], DAG_INIT_STATUS_NORMAL


def execute_python_script(firestore_com_id, task_id):

    # Read the configuration is stored in Firestore
    #
    db                   = firestore.Client()
    collection           = "gbq-to-gbq-conf"
    conf_doc_id          = _dag_name
    task_statuses_doc_id = firestore_com_id

    # Set this task as RUNNING
    #
    task_infos = {}
    task_infos["execute_python_script"] = "running"
    db.collection("gbq-to-gbq-tasks-status").document(task_statuses_doc_id).set(task_infos, merge=True)

    # Retrieve DAG configuration from Firestore
    #
    dag_conf = db.collection(collection).document(conf_doc_id).get().to_dict()


    # Get PYTHON file
    #
    for wk_item in dag_conf["configuration"]["workflow"]:
        if wk_item["id"] == task_id:
            python_filename = wk_item["python_file"]

    python_filename_composed = "dags/TTT/python_script_tasks/" + _dag_name + "/"+ python_filename

    logging.info("Attempting to retrieve file : {}".format(python_filename_composed))

    python_script = get_gcs_file(bucket=dag_conf["dag_script"]["bucket"], filename=python_filename_composed)

    logging.info(python_script)

    # create file-like string to capture output
    codeOut = io.StringIO()
    codeErr = io.StringIO()

    # capture output and errors
    sys.stdout = codeOut
    sys.stderr = codeErr

    exec(str(python_script))

    # restore stdout and stderr
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__

    s = codeErr.getvalue()

    logging.info("Errors : {}".format(s))

    s = codeOut.getvalue()

    logging.info("Out : {}".format(s))

    codeOut.close()
    codeErr.close()

    # Set this task as SUCCESS
    #
    task_infos = {}
    task_infos["execute_python_script"] = "success"
    db.collection("gbq-to-gbq-tasks-status").document(task_statuses_doc_id).set(task_infos, merge=True)


def execute_expectation_script(
        sql_call,
        name):

    try:
        logging.info("[{}] Executing : {}".format(name, sql_call))

        gbq_client = bigquery.Client(project="fd-jarvis-datalake")

        # Job Config setup
        #
        job_config = bigquery.QueryJobConfig()
        job_config.use_query_cache = False

        query_job = \
            gbq_client.query(
                sql_call,
                location="EU",
                job_config=job_config)

        # Waits for query to complete.
        #
        results = query_job.result()

        child_jobs_iterable = gbq_client.list_jobs(parent_job=query_job)
        for child_job in child_jobs_iterable:

            # Look for last child job
            #
            if int((child_job.job_id).rpartition("_")[2]) == query_job.num_child_jobs - 1:

                for row in child_job.result():

                    return {"status": row.values()[0], "result": json.loads(row.values()[1])}

        return {"status": None, "result": "No result."}

    except Exception as ex:
        logging.info("[{}] Exception : {}".format(name, type(ex)))
        logging.info("[{}] Exception : {}".format(name, str(ex)))

        return {"status": None, "result": str(ex)}


def execute_expectation_process(
        gcp_project_id,
        bq_dataset,
        sql_query,
        task_id,
        firestore_com_id,
        dag_infos,
        task_criticality):

    try:

        # Caller function processing for logging
        #
        caller_task_id_for_logging = "[task_id=" + task_id + "]"

        logging.info("{} gcp_project_id : {}".format(caller_task_id_for_logging, gcp_project_id))
        logging.info("{} bq_dataset : {}".format(caller_task_id_for_logging, bq_dataset))
        logging.info("{} sql_query : {}".format(caller_task_id_for_logging, sql_query))
        logging.info("{} task_id : {}".format(caller_task_id_for_logging, task_id))
        logging.info("{} firestore_com_id : {}".format(caller_task_id_for_logging, firestore_com_id))
        logging.info("{} dag_infos : {}".format(caller_task_id_for_logging, dag_infos))

        # Create Firestore
        #
        db = firestore.Client(project="fd-jarvis-datalake")

        # Some init
        #
        error_occured = False

        # Set this task as RUNNING
        #
        logging.info("{} Setting task status : running".format(caller_task_id_for_logging))
        task_infos = {}
        task_infos[task_id] = "running"
        status_doc_id = firestore_com_id

        time.sleep(1)
        db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

        # Update the configuration context
        #
        doc_id = firestore_com_id
        airflow_com_doc, message = read_from_firestore(AIRFLOW_COM_FIRESTORE_COLLECTION, doc_id)

        if airflow_com_doc is None:
            logging.error("Error while retrieving configuration : \n{}".format(message))
            raise

        config_context = airflow_com_doc["configuration_context"]

        config_context['sql'][task_id] = sql_query
        final_config_context = {}
        final_config_context["configuration_context"] = config_context
        feedback, message = write_to_firestore(AIRFLOW_COM_FIRESTORE_COLLECTION, doc_id, final_config_context, merge=False)

        if feedback is False:
            logging.error("Error while writing configuration context to Firestore : \n{}".format(message))
            raise

        # Parse SQL query as list of scripts
        #
        sql_scripts = sqlparse.split(sql_query)

        # Futures init
        #
        fd_futures = {}
        global_results = {}
        executor = concurrent.futures.ThreadPoolExecutor(max_workers = 10)

        # Prepare the calls
        #
        index = 1
        for sql_call in sql_scripts:

            sql_call = sql_call.strip()

            if not sql_call:
                continue

            if ((sql_call.lower()).find("call") == -1) or ((sql_call.lower()).find(".expect") == -1):
                logging.info("Not a stored procedur call  : {}".format(sql_call))
                continue

            name = "script_" + str(index)

            future_instance = executor.submit(
                execute_expectation_script,
                sql_call,
                name)

            fd_futures[future_instance] = name
            index += 1

        # Get the results
        #
        for future in concurrent.futures.as_completed(fd_futures):
            try:
                tag = fd_futures[future].strip()
                global_results[tag] = future.result()
            except Exception as exc:
                logging.info("Exception : {}".format(str(exc)))

        # Process results
        #
        gbq_client = bigquery.Client(project="fd-jarvis-datalake")
        table_id = "{}.tailer_common.expectation_results".format(gcp_project_id)
        data_to_insert_into_firestore = []
        rows_to_insert_into_gbq = []

        for key in global_results.keys():

            logging.info("{}:\n\n{}".format(key, global_results[key]))

            # Process only expectations that have been processed successfully
            #
            if global_results[key]["status"] is None:
                logging.info("Technical error => {}".format(global_results[key]["result"]))
                error_occured = True
                continue

            if global_results[key]["result"]["passed"] is False:
                logging.info("ASSERT is FALSE.")
                error_occured = True

            tmp_data = {
                "job_id": dag_infos["job_id"],
                "dag_id": dag_infos["dag_id"],
                "account": dag_infos["account"],
                "environment": dag_infos["environment"],
                "run_id": dag_infos["dag_run_id"],
                "configuration_type": "table-to-table",
                "configuration_id": dag_infos["dag_id"],
                "task_id": task_id,
                "execution_date": dag_infos["dag_execution_date"],
                "task_criticality": task_criticality,
                "expectation_result": global_results[key]["result"]}

            data_to_insert_into_firestore.append(copy.deepcopy(tmp_data))

            tmp_data["expectation_result"] = json.dumps(tmp_data["expectation_result"])

            rows_to_insert_into_gbq.append(tmp_data)

        # Write data to GBQ
        #
        errors = gbq_client.insert_rows_json(table_id, rows_to_insert_into_gbq)
        if errors == []:
            logging.info("{} New rows have been added.".format(caller_task_id_for_logging))
        else:
            raise Exception(errors)

        # Write data to FIRESTORE
        #
        for row in data_to_insert_into_firestore:
            db.collection("tailer-expectations").document().set(row)

        # Set task status according to errors
        #
        logging.info("{} Setting task status : success".format(caller_task_id_for_logging))
        task_infos = {}

        if error_occured is True:
            task_infos[task_id] = "failed"
        else:
            task_infos[task_id] = "success"

        status_doc_id = firestore_com_id

        time.sleep(1)
        db.collection("gbq-to-gbq-tasks-status").document(status_doc_id).set(task_infos, merge=True)

        # Raise Exception upon failure
        #
        if task_infos[task_id] == "failed":
            raise Exception("Expectation executed successfully but the assertion failed.")

    except Exception as ex:

        logging.info("Exception during data quality process.")
        logging.info("Type      : {}".format(type(ex)))
        logging.info("Exception : {}".format(ex))
        raise ex


def execute_gbq(
    sql_id,
    env,
    dag_name,
    gcp_project_id,
    bq_dataset,
    table_name,
    write_disposition,
    sql_query_template,
    sql_execution_date=None,
    local_sql_query=None,
    firestore_com_id=None,
    use_query_cache=False,
    task_id=None,
    sql_parameters=None):

    # Caller function processing for logging
    #
    caller_task_id_for_logging = "[task_id=" + task_id + "]"

    # Strip the ENVIRONMENT out of the DAG's name
    # i.e : my_dag_PROD -> my_dag
    #
    # stripped_dag_name = _dag_name.rpartition("_")[0]

    # Firestore infos for TTT DAG Configuration
    #
    collection      = "gbq-to-gbq-conf"
    doc_id          = _dag_name

    # Set this task as RUNNING
    #
    logging.info("{} Setting task status : running".format(caller_task_id_for_logging))
    task_infos = {}
    task_infos[task_id] = "running"
    status_doc_id = firestore_com_id

    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, status_doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format(task_id, status_doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))
        raise

    # Retrieve SQL Query
    #
    logging.info("{} Trying to retrieve SQL query from Firestore : {} > {}  : sql -> {}".format(caller_task_id_for_logging, collection, doc_id, sql_id))
    data_read, message = read_from_firestore(collection, doc_id)
    if data_read is None:
        logging.error("Error while retrieving SQL query: \n{}".format(message))
        task_infos[task_id] = "failed"

    data_decoded = base64.b64decode(data_read['sql'][sql_id])
    sql_query = str(data_decoded, 'utf-8')

    # Update the configuration context
    #
    doc_id = firestore_com_id
    airflow_com_doc, message = read_from_firestore(AIRFLOW_COM_FIRESTORE_COLLECTION, doc_id)

    if airflow_com_doc is None:
        logging.error("Error while retrieving configuration : \n{}".format(message))
        raise

    config_context = airflow_com_doc["configuration_context"]

    config_context['sql'][sql_id] = sql_query
    final_config_context = {}
    final_config_context["configuration_context"] = config_context
    feedback, message = write_to_firestore(AIRFLOW_COM_FIRESTORE_COLLECTION, doc_id, final_config_context, merge=False)

    if feedback is False:
        logging.error("Error while writing configuration context to Firestore : \n{}".format(message))
        raise

    # Retrieve flag : temporary_table
    #
    temporary_table = False
    for wf_item in data_read["configuration"]["workflow"]:
        try:
            if wf_item["id"].strip() == task_id:
                temporary_table = wf_item["temporary_table"]
        except Exception as ex:
            logging.info("Error while retrieving temporary_table flag. Setting to default -> False")
            logging.info("{} : {}".format(type(ex), str(ex)))
            temporary_table = False

    logging.info("Temporary table flag : {}".format(temporary_table))

    # Replace "sql_query_template" with DAG Execution DATE
    #
    # The expected format id : YYYY-MM-DD
    #
    logging.info("{} sql_query_template : {}".format(caller_task_id_for_logging, sql_query_template))
    if sql_query_template != "":

        if sql_execution_date is not None:
            execution_date = sql_execution_date

        logging.info("{} execution_date : {}".format(caller_task_id_for_logging, execution_date))

        sql_query = sql_query.replace("{{" + sql_query_template + "}}", execution_date)

    # Process SQL parameters
    # sql_parameters
    #
    if sql_parameters is not None:

        for key in sql_parameters.keys():

            sql_query = sql_query.replace("{{" + key.strip() + "}}", str(sql_parameters[key]))

    # Escape " in the query
    #
    sql_query = sql_query.replace('"', '\"')

    logging.info("{} SQL Query : \n\r{}".format(caller_task_id_for_logging, sql_query))

    # Specify scopes
    #
    client_options = {
        "scopes": [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/datastore',
            'https://www.googleapis.com/auth/bigquery',
            'https://www.googleapis.com/auth/drive'
        ]}

    # Some initialization
    #
    exception_occured = False
    is_gbq_script = False
    task_information_payload = {
        "task_id": task_id,
        "task_type": "sql",
        "referenced_tables": []
    }

    try:

        # Instantiate GBQ client
        #
        gbq_client = bigquery.Client(
            project=gcp_project_id,
            client_options=client_options)

        dataset_id = bq_dataset
        dataset_ref = gbq_client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        # dataset.location = "EU"  

        if table_name is not None:
            table_ref = gbq_client.dataset(dataset_id).table(table_name)

        # Try to retrieve schema
        # This will be used later on in a case of query with WRITE_TRUNCATE
        # We do that only when we do not deal with a temporary table AND we have a destination table
        #
        if (temporary_table is False) and (table_name is not None):
            try:
                retrieved_schema = list(gbq_client.get_table(table_ref).schema)
                logging.info("{} {}".format(caller_task_id_for_logging, str(retrieved_schema)))
            except exceptions.NotFound:
                logging.info("{} Table {} does not exist, cannot retrieve schema.".format(caller_task_id_for_logging, table_name))
                retrieved_schema = None

        # Process temporary table
        #
        if (temporary_table is True) and (table_name is not None):

            logging.info("Processing temporary table ...")

            # First, we delete the table
            #
            logging.info("Deleting table : {}".format(table_ref.table_id))
            gbq_client.delete_table(table=table_ref, not_found_ok=True)

            # Second, create the table with an expiration after 12 hours
            #
            pst = pytz.timezone("UTC")
            expiry_date = datetime.datetime.now(pst) + datetime.timedelta(hours=12)
            temp_table = bigquery.Table(table_ref)
            temp_table.expires = expiry_date
            gbq_client.create_table(temp_table)

        # Special loop to determine if we have a regular SQL query or a script
        #
        retry = 3
        first_pass = True

        while retry > 0:

            try:
                # Job Config setup
                #
                job_config = bigquery.QueryJobConfig()
                job_config.use_query_cache = use_query_cache

                # Prepare labels
                #
                # labels = {}
                # labels["tailer_task_id"] = task_id.strip()
                # labels[task_id.strip()] = ""
                # job_config.labels = labels

                # We do a special init for the first pass
                # The goal is to determine if we will run a regular SQL query or a script
                #
                if (table_name is not None) and (first_pass is True):
                    job_config.write_disposition = write_disposition
                    job_config.destination = table_ref

                query_job = gbq_client.query(
                    sql_query,
                    location="EU",
                    job_config=job_config
                )

                results = None

                # Waits for query to complete.
                #
                results = query_job.result()
                break

            except google_exception.BadRequest as google_br_exception:
                if len(google_br_exception.errors) > 0:
                    for error in google_br_exception.errors:
                        try:
                            if (error["reason"].strip() == "invalid") \
                                and ("configuration.query.destinationTable" in error["message"]) \
                                and ("script" in error["message"]):

                                is_gbq_script = True
                                first_pass = False
                                exception_occured = False
                                break

                            else:
                                logging.info("Exception during query execution : {}".format(google_br_exception))
                                exception_occured = True
                                retry = 0
                                break

                        except Exception:
                            retry -= 1
                            logging.info("Exception during query execution : {}".format(type(ex)))
                            logging.info("Exception during query execution : {}".format(ex))
                            exception_occured = True

            except Exception as ex:
                retry -= 1
                logging.info("Exception during query execution : {}".format(ex))
                exception_occured = True

        # Test for exception occurence
        #
        if exception_occured is True:
            raise Exception("Exception during query execution")

        # Add some info
        #
        task_information_payload["is_gbq_script"] = is_gbq_script
        task_information_payload["temporary_table"] = temporary_table

        # Check if we have a simple query job or a SCRIPT
        #
        # if query_job.num_child_jobs > 0:
        #     is_gbq_script = True
        # else:
        #     is_gbq_script = False
        # logging.info("This job is GBQ script ? => {}".format(is_gbq_script))
        # task_information_payload["is_gbq_script"] = is_gbq_script

        # Get duration
        #
        job_duration = query_job.ended - query_job.created
        logging.info("{} Duration : {}".format(caller_task_id_for_logging, job_duration))
        task_information_payload["job_duration"] = str(job_duration)

        # Get extra info
        #
        task_information_payload["slot_millis"] = query_job.slot_millis
        task_information_payload["total_bytes_billed"] = query_job.total_bytes_billed
        task_information_payload["total_bytes_processed"] = query_job.total_bytes_processed
        task_information_payload["user_email"] = query_job.user_email

        # Retrieve some information
        #
        if is_gbq_script is True:
            child_jobs_iterable = gbq_client.list_jobs(parent_job=query_job)
            for child_job in child_jobs_iterable:

                # Referenced tables
                #
                for referenced_table in child_job.referenced_tables:
                    task_information_payload["referenced_tables"].append({
                            "table_id": referenced_table.table_id,
                            "dataset_id": referenced_table.dataset_id,
                            "project_id": referenced_table.project})

                # Look for last child job
                #
                if int((child_job.job_id).rpartition("_")[2]) == query_job.num_child_jobs - 1:
                    last_child_job = child_job
                    logging.info("\nThe last job of the script should be : {}\n".format(last_child_job.job_id))
                    # Source table
                    source_table = last_child_job.destination

        else:

            # Referenced tables
            #
            for referenced_table in query_job.referenced_tables:
                task_information_payload["referenced_tables"].append({
                        "table_id": referenced_table.table_id,
                        "dataset_id": referenced_table.dataset_id,
                        "project_id": referenced_table.project})

            # Source table
            #
            source_table = query_job.destination

        # Retrieve Referenced Tables
        #
        # referenced_tables = query_job.referenced_tables
        # logging.info("{} Referenced tables : {}".format(caller_task_id_for_logging, referenced_tables))

        # Copy job result to the table
        #
        if (table_name is not None) and (is_gbq_script is True):

            retry = 3
            while retry != 0:
                try:
                    logging.info("Results of the script are going to be written to table : {}".format(table_ref.table_id))

                    # Copy table
                    #
                    job_config = bigquery.CopyJobConfig()
                    job_config.create_disposition = "CREATE_IF_NEEDED"
                    job_config.write_disposition = write_disposition
                        
                    logging.info("{} Source table : {}".format(caller_task_id_for_logging, source_table))

                    job = gbq_client.copy_table(
                            source_table,
                            table_ref,
                            job_config=job_config,
                            location="EU")

                    job.result()
                    break

                except Exception as ex:
                    logging.info("Exception type : {}".format(type(ex)))
                    logging.info(str(ex))
                    retry -= 1

                    if retry == 0:
                        raise

        # Try to update destination schema
        # This is useful in a WRITE_TRUNCATE context
        #
        if (temporary_table is False) and (table_name is not None):
            try:

                # Update schema
                #
                if (write_disposition == "WRITE_TRUNCATE") and (retrieved_schema is not None):
                    logging.info("{} Updating table schema ...".format(caller_task_id_for_logging))
                    table_ref = gbq_client.dataset(dataset_id).table(table_name)
                    table_to_modify = gbq_client.get_table(table_ref)
                    table_to_modify.schema = retrieved_schema
                    table_to_modify = gbq_client.update_table(table_to_modify, ["schema"])
                    assert table_to_modify.schema == retrieved_schema

                next(iter(results))
                logging.info("{} Output of result : {}".format(caller_task_id_for_logging, results))
                logging.info("{} Rows             : {}".format(caller_task_id_for_logging, results.total_rows))

            except Exception as ex:
                logging.info("{} Error while updating table schema : {}".format(caller_task_id_for_logging, str(ex)))


        # Update task status information
        #
        feedback, message = \
            write_to_firestore(
                TASK_STATUS_FIRESTORE_COLLECTION,
                status_doc_id,
                task_information_payload,
                sub_collection="task-information",
                sub_doc_id=task_id,
                merge=True)

        if feedback is True:
            logging.info("Pushed {} task information to : {}".format(task_id, status_doc_id))
        else:
            logging.error("Error while processing Task Information : \n{}".format(message))
            exception_occured = True
            raise

    except Exception as ex:
        logging.error("{} ERROR while executing query : {}".format(caller_task_id_for_logging, ex))
        exception_occured = True

    # Set task status
    #
    if exception_occured is True:
        task_status = "failed"
    else:
        task_status = "success"

    logging.info("{} Setting task status : {}".format(caller_task_id_for_logging, task_status))
    task_infos = {}
    task_infos[task_id] = task_status
    status_doc_id = firestore_com_id

    feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, status_doc_id, task_infos, merge=True)

    if feedback is True:
        logging.info("Pushed {} status to : {}".format(task_id, status_doc_id))
    else:
        logging.error("Error while processing Task Status : \n{}".format(message))
        raise

    if exception_occured is True:
        raise
