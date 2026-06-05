// src/pages/auth/LoginPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin } from "@react-oauth/google";
import toast from "react-hot-toast";

import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import { syncAssessmentDraft } from "../../utils/syncAssessmentDraft";

export default function LoginPage({ onLogin }) {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const emailValue = email.trim();
  const passwordValue = password.trim();

  const isLoginDisabled = loading || !emailValue || !passwordValue;

  const handleAfterLogin = async (result) => {
    const token = result.data?.token || result.token;
    const user = result.data?.user || result.user;

    if (!token || !user) {
      throw new Error("Token atau data user tidak ditemukan");
    }

    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));

    if (user.role === "admin") {
      navigate("/admin/dashboard", { replace: true });
      return;
    }

    const hasSyncedAssessment = await syncAssessmentDraft();

    if (hasSyncedAssessment) {
      const updatedUser = {
        ...user,
        is_assessment_done: true,
        isAssessmentDone: true,
      };

      localStorage.setItem("user", JSON.stringify(updatedUser));
      navigate("/dashboardUser", { replace: true });
      return;
    }

    if (user.is_assessment_done || user.isAssessmentDone) {
      navigate("/dashboardUser", { replace: true });
      return;
    }

    navigate("/dashboard", { replace: true });
  };

  const handleLogin = async () => {
    if (!emailValue || !passwordValue) {
      toast.error("Email dan password wajib diisi");
      return;
    }

    try {
      setLoading(true);

      const res = await api.post("/auth/login", {
        email: emailValue,
        password: passwordValue,
      });

      const result = res.data;

      await handleAfterLogin(result);

      toast.success("Login berhasil 🎉");

      if (onLogin) {
        onLogin(result.data?.user || result.user);
      }
    } catch (error) {
      console.log(error.response?.data || error.message);
      toast.error(error.response?.data?.message || "Login gagal");
    } finally {
      setLoading(false);
    }
  };

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        setLoading(true);

        const res = await api.post("/auth/google", {
          access_token: tokenResponse.access_token,
        });

        const result = res.data;

        await handleAfterLogin(result);

        toast.success("Login Google berhasil 🎉");

        if (onLogin) {
          onLogin(result.data?.user || result.user);
        }
      } catch (error) {
        console.log(error.response?.data || error.message);

        toast.error(
          error.response?.data?.message || "Google login gagal"
        );
      } finally {
        setLoading(false);
      }
    },

    onError: () => {
      toast.error("Google login gagal");
    },
  });

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
              Selamat datang kembali
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
              Login
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
              Masuk untuk melanjutkan perjalanan kariermu di Compana.
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
            <div style={{ marginBottom: "15px" }}>
              <label htmlFor="email" style={labelStyle}>
                Email
              </label>

              <input
                id="email"
                type="email"
                placeholder="contoh@email.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                onFocus={onFocus}
                onBlur={onBlur}
                style={inputBase}
                autoComplete="email"
              />
            </div>

            <div style={{ marginBottom: "16px" }}>
              <label htmlFor="password" style={labelStyle}>
                Password
              </label>

              <input
                id="password"
                type="password"
                placeholder="Masukkan password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                onFocus={onFocus}
                onBlur={onBlur}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    handleLogin();
                  }
                }}
                style={inputBase}
                autoComplete="current-password"
              />
            </div>

            <button
              onClick={handleLogin}
              disabled={isLoginDisabled}
              style={{
                width: "100%",
                padding: "14px",
                borderRadius: "12px",
                border: "none",
                background: isLoginDisabled
                  ? "rgba(45,140,94,0.45)"
                  : "rgba(45,140,94,0.92)",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "15px",
                fontWeight: 800,
                cursor: isLoginDisabled ? "not-allowed" : "pointer",
                transition: "all 0.25s",
                marginBottom: "16px",
              }}
              onMouseEnter={(event) => {
                if (!isLoginDisabled) {
                  event.target.style.background = "#3dba74";
                  event.target.style.transform = "translateY(-1px)";
                }
              }}
              onMouseLeave={(event) => {
                event.target.style.background = isLoginDisabled
                  ? "rgba(45,140,94,0.45)"
                  : "rgba(45,140,94,0.92)";
                event.target.style.transform = "translateY(0)";
              }}
            >
              {loading ? "Masuk..." : "Login"}
            </button>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(60,80,70,0.7)",
                textAlign: "center",
                margin: "0 0 16px",
              }}
            >
              Belum punya akun?{" "}
              <span
                onClick={() => navigate("/register")}
                style={{
                  color: "#2d8c5e",
                  cursor: "pointer",
                  fontWeight: 800,
                }}
              >
                Register
              </span>
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr auto 1fr",
                alignItems: "center",
                gap: "12px",
                margin: "14px 0 16px",
              }}
            >
              <div
                style={{
                  height: "1px",
                  background: "rgba(45,140,94,0.14)",
                }}
              />

              <span
                style={{
                  fontSize: "12px",
                  color: "rgba(60,80,70,0.45)",
                  fontWeight: 700,
                }}
              >
                atau
              </span>

              <div
                style={{
                  height: "1px",
                  background: "rgba(45,140,94,0.14)",
                }}
              />
            </div>

            <button
              onClick={() => {
                if (!loading) {
                  googleLogin();
                }
              }}
              disabled={loading}
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: "12px",
                border: "1px solid rgba(45,140,94,0.18)",
                background: "rgba(255,255,255,0.72)",
                color: "#1a3a2a",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 800,
                cursor: loading ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
                opacity: loading ? 0.65 : 1,
                marginBottom: "16px",
              }}
              title="Login dengan Google"
            >
              <svg
                width="22"
                height="22"
                viewBox="0 0 36 36"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="18" cy="18" r="18" fill="white" />

                <path
                  d="M27.36 18.2c0-.63-.06-1.25-.16-1.84H18v3.48h5.24a4.48 4.48 0 01-1.94 2.94v2.44h3.14c1.84-1.69 2.92-4.19 2.92-7.02z"
                  fill="#4285F4"
                />

                <path
                  d="M18 28c2.63 0 4.84-.87 6.44-2.38l-3.14-2.44c-.87.58-1.98.93-3.3.93-2.54 0-4.69-1.71-5.46-4.02H9.3v2.52A9.99 9.99 0 0018 28z"
                  fill="#34A853"
                />

                <path
                  d="M12.54 20.09A5.97 5.97 0 0112.22 18c0-.73.13-1.44.32-2.09v-2.52H9.3A9.99 9.99 0 008 18c0 1.61.39 3.13 1.3 4.61l3.24-2.52z"
                  fill="#FBBC05"
                />

                <path
                  d="M18 12.88c1.43 0 2.71.49 3.72 1.46l2.78-2.78C22.84 9.99 20.63 9 18 9a9.99 9.99 0 00-8.7 5.09l3.24 2.52c.77-2.31 2.92-4.73 5.46-4.73z"
                  fill="#EA4335"
                />
              </svg>

              Login dengan Google
            </button>

            <div
              style={{
                height: "1px",
                background: "rgba(45,140,94,0.12)",
                margin: "14px 0",
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