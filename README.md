## Note

This repository was created in November 2021 as an coding assignment for a job application. Please take it with a grain of salt, as it does not represent my current abilities.

In particular, installation is too complicated and should be standardized by using modern practices such as Dockerization.

## Michelangelo

This is the Python (Flask) rewrite of a project I originally did with Node.js. You can check the original project at [GitHub](https://github.com/moraesvic/davinci) (although you probably shouldn't, this Python version is better written and better tested).

**MICHELANGELO** is a fashion store for clothes you would find from the 17th to the end of 19th century. You will find everything, Victorian clothes, pirate clothes, royalty, French Revolution and so on!

![Screenshot 1](/screenshot-1.png)

---

![Screenshot 2](/screenshot-2.png)

---

![Screenshot 3](/screenshot-3.png)

## Installation

After cloning the Git repo, run `sudo python3.8 install.py`. The script will guide you through the dependencies and database installation.

## Testing

Unit tests can be run with the script `scripts/run_tests`. This will launch the corresponding Python files in `tests` (do not run them directly, as they will not be able to import the necessary modules).

## Running

Development and production mode are accessible in the same path, but at different ports (http://localhost/michelangelo). Development mode must be run in port 7777, whereas production mode should be run in port 80, behind a reverse proxy. The server block to be appended to nginx is described in the installation script.

## Future improvement

I would like to implement a search feature, as well as refactor the front-end navigation using `ReactRoute`. Regarding the back-end, it would be nice to implement asynchronous handling of some subprocesses launched, especially those that process images (resizing, conversion, etc).
