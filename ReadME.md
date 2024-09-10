# Unified Semantic Web Interface: Managing, Querying, and Visualizing Integrated RDF Data

## Project Requirements

This project must run on an ARM architecture (e.g. MacOS) system and relies on Python interpreter version 3.11.8 (ARM version). Running on other architectures may cause compatibility issues. Ensure that the project environment meets the following requirements:

1. Python interpreter: 3.11.8 (ARM version).
2. MongoDB is correctly installed and configured.
3. Jena Fuseki server is correctly installed and configured.

## Database Connection

* Mongoose Connection (in `app.py`):

        # ini database connection
        db, fs = init_db("mongodb://localhost:27017") #input the conne4ction uri
        db_interface = MongoDBInterface(db, fs)

* Jena Fuseki Connection (in `app.py`):

        # ini Jena connection
        jena_client = JenaClient(jena_url='http://127.0.0.1:3030', dataset='test')

## Set up
1. Download ARM python interpreter.
2. Make sure you have set up MongoDB and Jena Fuseki correctly.
3. Download the python libraries
`pip install -r requirements.txt`.
4. In `app.py`, make sure the database connection uri is correct.
5. Run the project `python app.py`

## Others
`Github`: https://github.com/Tommyczc/Master_Dissertation_Project
