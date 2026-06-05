import { Navigate } from "react-router-dom";
import { getUser, isLoggedIn } from "../utils/auth";

export default function AuthRoute({ children }) {
  if (!isLoggedIn()) {
    return children;
  }

  const user = getUser();

  if (!user) {
    return children;
  }

  if (user.role === "admin") {
    return <Navigate to="/admin/dashboard" replace />;
  }

  if (user.is_assessment_done) {
    return <Navigate to="/dashboardUser" replace />;
  }

  return <Navigate to="/dashboard" replace />;
}