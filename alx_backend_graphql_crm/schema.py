import graphene
from alx_backend_graphql_crm.crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=CRMQuery, mutation=CRMMutation)
