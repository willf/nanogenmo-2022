# Nanogenmo 2022

Use OpenAI's DaVinci model to convert from a formal text to a modern English version. Often translations from Greek or Latin done in the late 1800s and early 1900s seem very "stuffy". Can OpenAI convert this for me?

## Installation

This assumes you use Poetry to manage Python libraries etc

```bash
> poetry shell
```

You will also need an API key from https://openai.com/api/

You can put this in a environment variable called `OPENAI_API_KEY` or in a local config file called `.env` which should look like:

```
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

where the value is your OpenAI API key.

Assuming you have a text in Markdown format -- in particular, plainish text with paragraphs separated by two newlines, you can do the following (assuming you also have `tee`, `sed`, and `jq` installed.)

```bash
cat examples/YOUR_TEXT | poetry run python openapi_completer.py| tee /tmp/juliet.json | jq  -r .conversion | sed G | cat -s > YOUR_CONVERTED_TEXT
```

You still may need to massage the output a bit.

This part:

```
cat examples/YOUR_TEXT | poetry run python openapi_completer.py
```

will send to standard output, for each paragraph, a 'JSONL' record with keys `paragraph` and `conversion`, where `paragraph` is the original paragraph, and `conversion` is the converted paragraph.

The `openapi_completer.py` script is actually pretty general. You can replace the `prompt.template` file with your own template if you want to try different things. It is left as an exercise for the reader to make the script take command line arguments to allow this in general...

Enjoy!

Made with :heart: by @willf.
