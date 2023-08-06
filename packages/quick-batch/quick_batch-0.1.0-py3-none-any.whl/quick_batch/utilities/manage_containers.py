from utilities import base_directory, processor_path, \
    queue_path
from utilities import log_exceptions


# remove all docker containers
@log_exceptions
def remove_all_containers(client):
    for container in client.containers.list(all=True):
        container.remove(force=True)


# start queue_app docker container with interactive terminal
@log_exceptions
def startup_queue_app_container(client, config_path, input_path):
    queue_container = client.containers.run(
        image='quick_batch_queue_app',
        network='quick_batch_network',
        detach=True,
        name='queue_app',
        tty=True,
        stdin_open=True,
        ports={'80/tcp': 80},
        volumes={
            queue_path + '/queue_app':
            {'bind': '/queue_app', 'mode': 'ro'},
            config_path:
            {'bind': '/my_configs/config.yaml', 'mode': 'ro'},
            input_path:
            {'bind': '/my_data/input', 'mode': 'ro'}
        },
        command='python /queue_app/run.py'
        )

    return queue_container


# start queue_app docker container with interactive terminal
@log_exceptions
def startup_processor_app(client, config_path, input_path, output_path):
    # start processor_app docker container with interactive terminal
    processor_container = client.containers.run(
        image='quick_batch_processor_app',
        network='quick_batch_network',
        detach=True,
        name='processor_app',
        tty=True,
        stdin_open=True,
        ports={'80/tcp': None},
        volumes={
            processor_path + '/processor_app':
            {'bind': '/processor_app', 'mode': 'ro'},
            config_path:
            {'bind': '/my_configs/config.yaml', 'mode': 'ro'},
            input_path:
            {'bind': '/my_data/input', 'mode': 'ro'},
            output_path:
            {'bind': '/my_data/output', 'mode': 'rw'},
            base_directory + '/processor.py':
            {'bind': '/processor_app/processor.py', 'mode': 'ro'},
        },
        command='python /processor_app/run.py'
        )

    return processor_container
