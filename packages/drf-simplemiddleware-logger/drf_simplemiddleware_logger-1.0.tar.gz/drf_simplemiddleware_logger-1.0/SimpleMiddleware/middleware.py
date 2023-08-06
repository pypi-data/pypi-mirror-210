from django.middleware.common import CommonMiddleware
from django.utils.functional import SimpleLazyObject
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
import json
import datetime

naive_datetime = datetime.datetime.now()
aware_datetime = timezone.make_aware(naive_datetime)

class SimpleMiddleware:
    def __init__(self, get_response, model_name):
        self.get_response = get_response
        self.model_name = model_name

    def __call__(self, request):
        api_endpoint = request.path
        # if not api_endpoint.startswith('/admin-api/'):
        #     return self.get_response(request)

        requested_from = request.META.get('REMOTE_ADDR')
        try:
            request_body = request.body.decode('utf-8')
            request_data = json.loads(request_body)
        except ValueError:
            request_data = str(request.body)

        device_type = request.META.get('HTTP_USER_AGENT')

        model = self.get_model(self.model_name)  # Get the model dynamically

        user_request_log = model(
            apiEndpoint=api_endpoint,
            requestedFrom=requested_from,
            requestBody=request_data,
            createdOn=aware_datetime,
            isProcessed=False,
            deviceType=device_type,
        )
        user_request_log.save()

        response = self.get_response(request)

        if request.user.is_anonymous:
            user_id = 0
        else:
            user_id = request.user.id

        user_request_log.response_status_code = response.status_code
        user_request_log.isProcessed = True
        user_request_log.response_body = response.content
        user_request_log.processedTime = aware_datetime
        user_request_log.user_id = user_id
        user_request_log.save()

        return response

    def get_model(self, model_name):
        # Implement the logic to get the model dynamically based on the provided model_name
        # You can use Django's apps module to fetch the model dynamically
        # Example: from django.apps import apps
        #          model = apps.get_model(app_label='app_label', model_name=model_name)
        raise NotImplementedError("You need to implement the get_model method.")

