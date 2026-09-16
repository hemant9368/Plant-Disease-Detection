import React, { useState } from 'react';
import Layout from './Layout';

const Home = () => {
  const [selectedImage, setSelectedImage] = useState(null);

  const handleImageChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const imageFile = event.target.imagefile.files[0];

    if (!imageFile) {
      alert('Please select a file to analyze!');
      return;
    }

    const formData = new FormData();
    formData.append('file', imageFile);

    const response = await fetch(' http://localhost:8001/analyze', {
      method: 'POST',
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      window.location.href = `/result?id=${result.product_id}`;
    } else {
      alert(result.error);
    }
  };

  return (
    <Layout>
      <div className="container">
        <img src="../static/bg.avif" alt="background" />
      </div>
      <div className="heading">PLANT DISEASE DETECTION & TREATMENT</div>
      <div className="text">
        <p><b>Upload a picture of a Plant</b></p>
      </div>
      <div className="inner">
        <form id="analysis-form" onSubmit={handleSubmit} enctype="multipart/form-data">
          <div className="imgbox">
            <img
              src={selectedImage || '../static/logo1.jpeg'}
              className="img"
              id="selected_image"
              alt="Selected"
            />
            <div className="middle">
              <div className="add"><span>SELECT IMAGE</span></div>
              <input
                name="imagefile"
                id="imagefile"
                type="file"
                style={{ width: '360px', height: '300px' }}
                onChange={handleImageChange}
              />
            </div>
          </div>
          <button id="analyze-button" className="analyze-button">
            <span>Analyze</span>
          </button>
        </form>
      </div>
    </Layout>
  );
};

export default Home;
