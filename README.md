This is the Python (Flask) rewrite of a project I originally did with Node.js. You can check the original project at [GitHub](https://github.com/moraesvic/davinci) (although you probably shouldn't, this Python version is better written and better tested).

My intention here is to rewrite the back-end in Python, creating automated tests that guarantee that the new API produces the same output as the old one. Improving the front-end is also a possibility, if I have enough time.

### Installation

...

### Running

React is intended for single-page apps and its documentation is sometimes a bit difficult when it comes to running it as a domain of a subdirectory. In particular, serving static files from a relative path was impossible to do. Most tutorials recommend using homepage as "." or "./" and then rebuilding, but neither worked. If you put this together with proxying in development and nginx, it is very hard to understand what is going on.

A work around this was checking if we are running in development mode and appending a prefix to every route. Something like:

```
@app.get(f"{prefix}/list-products")
```

It is not beautiful or practical, and we should use a better solution in the future. For the while, it enables to work with development or production mode at the same URL (http://localhost/michelangelo), without having to change configuration files to deploy. Make sure you add this to your server block in nginx:

```
location = /michelangelo {
	return 302 /michelangelo/;
    }

location /michelangelo/ {
    proxy_set_header   X-Forwarded-For $remote_addr;
    proxy_set_header   Host $http_host;

    # Port 5000 was already taken by another service, so I picked a
    # random number within the expected range
    proxy_pass         http://localhost:7777/michelangelo/;
}
```

Hosting this app in other paths is possible, just change the value for APP_NAME in the ".env" file for the back-end, and the value of PUBLIC_URL in the ".env" file in the front-end. The port numbers are also completely arbitrary, and anything should work as long as you are consistent across files. Later I might also add a script that solves all this at once.