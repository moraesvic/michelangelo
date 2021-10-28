#!/usr/bin/env python3

import os
from flask import Flask, jsonify, request, send_file

app = Flask(
	__name__,
	static_url_path="/static",
	static_folder = "client/build/static")

# @app.route("/", methods=["GET"])
# def home():
# 	return f"hola mundo!"

@app.route("/stores/<string:name>", methods=["GET"])
def get_store(name):
	print(name)
	return jsonify({"data": 42})

@app.route("/stores", methods=["GET"])
def form_product():
	pass

@app.route("/stores", methods=["POST"])
def post_product():
	try:
		request_data = request.get_json()
		new_store = {
			"name": request_data["storeName"],
			"sector": request_data["storeSector"],
			"items": list()
		}
		return jsonify(new_store)	
	except:
		return jsonify({"error": True})

@app.route("/", defaults = {"path": ""}, methods = ["GET"])
@app.route("/<path:path>", methods = ["GET"])
def front_end(path):
	print(f"You tried to reach {path}, redirecting to index.html")
	return send_file("client/build/index.html")


def main():
	try:
		env = os.environ['FLASK_ENV']
	except KeyError:
		env = "development"

	try:
		port = os.environ["PORT"]
	except KeyError:
		port = 5000

	print(f"Starting server in port {port}. Using {env} mode...")

	if env == 'production':
		from waitress import serve
		serve(app, host="localhost", port=port)
	elif __name__ == "__main__":
		app.run(port=port)

main()
