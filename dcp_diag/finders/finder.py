class Finder:

    _finders = {}

    @classmethod
    def register(cls, finder_class):
        cls._finders[finder_class.name] = finder_class

    @classmethod
    def factory(cls, finder_name, deployment, **args):
        for name, finder in cls._finders.items():
            if name == finder_name:
                return finder(deployment=deployment, **args)
        raise RuntimeError(f"Unknown finder: {finder_name}")
