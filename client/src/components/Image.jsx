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

export default Image;