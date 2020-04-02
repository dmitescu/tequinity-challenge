# Synopsis

Build with

```
docker build . -t tequinity-mitescugd
```

Run with

```
docker run --rm -p 8000:8000 --net tequinity -it --name tq tequinity
```

Alternatively you can run it locally with

```
gunicorn --worker-class flask_sockets.worker Endpoints:app
```

To run it it requires either `nlp` host to exist or `SC_NLP_HOST`
set to the format `host:ip` to point to the StanfordCoreNLP (docker images
can be found, or you can run it locally).

# Few points

From what I've tested it, because of the worker class, one endpoint
doesn't block the rest.

I prefered to do the auth by myself.

The serialization/deserialization maybe should be moved somewhere else but
for now it makes sense to do it like this.

