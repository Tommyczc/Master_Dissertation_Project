import platform
from mlx_lm import load, generate
model, tokenizer = load("mlx-community/Meta-Llama-3-8B-Instruct-4bit")
# if __name__ == '__main__':
#     print(platform.processor())

from transformers import pipeline
from IPython.display import display

SYSTEM_MSG = "You are a helpful chatbot assistant."

def generateFromPrompt(promptStr,maxTokens=100):
    if platform.processor() == 'arm':
      messages = [ {"role": "system", "content": SYSTEM_MSG},
              {"role": "user", "content": promptStr}, ]
      input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
      prompt = tokenizer.decode(input_ids)
      response = generate(model, tokenizer, prompt=prompt, max_tokens=maxTokens)
    else:
      message = [{"role": "user", "content": promptStr},]
      pipe = pipeline("text-generation", model=model, tokenizer=tokenizer,max_new_tokens=maxTokens)
      result = pipe(message)
      response = result[0]['generated_text'][1]['content']
    return(response)


response = generateFromPrompt("Please introduce yourself")

print(response+"...")