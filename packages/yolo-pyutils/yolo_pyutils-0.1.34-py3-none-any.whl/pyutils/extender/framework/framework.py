import logging
import logging.config
import os
import yaml
from pyutils.structures import reflect as reflect_util
from pyutils.scheduling import event_driven
from pyutils.extender.constants import *
from pyutils.extender.framework import context, config, error


class Framework:

    def __init__(self, executing_path, conf_file, log_conf_file, console_log_level):
        self.__conf_file = conf_file
        self.__log_conf_file = log_conf_file
        self.__console_log_level = console_log_level
        self.__config = config.Config()
        self.__dispatcher = event_driven.Dispatcher()
        self.__context = context.Context(self.__config, executing_path, self.__dispatcher)

    def init(self):
        # init config
        self.__config.load_yaml(self.__conf_file)
        # init logging
        log_file_path = self.__config.get_or_default(DEFAULT_LOG_FILE_PATH, CONF_KEY_LOG_FILE_PATH)
        if not os.path.isabs(log_file_path):
            log_file_path = os.path.join(self.__context.get_executing_path(), log_file_path)
        init_logging(self.__context.get_executing_path(), self.__log_conf_file, log_file_path, self.__console_log_level)
        # init extendable instances
        add_extendable_instances(self.__context, [CONF_KEY_PLUGINS, CONF_KEY_COMPONENTS], self.__context.add_component)
        add_extendable_instances(self.__context, [CONF_KEY_PLUGINS, CONF_KEY_SERVICES], self.__context.add_service)
        add_extendable_instances(self.__context, [CONF_KEY_PLUGINS, CONF_KEY_COMMANDS], self.__context.add_command)

    def get_context(self):
        return self.__context

    def start(self):
        # start dispatcher
        for service in self.__context.get_services().values():
            for event_clazz in service.get_applicable_event_classes():
                self.__dispatcher.register(event_clazz, service)
        self.__dispatcher.start()
        # start components and services in ascending order
        for key, component in self.__context.get_components().items():
            err = component.start()
            if err:
                raise RuntimeError("failed to start component {}: {}".format(key, str(err)))
        for service in self.__context.get_services().values():
            err = service.start()
            if err:
                err_msg = "failed to start service {}: {}".format(key, str(err))
                logging.error(err_msg)
                raise RuntimeError(err_msg)

    def stop(self):
        # stop services, components in descending order
        for service in reversed(self.__context.get_services().values()):
            service.stop()
        for component in reversed(self.__context.get_components().values()):
            component.stop()
        # stop dispatcher
        self.__dispatcher.stop()

    def execute_cmd(self, args):
        # run command
        commands = self.__context.get_commands()
        if len(args) == 0:
            logging.error("no command specified! valid commands: {}".format(list(commands.keys())))
            return EXIT_CODE_RUN_ARGUMENTS_ERROR
        command_name = args[0]
        command_args = args[1:]
        command = commands.get(command_name)
        if command is None:
            logging.error("command {} not found! valid commands: {}".format(command_name, list(commands.keys())))
            return EXIT_CODE_RUN_ARGUMENTS_ERROR
        try:
            output, err = command.run(command_args)
        except Exception as e:
            logging.debug("failed to run command {}".format(command_args), exc_info=e)
            err = e
        except SystemExit as exit_code:
            logging.debug("failed to run command {}, exit_code={}".format(command_args, exit_code))
            return EXIT_CODE_UNKNOWN
        if err is not None:
            logging.error("failed to run command {}, error message: {}".format(command_args, str(err)))
            return EXIT_CODE_RUN_ARGUMENTS_ERROR if isinstance(err, error.ArgumentsError) else\
                EXIT_CODE_CONF_ERROR if isinstance(err, error.ConfError) else EXIT_CODE_UNKNOWN
        if isinstance(output, str):
            print(output)
        elif isinstance(output, list):
            for index, item in enumerate(output):
                print(item)
        return EXIT_CODE_NORMAL


def init_logging(executing_path, log_conf_file, log_file_path, console_log_level):
    if log_conf_file:
        with open(log_conf_file, 'r') as f_conf:
            dict_conf = yaml.load(f_conf, Loader=yaml.FullLoader)
        handlers = dict_conf.get('handlers')
        # initialize logs directory if necessary
        for handler in handlers.values():
            handler_class = handler.get('class')
            if handler_class.find('FileHandler') != -1:
                log_dir = os.path.dirname(log_file_path)
                if not os.path.isabs(log_dir):
                    log_dir = os.path.join(executing_path, log_dir)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                handler['filename'] = os.path.join(log_dir, os.path.basename(log_file_path))
        logging.config.dictConfig(dict_conf)
        # set log level for console
        root = logging.getLogger()
        for handler in root.handlers:
            if handler.name == 'console':
                handler.setLevel(console_log_level)
                break
    else:
        logging.info("logging to console since not found the log config file")


def init_context(executing_path, conf_file):
    ctx = context.Context(executing_path, conf_file)
    err = ctx.init()
    if err is not None:
        logging.error("{}. exit!".format(err))
        exit(EXIT_CODE_CONF_ERROR)
    return ctx


def add_extendable_instances(context, conf_keys, add_fn):
    conf = context.get_conf().get(*conf_keys)
    if not conf:
        logging.info("skip adding extendable instances of type {} without conf".format(conf_keys))
        return
    if isinstance(conf, list):
        conf_dict = dict()
        for conf_item in conf:
            key = conf_item.get(CONF_KEY_KEY)
            conf_dict[key] = conf_item
        conf = conf_dict
    for key, conf_item in conf.items():
        init_args = {CONF_KEY_KEY: key, CONF_KEY_CONTEXT: context}
        configured_init_args = conf_item.get(CONF_KEY_INIT_ARGS)
        if configured_init_args is not None:
            init_args.update(configured_init_args)
        try:
            construct_fn = reflect_util.reflect_fn(conf_item.get(CONF_KEY_CLASS))
            instance = construct_fn(**init_args)
        except Exception as ex:
            logging.error("failed to initialize instance: key={}, err={}".format(key, ex))
            exit(EXIT_CODE_CONF_ERROR)
        add_fn(key, instance)
