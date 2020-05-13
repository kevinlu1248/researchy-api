# Researchy API

[![Built with spaCy](https://img.shields.io/badge/made%20with%20❤%20and-spaCy-09a3d5.svg)](https://spacy.io)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

API for highlighting key terms in a website and making it easily readable, hosted on repl.it at https://researchy-api--kevinlu2.repl.co/. 
I am planning on making this into a Chrome Extension.
To get started run in command line 

```sh
pip install -r requirements && python app.py
```

Make POST requests at https://127.0.0.1:5000 with the following structure

```json
{
  "text": "Some HTML string",
  "url": "Some url"
}
```

Either the text or the url has to not be ```none```, but you can send one and omit the other. ```text``` should be html.
You can also directly send it to https://researchy-api--kevinlu2.repl.co/ but it might crash repl.it so preferably run it locally.

I used repl.it since I'm broke after using a couple Google products but I'll probably eventually migrate it to an actual server. 
I tried AWS Lambda but had issues with spacy breaking the 50 mb storage size. 

Chrome extension can be found at https://github.com/kevinlu1248/researchy-chrome-extension/tree/master.

# What I used
TODO
