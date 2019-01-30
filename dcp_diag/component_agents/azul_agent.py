import requests
import urllib


class AzulAgent:
    def __init__(self, deployment):
        self.deployment = deployment
        if self.deployment == 'prod':
            self.azul_service_url = 'https://service.explore.data.humancellatlas.org'
        else:
            self.azul_service_url = f'https://service.{deployment}.explore.data.humancellatlas.org'

    def get_project_bundle_fqids(self, document_id):
        page_size = 1000
        bundle_fqids = set()

        filter_dict = urllib.parse.quote('{"file":{"projectId":{"is":["' + document_id + '"]}}}')
        base_url = self.azul_service_url + f'/repository/files?filters={filter_dict}&order=desc&sort=entryId'
        url = base_url + f'&size={page_size}&order=desc'
        page = 0

        while True:
            page += 1
            response = requests.get(url)
            response_json = response.json()
            hit_list = response_json.get('hits', [])

            for content in hit_list:
                bundle_fqids.update(f"{bundle['bundleUuid']}.{bundle['bundleVersion']}"
                                    for bundle in content['bundles'])

            search_after = response_json['pagination']['search_after']
            search_after_uid = response_json['pagination']['search_after_uid']

            if search_after is None and search_after_uid is None:
                break
            else:
                url = base_url + f'&size={page_size}&search_after={search_after}&search_after_uid={search_after_uid}'

        return bundle_fqids
