import logging
import time

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)



class AsyncRequestLoggerMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        super().__init__(get_response)

        # Set up a logger for request logging
        log_file = getattr(settings, 'REQUEST_LOG_FILE', 'request.log')  # Default log file
        handler = logging.FileHandler(log_file)

        # Define an extended log format
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(status_code)d "%(http_method)s %(path)s" '
            '(%(duration).3f ms) [%(client_ip)s:%(client_port)s -> %(server_port)s] '
            '[%(user_agent)s]'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def __call__(self, request):
        # Capture the start time to calculate request duration
        start_time = time.monotonic()

        # Process the request and get the response
        response = await self.get_response(request)

        # Calculate the total duration (in milliseconds)
        duration = (time.monotonic() - start_time) * 1000

        # Log the request details
        await self.log_request(request, response, duration)

        return response

    async def log_request(self, request, response, duration):
        """
        Log the HTTP request and response data with extended details.
        """
        # Capture client and server-related data
        client_ip, client_port = self.get_client_ip_and_port(request)
        server_port = self.get_server_port(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        # Log all relevant details
        await sync_to_async(logger.info)(
            '',
            extra={
                'http_method': request.method,
                'path': request.get_full_path(),
                'status_code': response.status_code,
                'client_ip': client_ip,
                'client_port': client_port,
                'server_port': server_port,
                'duration': duration,  # request duration in milliseconds
                'user_agent': user_agent,
            }
        )  # noqa

    @staticmethod
    def get_client_ip_and_port(request):
        """
        Extract the client IP and port number from the request object.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_port = x_forwarded_for.split(',')[0]
        else:
            ip_port = request.META.get('REMOTE_ADDR', '')

        # Parse client IP and port if present
        if ':' in ip_port:
            ip, port = ip_port.rsplit(':', 1)
            return ip, port
        return ip_port, 'Unknown'

    @staticmethod
    def get_server_port(request):
        """
        Extract the server port number from the request object.
        """
        return request.META.get('SERVER_PORT', 'Unknown')
