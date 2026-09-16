import React from 'react';
// import '../../static/style.css';

const Layout = ({ children }) => {
  return (
    <div>
      <head>
        <meta charSet="utf-8" />
        <title>Plant Disease Detector</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link
          href="https://fonts.googleapis.com/css?family=Merriweather&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css?family=Abril+Fatface&display=swap"
          rel="stylesheet"
        />
        <link rel="stylesheet" href="../static/style.css" />
        <link rel="icon" type="image/x-icon" href="../static/logo1.jpeg" />
      </head>
      <body>
        {children}
      </body>
      <footer>Copyright © 2023 TVS</footer>
    </div>
  );
};

export default Layout;
