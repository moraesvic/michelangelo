import React from 'react';

import "./MainContent.css";
import ProductForm from './ProductForm';
import Products from "./Products";
import FourOFour from "./FourOFour";
import SingleProduct from "./SingleProduct"


function Navigator()
{
    /* get pathname without prefix and without trailing slash
     * reject route if it does not have the prefix */
    const regex = RegExp(`^${process.env.PUBLIC_URL}`);
    const pathName = window.location.pathname.match(regex) ?
        window.location.pathname
        .replace(regex, "")
        .replace(/(?<=.+)\/$/, '')
        :
        null;

    switch(true){
    case /^(\/?|\/view)$/.test(pathName):
        return <Products />;
    case /^(\/?|\/view)\/[0-9]+$/.test(pathName):
        const productId = 
            parseInt(pathName.match(/^\/view\/([0-9]+)$/)[1]);
        return <SingleProduct id={productId} />;
    case /^\/insert$/.test(pathName):
        return (
        <ProductForm
            action="/products"
            fieldName="picture"
        /> );
    default:
        return <FourOFour />;
    }
}

function MainContent(props)
{
    return (
    <div className="main-content">
        <Navigator />
    </div>
    );
}

export default MainContent;