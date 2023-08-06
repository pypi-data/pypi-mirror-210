import os
import sys
from utilities.manage_loggers import LogExceptions


# path to this file's directory and parent directory
file_path = os.path.abspath(__file__)
base_directory = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))

# add to path
sys.path.append(base_directory)

# define paths to each app dockerfile location
processor_path = os.path.join(base_directory, 'quick_batch', 'processor_app')
queue_path = os.path.join(base_directory, 'quick_batch', 'queue_app')


# instantiate progress logger
log_exceptions = LogExceptions()
