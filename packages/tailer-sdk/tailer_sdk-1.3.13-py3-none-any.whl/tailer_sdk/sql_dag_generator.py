#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This tool will generate a DAG according to the JSON file passed in.

20190107  : JGU
For now, this tool will generate a workflow containing a sequence of GBQ SQL queries executions.

20190306 : JGU
The "--deploy" switch will work only if this script is executed within the directory where the .sql files are.
process_status_details(
                                                status="SUCCESS",
                                                failed_task_critical=failed_task_critical,
                                                failed_task_warning=failed_task_warning,
                                                failed_task_transparent=failed_task_transparent)
ie :
|
|-- someDirectory
|      |
       |-- my_dag_description.json
       |-- sql_001.sql
       |-- step_N.sql
       |-- cleanup.sql

"""

import json
import base64
import warnings
import requests
import pickle
import re
import sys
import copy
import networkx as nx
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE, STDOUT

from tailer_sdk import tailer_config
from tailer_sdk import tailer_auth
from tailer_sdk import tailer_misc

# Globals
#
_current_version = "2021.02.22.001"

TAILER_SDK_TEMPLATES_PATH = tailer_misc.get_path_from_file(tailer_config.__file__, sub_element="tailer_sdk_templates")
print(TAILER_SDK_TEMPLATES_PATH)

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

REGEX_TASKS_ARRAY = re.compile(r"^\[{1}(\s*[0-9a-zA-Z]+[^\s]+[0-9a-zA-Z]+\s*[,]?)+\]{1}$")
REGEX_WHITESPACES = re.compile(r"\s+")
REGEX_BRACKETS = re.compile(r"\[+|\]")

_dag_type = "gbq-to-gbq"


def pickle_and_encode_file_content(input_file):

    with open(input_file, "r") as f:

        file_content = f.read()

    pickled_payload = pickle.dumps(file_content)
    encoded_payload_forced = base64.b64encode(pickled_payload)
    encoded_payload_forced = str(encoded_payload_forced, "utf-8")

    return encoded_payload_forced


def check_criticality(parent_task, child_task, task_workflow):

    parent_task_criticality = None
    child_task_criticality = None

    for current_task in task_workflow:

        if current_task["id"].strip() == parent_task.strip():
            try:
                parent_task_criticality = current_task["criticality"].strip()
            except:
                parent_task_criticality = "critical"

        elif current_task["id"].strip() == child_task.strip():
            try:
                child_task_criticality = current_task["criticality"].strip()
            except:
                child_task_criticality = "critical"

        if (parent_task_criticality is not None) and (child_task_criticality is not None):

            # print(parent_task_criticality)
            # print(child_task_criticality)

            if ((parent_task_criticality == "warning") \
                    or (parent_task_criticality == "transparent")) \
                and (child_task_criticality == "critical"):

                print("")
                print("{} has criticality policy set to critical, {} criticality policy must be set to critical as well.".format(child_task, parent_task))
                print("")
                return False

            break

    return True


def parse_dag_dependencies(
        dependencies,
        task_worflow,
        entry_task=None,
        exit_task=None):

    print("Parsing DAG dependencies ...")

    graph = nx.DiGraph()
    previous_item = entry_task

    nodes = []

    check_criticality_status = True

    for line in dependencies:

        # Removing whitespaces
        #
        line = re.sub(REGEX_WHITESPACES, "", line)

        # DEBUG
        #
        # print("Processing line : {}".format(line))

        parsed_line = line.split(">>")

        for item in parsed_line:

            # DEBUG
            #
            print("Processing : {}".format(item))

            # Check for array
            #
            if re.match(REGEX_TASKS_ARRAY, item) is not None:

                # print("Tasks array found.")

                tasks_array = (re.sub(REGEX_BRACKETS, "", item)).split(",")

                # Check if previous item is an array of tasks
                #
                if previous_item is None:

                    previous_item = tasks_array
                    continue

                elif isinstance(previous_item, list):

                    for task_previous in previous_item:
                        for task in tasks_array:

                            if task != task_previous:
                                nodes.append((task_previous, task))
                                if check_criticality(task_previous, task, task_worflow) is False:
                                    check_criticality_status = False

                else:

                    for task in tasks_array:

                        if task != previous_item:
                            nodes.append((previous_item, task))
                            if check_criticality(previous_item, task, task_worflow) is False:
                                check_criticality_status = False

                previous_item = tasks_array

            else:

                # DEBUG
                #
                # print("Current item  : {}".format(item))
                # print("Previous item : {}".format(previous_item))
                # print("Prv item type : {}".format(type(previous_item)))

                # Check if previous item is an array of tasks
                #
                if previous_item is None:

                    previous_item = item
                    continue

                elif isinstance(previous_item, list):

                    for task in previous_item:

                        if item != task:
                            nodes.append((task, item))
                            if check_criticality(task, item, task_worflow) is False:
                                check_criticality_status = False

                else:

                    if item != previous_item:
                        nodes.append((previous_item, item))
                        if check_criticality(previous_item, item, task_worflow) is False:
                            check_criticality_status = False

                previous_item = item

        # END FOR
        #

        previous_item = None

    # Add nodes
    #
    graph.add_edges_from(nodes)

    if check_criticality_status is False:
        return None, None
    else:
        # convert the networkx graph to Mermaid format
        #
        mermaid_str = "graph TD;\n"
        for node in graph.nodes():
            mermaid_str += f"{node};\n"
        for edge in graph.edges():
            mermaid_str += f"{edge[0]}-->{edge[1]};\n"

        # Convert to base 64
        #
        mermaid_base64 = (base64.b64encode(mermaid_str.encode("utf-8"))).decode("utf-8")

        return \
            list(nx.topological_sort(graph)), mermaid_base64


def check_task_dependencies_vs_workflow(task_dependencies, workflow):

    # Process workflow
    #
    task_list = []
    for item in workflow:

        task_list.append(item["id"].strip())

    missing_tasks = []
    for line in task_dependencies:

        line = re.sub(">>|<<|\[|\]|,", " ", line)

        for item in line.split():

            if item not in task_list:

                missing_tasks.append(item.strip())

    if len(missing_tasks) > 0:

        print("\n")
        for missing_task in  missing_tasks:
            print("ERROR : the task with ID \"{}\" is present in \"task_dependencies\" but not in \"workflow\". Please fix this.".format(missing_task))

        print("\n")
        return False

    else:

        return True


def check_task_id_naming(workflow):

    # Process workflow
    #
    pattern = "(^[a-zA-Z])([a-zA-Z0-9_]+)([a-zA-Z0-9])$"
    final_result = True

    for item in workflow:

        result = re.match(pattern, item["id"].strip())

        if not result:
            final_result = False
            print("The task ID \"{}\" is malformed. First character must be a letter, you can use letters, numbers and underscores afterwards, but the last character cannot be an underscore.".format(item["id"].strip()))

    return final_result


def build_dag(dag_name):

    fileName = TAILER_SDK_TEMPLATES_PATH + "template_dag.py"
    with open(fileName, "r") as python_file:
        dag = python_file.read()

    dag = \
        dag.replace("{DAG_NAME}",dag_name.strip()).replace("{CURRENT_VERSION}", _current_version)

    return dag


def build_sql_task(
        payload,
        env,
        default_gcp_project_id,
        default_bq_dataset,
        default_bq_data_location,
        default_write_disposition,
        global_path,
        task_id=None,
        task_criticality="critical",
        context_data=None):

    # Check for overridden values : GCP Project ID, Dataset, ...
    #
    gcp_project_id = None
    bq_dataset = None
    write_disposition = None

    print("Building SQL task : {}".format(task_id))

    try:
        gcp_project_id = payload["gcp_project_id"]

    except KeyError:
        gcp_project_id = default_gcp_project_id

    try:
        bq_dataset = payload["bq_dataset"]

    except KeyError:
        bq_dataset = default_bq_dataset

    try:
        write_disposition = payload["write_disposition"]

    except KeyError:
        write_disposition = default_write_disposition

    # Retrieve sql_query_template
    #
    try:
        sql_query_template = payload["sql_query_template"]
    except KeyError:
        sql_query_template = ""

    # Retrieve SQL file to inject into Documentation
    #
    sql_doc = " "

    try:
        # Read the content of the file, UTF-8 converted
        #
        sql_doc = tailer_misc.read_file_as_utf_8("./" + payload["sql_file"])

        if sql_doc is not None:

            sql_doc = sql_doc.decode("utf-8")

            # Do we need to parse the SQL file against the context
            #
            if context_data is not None:
                ret_code, sql_doc = tailer_misc.apply_context(sql_doc, context_data)
                if ret_code is False:
                    raise Exception("Error while applying context to SQL file ....")

            sql_doc = sql_doc.replace('"', '\\"')
        else:
            sql_doc = " "

    except Exception as ex:

        print("Error while processing SQL file : {}".format(payload["sql_file"]))
        print("Exception : \n {} \n".format(ex))


    # Retrieve SQL query cache flag
    #
    try:
        use_query_cache = "use_query_cache = " + str(payload["use_query_cache"])
    except Exception:
        use_query_cache = "use_query_cache = False"

    # Table name becomes optional
    #
    try:
        table_name = "table_name = \"" + payload["table_name"].strip() + "\""
    except Exception:
        table_name = "table_name = None"

    output_payload = """def """ + task_id + """(firestore_com_id, sql_execution_date, sql_parameters=None):

    logging.info("\\n\\nExecuting task with id : {}\\n".format(\"""" + task_id + """\"))

    execute_gbq(sql_id = \"""" + payload["id"] + """\",
        env = \"""" + env + """\",
        dag_name = "TEST",
        gcp_project_id = \"""" + gcp_project_id + """\",
        bq_dataset = \"""" + bq_dataset + """\",
        default_bq_data_location = \"""" + default_bq_data_location + """\",
        """ + table_name + """,
        write_disposition = \"""" + write_disposition + """\",
        sql_query_template = \"""" + sql_query_template + """\",
        local_sql_query = \"\"\"""" + sql_doc + """\"\"\",
        firestore_com_id = firestore_com_id,
        """ + use_query_cache + """,
        task_id = \"""" + task_id + """\",
        sql_execution_date = sql_execution_date,
        sql_parameters=sql_parameters
        )

"""

    return output_payload


def build_copy_bq_table_task(
        payload,
        default_gcp_project_id,
        default_bq_dataset,
        default_bq_data_location,
        task_id=None,
        firestore_com_id=None,
        task_criticality="critical"):

    # Check for overridden values : GCP Project ID, Dataset, ...
    #
    gcp_project_id = None
    bq_dataset = None

    try:
        gcp_project_id = payload["gcp_project_id"]

    except KeyError:
        gcp_project_id = default_gcp_project_id

    try:
        bq_dataset = payload["bq_dataset"]

    except KeyError:
        bq_dataset = default_bq_dataset

    destination_bq_table_date_suffix = "False"
    destination_bq_table_date_suffix_format = ""
    try:
        destination_bq_table_date_suffix = str(payload["destination_bq_table_date_suffix"])
        destination_bq_table_date_suffix_format = payload["destination_bq_table_date_suffix_format"].strip()
    except KeyError:
        print()

    # Prepare output value
    #
    output_payload = ""

    output_payload += """def """ + task_id + """(firestore_com_id):

    logging.info("\\n\\nExecuting task with id : {}\\n".format(\"""" + task_id + """\"))

    execute_bq_copy_table(source_gcp_project_id = \"""" + payload["source_gcp_project_id"].strip() + """\",
        source_bq_dataset = \"""" + payload["source_bq_dataset"].strip() + """\",
        source_bq_table = \"""" + payload["source_bq_table"].strip() + """\",
        destination_gcp_project_id = \"""" + gcp_project_id.strip() + """\",
        destination_bq_dataset = \"""" + bq_dataset.strip() + """\",
        destination_bq_table = \"""" + payload["destination_bq_table"].strip() + """\",
        destination_bq_table_date_suffix = """ + destination_bq_table_date_suffix + """,
        destination_bq_table_date_suffix_format = \"""" + destination_bq_table_date_suffix_format + """\",
        default_bq_data_location = \"""" + default_bq_data_location + """\",
        firestore_com_id=firestore_com_id,
        task_id = \"""" + task_id + """\"
        )

"""

    return output_payload


def build_expectation_task(
        payload,
        default_gcp_project_id,
        default_bq_dataset,
        default_bq_data_location,
        task_id=None,
        firestore_com_id=None,
        task_criticality="critical",
        context_data=None):

    # Check for overridden values : GCP Project ID, Dataset, ...
    #
    gcp_project_id = None
    bq_dataset = None

    try:
        gcp_project_id = payload["gcp_project_id"]

    except KeyError:
        gcp_project_id = default_gcp_project_id

    try:
        bq_dataset = payload["bq_dataset"]

    except KeyError:
        bq_dataset = default_bq_dataset

    # Retrieve SQL file to inject into Documentation
    #
    sql_query = ""

    try:
        # Read the content of the file, UTF-8 converted
        #
        sql_query = tailer_misc.read_file_as_utf_8("./" + payload["sql_file"])

        if sql_query is not None:

            sql_query = sql_query.decode("utf-8")

            # Do we need to parse the SQL file against the context
            #
            if context_data is not None:
                ret_code, sql_query = tailer_misc.apply_context(sql_query, context_data)
                if ret_code is False:
                    raise Exception("Error while applying context to SQL file ....")

            sql_query = sql_query.replace('"', '\\"')
        else:
            sql_query = ""

    except Exception as ex:

        print("Error while processing SQL file : {}".format(payload["sql_file"]))
        print("Exception : \n {} \n".format(ex))

    # Prepare output value
    #
    output_payload = ""

    output_payload += """def """ + task_id + """(firestore_com_id, dag_infos, task_criticality):

    logging.info("\\n\\nExecuting task with id : {}\\n".format(\"""" + task_id + """\"))

    execute_expectation_process(
        gcp_project_id = \"""" + gcp_project_id.strip() + """\",
        bq_dataset = \"""" + bq_dataset.strip() + """\",
        default_bq_data_location = \"""" + default_bq_data_location + """\",
        sql_query = \"\"\"""" + sql_query + """\"\"\",
        task_id = \"""" + task_id + """\",
        firestore_com_id=firestore_com_id,
        dag_infos=dag_infos,
        task_criticality=task_criticality)

"""

    return output_payload


def build_create_bq_table_task(
        payload,
        default_gcp_project_id,
        default_bq_dataset,
        global_path,
        task_id=None,
        task_criticality="critical"):

    # Prepare output value
    output_payload = ""

    # Check for overridden values : GCP Project ID, Dataset, ...
    #
    gcp_project_id = None
    bq_dataset = None

    try:
        gcp_project_id = payload["gcp_project_id"]

    except KeyError:
        gcp_project_id = default_gcp_project_id

    try:
        bq_dataset = payload["bq_dataset"]

    except KeyError:
        bq_dataset = default_bq_dataset

    # Open DDL file
    #
    # Add the parameters inside the current payload to save them down the process.
    #

    # Read the content of the file, UTF-8 converted
    #
    ddl_file_read = tailer_misc.read_file_as_utf_8(payload["ddl_file"])

    try:

        payload_ddl = json.loads(ddl_file_read)

    except Exception as ex:
        print("\nError while parsing DDL JSON file : {}".format(payload["ddl_file"]))
        print(ex)
        return False

    payload["bq_table_description"] = payload_ddl["bq_table_description"]
    payload["bq_table_schema"] = payload_ddl["bq_table_schema"]

    # Optional fields
    #
    try:
        payload["bq_table_clustering_fields"] = payload_ddl["bq_table_clustering_fields"]
    except KeyError:
        print("Optional \"bq_table_clustering_fields\" parameter not provided.")

    try:
        payload["bq_table_timepartitioning_field"] = payload_ddl["bq_table_timepartitioning_field"]
    except KeyError:
        print("Optional \"bq_table_timepartitioning_field\" parameter not provided.")

    try:
        payload["bq_table_timepartitioning_expiration_ms"] = payload_ddl["bq_table_timepartitioning_expiration_ms"]
    except KeyError:
        print("Optional \"bq_table_timepartitioning_expiration_ms\" parameter not provided.")

    try:
        payload["bq_table_timepartitioning_require_partition_filter"] = payload_ddl["bq_table_timepartitioning_require_partition_filter"]
    except KeyError:
        print("Optional \"bq_table_timepartitioning_require_partition_filter\" parameter not provided.")

    # Table description
    #
    table_description = ""
    try:
        table_description = payload["bq_table_description"].strip()
    except KeyError:
        table_description = ""

    # Table Schema
    #
    table_schema = []
    try:
        table_schema = payload["bq_table_schema"]
    except KeyError:
        table_schema = []

    # Retrieve clustering fields options
    # Optional
    #
    bq_table_clustering_fields = None
    try:
        bq_table_clustering_fields = payload['bq_table_clustering_fields']
    except KeyError:
        bq_table_clustering_fields = None

    # Retrieve "force_delete" flag
    #
    force_delete = False
    try:
        force_delete = payload['force_delete']
    except KeyError:
        force_delete = False

    # Retrieve BQ Table Time Partitioning options
    # These are optional
    #
    bq_table_timepartitioning_type = "DAY"
    bq_table_timepartitioning_field = None
    bq_table_timepartitioning_expiration_ms = None
    bq_table_timepartitioning_require_partition_filter = None

    try:
        bq_table_timepartitioning_type = payload["bq_table_timepartitioning_type"].strip().upper()
    except:
        bq_table_timepartitioning_type = "DAY"

    try:
        bq_table_timepartitioning_field = payload['bq_table_timepartitioning_field']
    except:
        bq_table_timepartitioning_field = None

    try:
        bq_table_timepartitioning_expiration_ms = payload['bq_table_timepartitioning_expiration_ms']
    except:
        bq_table_timepartitioning_expiration_ms = None

    try:
        bq_table_timepartitioning_require_partition_filter = payload[
            'bq_table_timepartitioning_require_partition_filter']
    except:
        bq_table_timepartitioning_require_partition_filter = None


    # Passing arguments
    #
    output_payload += """def """ + task_id + """(firestore_com_id, sql_execution_date, sql_parameters=None):

    logging.info("\\n\\nExecuting task with id : {}\\n".format(\"""" + task_id + """\"))

    execute_bq_create_table(gcp_project_id = \"""" + gcp_project_id + """\",
        force_delete = """ + str(force_delete) + """,
        bq_dataset = \"""" + bq_dataset + """\",
        bq_table = \"""" + payload["bq_table"].strip() + """\",
        bq_table_description = \"""" + table_description + """\",
        bq_table_schema = """ + str(table_schema) + """,
        bq_table_clustering_fields = """ + str(bq_table_clustering_fields) + """,
        bq_table_timepartitioning_type = \"""" + str(bq_table_timepartitioning_type) + """\",
        bq_table_timepartitioning_field = """ + (str(bq_table_timepartitioning_field) if (bq_table_timepartitioning_field is None) else ("\"" + bq_table_timepartitioning_field + "\"")) + """,
        bq_table_timepartitioning_expiration_ms = """ + (str(bq_table_timepartitioning_expiration_ms) if (bq_table_timepartitioning_expiration_ms is None) else ("\"" + bq_table_timepartitioning_expiration_ms + "\"")) + """,
        bq_table_timepartitioning_require_partition_filter = """ + (str(bq_table_timepartitioning_require_partition_filter) if (bq_table_timepartitioning_require_partition_filter is None) else ("\"" + bq_table_timepartitioning_require_partition_filter + "\"")) + """,
        firestore_com_id=firestore_com_id,
        sql_execution_date=sql_execution_date,
        task_id = \"""" + task_id + """\",
        sql_parameters=sql_parameters
        )

"""

    return output_payload


def build_vm_launcher_task(
        payload,
        gcp_project_id,
        task_id=None):

    # Infos
    #
    print("Generating VM LAUNCHER task ...")

    # Retrieve parameters
    #
    try:
        vm_delete = payload["vm_delete"]
    except KeyError:
        vm_delete = False

    try:
        vm_working_directory = payload["vm_working_directory"]
    except KeyError:
        vm_working_directory = "/tmp"

    try:
        vm_compute_zone = payload["vm_compute_zone"]
    except KeyError:
        vm_compute_zone = "europe-west1-b"

    try:
        vm_core_number = payload["vm_core_number"]
    except KeyError:
        vm_core_number = "1"

    try:
        vm_memory_amount = payload["vm_memory_amount"]
    except KeyError:
        vm_memory_amount = "4"

    try:
        vm_disk_size = payload["vm_disk_size"]
    except KeyError:
        vm_disk_size = "10"

    # Prepare output value
    #
    output_payload = ""
    output_payload += "    " + payload["id"] + " = "
    output_payload += """FashiondDataGoogleComputeInstanceOperator(
        task_id=\"""" + payload["id"] + """\",
        dag=dag,
        gcp_project_id = \"""" + gcp_project_id + """\",
        script_to_execute =  """ + "{}".format(payload["script_to_execute"])  + """,
        vm_delete = """ + "{}".format(vm_delete)  + """,
        vm_working_directory = """ + "\"{}\"".format(vm_working_directory)  + """,
        vm_compute_zone = """ + "\"{}\"".format(vm_compute_zone)  + """,
        vm_core_number = """ + "\"{}\"".format(vm_core_number)  + """,
        vm_memory_amount = """ + "\"{}\"".format(vm_memory_amount)  + """,
        vm_disk_size = """ + "\"{}\"".format(vm_disk_size)  + """,
        private_key_id = \"COMPOSER_RSA_PRIVATE_KEY_SECRET\"
    )
"""

    return output_payload


def build_python_script_task(
        payload,
        task_id):

    # Infos
    #
    print("Generating Python Script task ...")

    output_payload = """def """ + task_id + """(firestore_com_id):

    logging.info("\\n\\nExecuting task with id : {}\\n".format(\"""" + task_id + """\"))

    execute_python_script(firestore_com_id=firestore_com_id,
        task_id = \"""" + task_id + """\"
        )
"""

    return output_payload


def build_python_script(
    configuration_file,
    read_configuration=None,
    arguments=None,
    context_data=None):

    # Do we run locally ?
    # We need to check the arguments
    #
    local_tasks = []
    if arguments is not None:

        index = 2
        while index < len(arguments):
            local_tasks.append(arguments[index].strip())
            index += 1

    # Default env
    #
    environment = "PROD"

    # Infos
    #
    print("Generating and deploying DAG ...")

    if read_configuration is None:

        print("File to process      : {}".format(configuration_file))

        # Open JSON configuration file
        #
        try:

            # Read the content of the file, UTF-8 converted
            #
            json_file_read = tailer_misc.read_file_as_utf_8(configuration_file)

            json_payload = json.loads(json_file_read)

        except Exception as ex:
            print("Error while parsing JSON file : {}".format(configuration_file))
            print(ex)
            return False

    else:

        json_payload = read_configuration

    # Get path of filename
    #
    global_path = tailer_misc.get_path_from_file(configuration_file)

    # Process environment
    #
    # The value set in the JSON file will always be the greatest priority
    #
    try:

        environment = json_payload["environment"].strip()

    except KeyError as ex:

        environment = environment.strip()

    print("Environment          : {}".format(environment))

    # Process ACCOUNT
    #
    try:
        account = json_payload["account"].strip()
    except KeyError as ex:
        account = "000000"

    print("Account          : {}".format(environment))

    # Extract dag name and add the ENV
    #
    if read_configuration is None:
        dag_name = json_payload["configuration_id"] + "_" + environment
    else:
        dag_name = json_payload["configuration_id"]

    # DEBUG
    #
    print(f"\nDAG name : {dag_name}\n")

    # Extract "start_date" and "schedule_interval"
    #
    dag_start_date = json_payload["start_date"]

    # Extract DAG's description
    #
    dag_description = ""
    try:
        dag_description = json_payload["short_description"]
    except KeyError:
        print("No description provided for the DAG.")
        raise Exception("No description provided for the DAG.")

    # Extract max_active_runs
    #
    max_active_runs = None
    try:
        max_active_runs = json_payload["max_active_runs"]
    except KeyError:
        max_active_runs = 1

    # Extract task_concurrency
    #
    task_concurrency = None
    try:
        task_concurrency = json_payload["task_concurrency"]
    except KeyError:
        task_concurrency = 5

    # Extract catchup
    #
    catchup = False
    try:
        catchup = json_payload["catchup"]
    except KeyError:
        print("Global parameter \"catchup\" not found. Setting to default : False")

    # Check for direct execution
    #
    try:
        direct_execution = json_payload["direct_execution"]
    except Exception:
        direct_execution = False


    # Extract various default values
    #
    default_gcp_project_id = json_payload["default_gcp_project_id"]
    default_bq_dataset = json_payload["default_bq_dataset"]
    default_write_disposition = json_payload["default_write_disposition"]

    try:
        default_bq_data_location = json_payload["default_bq_data_location"]
    except:
        default_bq_data_location = "EU"

    # Extract task dependencies, this should use the Airflow syntax : t1>>t2>>[t31,t32]>>t4
    #
    dag_task_dependencies = json_payload["task_dependencies"]

    # Check that all task declared in "task_dependencies" are properly described in "workflow".
    #
    if check_task_dependencies_vs_workflow(task_dependencies=dag_task_dependencies, workflow=json_payload["workflow"]) is False:
        return False

    # Check that all task IDs are formed properly
    #
    if check_task_id_naming(workflow=json_payload["workflow"]) is False:
        return False

    # Start building the payload
    #
    output_payload = build_dag(dag_name=dag_name)
    
    # Main code
    #

    # Check for Schedule Interval
    #
    if json_payload["schedule_interval"] == "None":
        dag_schedule_interval = "None"
    else:
        dag_schedule_interval = "\"" + json_payload["schedule_interval"] + "\""

    # In the case we run locally and the user asked for specific tasks,
    # we need to filter out which task to process
    #
    # First, we make a copy of the original tasks
    #
    tasks_to_process = copy.deepcopy(json_payload["workflow"])

    if len(local_tasks) > 0:

        tmp_tasks_to_process = []

        for task_requested in local_tasks:

            print("Looking for task : {}".format(task_requested))

            found = False

            for item in tasks_to_process:

                if item["id"].strip() == task_requested:

                    tmp_tasks_to_process.append(copy.deepcopy(item))
                    found = True
                    break

            # No match found
            #
            if found is False:
                print("\nThe task \"{}\" that you've requested does not exist in the configuration workflow. Please check and retry.\n".format(task_requested))
                return

        # Finally overwrite the tasks to process
        #
        tasks_to_process = copy.deepcopy(tmp_tasks_to_process)

    # Process all the tasks
    #
    for item in json_payload["workflow"]:
    #
    #for item in tasks_to_process:

        generated_code = ""

        # Retrieve task criticality
        #
        try:
            task_criticality = item["criticality"].strip()
            if task_criticality not in ["critical", "warning", "transparent", "break", "stop"]:
                print("\nError criticality unknown for task {} : {}\n".format(item["id"].strip(), task_criticality))
                sys.exit(1)
        except Exception:
            task_criticality = "critical"

            # update criticality
            #
            item["criticality"] = task_criticality

        # Retrieve the task type
        #
        task_type = None
        try:
            task_type = item['task_type'].strip()
        except Exception:
            print("Could not retrieve task type for task id : " +
                  item['id'] + ". This task will be considered as SQL query task.")

        if task_type == "copy_gbq_table":
            generated_code = build_copy_bq_table_task(
                item,
                default_gcp_project_id,
                default_bq_dataset,
                default_bq_data_location,
                task_id=item['id'],
                task_criticality=task_criticality)

        elif task_type == "expectation":
            generated_code = build_expectation_task(
                item,
                default_gcp_project_id,
                default_bq_dataset,
                default_bq_data_location,
                task_id=item['id'],
                task_criticality=task_criticality,
                context_data=context_data)

        elif task_type == "create_gbq_table":
            generated_code = build_create_bq_table_task(
                item,
                default_gcp_project_id,
                default_bq_dataset,
                global_path,
                task_id=item['id'],
                task_criticality=task_criticality)

            if generated_code is False:
                return False

        elif task_type == "vm_launcher":
            generated_code = \
                build_vm_launcher_task(
                    item,
                    default_gcp_project_id,
                    task_id=item['id'])

        elif task_type == "python_script":
            generated_code = \
                build_python_script_task(
                    item,
                    task_id=item['id'])

        else:
            generated_code = build_sql_task(
                item,
                environment,
                default_gcp_project_id,
                default_bq_dataset,
                default_bq_data_location,
                default_write_disposition,
                global_path,
                task_id=item['id'],
                task_criticality=task_criticality,
                context_data=context_data)

        output_payload += generated_code + "\n"

    # Add "main" for local execution
    #
    # output_payload += """if __name__ == \"__main__\":"""

    fileName = TAILER_SDK_TEMPLATES_PATH + "template_main.py"
    with open(fileName, "r") as python_file:
        tpMain = python_file.read()

    output_payload += \
        tpMain.replace("{DAG_NAME}",dag_name.strip())\
            .replace("{CURRENT_VERSION}", _current_version)\
            .replace("{DAG_TYPE}", _dag_type)\
            .replace("{ENVIRONMENT}", environment)\
            .replace("{ACCOUNT}", account)\

    # Parse dependencies
    #
    # if len(json_payload["task_dependencies"]) == 0:
    if len(json_payload["workflow"]) <= 1:

        # In that case, we are going to build the execution in the order of the workflow
        #
        mermaid_str = "graph TD;\n"

        parsed_dag_dependencies = []
        for task in tasks_to_process:
            parsed_dag_dependencies.append(task["id"].strip())
            mermaid_str += f"{task['id'].strip()};\n"

        # Convert to base 64
        #
        mermaidGraphB64 = (base64.b64encode(mermaid_str.encode("utf-8"))).decode("utf-8")

    else:

        # We try to parse as a DAG
        #
        parsed_dag_dependencies, mermaidGraphB64 = \
            parse_dag_dependencies(
                dependencies=json_payload["task_dependencies"],
                task_worflow=json_payload["workflow"])

        if parsed_dag_dependencies is None:
            print("\nThere are issues with some of your criticality policies.\n")
            sys.exit(1)

    print("Parsed dependencies : {}".format(parsed_dag_dependencies))
            
    json_payload["flat_tasks_workflow"] = parsed_dag_dependencies
    json_payload["mermaid_graph"] = mermaidGraphB64

    # DEBUG
    #
    print(json_payload["mermaid_graph"])

    # Add the user tasks
    #
    for task in parsed_dag_dependencies:

        # look for task details
        #
        for pr_task in tasks_to_process:

            if task == pr_task["id"]:
                
                # Get task criticality
                #
                task_details = next((item for item in json_payload["workflow"] if item["id"].strip() == task), None)
                if task_details is not None:
                    task_criticality = task_details["criticality"]
                else:
                    task_criticality = "critical"

                output_payload += """
        try:
            task_criticality = \"""" + task_criticality + """\""""

                # Add sql type if missing
                #
                try:
                    task_type = pr_task["task_type"].strip()
                except Exception:
                    task_type = "sql"

                if (task_type == "sql") \
                    or ( task_type == "create_gbq_table") \
                    or ( task_type == "run_gbq_script"):

                    output_payload += """
            """ + task + """(firestore_com_id=firestore_com_id, sql_execution_date=sql_execution_date, sql_parameters=sql_parameters)"""
                elif task_type == "expectation":
                    output_payload += """
            """ + task + """(firestore_com_id=firestore_com_id, dag_infos=pubsub_payload, task_criticality=task_criticality)"""
                else:
                    output_payload += """
            """ + task + """(firestore_com_id=firestore_com_id)"""

                output_payload += """
        except Exception as ex:

            # Set task status to failed
            #
            task_status_failed = {\"""" + task + """\": \"failed\"}
            feedback, message = write_to_firestore(TASK_STATUS_FIRESTORE_COLLECTION, firestore_com_id, task_status_failed, merge=True)

            if feedback is True:
                logging.info("Pushed {} status to : {}".format(task_status_failed, \"""" + task + """\"))
            else:
                logging.error("Error while processing Task Status : {}".format(message))
            
            if task_criticality == "warning":
                failed_task_warning.append(\"""" + task + """\")
                print(\"Warning occured during processing of task : {}\".format(\"""" + task + """\"))
            
            elif task_criticality == "break":
                failed_task_break.append(\"""" + task + """\")
                print(\"Break occured during processing of task : {}\".format(\"""" + task + """\"))
                raise CriticalityBreakException("Break occured !")

            elif task_criticality == "stop":
                failed_task_stop.append(\"""" + task + """\")
                print(\"Stop occured during processing of task : {}\".format(\"""" + task + """\"))
                raise CriticalityStopException("Stop occured !")

            elif task_criticality == "critical":
                failed_task_critical.append(\"""" + task + """\")
                raise ex
            else:
                failed_task_transparent.append(\"""" + task + """\")

"""


    output_payload += """

    except CriticalityBreakException:
        pass

    except CriticalityStopException:
        pass

    except Exception as ex:
        print(\"Exception type : {}\".format(type(ex)))
        print(\"Exception      : {}\".format(ex))

        # Failure
        #
        pubsub_payload[\"status_details\"] = process_status_details(
                                                status="FAILED",
                                                failed_task_critical=failed_task_critical,
                                                failed_task_warning=failed_task_warning,
                                                failed_task_transparent=failed_task_transparent,
                                                failed_task_break=failed_task_break,
                                                failed_task_stop=failed_task_stop)

        pubsub_payload[\"status\"] = \"FAILED\"
        pubsub_payload[\"duration\"] = str(datetime.datetime.now() - start_time)
        publish_dag_info_to_firestore(dag_name=\"""" + dag_name + """\", dag_run_id=dag_run_id, task_id=\"send_dag_infos_to_pubsub_failed\", payload=pubsub_payload)

        exit(0)

    # Success
    #
    pubsub_payload[\"status_details\"] = process_status_details(
                                                status="SUCCESS",
                                                failed_task_critical=failed_task_critical,
                                                failed_task_warning=failed_task_warning,
                                                failed_task_transparent=failed_task_transparent,
                                                failed_task_break=failed_task_break,
                                                failed_task_stop=failed_task_stop)

    pubsub_payload[\"status\"] = \"SUCCESS\"
    pubsub_payload[\"duration\"] = str(datetime.datetime.now() - start_time)
    publish_dag_info_to_firestore(dag_name=\"""" + dag_name + """\", dag_run_id=dag_run_id, task_id=\"send_dag_infos_to_pubsub_success\", payload=pubsub_payload)

    exit(0)
"""

    # Add direct_execution if not present
    #
    try:
        direct_execution = json_payload["direct_execution"]

        if type(direct_execution) is not bool:
            json_payload["direct_execution"] = True

    except Exception:
        json_payload["direct_execution"] = True

    return output_payload, json_payload, dag_name, environment


def process(
        configuration_file,
        read_configuration=None,
        arguments=None,
        tailer_sdk_version=None,
        cmd_line_no_launch=False,
        context_data=None,
        generate_dag_only=False):

    # Force local generation
    # Tailer Engine support
    #
    output_payload_forced, json_payload_forced, dag_name, environment = \
        build_python_script(
            configuration_file,
            read_configuration=read_configuration,
            arguments=None,
            context_data=context_data)

    data = {}
    sql_data = {}
    short_description_data = {}

    index = 0
    for item in json_payload_forced["workflow"]:

        # Info
        print("Processing task : " + item["id"])

        # Retrieve the task type
        #
        task_type = None
        try:
            task_type = item['task_type'].strip()
        except Exception:
            print("Could not retrieve task type for task id : " +
                    item['id'] + ". This task will be considered as SQL query task.")

            task_type = "sql"
            item["task_type"] = task_type
            json_payload_forced["workflow"][index]["task_type"] = task_type

        # retrieve short description
        #
        short_description = ""
        try:
            short_description = item['short_description']
            short_description_data[item["id"]] = short_description
        except KeyError:
            print("No short description found. Continue ...")

        # retrieve Markdown documentation
        #
        try:

            # Read the content of the file, UTF-8 converted
            #
            read_md_file = tailer_misc.read_file_as_utf_8("./" + item["doc_md"])
            json_payload_forced["workflow"][index]['doc_md'] = \
                str(base64.b64encode(read_md_file), "utf-8")

        except KeyError:
            print("No Markdown documentation to process. Continue.")
            json_payload_forced["workflow"][index]['doc_md'] = \
                str(base64.b64encode(bytes("No documentation provided.", "utf-8")), "utf-8")

        except Exception as error:
            print(type(error))
            print("Error while attempting to read Markdown doc : {}. Check your MD file. Continue.".format(error))

            json_payload_forced["workflow"][index]['doc_md'] = \
                str(base64.b64encode(bytes("Error while parsing documentation.", "utf-8")), "utf-8")

        # Specific processing depending of the task type
        #
        if task_type == "copy_gbq_table":
            print("")
        elif task_type == "create_gbq_table":
            print("")
        elif task_type == "vm_launcher":
            print("")
        elif task_type == "python_script":
            print("")
        else:

            # task type :
            # sql
            # expectation

            # Read the content of the file, UTF-8 converted
            #
            sql_file_read = tailer_misc.read_file_as_utf_8("./" + item["sql_file"])

            # Do we need to parse the SQL file against the context
            #
            if context_data is not None:
                ret_code, sql_file_read = tailer_misc.apply_context(sql_file_read.decode("utf-8"), context_data)
                if ret_code is False:
                    raise Exception("Error while applying context to SQL file ....")

                sql_file_read = sql_file_read.encode("utf-8")

            sql_data[item["id"]] = base64.b64encode(sql_file_read)

            if task_type == "sql":

                # Retrieve temporary_table flag
                #
                try:
                    temporary_table = item["temporary_table"]
                except KeyError:
                    # We set the flag to False and save it back to the main payload
                    #
                    json_payload_forced["workflow"][index]['temporary_table'] = False


        index += 1
    # END FOR

    # Add SQL data
    data["sql"] = sql_data

    # Add short descriptions
    data['short_descriptions'] = short_description_data

    # Add Markdown documentation
    #
    data["doc_md"] = json_payload_forced["doc_md"]
    try:
        del json_payload_forced["doc_md"]
    except:
        pass

    # Add account
    data['account'] = json_payload_forced['account']

    # Add environment
    data['environment'] = environment

    # Let's add the whole configuration file as well
    #
    data["configuration"] = json_payload_forced

    # Add info for regular processing by the API
    #
    data["configuration_type"] = _dag_type

    if read_configuration is None:
        data["configuration_id"] = dag_name
    else:
        data["configuration_id"] = json_payload_forced["configuration_id"]

    # Add Flat Task depencies
    #
    data["flat_tasks_workflow"] = json_payload_forced["flat_tasks_workflow"]
    data["mermaid_graph"] = json_payload_forced["mermaid_graph"]

    data["client_type"] = "tailer-sdk"
    data["client_version"] = tailer_sdk_version

    #######################
    # Prepare call to API #
    #######################

    # Get configuration
    #
    print()
    print("Get Tailer configuration ...")
    tailer_configuration = tailer_config.get_tailer_configuration_file()

    # Get firebase user
    #
    print("Get user information ...")
    firebase_user = tailer_auth.get_refreshed_firebase_user(tailer_configuration)

    # Check if the Default GCP Project is there
    #
    try:
        project_profile = json_payload_forced["default_gcp_project_id"].strip()

    except Exception:

        # Get list of project profiles open to the user and ask him to pick one
        #
        ret_code, project_profile = tailer_misc.choose_project_profiles(tailer_configuration, firebase_user)
        if ret_code is False:
            return False

    print("\nThis DAG is going to be deployed to : {}\n".format(project_profile))

    # Check for direct execution
    #
    try:
        direct_execution = json_payload_forced["direct_execution"]
    except Exception:
        direct_execution = False

    # Check if a DAG with the same name is already deployed
    #
    if direct_execution is False:

        try:

            print("Calling Tailer API ...")

            url = tailer_configuration["tailer_api_endpoint"] + "dag-generator-v2"
            payload = {
                "payload": {
                    "resource": "check_dag_exists",
                    "dag_file" : {
                        "name": dag_name + ".py"
                    },
                    "project_profile": project_profile
                }
            }
            headers = {
                "Content-type": "application/json",
                "Authorization": "Bearer " + firebase_user["idToken"]}

            r = requests.put(url, headers=headers, data=json.dumps(payload), verify=tailer_configuration["perform_ssl_verification"])

            if r.status_code == 200:
                response = r.json()
                print(response["payload"]["message"])

                # DAG file already exists
                # We need to ask the user if everything is OK
                #
                while True:
                    print("The DAG {} already exists, do you want to overwrite it y/n ? : ".format(dag_name), end='', flush=True)
                    user_value = input()

                    if user_value == "y":
                        break
                    elif user_value == "n":
                        return True
                    else:
                        continue

            elif r.status_code == 404:
                # Everything is OK
                print(str(r.content, "utf-8"))
            else:
                print("\nError : %s\n" % str(r.content, "utf-8"))
                print(r.json())
                return False

        except Exception as ex:
            print("Error while trying to contact Tailer API ...")
            print(ex)
            return False


    # Process data
    #
    pickled_data = pickle.dumps(data)
    encoded = base64.b64encode(pickled_data)
    encoded = str(encoded, "utf-8")

    # # Process payload
    # #
    # pickled_payload = pickle.dumps(output_payload)
    # encoded_payload = base64.b64encode(pickled_payload)
    # encoded_payload = str(encoded_payload, "utf-8")

    # Process AIRFLOW version
    # Debug
    # with open(dag_name + ".py", "w") as local_out_file:
    #     local_out_file.write(output_payload)
    #     return

    # Process LOCAL payload : Tailer Engine
    # DEBUG
    if generate_dag_only is True:
        with open(dag_name + ".py", "w") as local_out_file:
            local_out_file.write(output_payload_forced)
            return

    pickled_payload = pickle.dumps(output_payload_forced)
    encoded_payload_forced = base64.b64encode(pickled_payload)
    encoded_payload_forced = str(encoded_payload_forced, "utf-8")

    # Ask if the user wants to launch an execution upon successfull upload
    #
    execute_dag = False
    if cmd_line_no_launch is False:
        while True:
            print("Do you want to execute your TTT DAG upon successfull upload ? y/n. Press enter for \"n\" : ", end='', flush=True)
            user_value = input()

            if len(user_value) == 0:
                user_value = "n"

            if user_value == "y":
                execute_dag = True
                break
            elif user_value == "n":
                execute_dag = False
                break

    # Call API
    #
    try:

        print(f"Calling Tailer API to deploy DAG : {dag_name}")

        url = tailer_configuration["tailer_api_endpoint"] + "dag-generator-v2"
        payload = {
            "payload": {
                "resource": encoded,
                "dag_file" : {
                    "name" : dag_name + ".py",
                    "data" : encoded_payload_forced
                },
                "python_script" : {
                    "name" : dag_name + ".py",
                    "data" : encoded_payload_forced
                },
                "project_profile": project_profile,
                "uid": firebase_user["userId"],
                "client_type": "tailer-sdk",
                "client_version": tailer_sdk_version,
                "execute_dag": execute_dag
            }
        }

        # Add headers
        #
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer " + firebase_user["idToken"]}

        r = requests.put(url, headers=headers, data=json.dumps(payload), verify=tailer_configuration["perform_ssl_verification"])

        if r.status_code != 200:
            print("\nERROR : %s\n" % str(r.content, "utf-8"))
            return False
        else:
            response = r.json()
            print(response["payload"]["message"])
            return True

    except Exception as ex:
        print("Error while trying to contact Tailer API ...")
        print(ex)
        return False
