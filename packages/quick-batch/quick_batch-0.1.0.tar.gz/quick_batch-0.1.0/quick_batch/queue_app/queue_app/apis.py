from queue_app import app
from flask import jsonify, request
import json


# receive message from feeder of completion
@app.route('/', methods=['GET'])
def current_queue_lengths():
    return jsonify({"original_feed_queue_length":
                    app.original_feed_queue_length,
                    'feed_queue_length': app.feed_queue_length,
                    'wip_queue_length': app.wip_queue_length,
                    'done_queue_length': app.done_queue_length})


@app.route('/send_object_paths', methods=['GET'])
def send_object_paths():
    # feeder queue
    if not len(app.feeder_queue) == 0:
        # get next object data paths
        object_paths = []
        for i in range(app.feed_rate):
            # collect next path
            next_path = app.feeder_queue.popleft()
            object_paths.append(next_path)

            # update wip queue
            app.wip_queue.append(next_path)

            # update counters
            app.wip_queue_length += 1

        return jsonify({'object_paths': object_paths,
                        'queue_message': f"{app.feed_queue_length} objects "
                                         f"remaining in feeder queue"
                        })
    else:
        if app.empty_trigger == 0:
            app.empty_trigger += 1

            # send empty queue message to container log
            print('feeder queue is empty', flush=True)

        # return news to requester
        return jsonify({'object_paths': [],
                        'feed_queue_length': 0})


# receive message from processor of completion
@app.route('/done_from_processor', methods=['POST'])
def done_from_processor():
    # grab new datapoint from post
    try:
        # receive request
        data = request.get_data()

        # get datapoint from request
        data = json.loads(data)["paths_complete"]

        # update counters
        for d in data:
            app.feed_queue_length -= 1
            app.done_queue_length += 1
            app.wip_queue_length -= 1
            app.done_queue.append(d)

        # update wip queue
        app.wip_queue = list(set(app.wip_queue) - set(data))
        app.wip_queue_length = len(app.wip_queue)

        return jsonify("200")
    except Exception as e:
        print(e, flush=True)
        return jsonify("400")
