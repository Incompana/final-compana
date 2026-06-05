// src/pages/user/DashboardPage.jsx

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";

// ─── helper ──────────────────────────────────────────────────────────────────

const getStoredUser = () => {
  const savedUser = localStorage.getItem("user");

  if (!savedUser) return null;

  try {
    return JSON.parse(savedUser);
  } catch {
    return null;
  }
};

const getDashboardCards = (hasAssessment) => {
  if (!hasAssessment) {
    return [
      {
        icon: "📋",
        title: "Belum ada task aktif",
        desc: "Kamu belum memulai langkah pertamamu. Isi assessment untuk membuka task pertamamu.",
        cta: "Mulai Assessment →",
        action: "/input",
      },
      {
        icon: "🧭",
        title: "Belum ada skill gap",
        desc: "Skill gap akan muncul setelah kamu menyelesaikan assessment karier.",
        cta: "Buat Skill Gap →",
        action: "/input",
      },
      {
         icon: "🏠",
  title: "Pelajari alur Compana dulu",
  desc: "Lihat cara kerja Compana sebelum mulai assessment dan membuka roadmap personalmu.",
  cta: "Lihat Panduan →",
  action: "/",
      },
    ];
  }

  return [
    {
      icon: "🧭",
      title: "Skill gap sudah tersedia",
      desc: "Lihat gap kemampuanmu dan pahami skill yang perlu kamu tingkatkan terlebih dahulu.",
      cta: "Lanjut Skill Gap →",
      action: "/skill-gap",
    },
    {
      icon: "🗺️",
      title: "Action plan siap dibuka",
      desc: "Setelah memahami skill gap, lanjutkan ke roadmap dan langkah belajar personalmu.",
      cta: "Lanjut Action Plan →",
      action: "/action-plan",
    },
    {
      icon: "📊",
      title: "Masuk Dashboard User",
      desc: "Pantau progress, task aktif, feedback, dan perjalanan kariermu secara keseluruhan.",
      cta: "Lanjut Dashboard →",
      action: "/dashboardUser",
    },
  ];
};

const AI_THINKING_CARDS = [
  {
    icon: "🧩",
    title: "Menganalisis kondisimu...",
    desc: "Compana AI memproses profil karirmu.",
    steps: [
      { done: true, text: "Membaca input kondisi" },
      {
        done: false,
        spinning: true,
        text: "Menentukan target role...",
      },
      {
        done: false,
        spinning: false,
        text: "Menyusun action plan",
      },
    ],
  },
  {
    icon: "🔍",
    title: "Mengevaluasi taskmu...",
    desc: "AI memeriksa task dan menyiapkan feedback.",
    steps: [
      { done: true, text: "Task diterima" },
      { done: true, text: "Membaca detail task" },
      {
        done: false,
        spinning: true,
        text: "Menyiapkan feedback...",
      },
    ],
  },
  {
    icon: "🗺️",
    title: "Menyusun action plan...",
    desc: "Langkah disesuaikan dengan profil kamu.",
    steps: [
      { done: true, text: "Profil dianalisis" },
      { done: true, text: "Skill gap diidentifikasi" },
      {
        done: false,
        spinning: true,
        text: "Membuat urutan langkah...",
      },
    ],
  },
];

const LOCKED_STEPS = [
  {
    id: "s1",
    icon: "✓",
    iconBg: "#3dba74",
    title: "HTML5 Semantic Structure",
    meta: "Selesai · 2 hari · +50 XP",
    badge: "✓ Selesai",
    badgeBg: "rgba(61,186,116,0.15)",
    badgeColor: "#3dba74",
    status: "selesai",
  },
  {
    id: "s3",
    icon: "3",
    iconBg: "#4a9c6a",
    title: "JavaScript ES6 Dasar",
    meta: "Hari 3 dari 7 · +120 XP",
    badge: "▷ Sedang Berjalan",
    badgeBg: "rgba(61,186,116,0.1)",
    badgeColor: "#a8d8b8",
    status: "berjalan",
    cta: "Lanjutkan →",
  },
  {
    id: "s4",
    icon: "🔒",
    title: "DOM Manipulation",
    meta: "Buka setelah JS ES6 selesai",
    badge: "🔒 Terkunci",
    badgeBg: "rgba(255,255,255,0.06)",
    badgeColor: "rgba(255,255,255,0.3)",
    status: "terkunci",
  },
  {
    id: "s6",
    icon: "🔒",
    title: "Build Portfolio Project",
    meta: "Buka setelah semua Phase 1 selesai",
    badge: "🔒 Terkunci",
    badgeBg: "rgba(255,255,255,0.06)",
    badgeColor: "rgba(255,255,255,0.3)",
    status: "terkunci",
  },
];

// ─── sub components ──────────────────────────────────────────────────────────

function SectionLabel({ children }) {
  return (
    <p
      style={{
        fontFamily: "'DM Sans', sans-serif",
        fontSize: "10px",
        letterSpacing: "0.12em",
        textTransform: "uppercase",
        color: "rgba(255,255,255,0.3)",
        marginBottom: "12px",
        display: "flex",
        alignItems: "center",
        gap: "10px",
      }}
    >
      {children}
      <span
        style={{
          flex: 1,
          height: "1px",
          background: "rgba(255,255,255,0.08)",
          display: "inline-block",
        }}
      />
    </p>
  );
}

function EmptyCard({ card, onClick }) {
  const [hov, setHov] = useState(false);

  return (
    <div
      style={{
        background: "rgba(255,255,255,0.94)",
        borderRadius: "16px",
        padding: "28px 24px 22px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "10px",
        transition: "transform 0.2s, box-shadow 0.2s",
        transform: hov ? "translateY(-3px)" : "translateY(0)",
        boxShadow: hov
          ? "0 10px 32px rgba(0,0,0,0.22)"
          : "0 2px 12px rgba(0,0,0,0.12)",
        cursor: "default",
      }}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
    >
      <div
        style={{
          width: "52px",
          height: "52px",
          borderRadius: "50%",
          background: "rgba(45,140,94,0.12)",
          border: "1.5px solid rgba(45,140,94,0.25)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "22px",
        }}
      >
        {card.icon}
      </div>

      <p
        style={{
          fontFamily: "'Playfair Display', serif",
          fontWeight: 700,
          fontSize: "15px",
          color: "#1a3a2a",
          margin: 0,
          textAlign: "center",
          textDecoration: "underline",
          textDecorationColor: "rgba(45,140,94,0.3)",
          textUnderlineOffset: "3px",
        }}
      >
        {card.title}
      </p>

      <p
        style={{
          fontFamily: "'DM Sans', sans-serif",
          fontSize: "12px",
          color: "rgba(40,70,55,0.6)",
          textAlign: "center",
          margin: 0,
          lineHeight: 1.6,
        }}
      >
        {card.desc}
      </p>

      <button
        onClick={() => onClick(card.action)}
        style={{
          marginTop: "6px",
          padding: "9px 20px",
          borderRadius: "9px",
          border: "none",
          background: "rgba(45,140,94,0.85)",
          color: "white",
          fontFamily: "'DM Sans', sans-serif",
          fontSize: "13px",
          fontWeight: 600,
          cursor: "pointer",
          transition: "background 0.2s, transform 0.15s",
        }}
        onMouseEnter={(e) => {
          e.target.style.background = "rgba(61,186,116,1)";
          e.target.style.transform = "translateY(-1px)";
        }}
        onMouseLeave={(e) => {
          e.target.style.background = "rgba(45,140,94,0.85)";
          e.target.style.transform = "translateY(0)";
        }}
      >
        {card.cta}
      </button>
    </div>
  );
}

function AIThinkingCard({ card }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: "16px",
        padding: "22px 20px",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}
    >
      <div
        style={{
          width: "48px",
          height: "48px",
          borderRadius: "50%",
          background: "rgba(45,140,94,0.18)",
          border: "1.5px solid rgba(61,186,116,0.3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "20px",
          marginBottom: "4px",
        }}
      >
        {card.icon}
      </div>

      <p
        style={{
          fontFamily: "'Playfair Display', serif",
          fontWeight: 700,
          fontSize: "14px",
          color: "rgba(255,255,255,0.85)",
          margin: 0,
          textDecoration: "underline",
          textDecorationColor: "rgba(255,255,255,0.2)",
          textUnderlineOffset: "3px",
        }}
      >
        {card.title}
      </p>

      <p
        style={{
          fontFamily: "'DM Sans', sans-serif",
          fontSize: "12px",
          color: "rgba(255,255,255,0.4)",
          margin: "0 0 6px",
        }}
      >
        {card.desc}
      </p>

      {card.steps.map((step, index) => (
        <div
          key={index}
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          <span
            style={{
              fontSize: "12px",
              color: step.done
                ? "#3dba74"
                : step.spinning
                ? "#d4a844"
                : "rgba(255,255,255,0.25)",
              animation: step.spinning ? "spin 1.2s linear infinite" : "none",
              display: "inline-block",
            }}
          >
            {step.done ? "✓" : "◌"}
          </span>

          <span
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "12px",
              color: step.done
                ? "rgba(255,255,255,0.65)"
                : step.spinning
                ? "rgba(255,255,255,0.5)"
                : "rgba(255,255,255,0.25)",
            }}
          >
            {step.text}
          </span>
        </div>
      ))}
    </div>
  );
}

function StepRow({ step, onLanjutkan, hoveredLocked, setHoveredLocked }) {
  const isLocked = step.status === "terkunci";
  const isActive = step.status === "berjalan";
  const isDone = step.status === "selesai";
  const isHov = hoveredLocked === step.id;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "11px 14px",
        borderRadius: "10px",
        background: isActive
          ? "rgba(61,186,116,0.06)"
          : isLocked
          ? "rgba(255,255,255,0.02)"
          : "rgba(255,255,255,0.04)",
        border: isActive
          ? "1px solid rgba(61,186,116,0.2)"
          : "1px solid rgba(255,255,255,0.07)",
        opacity: isLocked ? 0.6 : 1,
        position: "relative",
        transition: "all 0.2s",
        cursor: isLocked ? "not-allowed" : "default",
      }}
      onMouseEnter={() => isLocked && setHoveredLocked(step.id)}
      onMouseLeave={() => isLocked && setHoveredLocked(null)}
    >
      <div
        style={{
          width: "30px",
          height: "30px",
          borderRadius: "50%",
          background: isLocked ? "rgba(255,255,255,0.07)" : step.iconBg,
          border: `1.5px solid ${
            isLocked ? "rgba(255,255,255,0.12)" : "rgba(61,186,116,0.4)"
          }`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: isLocked ? "14px" : "13px",
          color: isDone || isActive ? "white" : "rgba(255,255,255,0.4)",
          fontWeight: 700,
          flexShrink: 0,
        }}
      >
        {step.icon}
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontWeight: 600,
            fontSize: "13px",
            color: isLocked ? "rgba(255,255,255,0.4)" : "rgba(255,255,255,0.85)",
            margin: "0 0 2px",
            whiteSpace: "nowrap",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          {step.title}
        </p>

        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "11px",
            color: "rgba(255,255,255,0.3)",
            margin: 0,
          }}
        >
          {step.meta}
        </p>
      </div>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-end",
          gap: "5px",
          flexShrink: 0,
        }}
      >
        <span
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "11px",
            color: step.badgeColor,
            background: step.badgeBg,
            padding: "3px 10px",
            borderRadius: "999px",
            border: `1px solid ${
              isLocked ? "rgba(255,255,255,0.08)" : "rgba(61,186,116,0.2)"
            }`,
          }}
        >
          {step.badge}
        </span>

        {isActive && step.cta && (
          <button
            onClick={onLanjutkan}
            style={{
              padding: "5px 14px",
              borderRadius: "7px",
              border: "none",
              background: "#3dba74",
              color: "white",
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "12px",
              fontWeight: 600,
              cursor: "pointer",
              transition: "background 0.2s",
            }}
            onMouseEnter={(e) => (e.target.style.background = "#4dcf85")}
            onMouseLeave={(e) => (e.target.style.background = "#3dba74")}
          >
            {step.cta}
          </button>
        )}
      </div>

      {isLocked && isHov && (
        <div
          style={{
            position: "absolute",
            bottom: "calc(100% + 8px)",
            left: "50%",
            transform: "translateX(-50%)",
            background: "rgba(10,15,12,0.97)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: "10px",
            padding: "10px 14px",
            width: "220px",
            zIndex: 10,
            pointerEvents: "none",
          }}
        >
          <p
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontWeight: 600,
              fontSize: "12px",
              color: "#e05a5a",
              margin: "0 0 4px",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            🔒 Langkah ini masih terkunci
          </p>

          <p
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "11px",
              color: "rgba(255,255,255,0.45)",
              margin: 0,
              lineHeight: 1.5,
              textDecoration: "underline",
              textDecorationColor: "rgba(255,255,255,0.15)",
              textUnderlineOffset: "2px",
            }}
          >
            Selesaikan langkah sebelumnya terlebih dahulu untuk membuka langkah ini.
          </p>

          <div
            style={{
              position: "absolute",
              bottom: "-6px",
              left: "50%",
              transform: "translateX(-50%) rotate(45deg)",
              width: "10px",
              height: "10px",
              background: "rgba(10,15,12,0.97)",
              borderRight: "1px solid rgba(255,255,255,0.12)",
              borderBottom: "1px solid rgba(255,255,255,0.12)",
            }}
          />
        </div>
      )}
    </div>
  );
}

// ─── main page ───────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [hoveredLocked, setHoveredLocked] = useState(null);

  const routerNavigate = useNavigate();

  const user = useMemo(() => getStoredUser(), []);

  const hasAssessment = Boolean(user?.is_assessment_done);

  const dashboardCards = useMemo(
    () => getDashboardCards(hasAssessment),
    [hasAssessment]
  );

  const navigate = (path) => {
    routerNavigate(path);
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
          padding: "14px 40px",
          flexShrink: 0,
        }}
      >
        <Logo />

        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            background: "rgba(61,186,116,0.2)",
            border: "1.5px solid rgba(61,186,116,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "14px",
            cursor: "pointer",
          }}
          onClick={() => navigate("/dashboardUser")}
        >
          👤
        </div>
      </nav>

      <div
        style={{
          position: "relative",
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "0 24px 48px",
        }}
      >
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            width: "100%",
            maxWidth: "820px",
            animation: "slideUp 0.5s ease both",
          }}
        >
          <SectionLabel>
            {hasAssessment ? "Your Journey" : "Empty States"}
          </SectionLabel>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "14px",
              marginBottom: "32px",
            }}
          >
            {dashboardCards.map((card) => (
              <EmptyCard key={card.title} card={card} onClick={navigate} />
            ))}
          </div>

          <SectionLabel>AI Thinking / Loading States</SectionLabel>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "14px",
              marginBottom: "32px",
            }}
          >
            {AI_THINKING_CARDS.map((card) => (
              <AIThinkingCard key={card.title} card={card} />
            ))}
          </div>

          <SectionLabel>Locked Step UI — Visual Progression</SectionLabel>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "14px",
              marginBottom: "14px",
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.09)",
                borderRadius: "14px",
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {LOCKED_STEPS.map((step) => (
                <StepRow
                  key={step.id}
                  step={step}
                  onLanjutkan={() => navigate("/action-plan")}
                  hoveredLocked={hoveredLocked}
                  setHoveredLocked={setHoveredLocked}
                />
              ))}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div
                style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  borderRadius: "14px",
                  padding: "16px",
                }}
              >
                <p
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "10px",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: "rgba(255,255,255,0.25)",
                    marginBottom: "10px",
                  }}
                >
                  Locked Step — Hover Tooltip
                </p>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "10px 12px",
                    borderRadius: "10px",
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.07)",
                    opacity: 0.65,
                    marginBottom: "10px",
                  }}
                >
                  <div
                    style={{
                      width: "28px",
                      height: "28px",
                      borderRadius: "50%",
                      background: "rgba(255,255,255,0.06)",
                      border: "1.5px solid rgba(255,255,255,0.1)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "13px",
                      flexShrink: 0,
                    }}
                  >
                    🔒
                  </div>

                  <div style={{ flex: 1 }}>
                    <p
                      style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontWeight: 600,
                        fontSize: "13px",
                        color: "rgba(255,255,255,0.4)",
                        margin: "0 0 2px",
                      }}
                    >
                      Git & GitHub Dasar
                    </p>

                    <p
                      style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "11px",
                        color: "rgba(255,255,255,0.25)",
                        margin: 0,
                      }}
                    >
                      Terkunci · buka setelah DOM Manipulation
                    </p>
                  </div>
                </div>

                <div
                  style={{
                    background: "rgba(10,15,12,0.97)",
                    border: "1px solid rgba(255,255,255,0.12)",
                    borderRadius: "10px",
                    padding: "12px 14px",
                  }}
                >
                  <p
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontWeight: 600,
                      fontSize: "12px",
                      color: "#e05a5a",
                      margin: "0 0 5px",
                    }}
                  >
                    🔒 Langkah ini masih terkunci
                  </p>

                  <p
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "11px",
                      color: "rgba(255,255,255,0.45)",
                      margin: 0,
                      lineHeight: 1.55,
                    }}
                  >
                    Selesaikan DOM Manipulation terlebih dahulu untuk membuka langkah ini.
                  </p>
                </div>
              </div>

              <div
                style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.09)",
                  borderRadius: "14px",
                  padding: "16px",
                }}
              >
                <p
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "10px",
                    letterSpacing: "0.1em",
                    textTransform: "uppercase",
                    color: "rgba(255,255,255,0.25)",
                    marginBottom: "10px",
                  }}
                >
                  Just Unlocked State
                </p>

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    padding: "12px 14px",
                    borderRadius: "10px",
                    background: "rgba(61,186,116,0.07)",
                    border: "1.5px solid rgba(61,186,116,0.35)",
                  }}
                >
                  <div
                    style={{
                      width: "36px",
                      height: "36px",
                      borderRadius: "50%",
                      background: "rgba(61,186,116,0.18)",
                      border: "1.5px solid rgba(61,186,116,0.4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: "16px",
                      flexShrink: 0,
                    }}
                  >
                    🎉
                  </div>

                  <div style={{ flex: 1 }}>
                    <p
                      style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontWeight: 700,
                        fontSize: "13px",
                        color: "#3dba74",
                        margin: "0 0 2px",
                      }}
                    >
                      Langkah baru terbuka!
                    </p>

                    <p
                      style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "11px",
                        color: "rgba(61,186,116,0.7)",
                        margin: 0,
                      }}
                    >
                      DOM Manipulation · siap dimulai
                    </p>
                  </div>

                  <button
                    onClick={() => navigate("/action-plan")}
                    style={{
                      padding: "8px 18px",
                      borderRadius: "8px",
                      border: "none",
                      background: "#3dba74",
                      color: "white",
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "13px",
                      fontWeight: 600,
                      cursor: "pointer",
                      flexShrink: 0,
                    }}
                  >
                    Mulai →
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

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

        @media (max-width: 900px) {
          div[style*="grid-template-columns: 1fr 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}