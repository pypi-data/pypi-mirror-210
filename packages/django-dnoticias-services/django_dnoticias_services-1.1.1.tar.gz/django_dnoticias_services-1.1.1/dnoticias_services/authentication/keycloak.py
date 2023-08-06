import logging
import base64
import json
from distutils.util import strtobool
from typing import Optional

from django.contrib.auth import get_backends, get_user_model
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.conf import settings

import requests
from keycloak import KeycloakAdmin as BaseKeycloakAdmin, KeycloakOpenID, KeycloakDeleteError
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from dnoticias_services.communications import mail

from .utils import raise_error_from_response

User = get_user_model()
logger = logging.getLogger(__name__)


class KeycloakAdmin(BaseKeycloakAdmin):
    def delete_user_session(self, session: str):
        """Delete an specific user session on keycloak realm.

        :param session: session id
        :type session: str
        :return: realms list
        :rtype: list
        """
        params_path = {"realm": self.realm_name, "session": session}
        url = "admin/realms/{realm}/sessions/{session}"
        data_raw = self.raw_delete(url.format(**params_path))
        return raise_error_from_response(data_raw, KeycloakDeleteError)


class BaseKeycloak():
    """Base class to connect with keycloak

    This class uses a context manager to open and close the connection with keycloak.
    """
    def __init__(self):
        logger.debug("[Keycloak] Establishing a new connection with authentication server...")
        self.server_url = getattr(settings, "KEYCLOAK_SERVER_URL", "")
        self.admin_realm_name = getattr(settings, "KEYCLOAK_ADMIN_REALM_NAME", "")
        self.user_realm_name = getattr(settings, "KEYCLOAK_USER_REALM_NAME", "") or self.admin_realm_name
        self.username = getattr(settings, "KEYCLOAK_ADMIN_USERNAME", "")
        self.password = getattr(settings, "KEYCLOAK_ADMIN_PASSWORD", "")
        self.client_id = getattr(settings, "KEYCLOAK_CLIENT_ID", "")
        self.client_secret_key = getattr(settings, "KEYCLOAK_CLIENT_SECRET_KEY", "")

    def __enter__(self):
        self.keycloak_admin = KeycloakAdmin(
            server_url=self.server_url,
            username=self.username,
            password=self.password,
            realm_name=self.admin_realm_name,
            user_realm_name=self.user_realm_name,
            auto_refresh_token=['get', 'put', 'post', 'delete'],
            verify=True
        )

        self.keycloak_openid = KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.user_realm_name,
            client_secret_key=self.client_secret_key,
            verify=True
        )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.debug("[Keycloak] Closing connection with authentication server...")
        admin_refresh_token = self.keycloak_admin.token.get("refresh_token")

        if admin_refresh_token:
            self.keycloak_admin.keycloak_openid.logout(admin_refresh_token)

    def get_backend(self) -> OIDCAuthenticationBackend:
        """Returns the user backend
        :return: User backend used
        :rtype: OIDCAuthenticationBackend
        """
        backends = get_backends()

        for backend in backends:
            if issubclass(backend.__class__, OIDCAuthenticationBackend):
                return backend

        raise ValueError("No backend that is subclass of OIDCAuthenticationBackend")


class GetUserKeycloakInfo:
    """Get the user attributes from keycloak"""

    def __call__(self, email: str) -> Optional[dict]:
        """Gets all the user attributes from keycloak

        :param email: User email
        ...
        :return: User attributes dict or None
        :rtype: dict or None
        :raises: SuspiciousOperation if user does not exists on keycloak
        """
        user_info = None

        with BaseKeycloak() as base:
            user_id_keycloak = base.keycloak_admin.get_user_id(email)

            if user_id_keycloak is None:
                message = f"The user {email} does not exists on keycloak"
                raise SuspiciousOperation(message)

            user_info = base.keycloak_admin.get_user(user_id_keycloak)

        return user_info


class UpdateUser:
    """Updates an user in both sides (Keycloak and backends)."""

    def __call__(
        self,
        email: str,
        first_name: Optional[str] = '',
        last_name: Optional[str] = '',
        enabled: Optional[bool] = True,
        email_verified: Optional[bool] = None,
        is_staff: Optional[bool] = False,
        is_superuser: Optional[bool] = False,
        max_sessions: Optional[int] = 2,
        update_attributes: Optional[bool] = True,
        custom_attributes: Optional[dict] = dict()
    ) -> User:
        """Updates an user in backend and keycloak to keep the data consistency
        
        :param email: User email that we want to update
        :param first_name: New first name. Default=''
        :param last_name: New last name. Default=''
        :param enabled: True if the user is enabled (active). Default=True
        :param email_verified: True if the user email is verified. Default=None
        :param is_staff: If True, sets is_staff to True. Default=False
        :param is_superuser: If True, sets is_superuser to True. Default=False
        :param max_sessions: Max sessions allowed to this user. Default=2
        :param update_attributes: Updates the is_staff, is_superuser and max_session on keycloak
        if is True. Default: True
        :return: Created user
        :rtype: User
        """
        with BaseKeycloak() as base:
            user_id_keycloak = base.keycloak_admin.get_user_id(email)

            if user_id_keycloak is None:
                message = "That user doesn't exists in keycloak"
                raise SuspiciousOperation(message)

            payload = {
                'firstName': first_name,
                'lastName': last_name,
                'enabled': enabled,
            }

            if email_verified is not None:
                payload['emailVerified'] = email_verified

            if update_attributes:
                payload['attributes'] = {
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'max_sessions': max_sessions,
                }

                if custom_attributes:
                    payload['attributes'].update(custom_attributes)

            base.keycloak_admin.update_user(
                user_id=user_id_keycloak,
                payload=payload,
            )

            user_info = base.keycloak_admin.get_user(user_id_keycloak)

            backend = base.get_backend()
            claims_verified = backend.verify_claims(user_info)

            if not claims_verified:
                message = 'Claims verification failed'
                raise SuspiciousOperation(message)

            users = backend.filter_users_by_claims(user_info)

            user_info['given_name'] = first_name
            user_info['family_name'] = last_name
            user_info['is_active'] = enabled
            user_info['is_staff'] = is_staff
            user_info['is_superuser'] = is_superuser

            if len(users) == 1:
                return backend.update_user(users[0], user_info)
            else:
                message = 'Cannot update the user. Users returned zero or more than one entry.'
                raise SuspiciousOperation(message)


class CreateUser:

    def __call__(
        self,
        email: str,
        first_name: Optional[str] = '',
        last_name: Optional[str] = '',
        enabled: Optional[bool] = True,
        email_verified: Optional[bool] = False,
        password: Optional[str] = None,
        temporary_password: Optional[bool] = True,
        is_staff: Optional[bool] = False,
        is_superuser: Optional[bool] = False,
        send_email_to_user: Optional[bool] = False,
        max_sessions: Optional[int] = 2,
        custom_attributes: Optional[dict] = dict(),
        **kwargs
    ) -> User:
        """Creates an user in backend and keycloak server

        :param email: User email that we want to create
        :param first_name: New first name. Default=''
        :param last_name: New last name. Default=''
        :param enabled: True if the user is enabled (active). Default=True
        :param email_verified: True if the user email is verified. Default=False
        :param password: User password. Default=None
        :param temporary_password: If true sets a temporary password to user. Default=True
        :param is_staff: If True, sets is_staff to True. Default=False
        :param is_superuser: If True, sets is_superuser to True. Default=False
        :param send_email_to_user: If true, sends an email to the user notifying that the
        account was created. Default: False
        :param max_sessions: Max sessions allowed to this user. Default=2
        Defayult: False
        ...
        :return: Created user
        :rtype: User
        """
        with BaseKeycloak() as base:
            user_id_keycloak = base.keycloak_admin.get_user_id(email)
            is_new_user = not user_id_keycloak

            if is_new_user:
                if temporary_password:
                    password = User.objects.make_random_password(length=14)

                credentials = {
                    "type": "password",
                }

                if kwargs.get('credential_data') and kwargs.get('secret_data'):
                    salt = kwargs['secret_data'].get('salt', '')
                    salt = salt.encode()
                    kwargs['secret_data']['salt'] = base64.b64encode(salt).decode()
                    credentials['credentialData'] = json.dumps(kwargs.get('credential_data'))
                    credentials['secretData'] = json.dumps(kwargs.get('secret_data'))
                else:
                    credentials['value'] = str(password)

                credentials["temporary"] = temporary_password

                attributes = {
                    "is_staff": is_staff,
                    "is_superuser": is_superuser,
                    "max_sessions" : max_sessions,
                }

                if custom_attributes:
                    attributes.update(custom_attributes)

                user_id_keycloak = base.keycloak_admin.create_user(
                    {
                        "email": email,
                        "username": email,
                        "firstName": first_name,
                        "lastName": last_name,
                        "enabled": enabled,
                        "emailVerified" : email_verified,
                        "credentials": [credentials],
                        "realmRoles": ["user_default",],
                        "attributes": attributes
                    }
                )

            user_info = base.keycloak_admin.get_user(user_id_keycloak)
            self.normalize_user_info(user_info)

            email = user_info.get('email')

            backend = base.get_backend()
            claims_verified = backend.verify_claims(user_info)
            if not claims_verified:
                msg = 'Claims verification failed'
                raise SuspiciousOperation(msg)

            # email based filtering
            users = backend.filter_users_by_claims(user_info)

            user_info['given_name'] = user_info.get("firstName", first_name)
            user_info['family_name'] = user_info.get("lastName", last_name)
            user_info['is_active'] = enabled
            user_info['is_staff'] = user_info.get("is_staff", is_staff)
            user_info['is_superuser'] = user_info.get("is_superuser", is_superuser)

            if len(users) == 1:
                return backend.update_user(users[0], user_info)
            elif len(users) > 1:
                # In the rare case that two user accounts have the same email address,
                # bail. Randomly selecting one seems really wrong.
                msg = 'Multiple users returned'
                raise SuspiciousOperation(msg)
            elif backend.get_settings('OIDC_CREATE_USER', True):
                if send_email_to_user and is_new_user:
                    try:
                        mail.send_email(
                            email=email,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            template_uuid=settings.EMAIL_TEMPLATE_RESET_LOGIN_INFO_UUID,
                            brand_group_uuid=settings.EMAIL_BRAND_GROUP_UUID,
                            subject=settings.EMAIL_USER_CREATION_SUBJECT,
                            context={
                                'first_name': first_name,
                                'last_name': last_name,
                                'email': email,
                                'plain_password': str(password),
                            }
                        )
                    except:
                        logger.exception("Cannot send create user email")

                return backend.create_user(user_info)

            return None

    def normalize_user_info(self, user_info: dict):
        """Normalizes the user information dictionary"""
        attributes = user_info.get("attributes", {})

        for key in attributes:
            if isinstance(attributes[key], list):
                value = attributes[key][0] if len(attributes[key]) == 1 else attributes[key]

                if type(value) == list and len(value) > 0:
                    value = value[0]

                try:
                    attributes[key] = bool(strtobool(value))
                except ValueError:
                    attributes[key] = value
                except AttributeError:
                    logger.exception("Cannot convert to bool")
                    attributes[key] = value

        user_info.update(attributes)


class UpdatePassword:

    def __call__(
        self,
        email: str,
        password: Optional[str]=None,
        temporary: bool=False,
        send_email_to_user: bool=False,
        **kwargs
    ) -> JsonResponse:
        """Updates an user password on keycloak

        :param email: User email that we want to update the password
        :param password: New password. If None, temporary need to be True. Default=None
        :param temporary: If True the user will have a temporary password. Default=False
        :param send_email_to_user: Sends an email to the user notifying the new password.
        Default: False
        ...
        :return: {'result': 'OK/KO', 'reason': '', 'message': ''} (200 if OK, 500 if keycloak error)
        :retype: JsonResponse
        """
        status = 200
        data = {'result': 'OK', 'reason': 'SUCCESS', 'message': ''}

        with BaseKeycloak() as base:
            try:
                user_id_keycloak = base.keycloak_admin.get_user_id(email)
            except:
                data['result'] = 'KO'
                data['reason'] = 'ERROR'
                data['message'] = 'Error trying to find user in keycloak'
                status = 500
                return JsonResponse(data=data, safe=False, status=status)

            if temporary:
                password = User.objects.make_random_password(length=14)

            base.keycloak_admin.set_user_password(
                user_id=user_id_keycloak,
                password=password,
                temporary=temporary
            )

            if send_email_to_user:
                try:
                    mail.send_email(
                        email=email,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        template_uuid=settings.EMAIL_TEMPLATE_RESET_LOGIN_INFO_UUID,
                        brand_group_uuid=settings.EMAIL_BRAND_GROUP_UUID,
                        subject=settings.EMAIL_USER_PASSWORD_NOTIFICATION_SUBJECT,
                        context={
                            'name': kwargs.get('name', ''),
                            'email': email,
                            'plain_password': password,
                        }
                    )
                except:
                    logger.exception("Cannot send update password email")

            return JsonResponse(data=data, safe=False, status=status)


class SendUpdateAccount:

    def _action_exists(self, action):
        actions = ('UPDATE_PASSWORD', )
        return bool(action in actions)

    def __call__(self, email: str, action: str) -> JsonResponse:
        status = 200
        data = {'result': 'KO', 'reason': 'ERROR', 'message': ''}

        with BaseKeycloak() as base:
            if not self._action_exists(action):
                data['message'] = 'The provided action doesn\'t exists.'
                status = 400

            try:
                user_id = base.keycloak_admin.get_user_id(email)
                base.keycloak_admin.send_update_account(
                    user_id=user_id,
                    payload=json.dumps([action])
                )
                data['result'] = 'OK'
                data['reason'] = 'SUCCESS'
            except:
                status = 500
                logger.exception('Error on UpdateAccount service (dnoticias_service > keycloak)')
                data['message'] = 'An error has been ocurred on update account'

            return JsonResponse(data=data, safe=False, status=status)


class GetToken:

    def __call__(self, email: str, password: str) -> dict:
        """Get the user token and creates a new session on keycloak
        
        :param email: User email
        :param password: User password
        ...
        :return: Access token, refresh token dict
        :rtype: dict
        """
        with BaseKeycloak() as base:
            return base.keycloak_openid.token(email, password)


class RefreshToken:

    def __call__(self, refresh_token: str) -> dict:
        """Refresh the token on keycloak and returns the new generated token
        
        :param refresh_token: Refresh token used to generate a new access_token
        ...
        :return: Access Token and Refresh Token dict
        :rtype: dict
        """
        with BaseKeycloak() as base:
            return base.keycloak_openid.refresh_token(refresh_token)


class LogoutUser:

    def __call__(self, refresh_token: str) -> dict:
        """Logouts an user on keycloak (not backend)
        
        :param refresh_token: Refresh token used to logout the user
        """
        with BaseKeycloak() as base:
            return base.keycloak_openid.logout(refresh_token)


class GetTokenInfo:

    def __call__(self, access_token: str) -> dict:
        """Gets the token info from keycloak (access, refresh, expiration, etc)
        
        :param access_token: Access token used to retrieve the token info
        ...
        :return: Token user information
        :rtype: dict
        """
        with BaseKeycloak() as base:
            return base.keycloak_openid.introspect(access_token)


class KeycloakUserExists:

    def __call__(self, email: str) -> bool:
        """Verifies if the email given exists in keycloak
        
        :param email: Email we will check if exists
        ...
        :return: True if the email exists, False it doesn't
        :rtype: bool
        """
        if not email:
            return False

        with BaseKeycloak() as base:
            return bool(base.keycloak_admin.get_user_id(email))


class DeleteUserSession:

    def __call__(self, session: str) -> bool:
        """Deletes an specific session id

        :param session: Session id to delete
        :return: True if the email exists, False it doesn't
        :rtype: bool
        """
        if not session:
            return False

        with BaseKeycloak() as base:
            return base.keycloak_admin.delete_user_session(session)


class UpdateUserVerification:
    def __call__(self, email: str, verified: Optional[bool] = True) -> bool:
        if not email:
            return False

        with BaseKeycloak() as base:
            keycloak_user_id = base.keycloak_admin.get_user_id(email)
            return base.keycloak_admin.update_user(
                keycloak_user_id,
                {"emailVerified": verified}
            )
        

class UserIsVerified:
    """Get the user attributes from keycloak"""

    def __call__(self, email: str) -> Optional[dict]:
        user_info = None
        email_verified = False

        with BaseKeycloak() as base:
            user_id_keycloak = base.keycloak_admin.get_user_id(email)

            if user_id_keycloak is None:
                message = f"The user {email} does not exists on keycloak"
                raise SuspiciousOperation(message)

            user_info = base.keycloak_admin.get_user(user_id_keycloak)
            email_verified = user_info.get("emailVerified", False)

        return email_verified


class SendVerificationEmail:
    """Send a verification email to the user"""

    def __call__(self, email: str) -> Optional[dict]:
        response = requests.post(
            settings.SUBSCRIPTIONS_SEND_VERIFICATION_EMAIL_URL,
            json={"email": email}
        )

        return response


update_user = UpdateUser()
send_update_account = SendUpdateAccount()
create_user = CreateUser()
update_password = UpdatePassword()
get_token = GetToken()
refresh_token = RefreshToken()
logout_user = LogoutUser()
get_token_info = GetTokenInfo()
keycloak_user_exists = KeycloakUserExists()
get_user_keycloak_info = GetUserKeycloakInfo()
delete_user_session = DeleteUserSession()
update_user_verification = UpdateUserVerification()
user_is_verified = UserIsVerified()
send_verification_email = SendVerificationEmail()
