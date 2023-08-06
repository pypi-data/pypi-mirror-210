from collections import OrderedDict


class Context:

    def __init__(self, conf, executing_path, dispatcher):
        self.__conf = conf
        self.__executing_path = executing_path
        self.__components = OrderedDict()
        self.__services = OrderedDict()
        self.__commands = OrderedDict()
        self.__dispatcher = dispatcher

    def get_conf(self):
        return self.__conf

    def get_executing_path(self):
        return self.__executing_path

    def add_component(self, key, value):
        self.__components[key] = value

    def add_service(self, key, value):
        self.__services[key] = value

    def add_command(self, key, value):
        self.__commands[key] = value

    def get_components(self):
        return self.__components

    def get_services(self):
        return self.__services

    def get_commands(self):
        return self.__commands

    def dispatch(self, event):
        self.__dispatcher.dispatch(event)
