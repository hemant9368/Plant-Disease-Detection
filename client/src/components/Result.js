import React, { useEffect, useState } from 'react';
import Layout from './Layout';

const Result = () => {
  const [appData, setAppData] = useState({
    disease_name: 'undefined',
    supplement_name: 'null',
    supplement_image: 'null',
    buy_link: 'null',
  });

  useEffect(() => {
    const fetchData = async () => {
      const queryParams = new URLSearchParams(window.location.search);
      const productId = queryParams.get('id');

      const response = await fetch(`/result?id=${productId}`);
      const result = await response.json();
      setAppData(result);
    };

    fetchData();
  }, []);

  return (
    <Layout>
      <div className="container">
        <img src="../static/dark_leaf.jpg" id="right" alt="Leaf" />
      </div>
      <div className="container">
        <img src="../static/dark_leaf.jpg" id="left" alt="Leaf" />
      </div>
      <div className="heading">PREDICTING THE RESULTS...</div>
      <div className="text">
        <div className="text1">
          <h1 id="dis_name">
            Disease Detected: {appData.disease_name.replace('_', ' ').title()}
          </h1>
          {appData.disease_name.includes('healthy') ? (
            <h3 id="treatment">Treatment: No Treatment Required</h3>
          ) : (
            <>
              <h3 id="treatment">Treatment: {appData.supplement_name}</h3>
              <a href={appData.buy_link}>
                <img
                  src={appData.supplement_image}
                  id="img_treat"
                  alt="Product"
                  style={{ display: 'block' }}
                />
              </a>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Result;
