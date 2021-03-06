import os
import urllib
import certifi
import uuid

from django.contrib.auth import user_logged_in

# Create your views here.
import requests
from django.forms import model_to_dict
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView

from MyPortfolioDjango import settings
from blog.models import BlogMedia
from users.auth import CustomRefreshToken
from users.models import User
from users.serializers import UserSerializer


def saveNewUser(user, avatar_url):

    user["id"] = uuid.uuid4()
    serializer = UserSerializer(data=user)
    serializer.is_valid(raise_exception=True)
    newUser = serializer.save()

    if avatar_url is not None:
        try:
            userMediaFolder = f"{settings.MEDIA_ROOT}/{settings.USER_MEDIA_FOLDER}"
            if not os.path.isdir(userMediaFolder):
                os.mkdir(userMediaFolder)
            avatar_name = f"{user['id']}.jpeg"
            avatar_path = f"{userMediaFolder}/{avatar_name}"
            f = open(avatar_path, 'wb')
            f.write(urllib.request.urlopen(avatar_url, cafile=certifi.where()).read())
            f.close()
            newMedia = BlogMedia(
                ID=uuid.uuid4(),
                media_name=user['id'],
                media_author=newUser,
                media_path=f"{settings.USER_MEDIA_FOLDER}/{avatar_name}",
                media_type="image/jpeg",
                media_status="publish",
                media_parent=None,
                media_category=settings.MEDIA_CATEGORIES["userAvatar"]
            )
            BlogMedia.save(newMedia)

        except BaseException as err:
            print(err)

    return newUser


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        user = request.data
        res = saveNewUser(user, None)
        data = model_to_dict(res)
        return Response(data, status=status.HTTP_201_CREATED)


def createCredentials(request, user):
    user_logged_in.send(sender=user.__class__,
                        request=request, user=user)

    refresher = CustomRefreshToken.for_user(user)

    response = Response()
    # response.set_cookie(
    #     key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    #     value=str(refresh.access_token),
    #     max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_MAXAGE'],
    #     secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    #     httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    #     samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
    #     path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH']
    # )

    response.set_cookie(
        key=settings.SIMPLE_JWT['REFRESH_COOKIE'],
        value=str(refresher),
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_MAXAGE'],
        secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
        path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH']
    )
    response.data = {"message": "Signed in successfully", "access_token": str(refresher.access_token)}
    response.status_code = status.HTTP_200_OK
    return response


@api_view(['POST'])
@permission_classes([AllowAny, ])
@authentication_classes([])
def authenticate_user(request):
    try:
        email = request.data['email']
        password = request.data['password']

        try:
            user = User.objects.get(email=email)
            if user:
                if user.check_password(password) is False:
                    return Response({"message": "Wrong password"}, status=status.HTTP_400_BAD_REQUEST)

                try:
                    res = createCredentials(request, user)
                    return res

                except BaseException as error:
                    print(error)
                    return Response({"message": "User authentication failed"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {"message": "Can not authenticate with the given credentials or the account has been deactivated"},status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            return Response({"message": "Email or password is wrong"}, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        return Response({"message": 'Please provide a email and a password'}, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    # Allow only authenticated users to access this url
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = UserSerializer(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyGoogleTokenId(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        payload = {'access_token': request.data.get("token")}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)
        if "email" in data:
            user = User.objects.filter(email=data["email"])
            if user.count() == 1:
                try:
                    res = createCredentials(request, user[0])
                    return res
                except BaseException as error:
                    print(f"GG token ID check error: {error}")
                    return Response({"message": "Access token generation failed"}, status=status.HTTP_400_BAD_REQUEST)
            elif user.count() == 0:
                try:
                    avatar_url = None

                    if "picture" in data:
                        avatar_url = data["picture"]

                    userInstance = {
                        "email": data["email"],
                        "full_name": data["name"],
                        "password": str(uuid.uuid4())
                    }
                    newUser = saveNewUser(userInstance, avatar_url)

                    res = createCredentials(request, newUser)
                    res.data["message"] = "Signed in successfully, please change your password in user menu"
                    res.status = status.HTTP_201_CREATED

                    return res
                except BaseException as error:
                    print(error)
                    return Response({"message": "Can not create user with this email, please try again"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "There are more than 1 accounts with this email, please contact admin for more information"},
                                status=status.HTTP_400_BAD_REQUEST)
            # image_url = data["picture"]  # the image on the web
            # save_name = 'my_image.jpg'  # local name to be saved
            # urllib.request.urlretrieve(image_url, f"{settings.MEDIA_ROOT}/{save_name}")

        else:
            return Response({"message": "Google access token authentication failed"}, status=status.HTTP_400_BAD_REQUEST)