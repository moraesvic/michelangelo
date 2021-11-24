const { createProxyMiddleware } = require("http-proxy-middleware");
module.exports = function (app) {

  const prefix = process.env.PUBLIC_URL;
  const regex = `^${prefix}/`;

  app.use(
    createProxyMiddleware(
      [
        `${prefix}/products`,
        `${prefix}/pictures`
      ],
      {
      target: `http://localhost:${process.env.BACKEND_PORT}`,
      pathRewrite: {
        [regex]: "/"
      }
    })
  );
  
};