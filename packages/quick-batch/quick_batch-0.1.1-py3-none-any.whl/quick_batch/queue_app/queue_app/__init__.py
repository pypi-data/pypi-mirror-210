from flask import Flask
import queues_init
import subprocess
import yaml
import logging
import sys


def create():
    app = Flask(__name__)

    # Configure logging
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.DEBUG)

    # attach container id
    container_id = subprocess.Popen('hostname',
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE).communicate()[0]

    container_id = eval(str(container_id)).decode('utf-8').strip('\n')
    app.container_id = container_id

    # import config variables
    with open('/my_configs/config.yaml', "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    # extract required params
    app.path_to_feed = '/my_data/input'
    app.feed_rate = config["queue"]["feed_rate"]
    app.order_files = config["queue"]["order_files"]
    app.empty_trigger = 0

    # instantiate queues
    queues_init.create_queues(app)

    # report startup success to terminal
    print(f'queue_app running on container {app.container_id} has started',
          flush=True)

    return app


app = create()
import apis # noqa
