import graphene

from MyPortfolioDjango.graphQL import graph_ql_user_authenticated
from blog.graphQL import PostType
from blog.models import BlogPost


class Query(graphene.ObjectType):
    allBlogPosts = graphene.List(PostType)

    @graph_ql_user_authenticated
    def resolve_allBlogPosts(self, info, **kwargs):
        res = BlogPost.objects.all()
        return res


schema = graphene.Schema(query=Query)