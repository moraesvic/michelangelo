#!/usr/bin/env python3

import os, re
from flask import Flask, send_file
from dotenv import load_dotenv
from waitress import serve

from lib.singleton import Singleton
import lib.db as db

def path_rewrite(s):
	return re.sub(r"/{2,}", "/", s)

class App (metaclass = Singleton):
	STATIC_URL_PATH = "/static"
	STATIC_FOLDER = "client/build/static"
	UPLOAD_FOLDER = "uploads"
	REACT_MAIN_PAGE = "client/build/index.html"
	REACT_FAVICON = "client/build/favicon.ico"
	REACT_MANIFEST = "client/build/manifest.json"
	DEFAULT_PORT = 5000

	# We will allow a maximum payload size of 5 MB
	MAX_CONTENT_LENGTH = 5 * 1024 * 1024

	def __init__(self,
				flask_env: str,
				running_as_main: bool,
				port: int = DEFAULT_PORT,
				nginx_static: bool = False,
				app_name: str = ""):
		'''
		flask_env contains the value for environment variable "FLASK_ENV", it
		could be "production" or "development"

		running_as_main will tell us how this program was invoked, directly with
		"python3 app.py", or with "flask run"

		port is the port to listen (will not work if you do not run as __main__)

		nginx_static determines whether Nginx will serve static folder
		(recommended for production, but might cause issues, so default is false)
		'''
		# If no "FLASK_ENV" environment variable was given, we will assume
		# we are running in development mode
		self.production_mode = (flask_env == "production")
		self.running_as_main = running_as_main
		self.port = port or self.DEFAULT_PORT
		self.app_name = app_name
		self.prefix = f"/{self.app_name}" if self.production_mode == False else ""

		self.app = Flask(__name__)
		self.app.config["UPLOAD_FOLDER"] = self.UPLOAD_FOLDER
		self.app.config["MAX_CONTENT_LENGTH"] = self.MAX_CONTENT_LENGTH

		self.configure_static(nginx_static)
		print(f"app_name is \"{self.app_name}\"")
		print(f"static_url_path is {self.app.static_url_path}")
		print(f"static_folder is {self.app.static_folder}")
		print(f"API routes will be prefixed with \"{self.prefix}\"")

		# It is necessary to connect to DB before configuring routes, because
		# each route will receive DB as argument
		self.db = db.DB()

		self.configure_routes()
		self.configure_favicon()
		self.configure_manifest()
		self.configure_fallback()

		self.listen()


	def configure_static(self, nginx_static):
		# If this is production mode and we are serving static files from Nginx,
		# then we don't have to serve static files from Flask

		if self.production_mode and nginx_static:
			self.app.static_url_path = None
			self.app.static_folder = None
		else:
			self.app.static_url_path = path_rewrite(f"/{self.app_name}{self.STATIC_URL_PATH}")
			self.app.static_folder = self.STATIC_FOLDER

	def configure_routes(self):
		# The idea here is: every module (Products, Pictures, etc) should be
		# independent, and receive only what is strictly necessary for it to
		# operate — the app and the DB handlers
		import api.products, api.pictures

		routes = [
			api.products.Products,
			api.pictures.Pictures
		]
		
		for route in routes:
			route(self.app, self.db, self.prefix)

	def configure_fallback(self):
		# This is the fallback route. If the path does not match any of the API
		# routes, then it is seeking something from the front-end. And then,
		# if it does not exist in the front-end, React will give a 404 page.

		@self.app.get("/", defaults = {"path": ""})
		@self.app.get("/<path:path>")
		def front_end(path):
			rewritten_path = re.sub(rf"{self.prefix}", "", path)
			print(f"You tried to reach {rewritten_path}, redirecting to React main page")
			return send_file(self.REACT_MAIN_PAGE)

	def configure_favicon(self):
		# This is an exception which must be handled especially. File
		# "favicon.ico", even though it is static, is normally present in the
		# root of a domain

		@self.app.get("/favicon.ico")
		def serve_favicon():
			return send_file(self.REACT_FAVICON)

	def configure_manifest(self):
		# This is an exception which must be handled especially. File
		# "favicon.ico", even though it is static, is normally present in the
		# root of a domain

		@self.app.get("/manifest.json")
		def serve_manifest():
			return send_file(self.REACT_MANIFEST)

	def listen(self):
		# app.run() is only called in development and only when command is
		# "python3 app.py". The command "flask run" runs the app in a
		# port we cannot alter from here (it can be specified at invocation
		# time). It is not necessary to call app.run() if "flask run" is used,
		# and doing so causes the line to be ignored.

		if self.production_mode:
			print(f"Starting production server in port {self.port}.")
			serve(self.app, host = "localhost", port = self.port)

		elif self.running_as_main:
			print(f"Starting development server in port {self.port}.")
			self.app.run(port = self.port)

		else:
			print(f"Starting development server. Check parent process for port number")


################################################################################
########## """ MAIN """
################################################################################

# This application should not be run directly, only by using scripts
# ./run_dev.sh and ./run_prod.sh . In any case, it is safer to cover
# all possible scenarios here

load_dotenv()
flask_env = os.environ.get("FLASK_ENV", None)
port = os.environ.get("PORT", None)
app_name = os.environ.get("APP_NAME", None)
app_singleton = App(
	flask_env,
	__name__ == "__main__",
	port = port,
	app_name = app_name)

# This is required in order to have "flask run"
app = app_singleton.app
