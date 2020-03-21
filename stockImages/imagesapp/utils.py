from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    exce = response.data["detail"]

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
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