from termcolor import colored


class Workflow:
    """
    Model an Ingest Project entity
    """

    @classmethod
    def load_by_uuid(cls):
        pass

    def query_by_label(self):
        pass

    def __init__(self, workflow_data=None):
        self.data = workflow_data

    def __str__(self, prefix=""):

        workflow_info = colored(f"{prefix}Workflow {self.uuid}\n", 'green') + \
                        f"{prefix}    name={self.name}\n" \
                        f"{prefix}    status={self.status}\n"

        for label_key, label_value in self.labels:
            workflow_info += f"{prefix}    {label_key}={label_value}"
        return workflow_info

    @property
    def uuid(self):
        return self.data['id']

    @property
    def name(self):
        return self.data.get('name', '')

    @property
    def status(self):
        return self.data['status']

    @property
    def start_time(self):
        return self.data.get('start, ''')

    @property
    def end_time(self):
        return self.data.get('end', '')

    @property
    def submission_time(self):
        return self.data.get('submission', '')

    @property
    def labels(self):
        """

        Returns:

        """
        labels = {
            'bundle-uuid': self.data['labels'].get('bundle-uuid', ''),
            'bundle-version': self.data['labels'].get('bundle-version', ''),
            'project_shortname': self.data['labels'].get('project_shortname', ''),
            'workflow-version': self.data['labels'].get('workflow-version', ''),
            'comment': self.data['labels'].get('comment', ''),
        }
        return labels

    def show_associated(self, entities_to_show, prefix="", verbose=False):
        # Show associated bundle
        if 'bundles' in entities_to_show or 'bundle' in entities_to_show or 'all' in entities_to_show:
            print(f"{prefix}Bundle:")
            print(prefix + "    " + self.labels.get('bundle-uuid'))

        # Show associated project
        # TODO
