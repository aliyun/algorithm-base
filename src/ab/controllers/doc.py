from ab.utils import logger
from ab import jsonify
from ab import app
from ab.utils.exceptions import AlgorithmException

import yaml
import json
import collections


def __parse_request_object(request_object, segments_count):
    objs = request_object.split("||")

    # valid the segmetns num of the request line
    if len(objs) != segments_count:
        data = "the length of fields in `request` must be {}. line = {}".format(segments_count, request_object)
        raise AlgorithmException(data=data)

    ro = dict()
    ro['name'] = objs[0]
    ro['type'] = objs[1]
    ro['desc'] = objs[2]
    ro['sampleValue'] = objs[3]
    if segments_count > 4:
        ro['required'] = objs[4]

    # count of `_`
    counter = 0
    for i in ro['name']:
        if i is not '_':
            break
        counter = counter + 1

    # ignore properties start with `__`
    ro['__level'] = counter
    ro['name'] = ro['name'][counter:]
    return ro


def __parse_body(q, parse_type):
    """
    parse any body with level
    :param segments_count: the count of segments
    :param q: a dequeue to hold the contents
    :return:
    """
    ret = []

    last_request_object = None
    while len(q) > 0:
        current_line = q.popleft()
        current_request_object = __parse_request_object(current_line, 5 if parse_type == "req" else 4)

        if last_request_object is not None:
            level_diff = current_request_object['__level'] - last_request_object['__level']
            # diff == 0 means in the same level
            if level_diff == 1:
                q.appendleft(current_line)
                last_request_object['children'] = __parse_request(q) if parse_type == "req" else __parse_response(q)
                continue
            if level_diff > 1:
                raise AlgorithmException(
                    data="The next two lines of requests should not differ by more than 1 level")
            if level_diff < 0:
                q.appendleft(current_line)
                return ret

        # next line
        ret.append(current_request_object)
        last_request_object = current_request_object
    return ret


def __parse_request(request_objects_queue):
    return __parse_body(request_objects_queue, "req")


def __parse_response(response_objects_queue):
    return __parse_body(response_objects_queue, "resp")


def __valid_field(doc, field_name):
    """
    to check if the specfic field is in the `document`
    :param doc:
    :param field_name:
    :return:
    """
    if field_name not in doc:
        raise AlgorithmException(
            data="`{field}` must in your doc.yaml where `apiName`={doc_name}".format(field=field_name,
                                                                               doc_name=doc['apiName']))


def __parse_document(doc):
    new_doc = json.loads(json.dumps(doc))

    # valid filed in original document
    for field in ["apiName", "apiUrl", "method", "desc", "tag", "request", "response", "sampleRequestCode",
                  "sampleResponseCode"]:
        __valid_field(doc, field)

    new_doc['request'] = __parse_request(collections.deque((doc['request'])))
    new_doc['response'] = __parse_response(collections.deque((doc['response'])))
    return new_doc


@app.route('/doc', methods=['GET', 'POST'])
def doc():
    import os.path
    if not os.path.exists("./doc.yaml"):
        raise AlgorithmException(data="you have to put `doc.yaml` under the root dir ")

    ret = []
    with open("doc.yaml", 'r') as stream:
        data_loaded = yaml.load_all(stream, Loader=yaml.FullLoader)

        for data in data_loaded:
            ret.append(__parse_document(data))

    return jsonify({'code': 0, 'data': ret})
