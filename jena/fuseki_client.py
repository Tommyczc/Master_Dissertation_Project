from pyfuseki import FusekiUpdate, FusekiQuery
import requests
from rdflib import Graph


class JenaClient:
    def __init__(self, jena_url, dataset):
        self.jena_url = jena_url
        self.dataset = dataset
        self.update_client = FusekiUpdate(jena_url, dataset)
        self.query_client = FusekiQuery(jena_url, dataset)

    def upload_rdf_files(self, rdf_files, record_id):
        try:
            for rdf_file in rdf_files:
                rdf_data = rdf_file['content']
                rdf_type = rdf_file['type']

                # use rdflib to analyse RDF data and convert to N-Triples
                g = Graph()
                g.parse(data=rdf_data, format=rdf_type)
                ntriples_data = g.serialize(format='nt')

                headers = {
                    'Content-Type': 'application/sparql-update'
                }
                # insert the data to default graph
                update_query = f"""
                            INSERT DATA {{
                                {ntriples_data}
                                <http://example.org/record/{record_id}> <http://example.org/hasUploaded> _:b0 .
                            }}
                            """
                response = requests.post(f"{self.jena_url}/{self.dataset}/update", data=update_query.encode('utf-8'),
                                         headers=headers)
                if response.status_code >= 300:
                    print("Fuseki Error: {}".format(response.text))
                    return response.status_code, response.text

                # insert the data to single graph
                record_graph_query = f"""
                       INSERT DATA {{
                           GRAPH <http://example.org/graph/{record_id}> {{
                               <http://example.org/record/{record_id}> <http://example.org/hasUploaded> _:b0 .
                           }}
                       }}
                       """
                response = requests.post(f"{self.jena_url}/{self.dataset}/update",
                                         data=record_graph_query.encode('utf-8'), headers=headers)
                if response.status_code >= 300:
                    print("Fuseki Error: {}".format(response.text))
                    return response.status_code, response.text

            return 200, "All RDF files uploaded successfully"

        except Exception as e:
            print("Error: " + str(e))
            return 500, str(e)

    def execute_sparql_query(self, query):
        response = self.query_client.run_sparql(query)
        return response.convert()

    def execute_sparql_update(self, update):
        response = self.update_client.run_sparql(update)
        return response.convert()

    def delete_rdf_by_record_id(self, record_id):
        delete_query = f"""
        DELETE WHERE {{
            GRAPH <http://example.org/graph/{record_id}> {{
                ?s ?p ?o .
            }}
        }}
        """
        headers = {
            'Content-Type': 'application/sparql-update'
        }
        response = requests.post(f"{self.jena_url}/{self.dataset}/update", data=delete_query.encode('utf-8'),
                                 headers=headers)
        return response.status_code, response.text
