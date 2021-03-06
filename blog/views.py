

# Create your views here.
import os
import uuid

import magic
from django.core.files.storage import FileSystemStorage
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from MyPortfolioDjango import settings
from blog.models import BlogMedia
from blog.serializers import BlogMediaSerializer, BlogPostSerializer
from users.models import User


class uploadPostImg(APIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = BlogMediaSerializer

    def post(self, request, *args, **kwargs):
        upload = request.FILES['upload']
        _name, _ext = os.path.splitext(upload.name)
        newName = str(uuid.uuid4()) + _ext

        postMediaFolder = f"{settings.MEDIA_ROOT}/{settings.POST_MEDIA_FOLDER}"
        if not os.path.isdir(postMediaFolder):
            os.mkdir(postMediaFolder)

        fss = FileSystemStorage()
        fss.save(f"{settings.POST_MEDIA_FOLDER}/{newName}", upload)

        media_path = f"{postMediaFolder}/{newName}"
        file_type = magic.from_file(media_path, mime=True)

        if (file_type not in ['image/jpeg', 'image/png']):
            if os.path.isfile(media_path):
                os.remove(media_path)
                return Response({"message": "This file type is not allowed!"}, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        newMedia = BlogMedia(
            ID=uuid.uuid4(),
            media_name=newName,
            media_author=request.user,
            media_path=f"{settings.POST_MEDIA_FOLDER}/{newName}",
            media_type=file_type,
            media_status="trash",
            media_parent=None,
            media_category=settings.MEDIA_CATEGORIES["blogPost"]
        )
        BlogMedia.save(newMedia)

        serializer = self.serializer_class(newMedia)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAllTrashMedia(APIView):
    def post(self, request):
        try:
            allTrashMedia = BlogMedia.objects.filter(media_status="trash")
            for item in allTrashMedia.iterator():
                if item.media_path is not None:
                    realpath = f"{settings.MEDIA_ROOT}/{item.media_path}"
                    if os.path.isfile(realpath):
                        os.remove(realpath)
                    item.delete()
            return Response({"message": "All trash media successfully deleted"}, status=status.HTTP_200_OK)
        except BaseException as error:
            print(error)
            return Response({"message": "Can not execute command"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SaveSingleBlogPost(APIView):
    def post(self, request):
        postInfo = request.data["postInfo"]
        postInfo["id"] = uuid.uuid4()
        postInfo["post_author"] = request.user.id
        postInfo["post_status"] = "publish"
        postInfo["post_type"] = settings.POST_TYPES["blogPost"]
        validPostInfo = BlogPostSerializer(data=postInfo)
        validPostInfo.is_valid(raise_exception=True)
        newPost = validPostInfo.save()

        post_imgs = request.data.get('post_imgs')
        imgList = []
        for item in post_imgs:
            imgList.append(item['media_name'])
        allTrashMedia = BlogMedia.objects.filter(media_status="trash")
        for item in allTrashMedia.iterator():
            if item.media_name in imgList:
                item.media_status = "publish"
                item.media_parent = newPost
                item.save()
                print(item.media_name)
        return Response({"message": "Post saved successfully"}, status=status.HTTP_201_CREATED)