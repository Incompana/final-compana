// src/routes/AdminRedirectRoute.jsx

import { Navigate } from "react-router-dom";

const getStoredUser = () => {
  const savedUser = localStorage.getItem("user");

  if (!savedUser) return null;

  try {
    return JSON.parse(savedUser);
  } catch {
    return null;
  }
};

export default function AdminRedirectRoute({ children }) {
  const token = localStorage.getItem("token");
  const user = getStoredUser();

  if (token && user?.role === "admin") {
    return <Navigate to="/admin/dashboard" replace />;
  }

  return children;
}