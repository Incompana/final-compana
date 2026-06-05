// src/pages/RegisterPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";

export default function RegisterPage({ onLogin }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rePassword, setRePassword] = useState("");
  const [loading, setLoading] = useState(false);

  const emailValue = email.trim();
  const passwordValue = password.trim();
  const rePasswordValue = rePassword.trim();

  const isPasswordMatch =
    rePasswordValue.length > 0 && passwordValue === rePasswordValue;

  const isPasswordMismatch =
    rePasswordValue.length > 0 && passwordValue !== rePasswordValue;

  const isValid =
    emailValue.length > 0 &&
    passwordValue.length >= 6 &&
    rePasswordValue.length > 0 &&
    passwordValue === rePasswordValue;

  const handleRegister = async () => {
    if (!isValid || loading) {
      if (!emailValue) {
        toast.error("Email wajib diisi");
        return;
      }

      if (passwordValue.length < 6) {
        toast.error("Password minimal 6 karakter");
        return;
      }

      if (passwordValue !== rePasswordValue) {
        toast.error("Konfirmasi password tidak cocok");
        return;
      }

      return;
    }

    try {
      setLoading(true);

      await api.post("/auth/register", {
        email: emailValue,
        password: passwordValue,
      });

      toast.success("Register berhasil 🎉");

      if (onLogin) onLogin();

      setTimeout(() => {
        navigate("/login");
      }, 800);
    } catch (error) {
      console.log(error.response?.data || error.message);

      toast.error(error.response?.data?.message || "Register gagal");
    } finally {
      setLoading(false);
    }
  };

  const inputBase = {
    width: "100%",
    padding: "13px 15px",
    borderRadius: "12px",
    border: "1.5px solid rgba(45,140,94,0.28)",
    background: "rgba(45,140,94,0.035)",
    color: "#1a3a2a",
    fontFamily: "'DM Sans', sans-serif",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s, background 0.2s, box-shadow 0.2s",
    boxSizing: "border-box",
  };

  const labelStyle = {
    display: "block",
    marginBottom: "7px",
    color: "#1a3a2a",
    fontSize: "13px",
    fontWeight: 800,
    fontFamily: "'DM Sans', sans-serif",
  };

  const inputWrapStyle = {
    marginBottom: "15px",
  };

  const onFocus = (event) => {
    event.target.style.borderColor = "rgba(45,140,94,0.75)";
    event.target.style.background = "rgba(45,140,94,0.06)";
    event.target.style.boxShadow = "0 0 0 4px rgba(45,140,94,0.08)";
  };

  const onBlur = (event) => {
    event.target.style.borderColor = "rgba(45,140,94,0.28)";
    event.target.style.background = "rgba(45,140,94,0.035)";
    event.target.style.boxShadow = "none";
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
      <nav
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 40px",
          position: "relative",
          zIndex: 2,
        }}
      >
        <Logo />

        <button
          onClick={() => navigate("/")}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.55)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            cursor: "pointer",
          }}
        >
          ← Kembali
        </button>
      </nav>

      <main
        style={{
          flex: 1,
          position: "relative",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "34px 24px 58px",
        }}
      >
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            width: "100%",
            maxWidth: "470px",
            animation: "slideUp 0.6s ease both",
          }}
        >
          <div
            style={{
              textAlign: "center",
              marginBottom: "22px",
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "6px 16px",
                borderRadius: "999px",
                border: "1.5px solid rgba(61,186,116,0.4)",
                background: "rgba(61,186,116,0.08)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "12px",
                color: "rgba(255,255,255,0.75)",
                fontWeight: 600,
                marginBottom: "16px",
              }}
            >
              <span
                style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: "#3dba74",
                  boxShadow: "0 0 6px #3dba74",
                  display: "inline-block",
                }}
              />
              Buat akun Compana
            </div>

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(30px, 5vw, 40px)",
                color: "#3dba74",
                margin: "0 0 8px",
                letterSpacing: "-0.5px",
                textDecoration: "underline",
                textDecorationColor: "rgba(61,186,116,0.35)",
                textUnderlineOffset: "5px",
              }}
            >
              Register
            </h1>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                color: "rgba(255,255,255,0.52)",
                lineHeight: 1.7,
                margin: 0,
              }}
            >
              Daftar untuk menyimpan hasil analisis, action plan, dan progress
              belajarmu.
            </p>
          </div>

          <section
            style={{
              background: "rgba(255,255,255,0.96)",
              borderRadius: "22px",
              padding: "30px 32px 28px",
              boxShadow:
                "0 18px 60px rgba(0,0,0,0.38), 0 0 0 1px rgba(255,255,255,0.12)",
            }}
          >
            <div style={inputWrapStyle}>
              <label style={labelStyle}>Email</label>

              <input
                type="email"
                placeholder="contoh@email.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                style={inputBase}
                onFocus={onFocus}
                onBlur={onBlur}
                autoComplete="email"
              />
            </div>

            <div style={inputWrapStyle}>
              <label style={labelStyle}>Password</label>

              <input
                type="password"
                placeholder="Minimal 6 karakter"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                style={inputBase}
                onFocus={onFocus}
                onBlur={onBlur}
                autoComplete="new-password"
              />

              {passwordValue.length > 0 && passwordValue.length < 6 && (
                <p
                  style={{
                    fontSize: "12px",
                    color: "rgba(184,122,0,0.9)",
                    margin: "7px 0 0",
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                >
                  Password minimal 6 karakter.
                </p>
              )}
            </div>

            <div style={{ ...inputWrapStyle, marginBottom: "18px" }}>
              <label style={labelStyle}>Konfirmasi Password</label>

              <input
                type="password"
                placeholder="Masukkan ulang password"
                value={rePassword}
                onChange={(event) => setRePassword(event.target.value)}
                style={{
                  ...inputBase,
                  borderColor: isPasswordMismatch
                    ? "rgba(224,90,90,0.65)"
                    : isPasswordMatch
                    ? "rgba(45,140,94,0.65)"
                    : "rgba(45,140,94,0.28)",
                }}
                onFocus={onFocus}
                onBlur={(event) => {
                  event.target.style.borderColor = isPasswordMismatch
                    ? "rgba(224,90,90,0.65)"
                    : isPasswordMatch
                    ? "rgba(45,140,94,0.65)"
                    : "rgba(45,140,94,0.28)";
                  event.target.style.background = "rgba(45,140,94,0.035)";
                  event.target.style.boxShadow = "none";
                }}
                onKeyDown={(event) =>
                  event.key === "Enter" && handleRegister()
                }
                autoComplete="new-password"
              />

              {isPasswordMismatch && (
                <p
                  style={{
                    fontSize: "12px",
                    color: "rgba(224,90,90,0.9)",
                    margin: "7px 0 0",
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                >
                  Password tidak cocok.
                </p>
              )}

              {isPasswordMatch && (
                <p
                  style={{
                    fontSize: "12px",
                    color: "#2d8c5e",
                    margin: "7px 0 0",
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                >
                  Password cocok.
                </p>
              )}
            </div>

            <button
              onClick={handleRegister}
              disabled={loading || !isValid}
              style={{
                width: "100%",
                padding: "14px",
                borderRadius: "12px",
                border: "none",
                background:
                  loading || !isValid
                    ? "rgba(45,140,94,0.45)"
                    : "rgba(45,140,94,0.92)",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "15px",
                fontWeight: 800,
                cursor: loading || !isValid ? "not-allowed" : "pointer",
                transition: "all 0.25s",
                marginBottom: "18px",
              }}
              onMouseEnter={(event) => {
                if (!loading && isValid) {
                  event.target.style.background = "#3dba74";
                  event.target.style.transform = "translateY(-1px)";
                }
              }}
              onMouseLeave={(event) => {
                event.target.style.background =
                  loading || !isValid
                    ? "rgba(45,140,94,0.45)"
                    : "rgba(45,140,94,0.92)";
                event.target.style.transform = "translateY(0)";
              }}
            >
              {loading ? "Mendaftar..." : "Register"}
            </button>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(60,80,70,0.7)",
                textAlign: "center",
                margin: "0 0 14px",
              }}
            >
              Sudah punya akun?{" "}
              <span
                onClick={() => navigate("/login")}
                style={{
                  color: "#2d8c5e",
                  cursor: "pointer",
                  fontWeight: 800,
                }}
              >
                Login
              </span>
            </p>

            <div
              style={{
                height: "1px",
                background: "rgba(45,140,94,0.12)",
                margin: "16px 0",
              }}
            />

            <button
              onClick={() => navigate("/forgot-email")}
              style={{
                width: "100%",
                background: "transparent",
                border: "1px solid rgba(45,140,94,0.28)",
                borderRadius: "12px",
                padding: "11px 18px",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "#2d8c5e",
                cursor: "pointer",
                transition: "all 0.2s",
                fontWeight: 800,
              }}
              onMouseEnter={(event) => {
                event.target.style.background = "rgba(45,140,94,0.07)";
                event.target.style.borderColor = "rgba(45,140,94,0.55)";
              }}
              onMouseLeave={(event) => {
                event.target.style.background = "transparent";
                event.target.style.borderColor = "rgba(45,140,94,0.28)";
              }}
            >
              Lupa Password?
            </button>
          </section>
        </div>
      </main>

      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(18px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        input::placeholder {
          color: rgba(40,70,55,0.38);
        }

        @media (max-width: 560px) {
          nav {
            padding: 14px 22px !important;
          }

          section {
            padding: 26px 22px 24px !important;
          }
        }
      `}</style>
    </div>
  );
}