import shutil
import os
import docker
from utilities import queue_path, processor_path
from .manage_requirements import make_requirements
from .manage_requirements import infer_requirements
from .manage_dockerfile import check_requirements_copy_and_install
from utilities import log_exceptions
import subprocess


# create client for docker
@log_exceptions
def create_client():
    return docker.from_env()


@log_exceptions
def pull_and_tag_image(client, image_name, new_tag):
    try:
        print('INFO: Pulling and tagging image...')

        # Try tagging local image
        try: 
            image = client.images.get(image_name)
            tag_success = image.tag(new_tag)
            
            if tag_success:
                print('SUCCESS: Tagging local image successful!')
                return True
        except docker.errors.ImageNotFound:
            pass

        # Pull the image
        pulled_image = client.images.pull(image_name)

        # Tag the pulled image with a new name
        tagged_image = pulled_image.tag(new_tag)
        
        print('SUCCESS: Pulling and tagging image complete!')
        return True

    except docker.errors.APIError as e:
        print(f"FAILURE: Error occurred while pulling and tagging the image: {e}")
        return False


def check_requirements_file(requirements_path):
    if not os.path.isfile(requirements_path):
        return False  # The path is not a file

    if os.path.getsize(requirements_path) == 0:
        return False  # The file is empty

    return True  # The file exists and is not empty


# build processor_app docker image
@log_exceptions
def build_processor_image(client,
                          dockerfile_path,
                          requirements_path,
                          processor):

    # create container path for dockerfile
    container_dockerfile_path = os.path.join(processor_path, 'Dockerfile')

    # copy dockerfile to processor_path directory
    shutil.copy(dockerfile_path, container_dockerfile_path)

    # check if requirements.txt is being copied and installed in dockerfile
    check_requirements_copy_and_install(container_dockerfile_path)

    # create container path for requirements
    container_requirements_path = os.path.join(processor_path,
                                               'requirements.txt')

    # check if requirements_path is valid and not empty,
    # if so copy to container path
    if check_requirements_file(requirements_path):
        print('INFO: valid requirements file')
        make_requirements(requirements_path, container_requirements_path)
    else:
        # create requirements file from processor
        print('INFO: no valid requirements file, attempting to create '
              'from processor')
        infer_requirements(processor, container_requirements_path)

    # create docker image for processor app - including user defined
    def stream_build_logs(path, tag):
        command = ["docker", "build", "-t", tag, path]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Print build logs in real-time
        for line in process.stdout:
            print(line, end='')

        # Wait for the build process to complete
        process.wait()

        # Check the exit code
        if process.returncode == 0:
            print("SUCCESS: Image build completed successfully!")
        else:
            print("FAILURE: Image build failed!")

    # Usage example
    print('INFO: building processor image...')
    print('===============================')
    print('===============================')
    stream_build_logs(processor_path, 'quick_batch_processor_app')
    print('===============================')
    print('===============================')

    # Build completed
    print("INFO: ... processor image build completed!")

    # remove dockerfile from the processor_path directory
    os.remove(container_dockerfile_path)

    # remove processor_requirements.txt from the processor_path directory
    os.remove(container_requirements_path)


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
