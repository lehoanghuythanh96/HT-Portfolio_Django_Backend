from http.cookies import SimpleCookie

import jwt
from django.contrib.auth import get_user_model

from MyPortfolioDjango import settings


class CustomJSONWebTokenMiddleware:

    def get_user(self, token):
        validated_token = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT["ALGORITHM"])
        if "id" in validated_token:
            user = get_user_model().objects.get(id=validated_token["id"])
            if user:
                return user
        return None

    def check_refresh_token(self, info):
        raw_cookie = info.context.headers.get('Cookie')
        cookie = SimpleCookie()
        cookie.load(raw_cookie)
        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        if "refresh_token" in cookies:
            try:
                return self.get_user(cookies["refresh_token"])
            except BaseException as error:
                print(error)
                return None
        return None

    def resolve(self, next, root, info, **kwargs):

        user = self.check_refresh_token(info)
        if user is not None:
            info.context.user = user

        return next(root, info, **kwargs)


def graph_ql_user_authenticated(func):
    def inner(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise Exception("You don't have permission to access this data")
        return func(self, info, **kwargs)
    return inner
