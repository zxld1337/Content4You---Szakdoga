import React, { createContext, useState, useEffect } from 'react';
import { fetchUserById } from '../services/user';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
    setUser(storedUser);
    setLoading(false);
  }, []);

  const login = async (userData) => {
    const fullUserData = {
      id: userData.id || "",
      email: userData.email || "",
      username: userData.username || "",
      fullName: userData.full_name || "",
      phoneNumber: userData.phone_number || "",
      dateOfBirth: userData.date_of_birth || "",
      dateOfCreate: userData.date_of_create || "",
      profilePicture: userData.profile_picture || "",
      followerCount: userData.follower_count || 0,
      followingCount: userData.following_count || 0,
    };

    setUser(fullUserData);
    localStorage.setItem('user', JSON.stringify(fullUserData));
};

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};