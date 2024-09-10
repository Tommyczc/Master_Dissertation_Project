import json

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


# transfer the rdf data from jena to natural language
def rdf_to_natural_language(result):
    descriptions = []
    for s, o, p in result:
        subj = s.split('/')[-1]
        pred = p.split('/')[-1].replace('_', ' ')
        obj = o.split('/')[-1]
        description = f"{subj} {pred} {obj}."
        descriptions.append(description)
    return "\n".join(descriptions)
