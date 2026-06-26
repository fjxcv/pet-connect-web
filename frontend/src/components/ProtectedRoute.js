/**
 * @file ProtectedRoute.js
 * @module PawRescue
 * @description 可复用组件：ProtectedRoute。
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const isAuthenticated = localStorage.getItem('token');
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  
  // User is authenticated, render the protected component
  return children;
};

export default ProtectedRoute;

