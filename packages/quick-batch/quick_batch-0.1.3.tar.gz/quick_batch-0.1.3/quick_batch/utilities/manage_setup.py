import time
from utilities import log_exceptions
from utilities import manage_images
from utilities.param_checks import setup_logger
from utilities.param_checks import check_config
from utilities.param_checks import check_config_data_paths
from utilities.param_checks import check_processor
from utilities.manage_containers import remove_all_containers
from utilities.manage_networks import remove_network
from utilities.manage_services import remove_all_services
from utilities.manage_swarm import leave_swarm
from utilities.manage_swarm import create_swarm
from utilities.manage_networks import create_network
from utilities.manage_services import create_queue_service
from utilities.manage_services import create_processor_service
from utilities.manage_queue import monitor_queue_app_containers


@log_exceptions
def setup_client(config):
    # setup logger
    logger = setup_logger(config)

    # check that input files exist
    check_config(config)

    # check config data paths
    input_path, output_path, processor, num_processors, \
        requirements_path = check_config_data_paths(config)

    # check processor
    check_processor(processor)

    # create docker client
    client = manage_images.create_client()

    # build images
    manage_images.build_processor_image(client, requirements_path, processor)
    manage_images.build_queue_image(client)

    return client, input_path, output_path, processor, num_processors, logger


@log_exceptions
def reset_workspace(client):
    try:
        # remove all services
        remove_all_services(client)
        time.sleep(5)
    except Exception as e:
        print(f"Error removing services: {e}")

    # remove all containers
    remove_all_containers(client)

    # remove network
    remove_network(client)

    # remove swarms
    leave_swarm(client)


@log_exceptions
def setup_workspace(client,
                    config,
                    processor,
                    input_path,
                    output_path):
    # create new swarm
    create_swarm(client)

    # create network
    create_network(client)
    time.sleep(5)

    # create queue service
    create_queue_service(client, config, input_path)
    monitor_queue_app_containers(client)
    time.sleep(10)

    # create processor service
    create_processor_service(client, config, input_path, output_path,
                             processor)
