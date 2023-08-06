import json

from requests.models import Response


def response_return(response: Response):
    if not response.ok:
        message = f"Request failed with status " \
                  f"{str(response.status_code)}" \
                  f" with the message " \
                  f"{str(json.loads(response.text)['detail'])}"
        raise Exception(message)
    return True
