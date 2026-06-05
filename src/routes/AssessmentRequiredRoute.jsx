import { Navigate, useLocation } from "react-router-dom";
import { getUser, isLoggedIn } from "../utils/auth";

export default function AssessmentRequiredRoute({ children }) {
  const location = useLocation();

  if (!isLoggedIn()) {
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  const user = getUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role === "admin") {
    return <Navigate to="/admin/dashboard" replace />;
  }

  if (!user.is_assessment_done) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}