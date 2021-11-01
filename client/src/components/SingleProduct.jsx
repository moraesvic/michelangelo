import React from 'react';

import * as Fetch from '../js/fetch';
import * as myPath from "../js/myPath";
import "./SingleProduct.css";

import Image from "./Image";
import EditForm from "./EditForm";

function NonExistent(props)
{
    return (
        <p>The requested product ID does not exist.</p>
    )
}

function ProductContent(props)
{
    const product = props.product;

    return (
        <div className="product-page">
            <h1>{product.prod_name}</h1>
            <Image id={product.pic_id} alt={product.prod_descr} />
            <div className="prod-descr">
                <p>{product.prod_descr}</p>
            </div>
            <p className="prod-price">
                $ {(product.prod_price / 100).toFixed(2)}
            </p>
            <p className="prod-instock">
                ({product.prod_instock} in stock)
            </p>     
        </div>
    )
}

function PageInfo(props)
{
    const [waiting, setWaiting] = React.useState(true);
    const [okStatus, setOkStatus] = React.useState(true);
    const [product, setProduct] = React.useState();

    React.useEffect(() => {
        const wrapper = async () => {
            try {
                const response = await Fetch.get(`/products/${props.id}`);
                setProduct(response);
                setWaiting(false);
            } catch {
                setOkStatus(false);
                setWaiting(false);
            }
        }
        wrapper();
    }, [props.id]);

    if (waiting)
        return null;

    return okStatus ?
        <ProductContent product={product} />
        :
        <NonExistent /> ;
}

function SingleProduct(props)
{
    const [showEdit, setShowEdit] = React.useState(false);

    function clickEdit()
    {
        setShowEdit(!showEdit);
    }

    return (
        <div className="center">
            <PageInfo id={props.id} />
            <a href={myPath.linkTo("/")}>
                <button className="back-button" >
                    &lt; Back to main
                </button>
            </a>
            <button className="edit-button" onClick={clickEdit}>
                Edit
            </button>
            <EditForm show={showEdit} id={props.id} />
        </div>
    )
}

export default SingleProduct;