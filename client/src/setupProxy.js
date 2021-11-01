const { createProxyMiddleware } = require("http-proxy-middleware");
module.exports = function (app) {

  const prefix = process.env.PUBLIC_URL;
  const regex = `^${prefix}/`;

  app.use(
    [
      `${prefix}/list-products`,
      `${prefix}/products`,
      `${prefix}/pictures`],
    createProxyMiddleware({
      target: `http://localhost:${process.env.BACKEND_PORT}`,
      pathRewrite: {
        [regex]: "/"
      }
    })
  );
  
};