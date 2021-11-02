import React from 'react';

import * as myPath from "../js/myPath";
import "./DeleteProduct.css";

function DeletionButton(props)
{
    async function handleDelete()
    {
        const action = myPath.linkTo(`/products/${props.id}`);
        const ret = await fetch(
            action, {
                method: "DELETE"
            });
        if (ret.status === 200) {
            alert(`Product was deleted! Bye-bye, product!`);
            const json = await ret.json();
            const prodId = json.prodId
            const viewPage = myPath.linkTo(`/`);
            window.location.pathname = viewPage;
        }
        else {
            alert(`Error deleting product: ${await ret.text()}`);
            window.location.reload();
            return;
        }
    }

    return props.show ?
    (
        <button className="confirm-delete" onClick={handleDelete}>
            CONFIRM DELETION
        </button>
    )
    :
    null;
}

function DeleteProduct(props)
{
    const [showDeletionButton, setShowDeletionButton] = React.useState(false);
    const [confirmationText, setConfirmationText] = React.useState("");

    React.useEffect(() => {
        setShowDeletionButton(confirmationText.match(/^yes$/i));
    }, [confirmationText, props.show])

    function confirmationTextChange(e)
    {
        setConfirmationText(e.target.value);
    }

    return props.show ?
    (
        <div>
            <hr />
            <h3>Are you sure you want to delete this?</h3>
            <p>If you go ahead, this product will be gone <b>forever</b>.</p>
            <p>Type <b>yes</b> below to confirm.</p>
            <input type="text"
            placeholder="Type confirmation text"
            onChange={confirmationTextChange}
            value={confirmationText}>
            </input>
            <DeletionButton show={showDeletionButton} id={props.id} />
        </div>
    )
    :
    null;
}

export default DeleteProduct;