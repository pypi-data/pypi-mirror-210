from __future__ import print_function

import alchemite_apiclient as client
from alchemite_apiclient.extensions import Configuration

configuration = Configuration()
api_default = client.DefaultApi(client.ApiClient(configuration))
api_models = client.ModelsApi(client.ApiClient(configuration))
api_datasets = client.DatasetsApi(client.ApiClient(configuration))

# Provide path to the JSON containing your credentials
configuration.credentials = "credentials.json"

model_id_to_delete = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

# Can iterate through all models and delete a model with a particular ID.
# IDs are unique to each model and dataset so this guarantees we only delete
# the one model we want.
for model in api_models.models_get():
    if model.id == model_id_to_delete:
        print("deleting", model.id, model.name)
        api_models.models_id_delete(model.id)

# Datasets can also be deleted in a similar way
dataset_id_to_delete = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
for dataset in api_datasets.datasets_get():
    if dataset.id == dataset_id_to_delete:
        print("deleting", dataset.id, dataset.name)
        api_datasets.datasets_id_delete(dataset.id)
