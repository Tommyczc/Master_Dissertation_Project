import unittest
import os
import time
import requests
import socketio

# Define the endpoint URLs and paths
UPLOAD_URL = "http://localhost:5000/upload_rdf"  # Replace with your actual endpoint
QUERY_SOCKET_URL = "http://localhost:5000/socket.io/"  # Replace with your actual endpoint
TEST_RDF_FILES = ["format_rdf.rdf", "format_ttl.ttl", "format_nt.nt", "format_xml.xml"]  # List of test RDF files

# Initialize Socket.IO client
sio = socketio.Client()

class TestRDFUploadAndSocket(unittest.TestCase):

    def setUp(self):
        # Ensure the Socket.IO client is connected before testing
        sio.connect(QUERY_SOCKET_URL)

    def tearDown(self):
        # Disconnect the Socket.IO client after each test
        sio.disconnect()

    def test_upload_rdf_formats(self):
        """
        Test uploading RDF files in different formats (e.g., .rdf, .ttl, .n3) to the server.
        """
        for rdf_file in TEST_RDF_FILES:
            with open(f"rdf_data/format_test_files/{rdf_file}", 'rb') as f:
                files = {'file': (os.path.basename(rdf_file), f)}
                response = requests.post(UPLOAD_URL, files=files)
                self.assertEqual(response.status_code, 200, f"Upload failed for {rdf_file}")
                print(f"Upload successful for {rdf_file}")

    def test_socket_query_performance(self):
        """
        Test the performance of a SPARQL query over a WebSocket connection.
        Measures the round-trip time for a sample query.
        """
        start_time = time.time()
        query_response = []

        @sio.on('query_response')
        def handle_query_response(data):
            query_response.append(data)

        # Sending a test SPARQL query via WebSocket
        sample_query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        sio.emit('SPARQL_query', {'query': sample_query})

        # Wait for response or timeout after 5 seconds
        timeout = 5
        elapsed_time = 0
        while not query_response and elapsed_time < timeout:
            time.sleep(0.1)
            elapsed_time = time.time() - start_time

        if query_response:
            response_time = time.time() - start_time
            print(f"Query Response Time: {response_time:.2f} seconds")
        else:
            self.fail("Query did not return a response within the timeout period.")

if __name__ == "__main__":
    unittest.main()