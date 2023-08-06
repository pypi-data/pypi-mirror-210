import logging
from abc import ABC, abstractmethod
from pyutils.extender.framework import interface
from pyutils.extender.constants import *
from pyutils.structures import reflect as reflect_util
import argparse


class GenericCmdHandler(ABC):

    def __init__(self, key, context):
        self.key = key
        self.context = context

    # return (result, error) tuple
    @abstractmethod
    def handle(self, *keys): pass


class GenericCommand(interface.Command):

    def __init__(self, key, context, handlers):
        super().__init__(key, context)
        self.__handlers = dict()
        self.__args_parser = argparse.ArgumentParser()
        for handle_key, handler_conf_dict in handlers.items():
            clazz = handler_conf_dict.get(CONF_KEY_CLASS)
            if clazz is None:
                raise RuntimeError(
                    "'{}' field is required for handler {} in command {}".format(CONF_KEY_CLASS, handle_key, self.key))
            handler_constructor_fn = reflect_util.reflect_fn(clazz)
            init_args_dict = {CONF_KEY_KEY: handle_key, CONF_KEY_CONTEXT: context}
            init_args = handler_conf_dict.get(CONF_KEY_INIT_ARGS)
            if init_args is not None:
                init_args_dict.update(init_args)
            handler = handler_constructor_fn(**init_args_dict)
            handle_args_conf = handler_conf_dict.get(CONF_KEY_HANDLER_ARGS_CONF)
            if handle_args_conf is None:
                raise RuntimeError("'{}' field is required for handler {} in command {}".format(
                    CONF_KEY_HANDLER_ARGS_CONF, handle_key, self.key))
            if handle_key not in handle_args_conf:
                raise RuntimeError(
                    "handle_key '{}' must be defined in handle_args_conf for handler {} in command {}".format(
                        handle_key, handle_key, self.key))
            group_desc = handler_conf_dict.get(CONF_KEY_GROUP_DESC)
            group = None
            if group_desc is not None:
                group = self.__args_parser.add_argument_group(group_desc)
            handle_arg_names = list()
            for handle_arg_key, handle_arg_conf_dict in handle_args_conf.items():
                if CONF_KEY_TYPE in handle_arg_conf_dict:
                    handle_arg_conf_dict[CONF_KEY_TYPE] = reflect_util.reflect_fn(handle_arg_conf_dict[CONF_KEY_TYPE])
                new_action = '-{}'.format(handle_arg_key)
                if new_action not in self.__args_parser._option_string_actions:
                    if group is not None:
                        group.add_argument(new_action, **handle_arg_conf_dict)
                    else:
                        self.__args_parser.add_argument(new_action, **handle_arg_conf_dict)
                # else:
                #     logging.debug("skip duplicated argument {}".format(handle_arg_key))
                handle_arg_names.append(
                    handle_arg_key if handle_arg_conf_dict.get(CONF_KEY_DEST) is None
                    else handle_arg_conf_dict.get(CONF_KEY_DEST))
            self.__handlers[handle_key] = (handler, handle_arg_names)
            # logging.debug("registered handle key {}".format(handle_key))

    def run(self, args):
        # parse arguments
        parsed_args, _ = self.__args_parser.parse_known_args(args)
        for handle_key, handler_arg_names_tuple in self.__handlers.items():
            should_handle = getattr(parsed_args, handle_key)
            if should_handle:
                handler = handler_arg_names_tuple[0]
                handle_arg_names = handler_arg_names_tuple[1]
                handle_arg_values = list()
                for handle_arg_name in handle_arg_names:
                    handle_arg_values.append(getattr(parsed_args, handle_arg_name))
                output, err = handler.handle(*handle_arg_values)
                return output, err
        return None, RuntimeError('failed to run {} command with args: {}\n{}'
                                  .format(self.key, args, self.__args_parser.format_help()))
