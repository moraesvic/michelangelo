import React from 'react';

import * as myPath from "../js/myPath";
import "./Image.css";

function ImageTag(id, alt)
    {
        let src = myPath.linkTo(`/pictures/${id}`);
        return id ?
        <img src={src}
        title={alt}
        alt={alt}
        className="demo-pic"/>
        :
        <img src={require('../img/no-icon.png').default}
        title={alt}
        alt={alt}
        className="demo-pic" />;
    }

function Image(props)
{
    return (
    <div className="pic-box">
        {ImageTag(props.id, props.alt)}
    </div>
    );
}

function ImageHref(props)
{
    return props.id ?
    <a href={myPath.linkTo(`/pictures/${props.id}`)}>
        <Image id={props.id} alt={props.alt} />
    </a>
    :
    <Image id={props.id} alt={props.alt} />;
}

export {
    Image,
    ImageHref
};