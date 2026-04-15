import React, { useState } from "react";
import "../../styles/AuthForms.css";

const RegisterForm = ({ onSuccess, onToggle }) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(`http://localhost:5000/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password,
        }),
      });

      if (response.status === 201) onSuccess();
      else if (response.status === 409) {
        // Username conflict

        const errorData = await response.json();
        alert(errorData.message || "Username is already taken!");
      } else if (response.status === 400) {
        // Bad request/validation error

        const errorData = await response.json();
        console.error("Validation errors:", errorData);
        alert("Please check your input and try again.");
      } else if (response.status === 500) {
        // Server error

        alert("Server error. Please try again later.");
      } else {
        // Other errors
        alert("An unexpected error occurred.");
      }
    } catch (error) {
      console.error("Registration error:", error);
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

        <h2 className="login-title">Welcome on board!</h2>
        <p className="login-subtitle">Create your account</p>

        <form className="login-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
            className="login-input"
            required
          />
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            className="login-input"
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            className="login-input"
            required
          />
          <button type="submit" className="login-button">
            Sign Up
          </button>
        </form>
        <div className="login-divider">
          <span>or</span>
        </div>

        <p className="login-toggle-text">
          Already have an account?
          <button onClick={onToggle} className="toggle-button">
            Log In
          </button>
        </p>
      </div>
    </div>
  );
};

export default RegisterForm;
