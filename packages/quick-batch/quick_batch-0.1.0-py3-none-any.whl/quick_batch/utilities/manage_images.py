import shutil
import os
import docker
from utilities import queue_path, processor_path
from .manage_requirements import make_requirements
from utilities import log_exceptions


# create client for docker
@log_exceptions
def create_client():
    return docker.from_env()


def check_requirements_file(requirements_path):
    if not os.path.isfile(requirements_path):
        return False  # The path is not a file

    if os.path.getsize(requirements_path) == 0:
        return False  # The file is empty

    return True  # The file exists and is not empty


# build processor_app docker image
@log_exceptions
def build_processor_image(client, requirements_path, processor):
    # create container path for requirements
    container_path = os.path.join(processor_path, 'processor_requirements.txt')

    # check if requirements_path is valid and not empty,
    # if so copy to container path
    if check_requirements_file(requirements_path):
        print('INFO: valid requirements file')
        shutil.copyfile(os.path.join(requirements_path), container_path)
    else:
        # create requirements file from processor
        print('INFO: no valid requirements file, creating from processor')
        make_requirements(processor, container_path)

    # create docker image for processor app - including user defined
    # requirements
    client.images.build(path=processor_path, tag='quick_batch_processor_app',
                        quiet=False)

    # remove processor_requirements.txt from the processor_path directory
    os.remove(container_path)


@log_exceptions
def build_queue_image(client):
    # create docker image for queue app - including user defined requirements
    client.images.build(path=queue_path, tag='quick_batch_queue_app',
                        quiet=False)


@log_exceptions
def build_images(client, requirements_path, processor):
    # build queue image
    build_queue_image(client)

    # build processor image
    build_processor_image(client, requirements_path, processor)
