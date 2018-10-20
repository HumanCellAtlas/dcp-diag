import json
import os
from urllib.parse import urlencode

import requests


class DataStoreAgent:

    DSS_API_URL_TEMPLATE = "https://dss.{deployment}.data.humancellatlas.org/v1"

    def __init__(self, deployment):
        self.deployment = deployment
        self.dss_url = self.DSS_API_URL_TEMPLATE.format(deployment=deployment)

    def search(self, query, replica='aws'):
        results = []
        url = f"{self.dss_url}/search"
        query_params = { 'replica': replica}
        query_json = {'es_query': query}
        for response in self.iter_pages(url, query_params=query_params, json_body=query_json):
            results.extend(response['results'])
        return results

    def iter_pages(self, url, query_params={}, json_body={}, page_size=500):
        params = query_params.copy()
        params['per_page'] = page_size
        full_url = url + '?' + urlencode(params)

        while True:
            response = requests.post(full_url, json=json_body)
            yield response.json()

            link_header = response.headers.get('link', None)
            if link_header:
                next_link = link_header.split(';')[0]
                full_url = next_link.strip('<').strip('>')
            else:
                break

    def download_bundle(self, bundle_uuid, target_folder):
        print(f"Downloading bundle {bundle_uuid}:")
        manifest = self.bundle_manifest(bundle_uuid)
        bundle_folder = os.path.join(target_folder, bundle_uuid)
        try:
            os.makedirs(bundle_folder)
        except FileExistsError:
            pass

        for f in manifest['bundle']['files']:
            self.download_file(f['uuid'], save_as=os.path.join(bundle_folder, f['name']))
        return bundle_folder

    def bundle_manifest(self, bundle_uuid, replica='aws'):
        url = f"{self.dss_url}/bundles/{bundle_uuid}?replica={replica}"
        response = requests.get(url)
        assert response.ok
        assert response.headers['Content-type'] == 'application/json'
        return json.loads(response.content)

    def download_file(self, file_uuid, save_as, replica='aws'):
        url = f"{self.dss_url}/files/{file_uuid}?replica={replica}"
        print(f"Downloading file {file_uuid} to {save_as}")
        response = requests.get(url, stream=True)
        assert response.ok
        with open(save_as, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
