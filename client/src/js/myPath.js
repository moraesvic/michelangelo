
function rmDoubleSlash(s)
{
    return s.replace(/\/{2,}/, "/");
}

function getRootPath()
{
    return rmDoubleSlash(process.env.PUBLIC_URL + "/");
}

function linkTo(endpoint)
{
    return rmDoubleSlash(getRootPath() + endpoint);
}

export {
    rmDoubleSlash,
    getRootPath,
    linkTo
}