import json
import os
import re
import sys

import openai
from bs4 import BeautifulSoup


class ModernEnglishConverter():
    def __init__(self, api_key=None, base_prompt='Correct this to modern, idiomatic, plain English.\n\n', max_tokens=4000):
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        self.base_prompt = base_prompt
        self.max_tokens = max_tokens

    def convert(self, text):
        """Converts text to modern English."""
        # log to stderr
        print(f"Converting text: ->{text}<-", file=sys.stderr)

        prompt = f"{self.base_prompt}{text}"

        approximate_length = len(text) * 2 + len(self.base_prompt)
        approximate_number_of_tokens_required = approximate_length // 4
        if approximate_number_of_tokens_required > self.max_tokens:
            raise ValueError(f"Text is too long. Approximate number of tokens required: {approximate_number_of_tokens_required}")

        response = openai.Completion.create(
          model="text-davinci-002",
          prompt=prompt,
          temperature=0,
          max_tokens=self.max_tokens,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        d = {
            'text': text,
            'converted_text': response['choices'][0]['text'].strip(),
            'completion': response
            }
        return d

def squeeze(text):
    """Squeezes a string by removing extra spaces and newlines."""
    return re.sub(r'\s+', ' ', text).strip()

def split_on_punctuation(text):
    """Splits text on punctuation."""
    return re.split(r'(?<=[.!?]) +', text)

def flatten(l):
    return [item for sublist in l for item in sublist]

def split_on_size(text, max_size=200):
    """Split text into chunks of max_size."""
    return [text[i:i+max_size] for i in range(0, len(text), max_size)]

def split_text(text):
    """splits text into sentences and then splits sentences into chunks of 1000 characters."""
    return flatten([split_on_size(s) for s in split_on_punctuation(text)])

def convert_html_text(html_text, pretty_print=True):
    """Converts HTML text to modern English."""
    soup = BeautifulSoup(html_text, 'html.parser')
    converter = ModernEnglishConverter()
    # walk the tree and convert each text node
    for text_node in soup.find_all(text=True):
        if text_node.parent.name not in ['p','li','h1','h2','h3','h4','h5','h6','i','b','strong','em','a']:
            continue
        text = squeeze(str(text_node))
        if len(text) <= 20:
            continue
        splits = split_text(text)
        # log splits to stderr
        for s in splits:
          print(f"Split text: ->{s}<-", file=sys.stderr)
        replacement_texts = [converter.convert(s)['converted_text'] for s in splits]
        replacement_text = ''.join(replacement_texts)
        text_node.replace_with(replacement_text)
    if pretty_print:
        return soup.prettify()
    return soup

def convert_text(text):
    """Converts text to modern English."""
    converter = ModernEnglishConverter()
    splits = split_text(text)
    # log splits to stderr
    for s in splits:
      print(f"Split text: ->{s}<-", file=sys.stderr)
    replacement_texts = [converter.convert(s)['converted_text'] for s in splits]
    replacement_text = ''.join(replacement_texts)
    return replacement_text



if __name__ == '__main__':
    converter = ModernEnglishConverter()
    # collect text from stdin
    text = ''
    while True:
        try:
            line = input()
        except EOFError:
            break
        text += line
    # convert text
    d = convert_text(text)

    print(d)
