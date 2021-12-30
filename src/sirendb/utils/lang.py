class DelayedInstance:
    def __init__(self):
        self.__local = None

    def set_instance(self, instance):
        self.__local = instance

    def __getattr__(self, name):
        if name in ('__init__', 'init_app', 'set_instance'):
            return self.__dict__[name]
        elif name == '__local':
            return self.__local
        else:
            return getattr(self.__local, name)
