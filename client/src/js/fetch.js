import * as myPath from "./myPath";

async function myFetch(url, params)
{
	let response = await fetch(url, params);
	if (!response.ok)
		throw new Error("Server returned error code.");

	let parsed = await response.json();

	return parsed;
}

function checkType(path, payload, query)
{
	/* Check if objects are of the correct type
		*
		* Array path
		* Map   payload
		* Map   query
		*
		* */
	if (   (path 	&& !(path instanceof Array))
		|| (payload && !(payload.constructor === Object))
		|| (query 	&& !(query.constructor === Object))  ) {
		throw new Error("Invalid input");
	}
}

async function HTTPRequest(url, path, payload, query, method)
{
	/* This function supports the following HTTP verbs:
		* GET, HEAD, POST, PUT, PATCH, DELETE
		*/
	checkType(path, payload, query);

	let newUrl = myPath.linkTo(url);
	
	if (path)
		for (let subpath of path)
			newUrl += "/" + subpath;

	if (query) {
		let queryStr = new URLSearchParams(query).toString();
		newUrl += "?" + queryStr;
	}

	let opt = 
	{
		method: method,
		headers: {
			'Content-Type': 'application/json'
		}
	}

	if(method !== "GET" && method !== "HEAD" && payload)
		opt.body = JSON.stringify(payload);

	return myFetch(newUrl, opt);
}

async function get(url, path, query)
{
	/*
		* Array path
		* Map   query
		* */
	return HTTPRequest(url, path, null, query, "GET");
}

async function head(url, path, query)
{
	/*
		* Array path
		* Map   query
		* */
	return HTTPRequest(url, path, null, query, "HEAD");
}

async function post(url, path, payload, query)
{
	/*
		* Array path
		* Map   payload
		* Map   query
		* */
	return HTTPRequest(url, path, payload, query, "POST");
}

async function put(url, path, payload, query)
{
	/*
		* Array path
		* Map   payload
		* Map   query
		* */
	return HTTPRequest(url, path, payload, query, "PUT");
}

async function patch(url, path, payload, query)
{
	/*
		* Array path
		* Map   payload
		* Map   query
		* */
	return HTTPRequest(url, path, payload, query, "PATCH");
}

async function del(url, path, payload, query)
{
	/*
		* Array path
		* Map   payload
		* Map   query
		* */
	return HTTPRequest(url, path, payload, query, "DELETE");
}

export {
    get,
    head,
    post,
    put,
    patch,
    del
};