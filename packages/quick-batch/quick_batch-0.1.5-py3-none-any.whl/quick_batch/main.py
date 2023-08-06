import sys
import fire
from utilities.manage_setup import setup_client
from utilities.manage_setup import reset_workspace
from utilities.manage_setup import setup_workspace
from utilities.manage_queue import monitor_queue
from utilities.manage_services import scaleup_processor_service


def main(config=None):
    # check config - used as script fire will not be used
    if not config:
        config = sys.argv[1]

    # setup
    client, input_path, output_path, processor, num_processors, \
        logger = setup_client(config)

    # reset workspace
    reset_workspace(client)

    # create workspace
    setup_workspace(client, config,  processor, input_path, output_path)

    # scale up processor service
    scaleup_processor_service(client, num_processors)

    # monitor queue
    monitor_queue(client)

    # close log
    logger.close_log()


if __name__ == '__main__':
    fire.Fire(main)
