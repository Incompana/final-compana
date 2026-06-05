// src/utils/auth.js

export const isLoggedIn = () => {
  const token = localStorage.getItem("token");

  return (
    !!token &&
    token !== "undefined" &&
    token !== "null" &&
    token.split(".").length === 3
  );
};

export const getUser = () => {
  const savedUser = localStorage.getItem("user");

  if (!savedUser) return null;

  try {
    return JSON.parse(savedUser);
  } catch {
    return null;
  }
};

export const getUserDisplayName = () => {
  const user = getUser();

  if (!user) return "Guest";

  return (
    user.username ||
    user.name ||
    user.email?.split("@")[0] ||
    "User"
  );
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("isLoggedIn");
};