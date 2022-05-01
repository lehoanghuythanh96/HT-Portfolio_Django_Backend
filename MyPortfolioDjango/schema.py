import graphene
from graphene_django import DjangoObjectType

from MyPortfolioDjango.graphQL import graph_ql_user_authenticated, AdminPanelType
from blog.graphQL import BlogPostType
from blog.models import BlogPost, AdminPanel


class Query(graphene.ObjectType):
    allBlogPosts = graphene.List(BlogPostType)
    adminPanel = graphene.Field(AdminPanelType)

    @graph_ql_user_authenticated
    def resolve_allBlogPosts(self, info, **kwargs):
        res = BlogPost.objects.all()
        return res

    @graph_ql_user_authenticated
    def resolve_adminPanel(self, info, **kwargs):
        if AdminPanel.objects.first() is None:
            AdminPanel.objects.create()
        res = AdminPanel.objects.first()
        return res


schema = graphene.Schema(query=Query)