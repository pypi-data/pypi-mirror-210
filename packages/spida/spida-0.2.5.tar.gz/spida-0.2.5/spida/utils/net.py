import requests
from requests.exceptions import ConnectionError
import time


class BadResponse(Exception):
    pass


def request(
    type=requests.get,
    fail_action=None,
    fail_message=None,
    retry_delay=1,
    retry_max=100,
    **kwargs,
):
    do_fail_action = True
    for i in range(retry_max):
        try:
            response = type(**kwargs)
            if response.status_code is 200:
                return response
            else:
                raise BadResponse("Status is not 200")
        except (ConnectionError, BadResponse) as error:
            if do_fail_action:
                if fail_message is not None:
                    print(fail_message)
                if fail_action is not None:
                    fail_action()
                do_fail_action = False
            time.sleep(retry_delay)
    raise Exception(f"No api response after {retry_max} attempts.")


def get(**kwargs):
    return request(type=requests.get, **kwargs)


def post(**kwargs):
    return request(type=requests.post, **kwargs)
