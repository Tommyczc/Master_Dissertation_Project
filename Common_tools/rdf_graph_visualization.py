import networkx as nx
import matplotlib.pyplot as plt
import io
import base64


def remove_uri_prefix(uri):
    return uri.split('/')[-1]


def transfer_RDF_to_graph(triples):
    G = nx.DiGraph()
    for s, p, o in triples:
        G.add_edge(remove_uri_prefix(s), remove_uri_prefix(o), label=remove_uri_prefix(p))

    pos = nx.spring_layout(G, k=0.15, iterations=20)

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, arrows=True, node_size=3000, node_color="skyblue", font_size=10,
            font_weight="bold", edge_color="gray",
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

    plt.tight_layout(pad=2.0)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64
