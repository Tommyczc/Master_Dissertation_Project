import networkx as nx
from pyvis.network import Network


def remove_uri_prefix(uri):
    return uri.split('/')[-1]


def transfer_RDF_to_graph(triples):
    G = nx.DiGraph()
    for s, p, o in triples:
        G.add_edge(remove_uri_prefix(s), remove_uri_prefix(o), label=remove_uri_prefix(p))

    nodes = [{'id': node, 'label': node} for node in G.nodes()]
    edges = [{'from': u, 'to': v, 'label': data['label'], 'title': data['label']} for u, v, data in G.edges(data=True)]
    return nodes, edges
