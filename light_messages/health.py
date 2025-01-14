from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import os

@api_view(['GET'])
def health_check(request):
    """
    A simple health check endpoint that returns 200 OK
    """
    return Response({
            "status": "healthy",
            "pod_name": os.getenv("POD_NAME", "N/A"),
        },
        status=status.HTTP_200_OK
    )