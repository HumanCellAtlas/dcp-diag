from urllib.parse import urlencode

import requests


class HateoasAgent:

    def __init__(self, api_url_base, auth_headers={}):
        self.api_url_base = api_url_base
        self.auth_headers = auth_headers

    """
    Get a collection resource.
    Iterates through all pages gathering results and returns a list.
    """
    def get_all(self, path_or_url, result_element_we_are_interested_in):
        results = []
        for page in self.iter_pages(path_or_url):
            results += page[result_element_we_are_interested_in]
        return results

    """
    Iterate through a collection using HATEOAS pagination, yielding pages.
    """
    def iter_pages(self, path_or_url, page_size=100, sort=None):
        url_params = {'size': page_size}
        if sort:
            url_params['sort'] = sort
        path_or_url += '?' + urlencode(url_params)

        while True:
            data = self.get(path_or_url)
            if '_embedded' not in data:
                break

            yield data['_embedded']

            if 'next' in data['_links']:
                path_or_url = data['_links']['next']['href']
            else:
                break

    """
    Get a singleton resource.
    """
    def get(self, path_or_url):
        if path_or_url.startswith('http'):
            url = path_or_url
        else:
            url = f"{self.api_url_base}{path_or_url}"

        response = requests.get(url, headers=self.auth_headers)

        if response.ok:
            return response.json()
        else:
            raise RuntimeError(f"GET {url} got {response}")
