// src/pages/user/ActionPlanPage.jsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";

const getStatusConfig = (step) => {
  if (step.isCompleted || step.status === "selesai") {
    return {
      label: "Selesai",
      icon: "✓",
      bg: "rgba(61,186,116,0.14)",
      border: "rgba(61,186,116,0.35)",
      color: "#3dba74",
      badgeBg: "rgba(61,186,116,0.16)",
      canStart: false,
    };
  }

  if (step.status === "revision") {
    return {
      label: "Perlu Revisi",
      icon: "!",
      bg: "rgba(212,168,68,0.1)",
      border: "rgba(212,168,68,0.35)",
      color: "#d4a844",
      badgeBg: "rgba(212,168,68,0.14)",
      canStart: true,
    };
  }

  if (step.status === "berjalan" || !step.isLocked) {
    return {
      label: "Sedang Berjalan",
      icon: "▶",
      bg: "rgba(61,186,116,0.08)",
      border: "rgba(61,186,116,0.28)",
      color: "#a8d8b8",
      badgeBg: "rgba(61,186,116,0.12)",
      canStart: true,
    };
  }

  return {
    label: "Terkunci",
    icon: "🔒",
    bg: "rgba(255,255,255,0.04)",
    border: "rgba(255,255,255,0.1)",
    color: "rgba(255,255,255,0.45)",
    badgeBg: "rgba(255,255,255,0.07)",
    canStart: false,
  };
};

export default function ActionPlanPage() {
  const navigate = useNavigate();

  const [actionPlan, setActionPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    const fetchActionPlan = async () => {
      try {
        const res = await api.get("/action-plans/me");
        const data = res.data.data;

        setActionPlan(data);

        const activeStep =
          data?.steps?.find(
            (step) =>
              step.status === "revision" ||
              step.status === "berjalan" ||
              (!step.isCompleted && !step.isLocked)
          ) ||
          data?.steps?.find((step) => !step.isCompleted) ||
          data?.steps?.[0] ||
          null;

        setExpanded(activeStep?.order || data?.steps?.[0]?.order || null);
      } catch (error) {
        console.log(error.response?.data || error.message);

        toast.error(
          error.response?.data?.message ||
            "Gagal mengambil action plan"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchActionPlan();
  }, []);

  const targetRole = actionPlan?.targetRole || "Belum ditentukan";
  const confidenceScore = actionPlan?.confidenceScore || 0;

  const steps = useMemo(() => {
    return actionPlan?.steps || [];
  }, [actionPlan]);

  const completedSteps = steps.filter(
    (step) => step.isCompleted || step.status === "selesai"
  ).length;

  const totalSteps = steps.length;

  const progressPct =
    totalSteps > 0
      ? Math.round((completedSteps / totalSteps) * 100)
      : 0;

  const activeStep = useMemo(() => {
    return (
      steps.find(
        (step) =>
          step.status === "revision" ||
          step.status === "berjalan" ||
          (!step.isCompleted && !step.isLocked)
      ) ||
      steps.find((step) => !step.isCompleted) ||
      null
    );
  }, [steps]);

  const allCompleted = totalSteps > 0 && completedSteps === totalSteps;

  const handleStartStep = (step) => {
    if (!step) {
      toast.error("Belum ada langkah yang bisa dimulai");
      return;
    }

    if (step.isCompleted || step.status === "selesai") {
      toast.success("Task ini sudah selesai.");
      return;
    }

    if (step.isLocked) {
      toast.error("Selesaikan langkah sebelumnya dulu.");
      return;
    }

    localStorage.setItem("activeTask", JSON.stringify(step));

    toast.success(`Mulai: ${step.title}`);
    navigate("/task-detail");
  };

  const handleStartCurrentStep = () => {
    if (allCompleted) {
      toast.success("Semua langkah sudah selesai. Mantap!");
      navigate("/dashboardUser");
      return;
    }

    handleStartStep(activeStep);
  };

  const handleGoDashboard = () => {
    navigate("/dashboardUser");
  };

  const handleBack = () => {
    navigate("/skill-gap");
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
        Memuat action plan...
      </div>
    );
  }

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
        }}
      >
        <Logo />

        <div
          style={{
            padding: "6px 20px",
            borderRadius: "999px",
            border: "1.5px solid rgba(255,255,255,0.25)",
            background: "rgba(255,255,255,0.08)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.85)",
            fontWeight: 500,
          }}
        >
          Action Plan
        </div>

        <button
          onClick={handleBack}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.55)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            cursor: "pointer",
          }}
        >
          Kembali ke Skill Gap
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
            maxWidth: "760px",
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
                width: "56px",
                height: "56px",
                borderRadius: "50%",
                background: "rgba(45,140,94,0.2)",
                border: "1.5px solid rgba(61,186,116,0.35)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "22px",
                margin: "0 auto 14px",
              }}
            >
              🗺️
            </div>

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(24px, 4vw, 32px)",
                margin: "0 0 10px",
              }}
            >
              <span
                style={{
                  color: "white",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(255,255,255,0.2)",
                  textUnderlineOffset: "4px",
                }}
              >
                Action Plan
              </span>{" "}
              <span style={{ color: "#3dba74" }}>Kamu</span>
            </h1>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(255,255,255,0.5)",
                lineHeight: 1.7,
                margin: 0,
              }}
            >
              Roadmap belajar personal untuk menjadi{" "}
              <span
                style={{
                  color: "#3dba74",
                  fontWeight: 600,
                }}
              >
                {targetRole}
              </span>
              .
            </p>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "12px",
                color: "rgba(255,255,255,0.35)",
                marginTop: "8px",
              }}
            >
              Confidence Score: {confidenceScore}%
            </p>
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "16px",
              padding: "18px 20px",
              marginBottom: "18px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "10px",
              }}
            >
              <div>
                <p
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "12px",
                    color: "rgba(255,255,255,0.45)",
                    margin: "0 0 4px",
                  }}
                >
                  Progress Action Plan
                </p>

                <p
                  style={{
                    fontFamily: "'Playfair Display', serif",
                    fontSize: "22px",
                    color: "#3dba74",
                    fontWeight: 700,
                    margin: 0,
                  }}
                >
                  {completedSteps}/{totalSteps} langkah
                </p>
              </div>

              <div
                style={{
                  width: "54px",
                  height: "54px",
                  borderRadius: "50%",
                  background: "rgba(61,186,116,0.12)",
                  border: "1.5px solid rgba(61,186,116,0.35)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#3dba74",
                  fontWeight: 700,
                  fontSize: "15px",
                }}
              >
                {progressPct}%
              </div>
            </div>

            <div
              style={{
                height: "6px",
                borderRadius: "999px",
                background: "rgba(255,255,255,0.08)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progressPct}%`,
                  borderRadius: "999px",
                  background:
                    "linear-gradient(90deg, #2d8c5e, #3dba74)",
                  transition: "width 0.8s ease",
                }}
              />
            </div>

            {allCompleted && (
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "12px",
                  color: "#3dba74",
                  margin: "12px 0 0",
                  fontWeight: 700,
                }}
              >
                🎉 Semua langkah sudah selesai.
              </p>
            )}
          </div>

          {steps.length === 0 && (
            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "16px",
                padding: "22px",
                textAlign: "center",
              }}
            >
              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  color: "rgba(255,255,255,0.6)",
                  margin: 0,
                }}
              >
                Action plan belum tersedia. Selesaikan assessment terlebih
                dahulu.
              </p>
            </div>
          )}

          {steps.map((step, index) => {
            const cfg = getStatusConfig(step);
            const isExpanded = expanded === step.order;

            return (
              <div
                key={step.order}
                style={{
                  display: "grid",
                  gridTemplateColumns: "42px 1fr",
                  gap: "12px",
                  marginBottom: "12px",
                  position: "relative",
                }}
              >
                <div
                  style={{
                    position: "relative",
                    display: "flex",
                    justifyContent: "center",
                  }}
                >
                  {index < steps.length - 1 && (
                    <div
                      style={{
                        position: "absolute",
                        top: "42px",
                        bottom: "-16px",
                        width: "2px",
                        background: step.isCompleted
                          ? "rgba(61,186,116,0.4)"
                          : "rgba(61,186,116,0.18)",
                      }}
                    />
                  )}

                  <div
                    style={{
                      width: "34px",
                      height: "34px",
                      borderRadius: "50%",
                      background: cfg.color,
                      border: `2px solid ${cfg.border}`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "white",
                      fontWeight: 700,
                      fontSize: "13px",
                      position: "relative",
                      zIndex: 1,
                    }}
                  >
                    {cfg.icon}
                  </div>
                </div>

                <div
                  onClick={() =>
                    setExpanded(isExpanded ? null : step.order)
                  }
                  style={{
                    background: cfg.bg,
                    border: `1px solid ${cfg.border}`,
                    borderRadius: "14px",
                    padding: "15px 18px",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: "12px",
                      alignItems: "flex-start",
                    }}
                  >
                    <div>
                      <p
                        style={{
                          fontFamily: "'DM Sans', sans-serif",
                          fontWeight: 700,
                          fontSize: "14px",
                          color: step.isCompleted
                            ? "#3dba74"
                            : "rgba(255,255,255,0.9)",
                          margin: "0 0 6px",
                          textDecoration: "underline",
                          textDecorationColor: "rgba(255,255,255,0.18)",
                          textUnderlineOffset: "3px",
                        }}
                      >
                        {step.title}
                      </p>

                      <p
                        style={{
                          fontFamily: "'DM Sans', sans-serif",
                          fontSize: "12px",
                          color: "rgba(255,255,255,0.45)",
                          margin: 0,
                        }}
                      >
                        Estimasi {step.estimatedDays} hari
                      </p>
                    </div>

                    <span
                      style={{
                        fontFamily: "'DM Sans', sans-serif",
                        fontSize: "11px",
                        color: cfg.color,
                        background: cfg.badgeBg,
                        padding: "4px 10px",
                        borderRadius: "999px",
                        border: `1px solid ${cfg.border}`,
                        flexShrink: 0,
                      }}
                    >
                      {cfg.label}
                    </span>
                  </div>

                  {isExpanded && (
                    <div
                      style={{
                        marginTop: "12px",
                        paddingTop: "12px",
                        borderTop: "1px solid rgba(255,255,255,0.08)",
                      }}
                    >
                      <p
                        style={{
                          fontFamily: "'DM Sans', sans-serif",
                          fontSize: "12px",
                          color: "rgba(255,255,255,0.55)",
                          lineHeight: 1.7,
                          margin: "0 0 12px",
                        }}
                      >
                        {step.description}
                      </p>

                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: "10px",
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            gap: "6px",
                            flexWrap: "wrap",
                          }}
                        >
                          <span
                            style={{
                              fontFamily: "'DM Sans', sans-serif",
                              fontSize: "11px",
                              color: "rgba(255,255,255,0.55)",
                              background: "rgba(255,255,255,0.07)",
                              border:
                                "1px solid rgba(255,255,255,0.12)",
                              padding: "3px 8px",
                              borderRadius: "6px",
                            }}
                          >
                            Step {step.order}
                          </span>

                          <span
                            style={{
                              fontFamily: "'DM Sans', sans-serif",
                              fontSize: "11px",
                              color: "rgba(255,255,255,0.55)",
                              background: "rgba(255,255,255,0.07)",
                              border:
                                "1px solid rgba(255,255,255,0.12)",
                              padding: "3px 8px",
                              borderRadius: "6px",
                            }}
                          >
                            {step.estimatedDays} hari
                          </span>
                        </div>

                        {cfg.canStart && (
                          <button
                            onClick={(event) => {
                              event.stopPropagation();
                              handleStartStep(step);
                            }}
                            style={{
                              padding: "8px 16px",
                              borderRadius: "9px",
                              border: "none",
                              background:
                                step.status === "revision"
                                  ? "#d4a844"
                                  : "#3dba74",
                              color: "white",
                              fontFamily: "'DM Sans', sans-serif",
                              fontSize: "12px",
                              fontWeight: 600,
                              cursor: "pointer",
                            }}
                          >
                            {step.status === "revision"
                              ? "Submit Ulang →"
                              : "Mulai →"}
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto",
              gap: "12px",
              marginTop: "18px",
            }}
          >
            <button
              onClick={handleStartCurrentStep}
              style={{
                padding: "14px",
                borderRadius: "12px",
                border: "1px solid rgba(61,186,116,0.25)",
                background: allCompleted
                  ? "rgba(61,186,116,0.16)"
                  : "linear-gradient(135deg, rgba(61,186,116,0.25), rgba(61,186,116,0.08))",
                color: "#3dba74",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
                textDecoration: "underline",
                textDecorationColor: "rgba(61,186,116,0.25)",
                textUnderlineOffset: "3px",
              }}
            >
              {allCompleted
                ? "Semua Langkah Selesai ✓"
                : activeStep?.status === "revision"
                ? "Submit Ulang Task →"
                : "Lanjutkan Langkah Sekarang →"}
            </button>

            <button
              onClick={handleGoDashboard}
              style={{
                padding: "14px 24px",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.2)",
                background: "rgba(255,255,255,0.07)",
                color: "rgba(255,255,255,0.75)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 500,
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
          div[style*="grid-template-columns: 42px 1fr"] {
            grid-template-columns: 34px 1fr !important;
          }

          div[style*="grid-template-columns: 1fr auto"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}