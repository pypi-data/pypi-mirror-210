# from .progress_logger import log_exceptions
from utilities import log_exceptions


@log_exceptions
def create_swarm(client):
    client.swarm.init()


@log_exceptions
def leave_swarm(client):
    client.swarm.leave(force=True)
