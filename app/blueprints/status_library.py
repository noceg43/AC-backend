def status_success(message : str, data = None):
    response = {
        "status" : "success",
        "message" : message
    }
    if data is not None:
        response["data"] = data
    return response

def status_error(message : str, data = None):
    retData = {
        "status" : "error",
        "message" : message
    }

    if (data is not None):
        retData["data"] = data
    return retData