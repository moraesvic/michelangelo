**image**

This is the Python (Flask) rewrite of a project I originally did with Node.js. You can check the original project at [GitHub](https://github.com/moraesvic/davinci) (although you probably shouldn't, this Python version is better written and better tested).

My intention here is to rewrite the back-end in Python, creating automated tests that guarantee that the new API produces the same output as the old one. Improving the front-end is also a possibility, if I have enough time.

### Installation

First of all, you will need to set up a virtual environment with Python3.8. At the project root directory, run `python3 -m venv venv`. Make sure to **activate** the environment before following all of the following steps.

The requirements for running the project are listed in `requirements.txt`. There is too much information there, but the essential is the output of the command `pip freeze`. Copy the output of this command into a file `python_requirements.txt` and have pip install everything by running `pip install -r python_requirements.txt`.

By the way, to generate `requirements.txt` file, if any library is added further in development, run the script `scripts/freeze_requirements`.

#### Setting up the database

The files for starting the database are in the directory `sql`.

### Testing

Unit tests can be run with the script `scripts/run_tests`. This will launch the corresponding Python files in `tests` (do not run them directly, as they will not be able to import the necessary modules).

### Running

Development and production mode are accessible in the same path, but at different ports (http://localhost/michelangelo). Development mode must be run in port 7777, whereas production mode should be run in port 80, behind a reverse proxy. Make sure you add this to your server block in nginx:

```
location = /michelangelo {
	return 302 /michelangelo/;
    }

location /michelangelo/ {
    rewrite /michelangelo/(.*) /$1 break;
    proxy_pass         http://localhost:7777/michelangelo/;
    proxy_set_header   X-Forwarded-For $remote_addr;
    proxy_set_header   Host $http_host;
    
}
```

It would be convenient to have development mode at the same port as production, but reverse-proxying makes things difficult, especially when debugging with websocket. I was getting the error `webpackHotDevClient.js:60 WebSocket connection to 'ws://localhost/sockjs-node' failed`. Solutions tried, without success: [1](https://stackoverflow.com/questions/60328836/how-to-proxy-a-websocket-connection), [2](https://stackoverflow.com/questions/59794148/webpack-with-proxy-the-development-server-has-disconnected), [3](https://stackoverflow.com/questions/58088218/websockets-in-create-react-app-with-webpack-proxy). This was a reported issue in 2020 still, and might be an area of active development for React.

The scripts `scripts/run_dev` and `scripts/run_prod` set up the environment variables and start the server(s). Hosting this app in other paths is possible, just change the value for APP_NAME in the ".env" file for the back-end, and the value of PUBLIC_URL in the ".env" file in the front-end. The port numbers are also completely arbitrary, and anything should work as long as you are consistent across files. Later I might also add a script that solves all this at once.

### Future improvement

React is intended for single-page apps and its documentation is sometimes a bit difficult when it comes to running it as a domain of a subdirectory. In particular, serving static files from a relative path was impossible to do. Most tutorials recommend using homepage as `.` or `./` and then rebuilding, but neither worked. If you put this together with proxying in development and nginx, it is very hard to understand what is going on.

I haven't found this information officially, but it seems that `homepage` and `PUBLIC_URL` are exactly the same, except `homepage` is in `package.json` file and `PUBLIC_URL` is an environment variable. I was also getting the error `Invalid host header`, which I was not able to solve.

Things I have not tried yet include using [base href tag](https://skryvets.com/blog/2018/09/20/an-elegant-solution-of-deploying-react-app-into-a-subdirectory/) and using [react-router](https://www.npmjs.com/package/react-router). I am also not sure what the current best practice for proxying is. The more recent tutorials tend to only use `proxy` key in the `package.json`, whereas older ones use `http-proxy-middleware`.

With a path rewrite for the proxy, we can make URLs be consistent across development and production:

```
/* setupProxy.js */
const { createProxyMiddleware } = require("http-proxy-middleware");
module.exports = function (app) {

  const prefix = process.env.PUBLIC_URL;
  const regex = `^${prefix}/`;

  app.use(
    [
      `${prefix}/list-products`,
      `${prefix}/products`,
      `${prefix}/pictures`],
    createProxyMiddleware({
      target: `http://localhost:${process.env.BACKEND_PORT}`,
      pathRewrite: {
        [regex]: "/"
      }
    })
  );
};
```

A weird, undocumented behavior is: a link to a resource will use *hostname* as the root path. Example: `<a href="/">Main Page</a>` will take you to `http://localhost/` . On the other hand, a **fetch request** to a resource will use *homepage* (PUBLIC_URL variable) as the root path, i.e., `fetch("/mydata")` will take you to `http://localhost/homepage/mydata`.