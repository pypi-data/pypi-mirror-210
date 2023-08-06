# from .progress_logger import log_exceptions
from utilities import log_exceptions


# create docker network
@log_exceptions
def create_network(client):
    if 'quick_batch_network' not in [network.name for network
                                     in client.networks.list()]:
        client.networks.create('quick_batch_network', driver='overlay')


@log_exceptions
def remove_network(client):
    if 'quick_batch_network' in \
     [network.name for network in client.networks.list()]:
        client.networks.get('quick_batch_network').remove()
