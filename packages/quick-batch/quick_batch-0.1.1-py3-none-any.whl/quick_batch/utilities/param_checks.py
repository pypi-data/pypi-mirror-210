import sys
import os
import ast
import yaml
from utilities import log_exceptions
from utilities.manage_loggers import Logger


def setup_logger(config):
    # import log path
    with open(config, "r") as yaml_file:
        config = yaml.safe_load(yaml_file)
    log_path = config["data"]["log_path"]

    # delete log file if it exists
    if os.path.exists(log_path):
        os.remove(log_path)

    # instantiate log_exceptions decorator
    logger = Logger(log_path)

    # Open the log file
    logger.open_log()

    # Redirect sys.stdout to the logger
    sys.stdout = logger

    return logger


@log_exceptions
def check_config_data_paths(config_path):
    # import config variables
    with open(config_path, "r") as yaml_file:
        config = yaml.safe_load(yaml_file)

    # check that data paths in config file entries are valid
    input_path = config["data"]["input_path"]
    output_path = config["data"]["output_path"]
    processor_path = config["processor"]["processor_path"]
    num_processors = config["processor"]["num_processors"]
    requirements_path = config.get("processor", {}). \
        get("requirements_path", "")

    # if requirements_path is not empty, check that it exists
    if not os.path.isfile(requirements_path):
        requirements_path = ""

    # check that processor_path is file and exists
    if not os.path.isfile(processor_path):
        print("FAILURE: processor_path does not exist")
        sys.exit(1)
    else:
        print("SUCCESS: processor_path exists")

    # check that input path exists
    if not os.path.isdir(input_path):
        print("FAILURE: input path does not exist")
        sys.exit(1)
    else:
        print("SUCCESS: config input path exists")

    # check that output path exists
    if not os.path.isdir(output_path):
        print("FAILURE: output path does not exist")
        sys.exit(1)
    else:
        print("SUCCESS: config output path exists")

    # check that input path is not empty
    if not os.listdir(input_path):
        print("FAILURE: input path is empty")
        sys.exit(1)
    else:
        print("SUCCESS: config input path is not empty")
        # files = os.listdir(input_path)
        # print(f"SUCCESS: files in input path: {files}")

    # check that num_processors is int greater than 0
    if not isinstance(num_processors, int):
        print("FAILURE: num_processors is not an integer")
        sys.exit(1)
    elif num_processors <= 0:
        print("FAILURE: num_processors is not greater than 0")
        sys.exit(1)
    else:
        print("SUCCESS: num_processors is an integer greater than 0")

    return input_path, output_path, processor_path, num_processors, \
        requirements_path


@log_exceptions
def check_config(config_path):
    # check if file exists
    if not os.path.isfile(config_path):
        print("FAILURE: config_path file does not exist")
        sys.exit(1)
    else:
        print("SUCCESS: config_path file exists")


# check to make sure processor.py is valid
# for now - that it contains a function named 'processor'
@log_exceptions
def check_processor(processor):
    # Module name to check for
    module_file = processor

    with open(module_file, 'r') as file:
        tree = ast.parse(file.read())

    processor_found = False

    # Traverse the abstract syntax tree to find function definitions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'processor':
            processor_found = True
            break

    if processor_found:
        print("SUCCESS: module contains a function named 'processor'")
    else:
        print("FAILURE: module does not contain a function named 'processor'")
        sys.exit(1)
