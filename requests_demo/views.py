from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import HasDemoApiKey
from .serializers import DemoRequestSerializer


class DemoRequestCreateAPIView(APIView):
    permission_classes = [HasDemoApiKey]

    def post(self, request):
        serializer = DemoRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        demo_request = serializer.save()

        return Response(
            {
                "ok": True,
                "id": demo_request.id,
            },
            status=status.HTTP_201_CREATED,
        )
