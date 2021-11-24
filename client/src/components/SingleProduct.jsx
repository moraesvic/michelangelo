import React from 'react';

import * as Fetch from '../js/fetch';
import * as myPath from "../js/myPath";
import "./SingleProduct.css";

import {ImageHref} from "./Image";
import EditForm from "./EditForm";
import DeleteProduct from "./DeleteProduct";

function ProductContent(props)
{
    const product = props.product;

    return props.show ?
    (
        <div className="product-page">
            <h1>{product.prod_name}</h1>
            <ImageHref
            id={product.pic_id}
            alt={product.prod_descr || ""}
            height="300px" />
            <div className="prod-descr">
                <p>{product.prod_descr || ""}</p>
            </div>
            <p className="prod-price">
                $ {(product.prod_price / 100).toFixed(2)}
            </p>
            <p className="prod-instock">
                ({product.prod_instock} in stock)
            </p>     
        </div>
    )
    :
    <p>The requested product ID does not exist.</p>;
}

function SingleProduct(props)
{
    const [showEdit, setShowEdit] = React.useState(false);
    const [showDelete, setShowDelete] = React.useState(false);

    const [waiting, setWaiting] = React.useState(true);
    const [okStatus, setOkStatus] = React.useState(true);
    const [product, setProduct] = React.useState();

    React.useEffect(() => {
        const wrapper = async () => {
            try {
                const response = await Fetch.get(`/products/${props.id}`);
                setProduct(response);
            } catch {
                setOkStatus(false);
            } finally {
                setWaiting(false);
            }
        }
        wrapper();
    }, [props.id] );

    function EditButton(props)
    {
        function clickEdit()
        {
            if (showDelete && !showEdit)
                setShowDelete(false)
            setShowEdit(!showEdit);
        }
        
        return props.show ?
        (
            <button className="edit-button" onClick={clickEdit}>
                Edit
            </button>
        )
        :
        null;
    }

    function DeleteButton(props)
    {
        function clickDelete()
        {
            if (!showDelete && showEdit)
                setShowEdit(false);
            setShowDelete(!showDelete);
        }
        return props.show ?
        (
            <button className="delete-button" onClick={clickDelete}>
                Delete
            </button>
        )
        :
        null;
    }

    return (
        <div className="center">
            <ProductContent
            product={product}
            show={!waiting && okStatus} />
            <a href={myPath.linkTo("/")}>
                <button className="back-button" >
                    &lt; Back to main
                </button>
            </a>
            <EditButton
            show={!waiting && okStatus} />
            <DeleteButton
            show={!waiting && okStatus} />
            <DeleteProduct
            show={showDelete && !waiting && okStatus}
            id={props.id} />
            <EditForm
            show={showEdit && !waiting && okStatus}
            id={props.id} />
        </div>
    )
}

export default SingleProduct;