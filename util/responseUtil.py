import time
import traceback

from flask import jsonify

# Define system error codes
codes = {
    200: 'success',
    400: None,
    10001: 'system error',
}


def response_filter(fn):
    """
    Responsive decorators
    :param fn: Modified method body
    :return:
    """

    def wrapper(*args, **kwargs):
        try:
            time1 = time.time()
            res = fn(*args, **kwargs)
            time2 = time.time()
            timeout = '%.3f' % (time2 - time1)
            return jsonify(response_ok(res=res, timeout=timeout))
        except Exception as e:
            traceback.print_exc()
            return jsonify(response_fail(error=str(traceback.format_exc())))

    return wrapper


def response_ok(res=None, timeout=None):
    if isinstance(res, tuple):
        if res[1] in codes:
            return {"code": res[1], "data": res[0], "timeout": timeout, "message": codes[res[1]]}
        else:
            return {"code": res[1], "data": res[0], "timeout": timeout, "message": res[2]}
    else:
        return {"code": 200, "data": res.to_dict(), "timeout": timeout, "message": codes[200]}


def response_fail(error=None):
    return {"code": 10001, "data": None, "error": error}
