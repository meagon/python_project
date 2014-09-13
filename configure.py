

import os
from yaml import Loader






CONFIG = {
          "LOG_LEVEL " : "DEBUG",
          "PROJECT_NAME" : "YAML_LEARN",
}


try:
    configure_file_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    configure = yaml.load(stream = file( configure_file_path), Loader = Loader)
    stream.close()
    CONFIG.update(localConf)
except Exception, e:
    print e


if __name__ == "__main__":
    config = CONFIG
    # print config['LOG_LEVEL']
    assert False
    config_file_path = os.path.join(os.path.dirname(__file__), "config.yaml") 
    yaml.dump(config, stream = file(configure_file_path), Dumper = Dumper, explicit_start=True, default_flow_style=False)
    stream.close() 
    print ("level = %s" % CONFIG["LOG_LEVEL"] )
    print("Project name =%s" % CONFIG["PROJECT"])
