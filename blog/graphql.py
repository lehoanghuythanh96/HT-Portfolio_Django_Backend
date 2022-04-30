from graphene_django import DjangoObjectType

from blog.models import BlogPost


class AllPostType(DjangoObjectType):
    class Meta:
        model = BlogPost
        fields = "__all__"
