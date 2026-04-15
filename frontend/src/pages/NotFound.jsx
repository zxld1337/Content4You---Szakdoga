import React from 'react';
import { useNavigate } from 'react-router-dom';
import "../styles/index.css";
import "../styles/NotFound.css";

const NotFound = () => {
  const navigate = useNavigate();

    return (
    <div className="notfound-container">
      <div className="notfound-content">
        <h1 className="notfound-error-code">404</h1>
        <h2 className="notfound-title">Page Not Found</h2>
        <p className="notfound-description">
          Oops! The page you are looking for doesn't exist or has been moved. 
        </p>
        <button className="notfound-btn" onClick={() => navigate('/')}>
          Go Home
        </button>
      </div>
    </div>
  );
};

export default NotFound;