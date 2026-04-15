import React, { useState } from "react";
import "../../styles/index.css";
import "../../styles/AuthForms.css";

const LoginForm = ({ onSuccess, onToggle }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`http://localhost:5000/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
        }),
      });

      if (response.status === 200) {
        const data = await response.json();
        onSuccess(data.user); 
      }
       else if (response.status === 401) {
        // Invalid credentials

        const errorData = await response.json();
        alert(errorData.message || "Invalid username or password!");
      } else if (response.status === 400) {
        // Validation error

        const errorData = await response.json();
        console.error("Validation errors:", errorData);
        alert("Please check your input and try again.");
      } else {
        // Other errors

        alert("An unexpected error occurred.");
      }
    } catch (error) {
      // Network error or request failed
      console.error("Login error:", error);
      alert("Unable to connect to the server. Please check your connection.");
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (      
    <div className="login-container">
      <div className="login-card">  
      <div className="login-brand">
        <div className="login-brand-icon">
          <svg width="20" height="20" viewBox="0 0 18 18" fill="none">
            <rect x="2" y="3" width="14" height="2" rx="1" fill="white" />
            <rect x="2" y="8" width="10" height="2" rx="1" fill="white" />
            <rect x="2" y="13" width="12" height="2" rx="1" fill="white" />
          </svg>
        </div>
        <span className="login-brand-name">Content4You</span>
      </div>

      <h2 className="login-title">Welcome back!</h2>
      <p className="login-subtitle">Sign in to your account</p>

      <form className="login-form" onSubmit={handleSubmit}>
        <div className="login-field">
          <label className="login-label" htmlFor="username">
            Username
          </label>
          <input
            id="username"
            type="text"
            name="username"
            placeholder="e.g., Jhony Bravo"
            value={formData.username || ""}
            onChange={handleChange}
            className="login-input"
            required
          />
        </div>

        <div className="login-field">
          <div className="login-field-header">
            <label className="login-label" htmlFor="password">
              Password
            </label>
          </div>
          <input
            id="password"
            type="password"
            name="password"
            placeholder="••••••••"
            value={formData.password || ""}
            onChange={handleChange}
            className="login-input"
            required
          />
        </div>

        <button type="submit" className="login-button">
          Sign In
        </button>
      </form>

      <div className="login-divider">
        <span>or</span>
      </div>

      <p className="login-toggle-text">
        Don't have an account?
        <button onClick={onToggle} className="toggle-button">
          Sign up for free
        </button>
      </p>
      </div>
    </div>
  );
};

export default LoginForm;
