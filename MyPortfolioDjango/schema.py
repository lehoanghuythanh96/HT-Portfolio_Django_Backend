import graphene

from MyPortfolioDjango.graphQL import graph_ql_user_authenticated
from blog.graphql import AllPostType
from blog.models import BlogPost


class Query(graphene.ObjectType):
    allBlogPosts = graphene.List(AllPostType)

    @graph_ql_user_authenticated
    def resolve_allBlogPosts(self, info, **kwargs):
        return BlogPost.objects.all()


schema = graphene.Schema(query=Query)