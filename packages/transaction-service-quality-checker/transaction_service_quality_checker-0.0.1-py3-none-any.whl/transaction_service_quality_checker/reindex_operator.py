import kopf
import kubernetes
import tempfile
import subprocess
import os
import logging
import yaml
import json
from dotenv import load_dotenv
from comparer import Comparer
from addresses_map import AddressesMap
from kubernetes import watch, client
from block_creation import BlockCreation

@kopf.on.create('app.example.com', 'v1alpha1', 'reindexes')
def create_fn(body, meta, spec, **kwargs):
    json_file = spec.get('json_file')

    if not json_file:
        raise kopf.PermanentError("JSON file must be provided.")

    # Setup env var for checker
    balance_in_usd_percentage_threshold = spec.get('balance_in_usd_percentage_threshold')

    log_level = 'DEBUG'
    logging.basicConfig(level=log_level)

    # TODO: use checker an external package
    # TODO: Use spec to set the output location file
    problematic_addresses = check_addresses(json_file, balance_in_usd_percentage_threshold, "output_metrics_2.json")

    earliest_block = spec.get('start_block')

    # Set etherscan api in a config map env var
    etherscan_api_key = spec.get('etherscan_api_key')
    if not etherscan_api_key:
        raise kopf.PermanentError("etherscan_api_key must be provided.")

    if not earliest_block:
        earliest_block = get_problematic_addresses_earliest_creation_block(etherscan_api_key, problematic_addresses)

    # Create job definition for re-indexing master copies for problematic addresses
    reindex_job_definition_master_copies = create_job_definition(json_file, problematic_addresses, earliest_block, "reindex_master_copies")

    kubernetes.config.load_kube_config()
    # Create and submit the Kubernetes Job
    create_job_kubernetes_api(json_file, reindex_job_definition_master_copies)

    # Create job definition for re-indexing erc20 events for problematic addresses
    # reindex_job_definition_erc20 = create_job_definition(json_file, problematic_addresses, earliest_block, "reindex_erc20")

    # # Create and submit the Kubernetes Job
    # create_job_kubernetes_api(json_file, reindex_job_definition_erc20)



def create_job_kubernetes_api(json_file, job_definition):
    # Create the job using the Kubernetes API
    batch_v1 = kubernetes.client.BatchV1Api()
    try:
        created_job = batch_v1.create_namespaced_job(namespace="mainnet", body=job_definition)
        print(f"Job created: {created_job.metadata.name}")
    except kubernetes.client.rest.ApiException as e:
        print(f"Failed to create job for {json_file}: {e}")

    wait_for_job_completion(batch_v1, job_definition)

def create_job_definition(json_file, problematic_addresses, earliest_block_creation, job_type):
    with open("k8s/reindex-job-template.yaml", "r") as f:
        job_definition = yaml.safe_load(f)

    # Customize the job name based on the JSON file
    job_definition["metadata"]["generateName"] += f"{json_file.split('.')[0].replace('_', '-')}-"

    # Define type of reindex job
    job_definition["spec"]["template"]["spec"]["containers"][0]["command"].append(str(job_type))

    for address in problematic_addresses:
        job_definition["spec"]["template"]["spec"]["containers"][0]["args"].append(str(address))
    job_definition["spec"]["template"]["spec"]["containers"][0]["args"].append("--block-process-limit")
    block_process_limit = 1000
    job_definition["spec"]["template"]["spec"]["containers"][0]["args"].append(str(block_process_limit))
    job_definition["spec"]["template"]["spec"]["containers"][0]["args"].append("--from-block-number")
    block_number= earliest_block_creation
    job_definition["spec"]["template"]["spec"]["containers"][0]["args"].append(str(block_number))

    logging.info(f"Job manifest to be created:\n {job_definition}")
    return job_definition


def check_addresses(path_to_json: str, balance_in_usd_percentage_threshold: float, output_results: str):
    # Load the map from the JSON file
    map1 = AddressesMap(path_to_json)
    # Compare
    comp = Comparer(domain_a=map1.get_domain_a(), domain_b=map1.get_domain_b(), log=logging,
                    balance_in_usd_percentage_threshold=balance_in_usd_percentage_threshold)
    comp.compare_safes(map=map1.get_full_dict())
    # Export metrics
    comp.export_metrics_to_json(output_results)
    # Return list addresses
    return comp.metrics.get_problematic_addresses('safe_transactions_1')

def get_problematic_addresses_earliest_creation_block(etherscan_api_key, addresses: list):
    creation = BlockCreation(etherscan_api_key, log=logging)
    addresses_with_creation_blocks = creation.get_safes_creation_block_from_list(addresses=addresses)
    # Return minimum block number of all problematic addresses
    earliest_block = creation.get_earliest_block_creation(addresses_with_creation_blocks)
    return earliest_block


def wait_for_job_completion(api_instance, job_definition):
    try:
        w = watch.Watch()
        core_api_instance = client.CoreV1Api()  # for reading logs

        for event in w.stream(api_instance.list_namespaced_job, namespace="mainnet"):
            job = event['object']
            if job.metadata.name.startswith(job_definition["metadata"]["generateName"]):
                if job.status.succeeded == 1:
                    print(f"Job {job.metadata.name} completed successfully")
                    w.stop()
                if job.status.failed == 1:
                    print(f"Job {job.metadata.name} failed")
                    # # Retrieve pod name from job
                    # pods_list = core_api_instance.list_namespaced_pod(namespace="default",
                    #                                                  label_selector=f"job-name={job.metadata.name}")
                    # if pods_list.items:
                    #     pod_name = pods_list.items[0].metadata.name

                    #     # Get the logs from the pod
                    #     pod_logs = core_api_instance.read_namespaced_pod_log(name=pod_name, namespace="default")

                    #     # Print the last 10 lines of the logs
                    #     print("\nLast 10 lines of logs:")
                    #     print("\n".join(pod_logs.split("\n")[-10:]))
                    # else:
                    #     print("No pods found for this job")

                    w.stop()
    except Exception as e:
        print(f"Error when watching job: {e}")