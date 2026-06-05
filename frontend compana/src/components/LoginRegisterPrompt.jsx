// src/components/LoginRegisterPrompt.jsx
// Muncul saat user ingin menyimpan hasil assessment sebagai guest

import { useState } from "react";

const BENEFITS = [
  { icon: "💾", text: "Simpan progress & hasil analisis" },
  { icon: "🗺️", text: "Akses action plan lengkap step-by-step" },
  { icon: "📊", text: "Pantau perjalanan karirmu dari dashboard" },
];

export default function LoginRegisterPrompt({
  onLogin,
  onRegister,
  onSkip,
}) {
  const [hovBtn, setHovBtn] = useState(null);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(10,31,18,0.92)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        boxSizing: "border-box",
        fontFamily: "'DM Sans', sans-serif",
        overflowX: "hidden",
        zIndex: 50,
        animation: "overlayFadeIn 0.18s ease-out",
      }}
    >
      <style>{`
        @keyframes overlayFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes cardPopUp {
          from {
            opacity: 0;
            transform: translateY(18px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>

      {/* Close button */}
      <button
        onClick={onSkip}
        style={{
          position: "absolute",
          top: "20px",
          right: "20px",
          width: "40px",
          height: "40px",
          borderRadius: "8px",
          border: "1.5px solid rgba(255,255,255,0.2)",
          background: "rgba(255,255,255,0.08)",
          color: "rgba(255,255,255,0.7)",
          fontFamily: "'DM Sans', sans-serif",
          fontSize: "24px",
          fontWeight: 400,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 0,
          lineHeight: 1,
          zIndex: 51,
        }}
      >
        ✕
      </button>

      <div
        style={{
          width: "100%",
          maxWidth: "430px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Top nav */}
        <nav
          style={{
            width: "100%",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "12px 16px 8px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "7px",
            }}
          >
            <span
              style={{
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#3dba74",
                display: "inline-block",
                boxShadow: "0 0 6px rgba(61,186,116,0.7)",
              }}
            />

            <span
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "16px",
                color: "white",
              }}
            >
              Compana
            </span>
          </div>

          <span
            style={{
              fontSize: "12px",
              color: "#3dba74",
              fontWeight: 500,
            }}
          >
            Hasil analisismu sudah siap ✨
          </span>
        </nav>

        {/* Main card */}
        <div
          style={{
            width: "100%",
            padding: "0 16px",
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              background: "rgba(255,255,255,0.95)",
              borderRadius: "16px",
              padding: "16px 16px 18px",
              boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
              animation: "cardPopUp 0.24s ease-out 0.05s both",
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "4px 10px",
                borderRadius: "999px",
                background: "rgba(45,140,94,0.1)",
                border: "1.5px solid rgba(45,140,94,0.3)",
                marginBottom: "8px",
              }}
            >
              <span
                style={{
                  width: "6px",
                  height: "6px",
                  borderRadius: "50%",
                  background: "#3dba74",
                  display: "inline-block",
                }}
              />

              <span
                style={{
                  fontSize: "11px",
                  color: "#2d8c5e",
                  fontWeight: 500,
                }}
              >
                Roadmap siap!
              </span>
            </div>

            <h2
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "22px",
                color: "#1a3a2a",
                margin: "0 0 6px",
                lineHeight: 1.2,
              }}
            >
              Lanjutkan{" "}
              <span style={{ color: "#2d8c5e" }}>
                perjalanan
              </span>
              <br />
              karirmu
            </h2>

            <p
              style={{
                fontSize: "12px",
                color: "rgba(40,70,55,0.65)",
                margin: "0 0 12px",
                lineHeight: 1.4,
              }}
            >
              Simpan hasil analisis dan mulai action plan untukmu.
              Gratis.
            </p>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "6px",
                marginBottom: "14px",
              }}
            >
              {BENEFITS.map((benefit) => (
                <div
                  key={benefit.text}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "6px 10px",
                    borderRadius: "8px",
                    background: "rgba(45,140,94,0.06)",
                    border: "1px solid rgba(45,140,94,0.15)",
                  }}
                >
                  <span
                    style={{
                      fontSize: "13px",
                      flexShrink: 0,
                    }}
                  >
                    {benefit.icon}
                  </span>

                  <span
                    style={{
                      fontSize: "11px",
                      color: "#2a4a38",
                    }}
                  >
                    {benefit.text}
                  </span>
                </div>
              ))}
            </div>

            {/* Login button */}
            <button
              onClick={onLogin}
              onMouseEnter={() => setHovBtn("login")}
              onMouseLeave={() => setHovBtn(null)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: "10px",
                border: "none",
                background:
                  hovBtn === "login" ? "#2a7a54" : "#2d8c5e",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
                marginBottom: "8px",
              }}
            >
              Login untuk Simpan Hasil →
            </button>

            {/* Register button */}
            <button
              onClick={onRegister}
              onMouseEnter={() => setHovBtn("register")}
              onMouseLeave={() => setHovBtn(null)}
              style={{
                width: "100%",
                padding: "9px",
                borderRadius: "10px",
                border: `1.5px solid ${
                  hovBtn === "register"
                    ? "rgba(45,140,94,0.5)"
                    : "rgba(0,0,0,0.12)"
                }`,
                background:
                  hovBtn === "register"
                    ? "rgba(45,140,94,0.04)"
                    : "white",
                color: "#1a3a2a",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "12px",
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.2s",
                marginBottom: "8px",
              }}
            >
              Buat Akun Baru
            </button>

            <p
              style={{
                textAlign: "center",
                margin: "8px 0 0",
              }}
            >
              <span
                onClick={onSkip}
                style={{
                  fontSize: "10px",
                  color: "rgba(40,70,55,0.5)",
                  cursor: "pointer",
                }}
              >
                Tutup
              </span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}