import sys
import api_connects
sys.path.append('..')
from custom_processor import processor # noqa 


def processor_wrapper(processor, app):
    try:
        processor.processor(app)
        app.success = True
        app.receipt_data['processor_message'] = \
            'SUCCESS PROCESSING:' + str(app.file_paths_to_process)
    except Exception as e:
        app.success = False
        print('failure for object paths', app.file_paths_to_process,
              flush=True)
        print(e, flush=True)
        app.receipt_data['processor_message'] = \
            'FAILURE PROCESSING (EXCEPTION):' + str(app.input_data)
        app.receipt_data['processor_exception'] = str(e)


def activate(app):
    # report startup success to terminal
    print('node has started', flush=True)

    # set lifetime - number of objects this container
    # can process before restart
    lifetime = 1000
    while lifetime > 0:
        # get next batch of file paths
        api_connects.request_object_paths(app)
        print('RETRIEVED: with', str(app.file_paths_to_process), flush=True)

        # process each file path
        processor_wrapper(processor, app)

        # update lifetime
        lifetime -= 1

        # print progress
        print('FINISHED: with', str(app.file_paths_to_process), flush=True)

        if app.success:
            # send report to queue_app
            api_connects.send_done_report(app)

            # reset success flag
            app.success = False

    # if reaching the lifetime end signal to orchestator
    # that a new container be built
    sys.exit(1)
