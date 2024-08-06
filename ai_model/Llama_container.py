from flask import current_app
from mlx_lm import load, generate

from Common_tools.rdf_tools import rdf_to_natural_language


class LlamaContainer:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.system_message = ''
        self.max_tokens = 100

    def initialize_model(self):
        with current_app.app_context():
            self.model, self.tokenizer = load("mlx-community/Meta-Llama-3-8B-Instruct-4bit")
            # generate system message
            self.generate_system_message()
            print("Llama model initialized")

    def generate_answer(self, question: str):
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": question},
        ]

        # transfer text into input index
        input_ids = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True)
        prompt = self.tokenizer.decode(input_ids)
        response = generate(self.model, self.tokenizer, prompt=prompt, max_tokens=self.max_tokens)
        return response

    def generate_system_message(self):
        jena_client = current_app.config['JENA_CLIENT']
        code, text = jena_client.execute_sparql_query_global("SELECT * WHERE { ?sub ?pred ?obj .}")
        if code == 200:
            rdf_to_nl = rdf_to_natural_language(text)
            self.system_message = (
                f"You are a knowledgeable assistant who answers questions based on the provided data, "
                f"If the user's question is out of scope for this dataset, you should only answer: Sorry, this question is out of scope."
                f"\n\nHere is the data:\n{rdf_to_nl}")
        else:
            self.system_message = "There was an error in database, if user ask questions, you should answer: Database error, Please tell the relevant personnel to deal with it"
