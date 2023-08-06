import requests
import sys
import json


def retrieval_check(app, data):
    if len(data['object_paths']) > 0:
        # update log
        app.receipt_data['retrieval_message'] = 'SUCCESS RETRIEVAL:' + \
         str(data['object_paths'])

        # attach received data to app
        app.input_data = data
        return True
    else:
        # ping log to report exit
        app.receipt_data['retrieval_message'] = 'SUCCESS: processer \
            exited properly'
        return False


def request_object_paths(app):
    # seed receipt for report to logger
    app.receipt_data = {}
    app.receipt_data['retrieval_message'] = ''
    app.receipt_data['retrieval_exception'] = ''
    app.receipt_data['processor_message'] = ''
    app.receipt_data['processor_exception'] = ''

    # retrieve next filename to process from api feeder container
    try:
        # hit get address
        get_address = 'http://queue_app:80/send_object_paths'
        datapackage = requests.get(get_address, verify=False, timeout=600)

        # unpack data
        data = datapackage.json()

        # check retrieval status
        checkval = retrieval_check(app, data)
        if checkval:
            # process
            app.file_paths_to_process = data['object_paths']
        else:
            # feeder queue is empty
            print('feeder queue is empty!', flush=True)
            print('shutting down...', flush=True)
            sys.exit(0)

    except Exception as e:
        # send report to queue_app
        app.receipt_data['retrieval_message'] = 'FAILURE RETRIEVAL'
        app.receipt_data['retrieval_exception'] = str(e)
        print(app.receipt_data, flush=True)
        # send_done_report(app)

        # fail out - restart and collect the next datapoint from the queue
        sys.exit(1)


# post done back to queue_app
def send_done_report(app):
    data = {'paths_complete': app.file_paths_to_process}
    data = json.dumps(data)

    # create post_address
    post_address = 'http://' + 'queue_app' + ':80/done_from_processor'

    # post data to child container
    requests.post(post_address, data=data,
                  headers={'content-type': 'application/json'},
                  verify=False, timeout=100)
