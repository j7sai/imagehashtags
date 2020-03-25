from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    try:
        data = response.data
    except:
        data = None
    if data:
        exce = response.data.get("detail", None)
        if response is not None:
            response.data['status_code'] = 400
        response.data["message"] = ''
        exce_st = str(exce).split('-')
        exce_st_de = exce_st[0]
        if 'AllImagesFailed' == exce_st_de:
            response.data["message"] = "Failed : all images are below ascept ratio or less than 1200 px shorter edge "
            response.data["status_code"] = exce.code
        elif "PartialImagesSuccess"==exce_st_de:
            message = exce_st[1].split(',')
            no_failed,passed = message[0],message[1]
            response.data["message"] = "Success : {1} images are successfullly saved another {0} images failed due to\n" \
                                       " below ascept ratio or less than 1200 px shorter edge ".format(no_failed,passed)
    return response