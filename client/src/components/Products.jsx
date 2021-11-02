import React from 'react';

import * as Fetch from '../js/fetch';
import * as myPath from "../js/myPath";
import "./Products.css";

import {Image} from "./Image";

function trim(text)
{
    /* According to experiments, that is the longest text that would fit into
    the box. */
    const MAX_LENGTH = 115;
    let trimmed;

    if (text.length > MAX_LENGTH)
    {
        let arr = text.split(" ");
        while ((arr.join(" ") + " (...)").length > MAX_LENGTH)
            arr.splice(arr.length - 1);
        trimmed = arr.join(" ") + " (...)";
    }
    else
        trimmed = text;

    return trimmed;
}

function ProductList(props)
{
    const [products, setProducts] = React.useState([]);

    React.useEffect(() => {
        const wrapper = async () => {
            const response = await Fetch.get(
                `/list-products?page=${props.page}`
            );
            setProducts(response);
        }
        wrapper();
    }, [props.page]);

    const classList = ["blue", "yellow", "green", "red"];
    let keyIndex = Math.floor ( Math.random() * classList.length );    

    return (
        <section className="flex-container">
        { products.map(prod => {
            const description = 
                (!prod.prod_descr || prod.prod_descr.length === 0) ?
                "No description available." :
                trim(prod.prod_descr);
            
            const price = (prod.prod_price / 100).toFixed(2);
            return (
            <div
            className={`card ${classList[keyIndex % classList.length]}`}
            key={keyIndex++}>
                <div className="center">
                    <div className="pic-box">
                        <a href={myPath.linkTo(`/view/${prod.prod_id}`)}>
                            <Image id={prod.pic_id} alt={prod.prod_descr} />
                        </a>
                    </div>
                    <p className="card-title">
                        {prod.prod_name} | $ {price}
                    </p>
                </div>
                <p className="card-descr">{description}</p>
            </div>
            );
        }) }
        </section>
    );
}

function Products(props)
{


    const [count, setCount] = React.useState(0);

    React.useEffect(() => {
        const wrapper = async () => {
            const response = await Fetch.get(`/products/count`);
            setCount(response);
        }
        wrapper();
    }, []);

    /* */

    const CARDS_PER_PAGE = 8;
    const [currentPage, setCurrentPage] = React.useState(0);

    function decreasePage()
    {
        if (currentPage > 0)
            setCurrentPage(currentPage - 1);
    }

    function increasePage()
    {
        if (currentPage + 1 < count / CARDS_PER_PAGE)
            setCurrentPage(currentPage + 1);
    }

    /* */

    function DecreasePageButton()
    {
        return currentPage > 0 ?
            <button className="pager-button" onClick={decreasePage}>← Previous page</button> :
            (null);
    }

    function IncreasePageButton()
    {
        return currentPage + 1 < count / CARDS_PER_PAGE ?
            <button className="pager-button" onClick={increasePage}>Next page →</button> :
            (null);
    }

    function PagerButtons()
    {
        const decreaseButton = DecreasePageButton();
        const increaseButton = IncreasePageButton();
        const separator = decreaseButton && increaseButton ?
            <span> &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; </span> :
            (null);
        return (
        <div>
            {decreaseButton}
            {separator}
            {increaseButton}
        </div>
        )
    }

    function Pager(props)
    {
        const pageStart = count === 0 ?
                    0 : currentPage * CARDS_PER_PAGE + 1;
        const pageEnd = (currentPage + 1) * CARDS_PER_PAGE < count ?
                    (currentPage + 1) * CARDS_PER_PAGE : 
                    count;
        return (
            <div className="center buffer">
                <p className="listing-products">
                    Listing products {pageStart} to {pageEnd}
                </p>
                <p className="listing-total">
                    from a total of {count}
                </p>
                {PagerButtons()}
            </div>
        )
    }
    
    return (
        <div>
        <Pager maxCount={count} />
        <ProductList page={currentPage} />
        <Pager maxCount={count} />
        </div>
    );
}

export default Products;