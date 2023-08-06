import yaml


class Config:

    def __init__(self):
        self.configs = None

    def load_yaml(self, config_file):
        if config_file is None:
            raise RuntimeError("config file is required but got None".format(config_file))
        with open(config_file, 'rb') as f:
            self.configs = yaml.load(f, Loader=yaml.FullLoader)

    def get(self, *conf_names):
        cur_conf = self.configs
        for conf_name in conf_names:
            cur_conf = cur_conf.get(conf_name, None)
            if cur_conf is None:
                break
        return cur_conf

    def get_or_default(self, default_value, *conf_names):
        result = self.get(*conf_names)
        if result is None:
            return default_value
        return result
