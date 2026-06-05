// src/pages/ForgotPasswordPage.jsx
import { useState } from "react";
import axios from "axios";
import { Logo, StarField } from "../../components/Shared";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

export default function ForgotPasswordPage({ onLogin }) {

  const token = new URLSearchParams(window.location.search).get("token");

  const [password, setPassword] = useState("");
  const [rePassword, setRePassword] = useState("");
  const [loading, setLoading] = useState(false);

  const isValid = password && rePassword && password === rePassword;
  const navigate = useNavigate();
  const handleSubmit = async () => {
    if (!isValid) {
      toast.error("Password tidak valid");
      return;
    }

    try {
      setLoading(true);

      await axios.post(
        "http://localhost:5000/api/auth/reset-password",
        {
          token,
          password,
        }
      );

    toast.success("Password berhasil direset 🎉");

setTimeout(() => {
  window.location.href = "/dashboard";
}, 1500);

    } catch (error) {
      console.log(error);

      toast.error(
        error.response?.data?.message ||
        "Reset password gagal"
      );

    } finally {
      setLoading(false);
    }
  };



  const pageStyle = {
  minHeight: "100vh",
  background: "#0a1f12",
  color: "white",
  display: "flex",
  flexDirection: "column",
  overflowX: "hidden",
};

const navStyle = {
  display: "flex",
  alignItems: "center",
  padding: "16px 40px",
};

const containerStyle = {
  flex: 1,
  position: "relative",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  padding: "40px 24px",
};

const contentStyle = {
  position: "relative",
  zIndex: 1,
  width: "100%",
  maxWidth: "520px",
  animation: "slideUp 0.6s ease both",
};

const titleContainerStyle = {
  textAlign: "center",
  marginBottom: "24px",
};

const titleStyle = {
  fontFamily: "'Playfair Display', serif",
  fontWeight: 700,
  fontSize: "clamp(26px, 5vw, 36px)",
  color: "#3dba74",
  marginBottom: "8px",
  letterSpacing: "-0.5px",
};

const subtitleStyle = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "14px",
  color: "rgba(255,255,255,0.5)",
};

const cardStyle = {
  background: "rgba(255,255,255,0.95)",
  borderRadius: "20px",
  padding: "36px 40px 32px",
  boxShadow:
    "0 8px 40px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.08)",
};

const labelStyle = {
  display: "block",
  marginBottom: "6px",
  color: "#1a3a2a",
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "14px",
  fontWeight: 600,
};

const inputBase = {
  width: "100%",
  padding: "14px 16px",
  borderRadius: "10px",
  border: "1.5px solid rgba(45, 140, 94, 0.4)",
  background: "rgba(255,255,255,0)",
  color: "#1a3a2a",
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "14px",
  outline: "none",
  transition: "border-color 0.2s, background 0.2s",
};

const loginTextStyle = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "13px",
  color: "rgba(60,80,70,0.75)",
  textAlign: "center",
  marginBottom: "18px",
};

const loginLinkStyle = {
  color: "#2d8c5e",
  cursor: "pointer",
  fontWeight: 500,
};

const buttonStyle = {
  width: "100%",
  padding: "14px",
  borderRadius: "10px",
  border: "none",
  background: "rgba(45, 140, 94, 0.85)",
  color: "white",
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "15px",
  fontWeight: 600,
  cursor: "pointer",
  transition: "all 0.25s",
};

const errorTextStyle = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "12px",
  color: "rgba(220, 80, 80, 0.85)",
  marginTop: "6px",
  paddingLeft: "4px",
};

  return (
  <div style={pageStyle}>
  <nav style={navStyle}>
    <Logo />
  </nav>

  <div style={containerStyle}>
    <div className="mesh-bg" />
    <StarField />

    <div style={contentStyle}>
      <div style={titleContainerStyle}>
        <h1 style={titleStyle}>Reset Password</h1>
        <p style={subtitleStyle}>
          Silahkan masukkan password baru untuk akun Anda
        </p>
      </div>

      <div style={cardStyle}>
        {/* Password Baru */}
        <div style={{ marginBottom: "14px" }}>
          <label style={labelStyle}>Password Baru</label>

          <input
            type="password"
            placeholder="Masukkan password baru"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={inputBase}
          />
        </div>

        {/* Konfirmasi Password */}
        <div style={{ marginBottom: "14px" }}>
          <label style={labelStyle}>Konfirmasi Password</label>

          <input
            type="password"
            placeholder="Masukkan ulang password"
            value={rePassword}
            onChange={(e) => setRePassword(e.target.value)}
            style={inputBase}
          />

          {rePassword && password !== rePassword && (
            <p style={errorTextStyle}>
              Password tidak cocok
            </p>
          )}
        </div>

        <p style={loginTextStyle}>
          Sudah ingat password?{" "}
          <span
            onClick={() => navigate("/login")}
            style={loginLinkStyle}
          >
            Login
          </span>
        </p>

        <button
          onClick={handleSubmit}
          disabled={!isValid || loading}
          style={{
            ...buttonStyle,
            opacity: !isValid ? 0.65 : 1,
          }}
        >
          {loading ? "Memproses..." : "Reset Password"}
        </button>
      </div>
    </div>
  </div>
</div>
  );
}