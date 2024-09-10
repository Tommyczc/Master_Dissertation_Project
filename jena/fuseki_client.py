from SPARQLWrapper import SPARQLWrapper, TURTLE
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
        named_graph_uri = record_id
        headers = {'Content-Type': 'application/sparql-update'}
        # print("current id: ", named_graph_uri)
        for rdf_file in rdf_files:
            rdf_data = rdf_file['content']
            rdf_format = rdf_file['type']
            # print("update id: ", named_graph_uri)
            # 使用 rdflib 解析 RDF 数据
            g = Graph()
            g.parse(data=rdf_data, format=rdf_format)

            # 将解析后的 RDF 数据转换为 N-Triples 格式
            ntriples_data = g.serialize(format='nt')

            # print(ntriples_data)
            # 构建 SPARQL UPDATE 查询
            update_query = f"""
            INSERT DATA {{
                GRAPH <{named_graph_uri}> {{
                    {ntriples_data}
                }}
            }}
            """

            response = requests.post(f"{self.jena_url}/{self.dataset}/update", data=update_query.encode('utf-8'),
                                     headers=headers)
            if response.status_code >= 300:
                print("error: ", response.status_code)
                return response.status_code, response.text

        return 200, "RDF files uploaded successfully"

    def execute_sparql_query_global(self, query):
        try:
            g = Graph()
            sparql = SPARQLWrapper(f"{self.jena_url}/{self.dataset}/query")
            sparql.setQuery(f"""
                            CONSTRUCT {{ ?s ?p ?o }}
                            WHERE {{
                                GRAPH ?g {{
                                    ?s ?p ?o .
                                }}
                            }}
                            """)
            sparql.setReturnFormat(TURTLE)
            results = sparql.query().convert()
            g.parse(data=results, format="turtle")

            result = g.query(query)
            return 200, result
        except Exception as e:
            print("Error: " + str(e))
            return 500, str(e)

    # def execute_sparql_query_for_graph(self, graph_url, query):
    #     # 检查是否是 SELECT 查询，并插入 FROM 子句
    #     if query.strip().lower().startswith("select"):
    #         select_index = query.lower().find("select")
    #         where_index = query.lower().find("where")
    #         wrapped_query = query[:where_index] + f" FROM <{graph_url}> " + query[where_index:]
    #     else:
    #         wrapped_query = query  # 对于非 SELECT 查询，我们不做任何修改
    #
    #     headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    #     response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': wrapped_query},
    #                              headers=headers)
    #
    #     return response.status_code, response.text

    def get_rdf_data_for_graph(self, graph_url):
        query = f"""
        CONSTRUCT {{
            ?s ?p ?o .
        }}
        WHERE {{
            GRAPH <{graph_url}> {{
                ?s ?p ?o .
            }}
        }}
        """
        response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': query},
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code < 300:
            # print(response.text)
            g = Graph()
            g.parse(data=response.text, format='n3')
            triples = [(str(s), str(p), str(o)) for s, p, o in g]
            # print(triples)
            return triples
        else:
            return None

    # def execute_sparql_update(self, update):
    #     response = self.update_client.run_sparql(update)
    #     return response.convert()

    def delete_rdf_by_record_id(self, record_id):
        named_graph_uri = record_id
        delete_query = f"""
        DELETE WHERE {{
            GRAPH <{named_graph_uri}> {{
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

    def recover_rdf_by_graph_uri(self, graph_uri, g):
        del_code, del_text = self.delete_rdf_by_record_id(graph_uri)
        print(del_code, del_text)
        if del_code >= 300:
            return del_text

        headers = {'Content-Type': 'application/sparql-update'}
        ntriples_data = g.serialize(format='nt')

        # print(ntriples_data)
        # 构建 SPARQL UPDATE 查询
        update_query = f"""
                    INSERT DATA {{
                        GRAPH <{graph_uri}> {{
                            {ntriples_data}
                        }}
                    }}
                    """

        response = requests.post(f"{self.jena_url}/{self.dataset}/update", data=update_query.encode('utf-8'),
                                 headers=headers)
        if response.status_code >= 300:
            return response.text
        return None

    def execute_simple_query(self, query):

        response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': query},
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code < 300:
            return response.text
        else:
            return None
