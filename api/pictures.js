const fsPromises = require('fs').promises;
const Path = require('path');
const Multer  = require('multer');

const DB = require("./db");
const chpr = require('./ChildProcess.js');

function processPicture(req, res, fieldName)
{
    return new Promise( (resolve, reject) => {
        const MAX_FILE_SIZE = 5 * 1024 * 1024 ; // 5 megabytes
        uploadFactory(fieldName, MAX_FILE_SIZE)(req, res, async function(err) {
            if (err)
                reject(err);
            else
                resolve(req.file);
        });
    }); 
}

function storePicture(fileStatus, allowRedundant = false)
{
    /* The option allowRedundant will allow a new picture into the database
     * even if there is already an identical picture.
     * This can be useful if many products have the same display image */

    return new Promise( async (resolve, reject) => {
        if (!fileStatus) {
            reject();
            return;
        }
        try {
            const MAX_PIC_RESOLUTION = 300; // pixels
            let picId;

            /* First thing is getting the MD5 hash */
            const md5sum = await md5File(fileStatus.path);

            let isPicAlreadyInDB = await DB.query(`
            SELECT pic_id FROM pics WHERE pic_md5 = $1 LIMIT 1
            `, [md5sum]);

            if (isPicAlreadyInDB.rows.length) {
                console.log("Picture was already in DB!")
                fsPromises.unlink(fileStatus.path);
                
                picId = isPicAlreadyInDB.rows[0].pic_id;
                DB.query(`
                UPDATE pics
                SET pic_ref_count = pic_ref_count + 1
                WHERE pic_md5 = $1 ;
                `, [md5sum]);

                resolve(isPicAlreadyInDB.rows[0].pic_id);
                return;

            } else {

                /* Let's process the file, stripping metadata, resizing
                 * and getting MD5 hash */

                await testMimeType(fileStatus.path, "image");
                await stripPicMetadata(fileStatus.path);
                await resizePic(fileStatus.path, MAX_PIC_RESOLUTION);
                fileStatus.path = await renameMimeType(fileStatus.path);

                const origName = fileStatus.originalname;

                let responseDB = await DB.query(`
                INSERT INTO pics (
                    pic_orig_name,
                    pic_md5,
                    pic_path
                ) VALUES (
                    $1::text,
                    $2::text,
                    $3::text
                ) RETURNING pic_id;`, [origName, md5sum, fileStatus.path]);

                picId = responseDB.rows[0].pic_id;

            }

            resolve(picId);

        } catch (err) {
            fsPromises.unlink(fileStatus.path);
            reject(err);
        }
    });
}

async function decreaseRefCount(picId)
{
    try {
        let responseDB = await DB.query(`
        UPDATE pics
        SET pic_ref_count = pic_ref_count + 1
        WHERE pic_id = $1 
        RETURNING pic_ref_count ;`,
        [ picId ]);
    
        if (!responseDB.rows.length)
            throw "Could not decrease picture reference count!"
        
        if (response.DB.rows[0].pic_ref_count === 0)
            deletePicture({ id: picId });

    } catch (err) {
        throw `Failed to decrease picture reference count!`;
    }
}

async function deletePicture(kwargs)
{
    /* Accepted kwargs are id (pic_id) and path (pic_path) */
    if (!kwargs)
        return;

    const {id, path} = kwargs;
    
    try {
        let responseDB = await DB.query(`
        DELETE FROM pics
        WHERE
            ($1::bigint IS NULL OR pic_id = $1::bigint)
            AND ($2::text IS NULL OR pic_path = $2::text)
        RETURNING pic_path;`,
        [ id, path ]);
    
        if (responseDB.rows.length)
            fsPromises.unlink(responseDB.rows[0].pic_path);
        else if (path)
            fsPromises.unlink(path);
    } catch (err) {
        throw `Failed to delete ${kwargs}`;
    }
    
}

module.exports = {
    processPicture,
    storePicture,
    deletePicture
};