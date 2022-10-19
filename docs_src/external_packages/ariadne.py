from ariadne import QueryType, make_executable_schema
from ariadne.asgi import GraphQL

from esmerald import Esmerald, Include

type_defs = """
    type Query {
        hello: String!
    }
"""

query = QueryType()


@query.field("hello")
def resolve_hello(*_):
    return "Hello world!"


# Create executable schema instance
schema = make_executable_schema(type_defs, query)

app = Esmerald(debug=True, routes=[Include("/graphql", GraphQL(schema, debug=True))])
