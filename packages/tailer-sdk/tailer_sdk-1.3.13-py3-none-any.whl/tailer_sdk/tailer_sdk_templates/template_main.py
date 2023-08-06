
if __name__ == "__main__":

    # Some init
    #

    # Task failures
    #
    failed_task_warning = []
    failed_task_transparent = []
    failed_task_critical = []
    failed_task_break = []
    failed_task_stop = []

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    root.addHandler(handler)

    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Display environment
    #
    logging.info("Environment : {}".format(os.environ))

    # Parsing arguments if any
    #
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execution-id", help="Execution ID for the DAG.", type=str, default=None)
    parser.add_argument("--configuration-id", help="Configuration ID for the DAG.", type=str, default=None)
    parser.add_argument("--sql-execution-date", help="Date used in SQL template. Format expected YYY-MM-DD", type=str, default=None)
    parser.add_argument("--sql-parameters", help="Extra parameters that will be replacer in the SQL queries", type=str, default=None)

    args, unknown = parser.parse_known_args()
    print("Arguments : {}".format(args))

    # Processing DAG Execution ID, if provided
    #
    if args.execution_id is not None:
        dag_run_id = args.execution_id
    else:
        dag_run_id = "{DAG_NAME}" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())

    # Generate Firestore Com ID
    #
    firestore_com_id = "{DAG_NAME}" + "_" + dag_run_id

    # Process SQL parameters
    #
    sql_parameters = None
    if args.sql_parameters is not None:
        try:
            sql_parameters = json.loads(args.sql_parameters)
        except Exception as ex:
            print("Exception")
            print("Type    : {}".format(type(ex)))
            print("Message : {}".format(ex))
            sql_parameters = None

    print("SQL Parameters : {}".format(sql_parameters))

    # DAG execution date
    #
    pst = pytz.timezone("UTC")
    dt_now = datetime.datetime.now(pst)
    dag_execution_date = dt_now.isoformat("T")

    # Processing DAG Execution DATE, if provided
    #
    sql_execution_date = args.sql_execution_date

    if sql_execution_date is None:
        sql_execution_date = dt_now.strftime("%Y-%m-%d")
    else:
        sql_execution_date = dt_parse(sql_execution_date).strftime("%Y-%m-%d")

    logging.info("SQL Execution date : {}".format(sql_execution_date))

    # Job ID
    #
    job_id =  _dag_type + "|" + "{DAG_NAME}"

    logging.info(f"Execution of DAG : {DAG_NAME}\n")
    logging.info(f"DAG Run ID       : {dag_run_id}\n\n")

    # First call to pubsub
    #
    pubsub_payload = {
        "dag_id": "{DAG_NAME}",
        "dag_execution_date": dag_execution_date,
        "dag_run_id": dag_run_id,
        "dag_type": "{DAG_TYPE}",
        "dag_generator_version": "{DAG_GENERATOR_VERSION}",
        "job_id": job_id,
        "status": "WAITING",
        "killswitch": False,
        "env_hostname": os.environ["HOSTNAME"],
        "environment": "{ENVIRONMENT}",
        "account": "{ACCOUNT}"
    }

    publish_dag_info_to_firestore(
        dag_name="{DAG_NAME}",
        dag_run_id=dag_run_id,
        task_id="send_dag_infos_to_pubsub",
        payload=pubsub_payload)

    # PubSub payload to be sent after the initialize function
    #
    pubsub_payload = {
        "dag_id": "{DAG_NAME}",
        "dag_execution_date": dag_execution_date,
        "dag_run_id": dag_run_id,
        "dag_type": "{DAG_TYPE}",
        "dag_generator_version": "{DAG_GENERATOR_VERSION}",
        "configuration_context": {"collection" : "airflow-com", "doc_id" : firestore_com_id, "item" : "configuration_context"},
        "job_id": job_id,
        "status": "RUNNING",
        "environment": "{ENVIRONMENT}",
        "account": "{ACCOUNT}"
    }

    # Initialize function
    #
    try:
        ret, account, environment, dag_init_status = \
            initialize(
                dag_run_id=dag_run_id,
                firestore_com_id=firestore_com_id)

        # Start time
        # The duration measurement will starts here
        #
        start_time = datetime.datetime.now()

        pubsub_payload = {
            "dag_id": "{DAG_NAME}",
            "dag_execution_date": dag_execution_date,
            "dag_run_id": dag_run_id,
            "dag_type": "{DAG_TYPE}",
            "dag_generator_version": "{DAG_GENERATOR_VERSION}",
            "configuration_context": {"collection" : "airflow-com", "doc_id" : firestore_com_id, "item" : "configuration_context"},
            "environment": "{ENVIRONMENT}",
            "account": "{ACCOUNT}",
            "job_id": job_id,
            "status": "RUNNING"
        }

        if dag_init_status == DAG_INIT_STATUS_FORCE_FAILED:

            # The DAG must be forced to FAILED
            #
            raise Exception("The DAG has been forced FAILED. An instance must have run before and turned into a staled state.")

        elif dag_init_status == DAG_INIT_STATUS_DUPLICATE_SUCCESS:

            # Duplicate RUN with previous already SUCCESS
            # most likely due to Pub/Sub re-dending a message
            #
            logging.info("Previous run already sucess, probably due to PubSub re-delivering a message. Exiting.")
            pubsub_payload["status"] = "SUCCESS"
            pubsub_payload["duration"] = str(datetime.datetime.now() - start_time)

            publish_dag_info_to_firestore(
                dag_name="{DAG_NAME}",
                dag_run_id=dag_run_id,
                task_id="send_dag_infos_to_pubsub_after_initialization",
                payload=pubsub_payload)

            exit(0)

        if ret is None:
            raise Exception("Error during initialization.")

        if ret is False:

            # The DAG is deactivated
            #
            pubsub_payload["status"] = "DEACTIVATED"
            pubsub_payload["duration"] = str(datetime.datetime.now() - start_time)

            publish_dag_info_to_firestore(
                dag_name="{DAG_NAME}",
                dag_run_id=dag_run_id,
                task_id="send_dag_infos_to_pubsub_after_initialization",
                payload=pubsub_payload)

            exit(0)

        # We keep going
        #
        publish_dag_info_to_firestore(
            dag_name="{DAG_NAME}",
            dag_run_id=dag_run_id,
            task_id="send_dag_infos_to_pubsub_after_initialization",
            payload=pubsub_payload)
