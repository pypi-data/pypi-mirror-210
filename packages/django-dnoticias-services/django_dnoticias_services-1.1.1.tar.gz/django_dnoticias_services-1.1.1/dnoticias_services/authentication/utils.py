import requests
from keycloak import KeycloakOperationError, KeycloakAuthenticationError


# https://github.com/marcospereirampj/python-keycloak/blob/a63982188ae14e1a0948f324bb3e9a8387650e65/src/keycloak/exceptions.py#L150
def raise_error_from_response(response, error, expected_codes=None, skip_exists=False):
    """Raise an exception for the response.

    :param response: The response object
    :type response: Response
    :param error: Error object to raise
    :type error: dict or Exception
    :param expected_codes: Set of expected codes, which should not raise the exception
    :type expected_codes: Sequence[int]
    :param skip_exists: Indicates whether the response on already existing object should be ignored
    :type skip_exists: bool
    :returns: Content of the response message
    :type: bytes or dict
    :raises KeycloakError: In case of unexpected status codes
    """  # noqa: DAR401,DAR402
    if expected_codes is None:
        expected_codes = [200, 201, 204]

    if response.status_code in expected_codes:
        if response.status_code == requests.codes.no_content:
            return {}

        try:
            return response.json()
        except ValueError:
            return response.content

    if skip_exists and response.status_code == 409:
        return {"msg": "Already exists"}

    try:
        message = response.json()["message"]
    except (KeyError, ValueError):
        message = response.content

    if isinstance(error, dict):
        error = error.get(response.status_code, KeycloakOperationError)
    else:
        if response.status_code == 401:
            error = KeycloakAuthenticationError

    raise error(
        error_message=message, response_code=response.status_code, response_body=response.content
    )
