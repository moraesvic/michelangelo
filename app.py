#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request, send_file
from waitress import serve





# @app.route("/stores", methods=["GET"])
# def form_product():
# 	pass

# @app.route("/stores", methods=["POST"])
# def post_product():
# 	try:
# 		request_data = request.get_json()
# 		new_store = {
# 			"name": request_data["storeName"],
# 			"sector": request_data["storeSector"],
# 			"items": list()
# 		}
# 		return jsonify(new_store)	
# 	except:
# 		return jsonify({"error": True})


class App:
	STATIC_URL_PATH = "/static"
	STATIC_FOLDER = "client/build/static"
	REACT_MAIN_PAGE = "client/build/index.html"
	DEFAULT_PORT = 5000

	def __init__(self,
				flask_env: str,
				running_as_main: bool,
				port: int = DEFAULT_PORT,
				nginx_static: bool = True):
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

		self.app = Flask(__name__)
		self.configure_static(nginx_static)

		self.configure_routes()
		self.configure_fallback()

		self.load_env()
		print(os.getenv("PG_PASSWORD"))
		sql_credentials = self.start_db()


	def configure_static(self, nginx_static):
		# If this is production mode and we are serving static files from Nginx,
		# then we don't have to serve static files from Flask

		if self.production_mode and nginx_static:
			self.app.static_url_path = None
			self.app.static_folder = None
		else:
			self.app.static_url_path = self.STATIC_URL_PATH
			self.app.static_folder = self.STATIC_FOLDER

	def configure_routes(self):
		import api.products as products
		products.Products(self.app)

		@self.app.route("/stores/<string:name>", methods=["GET"])
		def get_store(name):
			print(name)
			return jsonify({"data": 42})

	def configure_fallback(self):
		# This is the fallback route. If the path does not match any of the API
		# routes, then it is seeking something from the front-end. And then,
		# if it does not exist in the front-end, React will give a 404 page.

		@self.app.get("/", defaults = {"path": ""})
		@self.app.get("/<path:path>")
		def front_end(path):
			print(f"You tried to reach {path}, redirecting to React main page")
			return send_file(self.REACT_MAIN_PAGE)

	def load_env(self):
		from dotenv import load_dotenv
		load_dotenv()

	def start_db(self):
		import api.db as db
		self.db = db.DB()

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

flask_env = os.environ.get("FLASK_ENV", None)
port = os.environ.get("PORT", None)
app_singleton = App(flask_env, __name__ == "__main__", port)

# This is required in order to have "flask run"
app = app_singleton.app
