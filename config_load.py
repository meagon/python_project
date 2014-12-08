

import os
import yaml

from yaml import Loader

import sys
import traceback

CONFIG = {
          "LOG_LEVEL" : "DEBUG",
          "PROJECT_NAME" : "YAML_LEARN",
          "PROJECT" : "project" ,
}

def load_config( CONFIG):
    try:
        configure_file_path = os.path.join(os.path.dirname(__file__), "config.yaml" )
        LOCAL_CONFIG = yaml.load(stream = file( configure_file_path), Loader = Loader )
        stream.close()
        CONFIG.update(LOCAL_CONFIG)
        return CONFIG
    except Exception as error:
        traceback.print_exc()
        print(str(error))

if __name__ == "__main__":
    config = CONFIG
#    assert False

    CONFIG = load_config(CONFIG)
    print(CONFIG)
    print ("level = %s" % CONFIG["LOG_LEVEL"] )
    print("Project name =%s" % CONFIG["PROJECT"])
