import { Navigate } from "react-router-dom";
import { getUser, isLoggedIn } from "../utils/auth";

export default function AssessmentAccessRoute({ children }) {
  const loggedIn = isLoggedIn();
  const user = getUser();

  // Guest boleh akses input, assessment, hasil analisis
  if (!loggedIn || !user) {
    return children;
  }

  // Admin tidak perlu masuk assessment user
  if (user.role === "admin") {
    return <Navigate to="/admin/dashboard" replace />;
  }

  // User lama yang sudah assessment tidak boleh ulangi alur input-assessment
  if (user.is_assessment_done) {
    return <Navigate to="/dashboardUser" replace />;
  }

  // User baru yang belum assessment boleh lanjut
  return children;
}