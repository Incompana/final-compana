import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import { getUser, isLoggedIn, logout } from "../../utils/auth";
import FiturPage from "./FiturPage";
import TentangPage from "./TentangPage";
import LogoutConfirmModal from "../../components/LogoutConfirmModal";

const LANDING_FEATURES = [
  {
    icon: "🧭",
    title: "Panduan Personal",
    desc: "Rencana karir yang disesuaikan dengan kondisi dan tujuanmu.",
  },
  {
    icon: "⚡",
    title: "Action Kecil",
    desc: "Langkah nyata yang bisa dimulai hari ini juga.",
  },
  {
    icon: "📈",
    title: "Progres Nyata",
    desc: "Pantau perkembanganmu dan rayakan pencapaianmu.",
  },
];

const ChatBubble = () => {
  const [showTyping, setShowTyping] = useState(false);
  const [showReply, setShowReply] = useState(false);

  useEffect(() => {
    const t1 = setTimeout(() => setShowTyping(true), 800);

    const t2 = setTimeout(() => {
      setShowTyping(false);
      setShowReply(true);
    }, 2200);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, []);

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: "16px",
        padding: "20px",
        maxWidth: "520px",
        margin: "0 auto",
        backdropFilter: "blur(8px)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "16px",
          paddingBottom: "12px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <div style={{ display: "flex", gap: "5px" }}>
          {["#ff5f57", "#febc2e", "#28c840"].map((color, index) => (
            <div
              key={index}
              style={{
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                background: color,
              }}
            />
          ))}
        </div>

        <span
          style={{
            fontSize: "12px",
            color: "rgba(255,255,255,0.4)",
            marginLeft: "4px",
            fontFamily: "monospace",
          }}
        >
          Compana AI
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            alignItems: "flex-start",
            gap: "8px",
          }}
        >
          <div
            style={{
              background: "rgba(255,255,255,0.12)",
              borderRadius: "12px 12px 2px 12px",
              padding: "10px 14px",
              maxWidth: "75%",
              fontSize: "13px",
              color: "rgba(255,255,255,0.85)",
              lineHeight: 1.5,
            }}
          >
            Aku bingung harus mulai dari mana untuk berkarir di UI/UX..
          </div>

          <div
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              background: "rgba(255,255,255,0.15)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "11px",
              fontWeight: 600,
              color: "white",
              flexShrink: 0,
            }}
          >
            K
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
          <div
            style={{
              width: "28px",
              height: "28px",
              borderRadius: "50%",
              background: "linear-gradient(135deg, #2d8c5e, #1a5c3e)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "11px",
              fontWeight: 600,
              color: "white",
              flexShrink: 0,
            }}
          >
            C
          </div>

          <div
            style={{
              background: "rgba(45, 140, 94, 0.25)",
              border: "1px solid rgba(45, 140, 94, 0.3)",
              borderRadius: "12px 12px 12px 2px",
              padding: "10px 14px",
              maxWidth: "75%",
              fontSize: "13px",
              color: "rgba(255,255,255,0.85)",
              lineHeight: 1.5,
            }}
          >
            Tenang! Mari kita mulai dengan 3 langkah kecil hari ini
          </div>
        </div>

        {showTyping && (
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "8px",
              animation: "fadeIn 0.3s ease",
            }}
          >
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, #2d8c5e, #1a5c3e)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "11px",
                fontWeight: 600,
                color: "white",
                flexShrink: 0,
              }}
            >
              C
            </div>

            <div
              style={{
                background: "rgba(45, 140, 94, 0.15)",
                border: "1px solid rgba(45, 140, 94, 0.2)",
                borderRadius: "12px 12px 12px 2px",
                padding: "12px 16px",
                display: "flex",
                gap: "4px",
                alignItems: "center",
              }}
            >
              {[0, 1, 2].map((index) => (
                <div
                  key={index}
                  style={{
                    width: "6px",
                    height: "6px",
                    borderRadius: "50%",
                    background: "rgba(45, 200, 120, 0.7)",
                    animation: `bounce 1s ease-in-out ${
                      index * 0.2
                    }s infinite`,
                  }}
                />
              ))}
            </div>
          </div>
        )}

        {showReply && (
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              gap: "8px",
              animation: "fadeIn 0.4s ease",
            }}
          >
            <div
              style={{
                width: "28px",
                height: "28px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, #2d8c5e, #1a5c3e)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "11px",
                fontWeight: 600,
                color: "white",
                flexShrink: 0,
              }}
            >
              C
            </div>

            <div
              style={{
                background: "rgba(45, 140, 94, 0.25)",
                border: "1px solid rgba(45, 140, 94, 0.3)",
                borderRadius: "12px 12px 12px 2px",
                padding: "10px 14px",
                fontSize: "13px",
                color: "rgba(255,255,255,0.85)",
                lineHeight: 1.5,
              }}
            >
              Pertama, pelajari dasar-dasar Figma selama 30 menit hari ini 🎯
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default function LandingPage() {
  const navigate = useNavigate();

  const [scrolled, setScrolled] = useState(false);
  const [activePage, setActivePage] = useState("home");
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const user = getUser();
  const loggedIn = isLoggedIn();

  useEffect(() => {
    if (loggedIn && user?.role === "admin") {
      navigate("/admin/dashboard", { replace: true });
    }
  }, [loggedIn, user?.role, navigate]);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20);

    window.addEventListener("scroll", handler);

    return () => window.removeEventListener("scroll", handler);
  }, []);

  const getDisplayName = () => {
    if (!user) return "User";

    return user.username || user.name || user.email?.split("@")[0] || "User";
  };

  const handleOpenLogoutModal = () => {
  setShowLogoutModal(true);
};

const handleConfirmLogout = () => {
  logout();
  setShowLogoutModal(false);
  navigate("/", { replace: true });
};

  const handleMainCTA = () => {
    if (!loggedIn || !user) {
      navigate("/input");
      return;
    }

    if (user.role === "admin") {
      navigate("/admin/dashboard");
      return;
    }

    if (user.is_assessment_done || user.isAssessmentDone) {
      navigate("/dashboardUser");
      return;
    }

    navigate("/input");
  };

  const handleDashboard = () => {
    handleMainCTA();
  };

  if (activePage === "fitur") {
    return (
      <FiturPage
        onBack={() => setActivePage("home")}
        onMulai={handleMainCTA}
      />
    );
  }

  if (activePage === "tentang") {
    return (
      <TentangPage
        onBack={() => setActivePage("home")}
        onMulai={handleMainCTA}
      />
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a1f12",
        color: "white",
        overflowX: "hidden",
      }}
    >
      <nav
        style={{
          position: "sticky",
          top: 0,
          zIndex: 100,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 40px",
          background: scrolled ? "rgba(10, 31, 18, 0.85)" : "transparent",
          backdropFilter: scrolled ? "blur(12px)" : "none",
          borderBottom: scrolled
            ? "1px solid rgba(255,255,255,0.06)"
            : "none",
          transition: "all 0.3s",
        }}
      >
        <Logo />

        <div
          className="landing-nav-actions"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "20px",
          }}
        >
          <button
            type="button"
            className="nav-link"
            onClick={() => setActivePage("fitur")}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: 0,
            }}
          >
            Fitur
          </button>

          <button
            type="button"
            className="nav-link"
            onClick={() => setActivePage("tentang")}
            style={{
              background: "transparent",
              border: "none",
              cursor: "pointer",
              padding: 0,
            }}
          >
            Tentang
          </button>

          {!loggedIn ? (
            <>
              <button className="ghost-btn" onClick={() => navigate("/login")}>
                Login
              </button>

              <button
                className="cta-btn-nav"
                onClick={() => navigate("/register")}
              >
                Register
              </button>
            </>
          ) : (
            <>
              <button className="ghost-btn" onClick={handleDashboard}>
                {getDisplayName()}
              </button>

           <button className="cta-btn-nav" onClick={handleOpenLogoutModal}>
  Logout
</button>
            </>
          )}
        </div>
      </nav>

      <section
        style={{
          position: "relative",
          minHeight: "88vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "60px 24px 40px",
          overflow: "hidden",
        }}
      >
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            maxWidth: "720px",
          }}
        >
          <div className="badge-pill">
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: "#4de89a",
                flexShrink: 0,
              }}
            />
            AI Career Companion
          </div>

          <h1 className="hero-title">
            Dari{" "}
            <span
              style={{
                color: "#3dba74",
                textDecoration: "underline",
                textDecorationColor: "rgba(61,186,116,0.4)",
                textUnderlineOffset: "6px",
              }}
            >
              Kebingungan
            </span>
            <br />
            Menuju Kejelasan
          </h1>

          <p className="hero-subtitle" style={{ marginTop: "20px" }}>
            Temukan langkah karirmu dengan satu action kecil.
            <br />
            Compana memandu kamu dari bingung jadi yakin.
          </p>

          <div
            style={{
              marginTop: "32px",
              marginBottom: "48px",
            }}
          >
            <button className="cta-btn" onClick={handleMainCTA}>
              {loggedIn ? "Lanjutkan Perjalanan" : "Mulai Sekarang"}{" "}
              <span style={{ fontSize: "16px" }}>›</span>
            </button>
          </div>

          <ChatBubble />
        </div>
      </section>

      <section
        id="fitur"
        style={{
          padding: "60px 40px 80px",
          maxWidth: "900px",
          margin: "0 auto",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "16px",
            flexWrap: "wrap",
          }}
        >
          {LANDING_FEATURES.map((feature, index) => (
            <div key={index} className="feature-card">
              <div
                style={{
                  fontSize: "22px",
                  marginBottom: "12px",
                }}
              >
                {feature.icon}
              </div>

              <h3
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: 600,
                  fontSize: "15px",
                  color: "#3dba74",
                  marginBottom: "8px",
                }}
              >
                {feature.title}
              </h3>

              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "13px",
                  color: "rgba(255,255,255,0.45)",
                  lineHeight: 1.6,
                }}
              >
                {feature.desc}
              </p>
            </div>
          ))}

          <div
            style={{
              width: "100%",
              display: "flex",
              justifyContent: "center",
              marginTop: "18px",
            }}
          >
            <button
              onClick={() => setActivePage("fitur")}
              style={{
                padding: "12px 28px",
                borderRadius: "12px",
                border: "1px solid rgba(61,186,116,0.35)",
                background: "rgba(61,186,116,0.1)",
                color: "#3dba74",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Lihat Semua Fitur →
            </button>
          </div>
        </div>
      </section>

      <section
        id="tentang"
        style={{
          padding: "0 40px 70px",
          maxWidth: "900px",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.45)",
            lineHeight: 1.8,
            margin: "0 0 22px",
          }}
        >
          Compana membantu kamu memahami kondisi karier, menemukan skill gap,
          dan menyusun langkah kecil yang bisa langsung dikerjakan.
        </p>

        <button
          onClick={() => setActivePage("tentang")}
          style={{
            padding: "11px 24px",
            borderRadius: "12px",
            border: "1px solid rgba(255,255,255,0.14)",
            background: "rgba(255,255,255,0.06)",
            color: "rgba(255,255,255,0.75)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Pelajari Tentang Compana →
        </button>
      </section>

      <footer
        style={{
          borderTop: "1px solid rgba(255,255,255,0.06)",
          padding: "20px 40px",
          textAlign: "center",
        }}
      >
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "12px",
            color: "rgba(255,255,255,0.25)",
          }}
        >
          © 2025 Compana · Karirmu, Satu Langkah Lebih Jelas
        </p>
      </footer>

      <style>{`
        @media (max-width: 760px) {
          nav {
            padding: 14px 22px !important;
            align-items: flex-start !important;
            gap: 14px !important;
            flex-direction: column !important;
          }

          .landing-nav-actions {
            width: 100%;
            flex-wrap: wrap;
            gap: 12px !important;
          }
        }
      `}</style>
      <LogoutConfirmModal
  open={showLogoutModal}
  onCancel={() => setShowLogoutModal(false)}
  onConfirm={handleConfirmLogout}
/>
    </div>
  );
}