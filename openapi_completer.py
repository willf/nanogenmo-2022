import configparser
import json
import os
import re
import sys
import textwrap
import time

import openai


class ConfigReader():
    def __init__(self, config_var, config_file='.env', default=None):
        self.config_var = config_var
        self.default = default
        self.config_file = config_file

    def read(self):
        """
        Reads an config variable.
        It tries the following:
        1. If the config variable is set, it returns the value.
        2. If the config variable is not set, it tries to read it from a Config file.
        3. If the config variable is not set and the Config file is not found, it used the default value.
        4. Otherwise, it raises an exception.

        """
        value = os.getenv(self.config_var)
        if value is not None:
            return value
        if self.config_file:
            path = os.path.join(os.path.dirname(__file__), self.config_file)
            config = configparser.ConfigParser()
            config.read(path)
            value = config['DEFAULT'][self.config_var]
            if value is not None:
                return value
        if self.default is not None:
            return self.default
        raise Exception(f"Config variable {self.config_var} is not set.")

class ChunkingCompleter():
    def __init__(self, prompt_file='prompt.template',
        variable_name='{{TEXT}}',
        engine='text-davinci-002',
        temperature=0.6,
        top_p=1.0,
        frequency_penalty=0.25,
        presence_penalty=0.0,
        stop=['<<END>>'],
        max_tokens=3750,
        chunk_size=1000,
        max_tries=3):
        openai.api_key = ConfigReader('OPENAI_API_KEY').read()
        self.prompt_file = prompt_file
        self.variable_name = variable_name
        self.engine = engine
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.max_tokens = max_tokens
        self.chunk_size = chunk_size
        self.max_tries = max_tries

    def get_prompt(self):
        """Gets the prompt template."""
        path = os.path.join(os.path.dirname(__file__), self.prompt_file)
        with open(path) as f:
            prompt = f.read()
        return prompt

    def chunk_text(self, text):
        """Chunks text into chunks of size chunk_size."""
        return textwrap.wrap(text, self.chunk_size)

    def complete_chunk(self, chunk, prompt):
        """Completes a chunk of text."""
        tries = 1
        while tries < self.max_tries:
            tries += 1
            try:
                response = openai.Completion.create(
                    model="text-davinci-002",
                    prompt=prompt.replace(self.variable_name, chunk),
                    temperature=self.temperature,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=self.stop,
                    max_tokens=self.max_tokens
                )

                completion_chunk = response['choices'][0]['text'].strip()
                completion_chunk = re.sub('\s+', ' ', completion_chunk)
                return {'completion': completion_chunk, 'success': True}
            except Exception as e:
                print(e)
                sys.stderr.write('Error: {{}} Retrying... in {{}} seconds.\n'.format(e, tries-1))
                sys.stderr.flush()
                time.sleep(tries-1)
        return {'completion': '', 'success': False}
    def complete(self, text):
        """Completes text."""
        prompt = self.get_prompt()
        chunks = self.chunk_text(text)
        for chunk in chunks:
            completion = self.complete_chunk(chunk, prompt)
            result = {
                'chunk': chunk,
                'completion': completion["completion"],
                'success': completion["success"]
            }
            yield result

if __name__ == '__main__':
    completer = ChunkingCompleter()
    text = sys.stdin.read()
    for result in completer.complete(text):
        json.dump(result, sys.stdout)
        sys.stdout.write('\n')
        sys.stdout.flush()

## TODO:
# 1. Get a better chucking algorithm!
# 2. Maintain paragraph breaks.
