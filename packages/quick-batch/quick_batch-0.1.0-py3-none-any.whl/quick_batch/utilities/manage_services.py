
import time
import docker
from utilities import processor_path, \
    queue_path
from utilities import log_exceptions


@log_exceptions
def scaleup_processor_service(client, num_processors):
    # get processor_service from client
    processor_service = client.services.get('processor_app')

    # if num_processors < 5 scale up immeadiately
    if num_processors < 5:
        processor_service.scale(num_processors)
        return
    else:
        # scale up processor service to num_processors in increments of 5
        for i in range(5, num_processors + 1, 5):
            # report scale update in progress
            print(f"Scaling processor service to {i} instances...")

            # update processor service scale
            processor_service.scale(min(i, num_processors))
            time.sleep(30)

            # report update complete
            print("...complete")

            # break if i >= num_processors
            if i >= num_processors:
                break
        return


@log_exceptions
def remove_service(client, service_name):
    if service_name in [service.name for service in client.services.list()]:
        # remove service
        client.services.get(service_name).remove()

        # remove containers associated with service
        for container in client.containers.list(
                filters={'label': 'com.docker.swarm.service.name=' +
                         service_name}):
            container.remove()


@log_exceptions
def remove_all_services(client):
    for service in client.services.list():
        service.remove()


@log_exceptions
def create_queue_service(client,
                         config_path,
                         input_path):
    # remove queue_app service if it exists
    remove_service(client, 'queue_app')

    # Define the mounts for the service containers
    mounts = [
        docker.types.Mount(
            type='bind',
            source=queue_path + '/queue_app',
            target='/queue_app',
            read_only=True
        ),
        docker.types.Mount(
            type='bind',
            source=config_path,
            target='/my_configs/config.yaml',
            read_only=True
        ),
        docker.types.Mount(
            type='bind',
            source=input_path,
            target='/my_data/input',
            read_only=True
        ),
    ]

    # Define the service configuration
    service_config = {
        'image': 'quick_batch_queue_app',
        'name': 'queue_app',
        'maxreplicas': 1,
        'log_driver': 'json-file',
        'log_driver_options': {'max-size': '10m', 'max-file': '3'},
        'restart_policy': {'Condition': 'none', 'MaxAttempts': 0},
        'mounts': mounts,
        'networks': ['quick_batch_network'],
        'command': ['python', '/queue_app/run.py']
    }

    # Create the service
    client.services.create(**service_config)


@log_exceptions
def create_processor_service(client,
                             config_path,
                             input_path,
                             output_path,
                             processor):
    # remove processor_app service if it exists
    remove_service(client, 'processor_app')

    # Define the mounts for the service containers
    mounts = [
        docker.types.Mount(
            type='bind',
            source=processor_path + '/processor_app',
            target='/processor_app',
            read_only=True
        ),
        docker.types.Mount(
            type='bind',
            source=processor,
            target='/custom_processor/processor.py',
            read_only=False
        ),
        docker.types.Mount(
            type='bind',
            source=config_path,
            target='/my_configs/config.yaml',
            read_only=True
        ),
        docker.types.Mount(
            type='bind',
            source=input_path,
            target='/my_data/input',
            read_only=True
        ),
        docker.types.Mount(
            type='bind',
            source=output_path,
            target='/my_data/output',
            read_only=False
        ),
    ]

    # Define the service configuration
    service_config = {
        'image': 'quick_batch_processor_app',
        'name': 'processor_app',
        'log_driver': 'json-file',
        'log_driver_options': {'max-size': '10m', 'max-file': '3'},
        'restart_policy': {'Condition': 'none', 'MaxAttempts': 0},
        'mounts': mounts,
        'networks': ['quick_batch_network'],
        'command': ['python', '/processor_app/run.py'],
        # 'command': ['tail', '-f', '/dev/null'],
    }

    client.services.create(**service_config)
