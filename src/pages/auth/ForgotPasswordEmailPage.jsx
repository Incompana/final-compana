// src/pages/ForgotPasswordEmailPage.jsx
import { useState } from "react";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";


export default function ForgotPasswordEmailPage({ onLogin, onSubmit }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
const handleSubmit = async () => {
  if (!email) return;

  try {
    setLoading(true);

    const res = await api.post("/auth/forgot-password", {
      email,
    });

    toast.success(res.data.message || "Link reset password berhasil dikirim 📧");

    // pindah ke halaman reset password
    navigate("/reset-password");

  } catch (error) {
    toast.error(
      error.response?.data?.message || "Gagal mengirim email reset password"
    );
  } finally {
    setLoading(false);
  }
};
  const inputBase = {
    width: "100%",
    padding: "14px 16px",
    borderRadius: "10px",
    border: "1.5px solid rgba(45, 140, 94, 0.4)",
    background: "rgba(255,255,255,0.0)",
    color: "#1a3a2a",
    fontFamily: "'DM Sans', sans-serif",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s, background 0.2s",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a1f12",
        color: "white",
        display: "flex",
        flexDirection: "column",
        overflowX: "hidden",
      }}
    >
      <nav style={{ display: "flex", alignItems: "center", padding: "16px 40px" }}>
        <Logo />
      </nav>

      <div
        style={{
          flex: 1,
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 24px",
        }}
      >
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            width: "100%",
            maxWidth: "520px",
            animation: "slideUp 0.6s ease both",
          }}
        >
          {/* Title */}
          <div style={{ textAlign: "center", marginBottom: "24px" }}>
            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(26px, 5vw, 36px)",
                color: "#3dba74",
                marginBottom: "8px",
                letterSpacing: "-0.5px",
              }}
            >
              Masukkan Email
            </h1>
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                color: "rgba(255,255,255,0.5)",
              }}
            >
              Silahkan masukkan email untuk mengganti password
            </p>
          </div>

          {/* Card */}
          <div
            style={{
              background: "rgba(255,255,255,0.95)",
              borderRadius: "20px",
              padding: "36px 40px 32px",
              boxShadow:
                "0 8px 40px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.08)",
            }}
          >
            {/* Email */}
            <div style={{ marginBottom: "14px" }}>
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={inputBase}
                onFocus={(e) => {
                  e.target.style.borderColor = "rgba(45, 140, 94, 0.8)";
                  e.target.style.background = "rgba(45, 140, 94, 0.04)";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "rgba(45, 140, 94, 0.4)";
                  e.target.style.background = "rgba(255,255,255,0.0)";
                }}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              />
            </div>

            {/* Login link */}
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(60,80,70,0.75)",
                textAlign: "center",
                marginBottom: "16px",
              }}
            >
              Sudah punya akun?{" "}
              <span
              onClick={() => navigate("/login")}
                style={{
                  color: "#2d8c5e",
                  cursor: "pointer",
                  fontWeight: 500,
                  transition: "color 0.2s",
                }}
                onMouseEnter={(e) => (e.target.style.color = "#1a5c3e")}
                onMouseLeave={(e) => (e.target.style.color = "#2d8c5e")}
              >
                Login
              </span>
            </p>

            {/* Lanjut dengan Google */}
            <button
              style={{
                width: "100%",
                padding: "12px 16px",
                borderRadius: "10px",
                border: "1.5px solid rgba(45, 140, 94, 0.3)",
                background: "transparent",
                color: "#1a3a2a",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.2s",
                marginBottom: "14px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "rgba(45, 140, 94, 0.06)";
                e.currentTarget.style.borderColor = "rgba(45, 140, 94, 0.6)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "transparent";
                e.currentTarget.style.borderColor = "rgba(45, 140, 94, 0.3)";
              }}
            >
              {/* Google icon */}
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
                <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
                <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
                <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
              </svg>
              Lanjut dengan Google
            </button>

            {/* Submit Button */}
            <button
              onClick={handleSubmit}
              disabled={loading || !email}
              style={{
                width: "100%",
                padding: "14px",
                borderRadius: "10px",
                border: "none",
                background:
                  loading ? "rgba(45, 140, 94, 0.6)" : "rgba(45, 140, 94, 0.85)",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "15px",
                fontWeight: 600,
                cursor: loading || !email ? "not-allowed" : "pointer",
                transition: "all 0.25s",
                opacity: !email ? 0.65 : 1,
              }}
              onMouseEnter={(e) => {
                if (!loading && email) {
                  e.target.style.background = "rgba(55, 165, 110, 1)";
                  e.target.style.transform = "translateY(-1px)";
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "rgba(45, 140, 94, 0.85)";
                e.target.style.transform = "translateY(0)";
              }}
            >
              {loading ? "Mengirim..." : "Submit"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
