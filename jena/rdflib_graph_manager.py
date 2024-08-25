from flask import current_app
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, TURTLE
from rdflib.plugins.sparql import processUpdate


class GraphManager:
    def __init__(self):
        self.graphs = {}
        self.user_count = {}

    def load_graph(self, graph_uri):
        if 'JENA_CLIENT' in current_app.config:
            jena_client = current_app.config['JENA_CLIENT']
            fuseki_endpoint = f"{jena_client.jena_url}/{jena_client.dataset}/query"
            if graph_uri not in self.graphs:
                g = Graph()
                sparql = SPARQLWrapper(fuseki_endpoint)
                sparql.setQuery(f"""
                    CONSTRUCT {{ ?s ?p ?o }}
                    WHERE {{
                        GRAPH <{graph_uri}> {{
                            ?s ?p ?o .
                        }}
                    }}
                    """)
                sparql.setReturnFormat(TURTLE)
                results = sparql.query().convert()
                # print(graph_uri)
                # print(results)
                g.parse(data=results, format="turtle")

                self.graphs[graph_uri] = g
            self.user_count[graph_uri] = self.user_count.get(graph_uri, 0) + 1
            return 1
        else:
            return 0

    def query_graph(self, graph_uri, query):
        if graph_uri in self.graphs:
            result = self.graphs[graph_uri].query(query)
            data = []
            for s, o, p in result:
                data.append({'Subject': s, 'Object': o, 'Predicate': p})
            return data
        else:
            return None

    def update_query_graph(self, graph_uri, update_query):
        if graph_uri in self.graphs:
            try:
                processUpdate(self.graphs[graph_uri], update_query)
                jena_client = current_app.config['JENA_CLIENT']
                res=jena_client.recover_rdf_by_graph_uri(graph_uri,self.graphs[graph_uri])
                if res is not None:
                    return res
                return "Updated the data successfully"
            except Exception as e:
                return str(e)
        else:
            return "Cannot find this data record, jena's problem"



    def unload_graph(self, graph_uri):
        if graph_uri in self.user_count:
            self.user_count[graph_uri] -= 1
            if self.user_count[graph_uri] == 0:
                del self.graphs[graph_uri]
                del self.user_count[graph_uri]


graph_manager = GraphManager()
