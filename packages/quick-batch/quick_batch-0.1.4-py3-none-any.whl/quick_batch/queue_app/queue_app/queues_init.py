import os
from collections import deque
from os.path import isfile, join
from os import listdir
from subprocess import run


# load in object paths in base_path to process
def load_object_paths(base_path):
    datapaths = [f for f in listdir(base_path) if isfile(join(base_path, f))]
    datapaths = [base_path + '/' + a for a in datapaths]
    return datapaths


# load in object paths in base_path to process - in descending order of size
def load_object_paths_inorder(path):
    # define filenames sorting command
    command = 'ls -Ss1pqh ' + path + ' --block-size=1K'
    output = run(command, capture_output=True, shell=True).stdout

    # filter command output
    output = output.decode("utf-8").split('\n')
    output = [v for v in output if len(v) > 0]
    file_sizes = []
    file_names = []
    for num, o in enumerate(output):
        if num > 0:
            o_strip = o.strip()
            o_split = o_strip.split(' ')
            file_sizes.append(o_split[0])
            file_names.append(o_split[1])
    return file_sizes, file_names


# load in subdir paths in base_path - each containing objects to process
def load_subdir_paths(base_path):
    subdirs = [f.path for f in os.scandir(base_path) if f.is_dir()]
    return subdirs


# load in subdir paths in base_path - each containing objects to process - in
# descending order of size
def load_subdir_paths_inorder(path):
    # define subdir sorting command
    command = 'du -sh ' + path + '/* --block-size=1K | sort -hr'

    # run command
    output = run(command,
                 capture_output=True, shell=True).stdout

    # filter command output
    output = output.decode("utf-8").split('\n')
    output = [v for v in output if len(v) > 0]
    subdir_sizes = []
    subidr_names = []
    for o in output:
        o_split = o.split('\t')
        subdir_sizes.append(o_split[0])
        subidr_names.append(o_split[1])

    return subdir_sizes, subidr_names


# load in file object paths to process, create queues
def create_queues(app):
    # just load in paths or sort?
    organized_datapaths = []
    organized_sizes = []

    # csv or subdir?
    if app.order_files:
        print('sorting filenames by line-length in descending order!',
              flush=True)
        organized_sizes, organized_datapaths = \
            load_object_paths_inorder(app.path_to_feed)
    else:
        print('loading in filenames as they present themselves!', flush=True)
        organized_datapaths = load_object_paths(app.path_to_feed)

    print('done loading in filenames!', flush=True)

    app.organized_datapaths = organized_datapaths
    app.organized_sizes = organized_sizes

    # create queues for feeder, done, and wip
    app.feeder_queue = deque()
    app.done_queue = deque()
    app.wip_queue = []
    app.failed_queue = []  # to add

    # load up queue with organized_paths
    feed_counter = 0
    for item in organized_datapaths:
        app.feeder_queue.append(item)
        feed_counter += 1

    print('done loading feeder queue!', flush=True)
    print(app.feeder_queue, flush=True)

    # init queue counters
    app.feed_queue_length = feed_counter
    app.original_feed_queue_length = feed_counter
    app.wip_queue_length = 0
    app.done_queue_length = 0
