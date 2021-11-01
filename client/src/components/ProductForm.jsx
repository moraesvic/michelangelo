import React from 'react';
import './styles.css';
import "./ProductForm.css";

import * as myPath from "../js/myPath";

function ProductForm(props) {
    
    /* TO DO: include fields such as accept, limiting what kind
    of files are accepted */

    const fieldName = props.fieldName || "file";
    let file = null;

    let formDict = {};

    const handleChange = (event) => {
      const name = event.target.name;
      const value = event.target.value;
      formDict[name] = value;
    }

    const handleFile = (e) => {
        const MAX_FILE_SIZE = 5 * 1024 * 1024 ; // 5 megabytes
        const maxFileSizeMB = Math.round(MAX_FILE_SIZE / 1024 / 1024);
        file = e.target.files[0];
        if (file.size > MAX_FILE_SIZE) {
            alert(`Your file is too large! We accept up to ${maxFileSizeMB} megabytes.`);
            file = null;
            return;
        }
        alert("file successfully loaded")
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault();

        /* First let's send the file, if there's any */
        if (file) {
            let fileForm = new FormData();
            fileForm.append(fieldName, file);
            console.log(fileForm);
            let ret = await fetch(
                "pictures", {
                    method: "POST",
                    data: fileForm
                }
            );
            console.log(ret);
            console.log(await ret.json());
        }

        let data = new FormData();
        for (let [key, value] of Object.entries(formDict))
            data.append(key, value);

        const action = myPath.linkTo(props.action);
        const method = props.method || "POST";
        const ret = await fetch(
            action, {
                method: method,
                body: data,
        });
        if (!ret) {
            alert("Internal server error. We apologize for the inconvenience.");
            window.location.reload();
            return;
        }
        const parsed = await ret.json();
        if (!parsed.success) {
            alert("Error processing request. Please assure you have sent an image within the maximum size.");
            window.location.reload();          
            return;
        }
        alert(`Request succeeded!`);
        const viewPage = myPath.linkTo("/view");
        window.location.pathname = viewPage;
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
                onChange={handleChange} />
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