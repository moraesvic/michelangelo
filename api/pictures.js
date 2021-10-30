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


async function stripPicMetadata(path)
{
    await chpr(`
    exiftool -overwrite_original -all= "${path}"
    `);
}

async function getPicResolution(path)
{
    const [resolution, ] = await chpr(`
    exiftool "${path}" | \
	sed -rn "s/^Image Size[^0-9]*([0-9]+x[0-9]+)$/\\1/p" | \
    tr -d "\n"
    `);
    return resolution;
}

function calculateProportion(strResolution, maxSize)
{
    /* Returns resize proportion, in percentage */
    const resRegex = /^(\d+)x(\d+)$/;
    const match = resRegex.exec(strResolution);
    if (!match)
        throw `Bad input ${strResolution}!`

    const [width, height] = [ match[1], match[2] ];
    const biggest = Math.max(width, height);
    const factor = biggest <= maxSize ? 1.0 : maxSize / biggest;

    return Math.floor(factor * 100);
}

async function resizePicBenchmark(oldPath, newPath)
{
    const promises = [ fsPromises.stat(oldPath) , fsPromises.stat(newPath) ];
    const [ oldStat, newStat ] = await Promise.all(promises);
    const [ oldSize, newSize ] = [ oldStat.size, newStat.size ];
    const reduction = (100.0 * (1.0 - newSize / oldSize)).toFixed(2);
    const savedSpace = oldSize - newSize;
    console.log(
    `Old size was ${oldSize}, new size is ${newSize} (${reduction}% reduction).
    Saved space: ${savedSpace} bytes.
    `
    );
}

async function checkOperation(oldPath, newPath, opId = null)
{
    /* Reducing image resolution and changing file encoding
     * CAN reduce size, but not always does.
     * This will check if it was actually effective and
     * revert operation if it wasn't */

    const oldSize = (await fsPromises.stat(oldPath)).size;
    const newSize = (await fsPromises.stat(newPath)).size;

    opId = opId || "";

    console.log(`
    Original size: ${oldSize}
    After operation "${opId}": ${newSize}
    `)

    if (newSize < oldSize) {
        /* If that improved file size, overwrite image */
        console.log("Operation improved file size. Overwriting original");
        await fsPromises.rename(newPath, oldPath);
    }
    else {
        /* If not, remove converted file */
        console.log("Operation did not improve file size. Rolling back");
        await fsPromises.unlink(newPath);
    }
}

async function resizePic(path, maxSize, convertToJPEG = true, benchmark = true)
{
    /* Will always overwrite original */
    /* Please note that sometimes JPEG can be larger than PNG,
     * this is not a bug, although it is annoying
     * https://stackoverflow.com/questions/43970574/my-jpg-file-is-larger-than-png
     * */

    /* Another weird fact is that sometimes shrinking resolution can make
     * a file have a larger size. This is due to how compression operates
     * https://computergraphics.stackexchange.com/questions/4824/reducing-image-size-increases-file-size/4825
     */

    /* For these two cases we have helper function checkOperation() */

    const resolution = await getPicResolution(path);
    const proportion = calculateProportion(resolution, maxSize);
    const [, subtype] = await getMimeType(path);
    const needsConversion = convertToJPEG && subtype !== "jpeg";

    let oldSize, newSize;
    oldSize = (await fsPromises.stat(path)).size;

    if (benchmark) {
        console.log(
        `Path ${path}
        Current resolution is ${resolution}.
        Dimensions must be reduced to ${proportion} % of original
        Needs conversion : ${needsConversion}`
        );
    }
    
    if (proportion < 100) {
        const newPath = `${path}_resize`;
        await chpr(`convert -resize ${proportion}% "${path}" "${newPath}"`);
        await checkOperation(path, newPath, opId = "resize");
    }
        
    if (needsConversion) {
        const newPath = `${path}.jpeg`;
        await chpr(`convert "${path}" "${newPath}"`);
        await checkOperation(path, newPath, opId = "JPEG conversion");
    }

    if (benchmark) {
        newSize = (await fsPromises.stat(path)).size;
        const reduction = (100.0 * (1.0 - newSize / oldSize)).toFixed(2);
        const savedSpace = oldSize - newSize;
        console.log(
        `Old size was ${oldSize}, new size is ${newSize} (${reduction}% reduction).
        Saved space: ${savedSpace} bytes.
        `
        );
    }
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