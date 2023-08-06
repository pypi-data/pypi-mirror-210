import logging
from typing import Any, Iterable
from urllib.parse import urljoin

from django.db import connections, close_old_connections
from django.views.generic import View
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

import requests
from rest_framework import status as http_status
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class APIResponseView(APIView):
    STATUS = http_status

    def dispatch(self, request, *args, **kwargs):
        self.data = {"errors": [], "message": "", "results": {}}
        return super().dispatch(request, *args, **kwargs)

    def add_error(self, message: str):
        """Add an error message to the response

        :param message: Error message
        """
        self.data["errors"].append(message)

    def set_message(self, message: str):
        """Set a message to the response

        :param message: Message to set
        """
        self.data["message"] = message

    def add_errors(self, errors: Iterable):
        """Add errors to the response, this method accepts an iterable of errors only

        :param errors: Iterable of errors
        """
        self.data["errors"] += errors

    def set_results(self, results: Any):
        """Set results to the response

        :param results: Results to set
        """
        self.data["results"] = results


class BaseCheckView(View):
    TYPE = ""
    CHECK_SECRET = "{}_SECRET"

    def check_database(self):
        """Check if the database is responding"""
        if not getattr(settings, f"{self.TYPE}_CHECK_DATABASE", False):
            logger.debug("Database check disabled")
            return

        try:
            # Try to connect to the default database
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT 1")
                row = cursor.fetchone()
                assert row, "No database response"
        except Exception as e:
            # Close old database connections to prevent "too many connections" errors
            close_old_connections()
            raise e

    def check_cache(self):
        """Check if the cache is working"""
        if not getattr(settings, f"{self.TYPE}_CHECK_CACHE", False):
            logger.debug("Cache check disabled")
            return

        try:
            cache.set('test_key', 'test_value', 60)
            assert cache.get('test_key') == 'test_value', "Cache not working"
        except Exception as e:
            raise e

    def check_keycloak(self):
        """Check if the keycloak server is responding"""
        if not getattr(settings, f"{self.TYPE}_CHECK_KEYCLOAK", False):
            logger.debug("Keycloak check disabled")
            return

        keycloak_base_url = getattr(settings, "KEYCLOAK_SERVER_URL", None)

        if keycloak_base_url:
            # Check connection to the keycloak server
            try:
                response = requests.get(
                    urljoin(keycloak_base_url, "realms/master/.well-known/openid-configuration")
                )
                response.raise_for_status()
                assert response.status_code == 200, "Keycloak server not responding"
            except Exception as e:
                raise e

    def check_secrets(self, request):
        """Check if the secret is valid"""
        check_secret = getattr(settings, f"{self.TYPE}_SECRET", None)
        request_secret = request.GET.get("hsid", None)

        if not check_secret:
            raise Exception("Check secret not set")

        if not request_secret or request_secret != check_secret:
            raise Exception("Invalid check secret")

    def check_external_services(self):
        """Check if the external services are responding"""
        pass

    def get(self, request):
        try:
            self.check_secrets(request)
            self.check_database()
            self.check_cache()
            self.check_keycloak()
            self.check_external_services()
        except Exception as e:
            logger.exception("Health check failed")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        logger.debug("Health check passed")
        return JsonResponse({"status": "ok"})


class HealthCheckView(BaseCheckView):
    TYPE = "HEALTH"

    def get(self, request):
        return super().get(request)


class ReadinessCheckView(BaseCheckView):
    TYPE = "READINESS"

    def get(self, request):
        logger.debug("Readiness check called")
        return super().get(request)
