import React from 'react';

import * as myPath from "../js/myPath";
import "./Image.css";

function ImageTag(id, alt, loading = "eager")
    {
        let src = myPath.linkTo(`/pictures/${id}`);
        return id ?
        <img src={src}
        title={alt}
        alt={alt}
        loading={loading}
        className="demo-pic" />
        :
        <img src={require('../img/no-icon.png').default}
        title={alt}
        alt={alt}
        loading={loading}
        className="demo-pic" />;
    }

function Image(props)
{
    const defaultHeight = "180px";
    const style = {};
    if (props.height)
        style.height = `${props.height || defaultHeight}`;
    return (
    <div
    className="pic-box"
    style={style}
    >
        {ImageTag(props.id, props.alt, props.loading)}
    </div>
    );
}

function ImageHref(props)
{
    return props.id ?
    <a href={myPath.linkTo(`/pictures/${props.id}`)}>
        <Image
        id={props.id}
        alt={props.alt}
        height={props.height}
        loading={props.loading} />
    </a>
    :
    <Image
    id={props.id}
    alt={props.alt}
    height={props.height}
    loading={props.loading} />
    ;
}

export {
    Image,
    ImageHref
};