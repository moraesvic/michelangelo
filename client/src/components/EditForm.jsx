import React from 'react';
import './styles.css';
import "./ProductForm.css";

import * as myPath from "../js/myPath";

function EditForm(props) {
    
    /* TO DO: include fields such as accept, limiting what kind
    of files are accepted */

    const [formDict, setFormDict] = React.useState({});

    const handleChange = (event) => {
      const name = event.target.name;
      const value = event.target.value;
      setFormDict(previous => ({...previous, [name] : value}) );
    }
    
    const handleSubmit = async (e) => {
        e.preventDefault();

        formDict["prodId"] = props.id;

        const action = myPath.linkTo(`/products/${props.id}`);
        const method = "PATCH";
        const ret = await fetch(
            action, {
                method: method,
                body: JSON.stringify(formDict),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        if (ret.status === 200) {
            alert(`Request succeeded!`);
            const json = await ret.json();
            const prodId = json.prodId
            const viewPage = myPath.linkTo(`/view/${prodId}`);
            window.location.pathname = viewPage;
        }
        else {
            alert(`Error submitting product: ${await ret.text()}`);
            window.location.reload();
        }
        
    }

    return props.show ?
    (
        <div className="product-form">
        <hr />
        <h3>Edit product</h3>
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
    )
    :
    null;
}

export default EditForm;