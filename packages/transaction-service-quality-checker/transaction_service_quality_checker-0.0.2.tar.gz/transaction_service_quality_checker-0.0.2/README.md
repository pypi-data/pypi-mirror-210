# Intro

The transaction indexer quality checkers help us compare the response from two infrastructures that support the Safe REST interface.

## Concepts

Through the code, you will see the nomenclature A and b. A represents the source of truth and b represents the infrastructure that you want to compare.
For our purposes, A is Safe and B is our own infra.

### JSON

You can create a JSON file that the address_map.py can read. You can pass the path to the JSON file when instantiate the address_map instance.
Within the JSON, you will need utilize the following fields: 
* "config_domains": the url to the REST service from the config service. You need to define field "a" and "b"
* "chains": a dictionary where the key is the chain id of a blockchain and its value is an array with safe addresses. The addresses don't need to be checksummed for your convenience. 


### Run KOPF

1/ Check if the Custom Resource Definition is up to date in the cluster
If not:
```
k apply -f k8s/reindex-crd.yaml
```

2/ Run Kopf script that will be waiting for any new Reindex CRD job created
```
kopf run reindex_operator.py
```

3/ Create a Reindex CRD object with the parameters to pass the k8s job
- json_file (path to json file that has the addresses to be checked). For now don't use relative path, the json file should be at the root folder.
- etherscan_api_key
- balance_in_usd_percentage_threshold

```
k apply -f k8s/operator/reindex_resource.yaml
```

4/ Verify that the created resource has been processed by the kopf 


### Next steps

* add missing env vars such as a way to modulate logging level