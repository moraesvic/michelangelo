const Multer  = require('multer');
const path = require('path');

const DB = require("./db");
const pictures = require("./pictures");
const Exceptions = require("./exceptions");

require("dotenv").config();

module.exports = function(app){
	const IsProductionMode = process.env.NODE_ENV === "production";

	/* In production mode, there is no need for a prefix, as Nginx will
		proxy connections to :80/davinci to :37991/ */
	const prefix = IsProductionMode ? "" : process.env.ROOT_PATH;

    /* PRODUCTS */
	app.get(`${prefix}/products`, async function(req,res) {
		let result = await DB.query(
			`
			SELECT * FROM products
			WHERE
				($1::text IS NULL OR prod_name ILIKE '%' || $1::text || '%')
				AND ($2::bigint IS NULL OR prod_id = $2::bigint);`,
			[req.query.name, req.query.id]
			);
		if (!result.rows)
			res.send(Exceptions.InternalServerError.name);
		else
			res.send(result.rows);
	});
	
	app.post(`${prefix}/products`, async function(req,res){
		let picId = null;
		try {
			const fileStatus = await pictures.processPicture(req, res, "picture");
			picId = fileStatus ? 
					await pictures.storePicture(fileStatus) :
					null;

			/* req.body is only populated after Multer runs. Which is unfortunate,
			 * because we would be able to reduce server load by not processing
			 * pictures if the rest of the form presents a bad request */

			const prodName = req.body.prodName,
				prodDescr = req.body.prodDescr,
				prodPrice = Math.floor ( parseFloat(req.body.prodPrice) * 100),
				prodInStock = parseInt(req.body.prodInStock);

			const query = `
			INSERT INTO products (
				prod_name,
				prod_descr,
				prod_img,
				prod_price,
				prod_instock
			) VALUES (
				$1::text,
				$2::text,
				$3::bigint,
				$4::bigint,
				$5::bigint
			) RETURNING * ;
			`;

			try {
				let responseDB = await DB.query(query, [
					prodName, prodDescr, picId, prodPrice, prodInStock
				]);
			} catch (err) {
				console.log("Error doing DB query");
				console.log(err);
				throw Exceptions.InvalidInput;
			}

			res.send({
				success: true,
				picId: picId
			});
		} catch(err) {
			console.log(err);

			/* In case picture was already saved, we need to delete it */
			if (picId)
					pictures.deletePicture({ id: picId });
						
			return res.status(400).send({
				success: false,
				code: err.name
			});
		}
	});

	app.delete(`${prefix}/products/all`, async function(req, res){
		let result = await DB.query(`
		SELECT prod_id, prod_img
		FROM products;`
		);
		console.log(result);

		try {
			/* first, delete the pictures */
			let picsSet = new Set();
			for (let i = 0; i < result.rows.length; i++) {
				let picId = result.rows[i].prod_img;
				if (picId)
					picsSet.add(picId);
			}
			for (let pic of picsSet)
				pictures.deletePicture({id: pic});

			await DB.query(`
			DELETE FROM products ;
			`);

			let delPics = await DB.query(`
			DELETE FROM pics
			RETURNING pic_id ;
			`);
			
			res.send(`deleted ${picsSet.size + delPics.rows.length} pictures and ${result.rows.length} products`);

		} catch (err) {
			console.log(err);
			res.send(`failed to delete all products`);
		}
		
	});

	/* PICTURES */

	app.get(`${prefix}/pictures/:id`, async function(req,res){
		let result = await DB.query(
			`SELECT * FROM pics
			WHERE pic_id = $1
			LIMIT 1;`,
			[req.params.id]
			);

		if (result.rows.length === 0)
			res.status(404).send("404 NOT FOUND");
		else
			res.sendFile(path.join(app.get('root'), result.rows[0].pic_path));
	});

	app.delete(`${prefix}/pictures/all`, async function(req, res){
		let result = await DB.query(`SELECT * FROM pics;`);
		try {
			result.rows.forEach( row => pictures.deletePicture({id: row.pic_id}) );
			res.send(`deleted ${result.rows.length} pictures`);
		} catch (err) {
			console.log(err);
			res.send(`failed to delete all pictures`);
		}
		
	});

	app.post(`${prefix}/pictures`, async function(req, res){
		/* This is useful for testing, but is probably not going to be in the final API */
		try {
			const fileStatus = await pictures.processPicture(req, res, "picture");
			const picId = await pictures.storePicture(fileStatus);

			res.send({
				success: true,
				picId: picId
			});
		} catch(err) {
			let errCode = err instanceof Multer.MulterError ?
						err.code :
						"INTERNAL_SERVER_ERROR";
						
			return res.status(400).send({
				success: false,
				code: errCode
			});
		}
	});
}

