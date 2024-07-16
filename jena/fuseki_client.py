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

        for rdf_file in rdf_files:
            rdf_data = rdf_file['content']
            rdf_format = rdf_file['type']

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
                return response.status_code, response.text

        return 200, "RDF files uploaded successfully"

    def execute_sparql_query_global(self, query):
        # 获取所有命名图
        list_graphs_query = """
               SELECT DISTINCT ?g WHERE {
                   GRAPH ?g { ?s ?p ?o }
               }
               """
        graph_results = self.query_client.run_sparql(list_graphs_query).convert()
        graph_uris = [result['g']['value'] for result in graph_results['results']['bindings']]

        # 构建 FROM 子句
        from_clauses = " ".join([f"FROM <{graph_uri}>" for graph_uri in graph_uris])

        # 检查是否是 SELECT 查询，并插入 FROM 子句
        wrapped_query=''
        if query.strip().lower().startswith("select"):
            select_index = query.lower().find("select")
            where_index = query.lower().find("where")
            wrapped_query = query[:where_index] + " " + from_clauses + " " + query[where_index:]
        else:
            wrapped_query = query  # 对于非 SELECT 查询，我们不做任何修改
        # print(wrapped_query)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': wrapped_query.encode('utf-8')},
                                 headers=headers)

        # print('res: ',response.status_code,response.text)
        # if response.status_code < 300:
        #     return 200,response.json()
        # else:
        return response.status_code, response.text

    def execute_sparql_query_for_graph(self, graph_url, query):
        # 检查是否是 SELECT 查询，并插入 FROM 子句
        if query.strip().lower().startswith("select"):
            select_index = query.lower().find("select")
            where_index = query.lower().find("where")
            wrapped_query = query[:where_index] + f" FROM <{graph_url}> " + query[where_index:]
        else:
            wrapped_query = query  # 对于非 SELECT 查询，我们不做任何修改

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': wrapped_query},
                                 headers=headers)

        return response.status_code, response.text

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
        response = requests.post(f"{self.jena_url}/{self.dataset}/query", data={'query': query}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code < 300:
            g = Graph()
            g.parse(data=response.text, format='n3')
            triples = [(str(s), str(p), str(o)) for s, p, o in g]
            # print(triples)
            return triples
        else:
            return None

    def execute_sparql_update(self, update):
        response = self.update_client.run_sparql(update)
        return response.convert()

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

