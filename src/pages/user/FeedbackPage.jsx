// src/pages/user/FeedbackPage.jsx

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";

const getBackendBaseUrl = () => {
  const baseURL = api.defaults.baseURL || "http://localhost:5000/api";
  return baseURL.replace(/\/api\/?$/, "");
};

const getFileUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;

  return `${getBackendBaseUrl()}${path}`;
};

const ScoreBar = ({ label, pct, color }) => (
  <div style={{ flex: 1, textAlign: "center", padding: "0 10px" }}>
    <p
      style={{
        fontFamily: "'DM Sans', sans-serif",
        fontSize: "11px",
        color: "rgba(60,80,70,0.5)",
        textTransform: "capitalize",
        marginBottom: "8px",
        letterSpacing: "0.03em",
      }}
    >
      {label}
    </p>

    <div
      style={{
        height: "4px",
        borderRadius: "999px",
        background: "rgba(0,0,0,0.08)",
        marginBottom: "8px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${pct}%`,
          borderRadius: "999px",
          background: color,
          transition: "width 1s ease",
        }}
      />
    </div>

    <p
      style={{
        fontFamily: "'Playfair Display', serif",
        fontWeight: 700,
        fontSize: "20px",
        color: "#1a3a2a",
        margin: 0,
      }}
    >
      {pct}%
    </p>
  </div>
);

export default function FeedbackPage() {
  const navigate = useNavigate();

  const [feedbackData, setFeedbackData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hasFeedback, setHasFeedback] = useState(true);

  useEffect(() => {
    const fetchFeedback = async () => {
      try {
        const res = await api.get("/feedback/me");
        setFeedbackData(res.data.data);
        setHasFeedback(Boolean(res.data.data));
      } catch (error) {
        console.log(error.response?.data || error.message);

        if (error.response?.status === 404) {
          setHasFeedback(false);
          return;
        }

        toast.error(
          error.response?.data?.message ||
            "Gagal mengambil feedback"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchFeedback();
  }, []);

  const handleDashboard = () => {
    navigate("/dashboardUser");
  };

  const handleActionPlan = () => {
    navigate("/action-plan");
  };

  const handleSubmitAgain = () => {
    navigate("/task-detail");
  };

  const handleImprove = () => {
    toast("Fitur perbaiki dengan AI akan dibuat nanti.");
    navigate("/task-detail");
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#0a1f12",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        Memuat feedback...
      </div>
    );
  }

  if (!hasFeedback || !feedbackData) {
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

          <button
            onClick={handleDashboard}
            style={{
              background: "transparent",
              border: "none",
              color: "rgba(255,255,255,0.55)",
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "13px",
              cursor: "pointer",
            }}
          >
            Dashboard
          </button>
        </nav>

        <div
          style={{
            position: "relative",
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "32px 24px 60px",
          }}
        >
          <div className="mesh-bg" />
          <StarField />

          <div
            style={{
              position: "relative",
              zIndex: 1,
              width: "100%",
              maxWidth: "560px",
              background: "rgba(255,255,255,0.94)",
              borderRadius: "18px",
              padding: "30px",
              textAlign: "center",
              color: "#1a3a2a",
              animation: "slideUp 0.5s ease both",
            }}
          >
            <div
              style={{
                width: "62px",
                height: "62px",
                borderRadius: "50%",
                background: "rgba(61,186,116,0.14)",
                border: "1.5px solid rgba(61,186,116,0.32)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto 16px",
                fontSize: "26px",
              }}
            >
              💬
            </div>

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: "28px",
                margin: "0 0 8px",
                color: "#1a3a2a",
              }}
            >
              Belum Ada Feedback
            </h1>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                color: "rgba(40,70,55,0.65)",
                lineHeight: 1.7,
                margin: "0 0 22px",
              }}
            >
              Kamu belum memiliki feedback karena belum ada task yang
              disubmit. Mulai dari action plan, kerjakan task, lalu submit
              agar feedback bisa muncul di sini.
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px",
              }}
            >
              <button
                onClick={handleActionPlan}
                style={{
                  padding: "13px 16px",
                  borderRadius: "12px",
                  border: "none",
                  background: "#2d8c5e",
                  color: "white",
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Buka Action Plan →
              </button>

              <button
                onClick={handleDashboard}
                style={{
                  padding: "13px 16px",
                  borderRadius: "12px",
                  border: "1px solid rgba(45,140,94,0.28)",
                  background: "transparent",
                  color: "#2d8c5e",
                  fontFamily: "'DM Sans', sans-serif",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>

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

          @media (max-width: 640px) {
            div[style*="grid-template-columns: 1fr 1fr"] {
              grid-template-columns: 1fr !important;
            }
          }
        `}</style>
      </div>
    );
  }

  const score = feedbackData?.feedback?.score || 0;

  const data = {
    breadcrumb: ["Action Plan", "Task Detail", "Feedback"],
    status: feedbackData?.status || "revision",
    summary: {
      title:
        feedbackData?.status === "passed"
          ? "Passed!"
          : "Need Revision",
      desc:
        feedbackData?.status === "passed"
          ? "Selamat! Task kamu sudah memenuhi kriteria."
          : "Ada beberapa hal yang perlu diperbaiki sebelum lanjut ke langkah berikutnya.",
      xp: feedbackData?.status === "passed" ? 120 : 60,
    },
    strengths: feedbackData?.feedback?.strengths || [],
    weaknesses: feedbackData?.feedback?.weaknesses || [],
    suggestions: feedbackData?.feedback?.suggestions || [],
    scores: {
      ketepatan: score,
      kelengkapan: Math.max(score - 7, 0),
      kualitas: Math.min(score + 6, 100),
    },
  };

  const isPassed = data.status === "passed";
  const submittedFileUrl = getFileUrl(feedbackData?.fileUrl);

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
            padding: "6px 20px",
            borderRadius: "999px",
            border: "1.5px solid rgba(61,186,116,0.5)",
            background: "rgba(61,186,116,0.1)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.85)",
            fontWeight: 500,
          }}
        >
          Hasil Evaluasi
        </div>

        <button
          onClick={handleDashboard}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.55)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            cursor: "pointer",
          }}
        >
          Dashboard
        </button>
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
            maxWidth: "680px",
            animation: "slideUp 0.5s ease both",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              marginBottom: "14px",
              flexWrap: "wrap",
            }}
          >
            {data.breadcrumb.map((crumb, index) => (
              <span
                key={crumb}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                {index > 0 && (
                  <span
                    style={{
                      color: "rgba(255,255,255,0.25)",
                      fontSize: "12px",
                    }}
                  >
                    →
                  </span>
                )}

                <span
                  onClick={() => {
                    if (index === 0) navigate("/action-plan");
                    if (index === 1) navigate("/task-detail");
                  }}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "12px",
                    color:
                      index === data.breadcrumb.length - 1
                        ? "rgba(255,255,255,0.85)"
                        : "rgba(255,255,255,0.4)",
                    cursor:
                      index < data.breadcrumb.length - 1
                        ? "pointer"
                        : "default",
                    textDecoration:
                      index < data.breadcrumb.length - 1
                        ? "underline"
                        : "none",
                    textDecorationColor: "rgba(255,255,255,0.2)",
                    textUnderlineOffset: "3px",
                  }}
                >
                  {crumb}
                </span>
              </span>
            ))}
          </div>

          <div
            style={{
              background: isPassed
                ? "rgba(235,255,245,0.95)"
                : "rgba(255,248,230,0.95)",
              border: isPassed
                ? "1px solid rgba(61,186,116,0.4)"
                : "1px solid rgba(212,168,68,0.4)",
              borderRadius: "14px",
              padding: "18px 20px",
              display: "flex",
              alignItems: "flex-start",
              gap: "14px",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                width: "42px",
                height: "42px",
                borderRadius: "50%",
                background: isPassed
                  ? "rgba(61,186,116,0.2)"
                  : "rgba(212,168,68,0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "20px",
                flexShrink: 0,
              }}
            >
              {isPassed ? "🎉" : "💬"}
            </div>

            <div style={{ flex: 1 }}>
              <p
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "18px",
                  color: isPassed ? "#2d8c5e" : "#b87a00",
                  textDecoration: "underline",
                  textDecorationColor: isPassed
                    ? "rgba(45,140,94,0.3)"
                    : "rgba(184,122,0,0.35)",
                  textUnderlineOffset: "3px",
                  margin: "0 0 4px",
                }}
              >
                {data.summary.title}
              </p>

              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "13px",
                  color: isPassed
                    ? "rgba(30,80,55,0.7)"
                    : "rgba(100,70,0,0.7)",
                  margin: 0,
                  lineHeight: 1.6,
                }}
              >
                {data.summary.desc}
              </p>
            </div>

            <span
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "12px",
                fontWeight: 600,
                color: isPassed ? "#2d8c5e" : "#b87a00",
                background: isPassed
                  ? "rgba(45,140,94,0.12)"
                  : "rgba(212,168,68,0.15)",
                padding: "4px 10px",
                borderRadius: "999px",
                flexShrink: 0,
              }}
            >
              +{data.summary.xp} XP
            </span>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "10px",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.93)",
                borderRadius: "14px",
                padding: "16px 18px",
              }}
            >
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 700,
                  color: "#2d8c5e",
                  margin: "0 0 12px",
                }}
              >
                ● Strengths
              </p>

              {data.strengths.map((item, index) => (
                <p
                  key={index}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "12px",
                    color: "#2a4a38",
                    margin: "0 0 8px",
                    lineHeight: 1.55,
                  }}
                >
                  ✓ {item}
                </p>
              ))}
            </div>

            <div
              style={{
                background: "rgba(255,255,255,0.93)",
                borderRadius: "14px",
                padding: "16px 18px",
              }}
            >
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 700,
                  color: "#c04040",
                  margin: "0 0 12px",
                }}
              >
                ● Weakness
              </p>

              {data.weaknesses.map((item, index) => (
                <p
                  key={index}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "12px",
                    color: "#2a4a38",
                    margin: "0 0 8px",
                    lineHeight: 1.55,
                  }}
                >
                  ✕ {item}
                </p>
              ))}
            </div>
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.93)",
              borderRadius: "14px",
              padding: "16px 20px",
              marginBottom: "10px",
            }}
          >
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 700,
                color: "#1a3a2a",
                margin: "0 0 12px",
              }}
            >
              ● Saran Perbaikan
            </p>

            {data.suggestions.map((item, index) => (
              <p
                key={index}
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "13px",
                  color: "#2a4a38",
                  margin: "0 0 8px",
                  lineHeight: 1.6,
                }}
              >
                💡 {item}
              </p>
            ))}
          </div>

          {feedbackData?.fileUrl && (
            <div
              style={{
                background: "rgba(255,255,255,0.93)",
                borderRadius: "14px",
                padding: "16px 20px",
                marginBottom: "10px",
              }}
            >
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 700,
                  color: "#1a3a2a",
                  margin: "0 0 12px",
                }}
              >
                ● File Submission
              </p>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  padding: "12px 14px",
                  borderRadius: "10px",
                  background: "rgba(45,140,94,0.08)",
                  border: "1px solid rgba(45,140,94,0.18)",
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <p
                    style={{
                      margin: "0 0 4px",
                      fontSize: "13px",
                      fontWeight: 800,
                      color: "#1a3a2a",
                      wordBreak: "break-word",
                    }}
                  >
                    📎 {feedbackData.fileName || "File submission"}
                  </p>

                  <p
                    style={{
                      margin: 0,
                      fontSize: "12px",
                      color: "rgba(40,70,55,0.58)",
                    }}
                  >
                    Bukti file yang kamu upload saat submit task.
                  </p>
                </div>

                <a
                  href={submittedFileUrl}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    padding: "9px 13px",
                    borderRadius: "10px",
                    background: "#2d8c5e",
                    color: "white",
                    fontSize: "12px",
                    fontWeight: 800,
                    textDecoration: "none",
                    whiteSpace: "nowrap",
                  }}
                >
                  Lihat File →
                </a>
              </div>
            </div>
          )}

          <div
            style={{
              background: "rgba(255,255,255,0.93)",
              borderRadius: "14px",
              padding: "16px 20px",
              marginBottom: "20px",
            }}
          >
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 700,
                color: "#1a3a2a",
                margin: "0 0 16px",
              }}
            >
              ● Skor Evaluasi
            </p>

            <div
              style={{
                display: "flex",
                borderTop: "1px solid rgba(0,0,0,0.07)",
                paddingTop: "14px",
              }}
            >
              <ScoreBar
                label="Ketepatan"
                pct={data.scores.ketepatan}
                color="linear-gradient(90deg,#7c6fe0,#a89cf0)"
              />

              <ScoreBar
                label="Kelengkapan"
                pct={data.scores.kelengkapan}
                color="linear-gradient(90deg,#d4a844,#f0c85c)"
              />

              <ScoreBar
                label="Kualitas"
                pct={data.scores.kualitas}
                color="linear-gradient(90deg,#2d8c5e,#3dba74)"
              />
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: isPassed ? "1fr 1fr" : "1fr auto auto",
              gap: "12px",
            }}
          >
            {!isPassed && (
              <button
                onClick={handleImprove}
                style={{
                  padding: "14px",
                  borderRadius: "12px",
                  border: "none",
                  background: "rgba(255,255,255,0.1)",
                  color: "rgba(255,255,255,0.7)",
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 500,
                  cursor: "pointer",
                }}
              >
                Perbaiki dengan AI →
              </button>
            )}

            {!isPassed && (
              <button
                onClick={handleSubmitAgain}
                style={{
                  padding: "14px 22px",
                  borderRadius: "12px",
                  border: "1px solid rgba(255,255,255,0.2)",
                  background: "rgba(255,255,255,0.08)",
                  color: "rgba(255,255,255,0.8)",
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Submit Ulang
              </button>
            )}

            {isPassed && (
              <button
                onClick={handleActionPlan}
                style={{
                  padding: "14px 22px",
                  borderRadius: "12px",
                  border: "1px solid rgba(255,255,255,0.2)",
                  background: "rgba(255,255,255,0.08)",
                  color: "rgba(255,255,255,0.8)",
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "14px",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                Lihat Roadmap
              </button>
            )}

            <button
              onClick={handleDashboard}
              style={{
                padding: "14px 22px",
                borderRadius: "12px",
                border: "none",
                background: "#3dba74",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Dashboard
            </button>
          </div>
        </div>
      </div>

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

        @media (max-width: 760px) {
          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1fr auto auto"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}