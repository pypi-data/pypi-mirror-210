import json
import time
import sys
from .manage_containers import remove_all_containers
from .manage_networks import remove_network
from .manage_services import remove_all_services
from utilities import log_exceptions


@log_exceptions
# monitor number of containers in queue_app service, return if greater than 0
def monitor_queue_app_containers(client):
    # set 5 minute timeout
    timeout = time.time() + 60 * 5
    time.sleep(5)

    # run check_queue_app_containers until timeout
    while True and time.time() < timeout:
        # Get the list of running containers for the service
        queue_app_containers = \
         client.containers.list(
             filters={'label': 'com.docker.swarm.service.name=queue_app'})

        if len(queue_app_containers) > 0:
            print("SUCCESS: queue_app service is running.")
            return
        else:
            print("WARNING: queue_app service is not running yet...")
        time.sleep(5)

        if time.time() > timeout:
            print("FAILURE: queue_app service did not start within 5 minutes.")
            sys.exit(1)
            break
    return


def get_current_queue_lengths(client):
    # Get the list of running containers for the service
    queue_app_container = client.containers.list(
        filters={'label': 'com.docker.swarm.service.name=queue_app'})

    # Assuming there is only one container for the service
    if queue_app_container:
        queue_app_container = queue_app_container[0]
        command = 'curl -s localhost:80'
        response = queue_app_container.exec_run(command)
        response = json.loads(response.output.decode('utf-8'))
        return response
    else:
        print("No running containers found for the service.")
        return None


# watch feed_queue_length, when it reaches 0, stop the processor service
@log_exceptions
def monitor_queue(client):
    time.sleep(5)
    while True:
        response = get_current_queue_lengths(client)
        feed_queue_length = response['feed_queue_length']

        # print current feed_queue_length
        print('current feed_queue_length: ', feed_queue_length, flush=True)

        # check if feed_queue_length is 0
        if feed_queue_length == 0:
            print('SUCCESS: feed_queue_length is 0, stopping services...',
                  flush=True)
            remove_all_services(client)
            remove_all_containers(client)
            remove_network(client)

            break
        time.sleep(5)
