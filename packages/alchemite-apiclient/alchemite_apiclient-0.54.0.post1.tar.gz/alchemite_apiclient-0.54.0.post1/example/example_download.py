from __future__ import print_function

import alchemite_apiclient as client
from alchemite_apiclient.extensions import Configuration

configuration = Configuration()
api_datasets = client.DatasetsApi(client.ApiClient(configuration))

# Provide path to the JSON containing your credentials
configuration.credentials = "credentials.json"

dataset_id_to_download = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"

r = api_datasets.datasets_id_download_get(
    dataset_id_to_download, _preload_content=False
)
with open(dataset_id_to_download + ".csv", "w", encoding="UTF-8") as f:
    f.write(r.data.decode())
