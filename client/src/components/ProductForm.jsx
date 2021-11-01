import React from 'react';
import './styles.css';
import "./ProductForm.css";

import * as myPath from "../js/myPath";

function ProductForm(props) {
    
    /* TO DO: include fields such as accept, limiting what kind
    of files are accepted */

    const fieldName = props.fieldName || "file";
    const [selectedFile, setSelectedFile] = React.useState();
    const [isFileSelected, setFileSelected] = React.useState(false);
    const [formDict, setFormDict] = React.useState({});

    const handleChange = (event) => {
      const name = event.target.name;
      const value = event.target.value;
      setFormDict(previous => ({...previous, [name] : value}) );
    }

    const handleFile = (e) => {
        const MAX_FILE_SIZE = 5 * 1024 * 1024 ; // 5 megabytes
        const maxFileSizeMB = Math.round(MAX_FILE_SIZE / 1024 / 1024);
        
        if (e.target.files[0].size > MAX_FILE_SIZE) {
            alert(`Your file is too large! We accept up to ${maxFileSizeMB} megabytes.`);
            setSelectedFile(undefined);
            return;
        }
        setSelectedFile(e.target.files[0]);
        setFileSelected(true);
        console.log(selectedFile);
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault();

        let picName = null;
        let md5 = null;

        /* First let's send the file, if there's any */
        if (selectedFile) {
            let fileForm = new FormData();
            fileForm.append(fieldName, selectedFile);
            let ret = await fetch(
                myPath.linkTo("/pictures"),
                {
                    method: "POST",
                    body: fileForm
                }
            );
            if (ret.status === 200) {
                let parsed = await ret.json();
                [picName, md5] = [parsed.picName, parsed.md5]
            }
            else {
                alert(`Error uploading picture: ${await ret.text()}`);
                window.location.reload();
                return;
            }
        }

        let payload = {};
        payload["picName"] = picName;
        payload["md5"] = md5;

        for (let [key, value] of Object.entries(formDict))
            payload[key] = value;

        const action = myPath.linkTo(props.action);
        const method = props.method || "POST";
        const ret = await fetch(
            action, {
                method: method,
                body: JSON.stringify(payload),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        if (ret.status === 200) {
            alert(`Request succeeded!`);
            const viewPage = myPath.linkTo("/view");
            window.location.pathname = viewPage;
        }
        else {
            alert(`Error submitting product: ${await ret.text()}`);
            window.location.reload();
            return;
        }
        
    }

    return (
        <div className="product-form">
        <h1>Enter a new product!</h1>
        <form 
        onSubmit={handleSubmit}>
        <table className="center">
        <tbody>
        <tr>
            <td>
                <label htmlFor="prodName">Product name</label>
            </td>
            <td>
                <input type="text"
                name="prodName"
                id="prodName"
                onChange={handleChange}
                value={formDict["prodName"]}
                required
                />
            </td>
        </tr>
        <tr>
            <td>
                <label htmlFor="prodDescr">Product description</label>
            </td>
            <td>
                <textarea
                name="prodDescr"
                id="prodDescr"
                onChange={handleChange}
                value={formDict["prodDescr"]}
                 />
            </td>
        </tr>
        <tr>
            <td>
                <label htmlFor="prodPrice">Price</label>
            </td>
            <td>
                <input type="number"
                name="prodPrice"
                id="prodPrice"
                min="0.01"
                step="0.01"
                onChange={handleChange}
                value={formDict["prodPrice"]
                }
                />
            </td>
        </tr>
        <tr>
            <td>
                <label htmlFor="prodInStock">How many in stock?</label>
            </td>
            <td>
                <input type="number"
                name="prodInStock"
                id="prodInStock"
                min="0"
                step="1"
                onChange={handleChange}
                value={formDict["prodInStock"]}
                />
            </td>
        </tr>
        <tr>
            <td>
                Product image<br/>
                <span className="small">
                    (up to 5 MiB)
                </span>
            </td>
            <td>
                <label htmlFor="file-upload" className="form-button" type="button">
                    Choose file
                </label>
                <input type="file"
                name={fieldName}
                onChange={handleFile}
                accept="image/*"
                id="file-upload"
                />
                <div>
                    {isFileSelected ? (
                        <div>
                            <p>{selectedFile.name}</p>
                            <p>({(selectedFile.size / 1000).toFixed(2)} KB)</p>
                        </div>
                    ) : (
                        null
                    )}
                </div>
            </td>
        </tr>
        <tr>
            <td colSpan="2">
                <button
                type="submit"
                className="submit-button">
                    Submit
                </button>
            </td>
        </tr>
        </tbody>
        </table>
        </form>
        </div>
    );
}

export default ProductForm;