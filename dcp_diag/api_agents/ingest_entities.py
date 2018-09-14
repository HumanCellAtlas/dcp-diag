import json


class Project:
    """
    Model an Ingest Project entity
    """

    def __init__(self, project_id, ingest_api_agent):
        self.project_id = project_id
        self.api = ingest_api_agent
        self.data = None
        self._load()

    @property
    def uuid(self):
        return self.data['uuid']

    def submission_envelopes(self):
        data = self.api.get(self.data['_links']['submissionEnvelopes']['href'])
        return [
            SubmissionEnvelope(data=subm_data, ingest_api_agent=self.api)
            for subm_data in data['_embedded']['submissionEnvelopes']
        ]

    def _load(self):
        self.data = self.api.get(f"/projects/{self.project_id}")


class SubmissionEnvelope:
    """
    Model an Ingest Submission Envelope entity
    """

    # May be primed wih data, or of you supply an ID, we will go get the data

    def __init__(self, ingest_api_agent, envelope_id=None, data=None):
        if not envelope_id and not data:
            raise RuntimeError("either envelope_id or data must be provided")
        self.api = ingest_api_agent
        self.data = None
        if envelope_id:
            self.envelope_id = envelope_id
            self._load()
        else:
            self.data = data
            self.envelope_id = data['_links']['self']['href'].split('/')[-1]

    def __str__(self):
        return f"SubmissionEnvelope\n\tid={self.envelope_id}\n\tuuid={self.uuid}\n\tstatus={self.status}"

    def show_associated(self, entities_to_show, verbose=False):
        self.verbose = verbose
        if 'bundles' in entities_to_show:
            if self.status == 'Complete':
                print("\tBundles:")
                for bundle in self.bundles():
                    print(f"\t\t{bundle}")

        if 'files' in entities_to_show:
                print("\tFiles:")
                for file in self.files():
                    self._output(file)

    def _output(self, thing):
        if self.verbose:
            print("%r" % thing)
        else:
            print(thing)

    def files(self):
        return [File(file_data) for file_data in
                self.api.get_all(self.data['_links']['files']['href'], 'files')]

    def iter_files(self):
        url = self.data['_links']['files']['href']
        for page in self.api.iter_pages(url):
            for file in page['files']:
                yield file

    def reload(self):
        self._load()
        return self

    @property
    def status(self):
        return self.data['submissionState']

    @property
    def uuid(self):
        return self.data['uuid']['uuid']

    def upload_credentials(self):
        """ Return upload area credentials or None if this envelope doesn't have an upload area yet """
        staging_details = self.data.get('stagingDetails', None)
        if staging_details and 'stagingAreaLocation' in staging_details:
            return staging_details.get('stagingAreaLocation', {}).get('value', None)
        return None

    def bundles(self):
        url = self.data['_links']['bundleManifests']['href']
        manifests = self.api.get_all(url, 'bundleManifests')
        return [manifest['bundleUuid'] for manifest in manifests]

    def _load(self):
        self.data = self.api.get(f"/submissionEnvelopes/{self.envelope_id}")


class File:
    """
    Model an Ingest File entity
    """

    def __init__(self, file_data):
        self._data = file_data

    def __str__(self):
        return (f"\t\tfileName {self.name}\n" +
                f"\t\tcloudUrl {self.cloud_url}\n")

    def __repr__(self):
        return json.dumps(self._data, indent=2)

    @property
    def name(self):
        return self._data['fileName']

    @property
    def cloud_url(self):
        return self._data['cloudUrl']
