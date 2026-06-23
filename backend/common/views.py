import os
import uuid

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView


class UploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(file_obj.name)[1].lower()
        allowed = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf'}
        max_size = 5 * 1024 * 1024
        if ext not in allowed:
            return Response({'detail': 'Unsupported file type'}, status=status.HTTP_400_BAD_REQUEST)
        if file_obj.size > max_size:
            return Response({'detail': 'File size must be 5MB or smaller'}, status=status.HTTP_400_BAD_REQUEST)

        subdir = request.data.get('subdir', 'uploads')
        folder = os.path.join(settings.MEDIA_ROOT, subdir)
        os.makedirs(folder, exist_ok=True)

        filename = f'{uuid.uuid4().hex}{ext}'
        filepath = os.path.join(folder, filename)
        with open(filepath, 'wb+') as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        url = request.build_absolute_uri(settings.MEDIA_URL + f'{subdir}/{filename}')
        return Response({'url': url, 'filename': filename})
