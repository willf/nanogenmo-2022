import os

import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

response = openai.Completion.create(
  model="text-davinci-002",
  prompt="Correct this to modern, idiomatic, plain English.\n\nNay but he himself rather is a liar from, the beginning,3 and so is any man whom he has suborned with his own <coin>, like Praxeas.",
  temperature=0,
  max_tokens=3887,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
