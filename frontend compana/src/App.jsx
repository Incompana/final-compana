import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import ProtectedRoute from "./routes/ProtectedRoute";
import RoleRoute from "./routes/RoleRoute";
import AssessmentAccessRoute from "./routes/AssessmentAccessRoute";
import AssessmentRequiredRoute from "./routes/AssessmentRequiredRoute";
import AdminRedirectRoute from "./routes/AdminRedirectRoute";
import AuthRoute from "./routes/AuthRoute";


// PUBLIC
import LandingPage from "./pages/public/LandingPage";
import InputPage from "./pages/public/InputPage";
import AssessmentPage from "./pages/public/AssessmentPage";
import LoadingScreen from "./pages/public/LoadingScreen";
import HasilAnalisisPage from "./pages/public/HasilAnalisisPage";

// AUTH
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ForgotPasswordEmailPage from "./pages/auth/ForgotPasswordEmailPage";
import ForgotPasswordPage from "./pages/auth/ForgotPasswordPage";


// USER
import SkillGapPage from "./pages/user/SkillGapPage";
import DashboardUserPage from "./pages/user/DashboardUserPage";
import ActionPlanPage from "./pages/user/ActionPlanPage";
import TaskDetailPage from "./pages/user/TaskDetailPage";
import FeedbackPage from "./pages/user/FeedbackPage";
import DashboardPage from "./pages/user/DashboardPage";
import ProfilePage from "./pages/user/ProfilePage";

// ADMIN
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";

export default function App() {
  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
        }}
      />

      <Routes>

 {/* =========================
    ADMIN
========================= */}
<Route
  path="/admin/dashboard"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["admin"]}>
        <AdminDashboardPage />
      </RoleRoute>
    </ProtectedRoute>
  }
/>

       {/* =========================
    PUBLIC
========================= */}
<Route
  path="/"
  element={
    <AdminRedirectRoute>
      <LandingPage />
    </AdminRedirectRoute>
  }
/>

<Route
  path="/input"
  element={
    <AssessmentAccessRoute>
      <InputPage />
    </AssessmentAccessRoute>
  }
/>

<Route
  path="/assessment"
  element={
    <AssessmentAccessRoute>
      <AssessmentPage />
    </AssessmentAccessRoute>
  }
/>

<Route
  path="/loading"
  element={
    <AssessmentAccessRoute>
      <LoadingScreen />
    </AssessmentAccessRoute>
  }
/>

<Route
  path="/hasil-analisis"
  element={
    <AssessmentAccessRoute>
      <HasilAnalisisPage />
    </AssessmentAccessRoute>
  }
/>
        {/* =========================
            AUTH
        ========================= */}
      <Route
  path="/login"
  element={
    <AuthRoute>
      <LoginPage />
    </AuthRoute>
  }
/>

<Route
  path="/register"
  element={
    <AuthRoute>
      <RegisterPage />
    </AuthRoute>
  }
/>

<Route
  path="/forgot-email"
  element={
    <AuthRoute>
      <ForgotPasswordEmailPage />
    </AuthRoute>
  }
/>

<Route
  path="/reset-password"
  element={
    <AuthRoute>
      <ForgotPasswordPage />
    </AuthRoute>
  }
/>

        {/* =========================
            USER
        ========================= */}
      <Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <DashboardPage />
      </RoleRoute>
    </ProtectedRoute>
  }
/>

<Route
  path="/dashboardUser"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <AssessmentRequiredRoute>
          <DashboardUserPage />
        </AssessmentRequiredRoute>
      </RoleRoute>
    </ProtectedRoute>
  }
/>
<Route
  path="/profile"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <AssessmentRequiredRoute>
          <ProfilePage />
        </AssessmentRequiredRoute>
      </RoleRoute>
    </ProtectedRoute>
  }
/>

<Route
  path="/skill-gap"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <AssessmentRequiredRoute>
          <SkillGapPage />
        </AssessmentRequiredRoute>
      </RoleRoute>
    </ProtectedRoute>
  }
/>

<Route
  path="/action-plan"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <AssessmentRequiredRoute>
          <ActionPlanPage />
        </AssessmentRequiredRoute>
      </RoleRoute>
    </ProtectedRoute>
  }
/>

<Route
  path="/task-detail"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <AssessmentRequiredRoute>
          <TaskDetailPage />
        </AssessmentRequiredRoute>
      </RoleRoute>
    </ProtectedRoute>
  }
/>

<Route
  path="/feedback"
  element={
    <ProtectedRoute>
      <RoleRoute allowedRoles={["user"]}>
        <FeedbackPage />
      </RoleRoute>
    </ProtectedRoute>
  }
/>

        {/* fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}