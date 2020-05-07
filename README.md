# Researchy API
API for highlighting key terms in a website and making it easily readable, hosted on repl.it at https://researchy-api--kevinlu2.repl.co/. 
I am planning on making this into a Chrome Extension.
To get started run in command line 

```sh
pip install -r requirements && python app.py
```

Make POST requests at https://127.0.0.1:5000 with the following structure

```json
{
  "text": "Some string",
  "url": "Some url"
}
```

Either the text or the url has to not be ```none```, but you can send one and omit the other. ```text``` should be html.
You can also directly send it to https://researchy-api--kevinlu2.repl.co/ but it might crash repl.it so preferably run it locally.

# What I used
TODO
