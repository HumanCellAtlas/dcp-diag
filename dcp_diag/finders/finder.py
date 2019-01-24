class Finder:

    _finders = {}

    @classmethod
    def register(cls, finder_class):
        cls._finders[finder_class.name] = finder_class

    @classmethod
    def factory(cls, finder_name, deployment, service_account_key=''):
        for name, finder in cls._finders.items():
            if name == finder_name:
                # TODO: simplify this by switching to OAuth
                if service_account_key:
                    return finder(deployment=deployment, service_account_key=service_account_key)
                else:
                    return finder(deployment=deployment)
        raise RuntimeError(f"Unknown finder: {finder_name}")
