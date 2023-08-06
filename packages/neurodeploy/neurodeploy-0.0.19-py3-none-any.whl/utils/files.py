from utils.query import post


# def check(f):
#     def g(args, **kwargs):
#         # 1. check if credentials are present
#         # 2. if not, check if token is present and has not expired
#         # print error and raise exception if neither conditions are valid

#         return f(args, **kwargs)

#     return g


# @check
def upload_file(data_in, file_path):
    try:
        response = post(
            data_in["url"],
            data=data_in["fields"],
            headers=None,
            files={"file": open(file_path, "rb")},
        )
    except IOError:
        return {"message": "Can't send  model file", "status_code": 400}
    if response["status_code"] == 200:
        return {"message": "Upload successful", "status_code": 200}
    else:
        return {"message": "Your file could not be uploaded", "status_code": 400}
