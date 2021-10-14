import inspect

from ab import app, jsonify
from ab.utils.algorithm import algorithms


def cl():
    return "<br />"


def parse_algorithm(algo):
    content = ""

    # line
    content = content = "-----" + cl()
    # name
    content = content + "API：" + __parse_algorithm_name(algo.name) + cl()

    # api signature
    content = content + "签名：" + __parse_algorithm_signature(algo.main) + cl()

    # doc
    content = content + "文档：" + __parse_algorithm_doc(algo.main) + cl()

    # curl example
    content = content + "curl例子：" + cl()
    content = content + __parse_curl_example(algo.name, algo.main) + cl()

    # end
    content = content + cl()
    return content


def __parse_algorithm_name(name):
    return "api/algorithm/{}".format(name)


def __parse_algorithm_signature(func):
    sig = inspect.signature(func)
    return str(sig) if sig is not None else ""


def __parse_algorithm_doc(func):
    doc = inspect.getdoc(func)
    if doc is not None:
        lines = cl()
        doc_list = doc.split("\n")
        for i, l in enumerate(doc_list):
            lines = lines + l

            if i < len(doc_list) - 1:
                lines = lines + cl()
        return lines
    return ""


def __parse_curl_example(name, func):
    sig = inspect.signature(func)

    curl_template = """
curl --location --request POST 'localhost:8000/api/algorithm/$func_name' \
--header 'Content-Type: application/json' \
--data '{ "args": { $kv } }'
"""
    ret = ""
    l = len(sig.parameters)
    i = 0
    for k, v in sig.parameters.items():
        i = i + 1
        if v.kind != inspect.Parameter.VAR_KEYWORD:
            # change default value
            v = v.replace(default=gen_default_value(v))
            ret = ret + "\"{k}\":{v}".format(k=k, v=v.default)

            if i < l:
                ret = ret + ","

    from string import Template
    s = Template(curl_template)
    lines = s.substitute(func_name=name, kv=ret)
    return lines


def gen_default_value(parameter):
    if ": int" in str(parameter):
        return 0 if parameter.default is inspect.Parameter.empty else parameter.default
    if ": float" in str(parameter):
        return 0.0 if parameter.default is inspect.Parameter.empty else parameter.default
    if ": str" in str(parameter):
        return "\"str\"" if parameter.default is inspect.Parameter.empty else "\"{}\"".format(parameter.default)

    return "\"tbd\""


@app.route('/doc', methods=['GET', 'POST'])
def doc():
    ret = ""
    for algo_engine_tuple, algorithm in algorithms.items():
        ret = ret + parse_algorithm(algorithm)
    return ret
