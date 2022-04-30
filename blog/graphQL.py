from graphene import relay, Field
from graphene_django import DjangoObjectType

from blog.models import BlogPost
from users.graphQL import UserType
from users.models import User


class PostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        fields = "__all__"

    post_author = Field(UserType)

    def resolve_post_author(parent, info):
        return User.objects.get(id=parent.post_author)
