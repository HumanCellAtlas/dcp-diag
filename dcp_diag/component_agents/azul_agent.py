import requests
import json


class AzulAgent:
    def __init__(self, deployment):
        self.deployment = deployment
        if self.deployment == 'prod':
            self.azul_service_url = 'https://service.explore.data.humancellatlas.org'
        else:
            self.azul_service_url = f'https://service.{deployment}.explore.data.humancellatlas.org'

    def get_project_bundle_fqids(self, document_id, page_size=1000):
        bundle_fqids = set()

        filters = {
            'projectId': {
                'is': [
                    document_id
                ]
            }
        }
        params = {
            'filters': json.dumps(filters),
            'size': page_size
        }
        url = self.azul_service_url + f'/repository/bundles'
        page = 0

        while True:
            page += 1
            response = requests.get(url, params=params)
            response_json = response.json()
            hit_list = response_json.get('hits', [])

            for content in hit_list:
                bundle_fqids.update(f"{bundle['bundleUuid']}.{bundle['bundleVersion']}"
                                    for bundle in content['bundles'])

            pagination = response_json.get('pagination')
            if pagination is None:
                break

            search_after = pagination.get('search_after')
            search_after_uid = pagination.get('search_after_uid')

            if search_after is None and search_after_uid is None:
                break

            params.update({
                'size': page_size,
                'search_after': search_after,
                'search_after_uid': search_after_uid
            })

        return bundle_fqids
