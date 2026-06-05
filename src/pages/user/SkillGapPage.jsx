// src/pages/user/SkillGapPage.jsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";

const ProgressBar = ({ pct, color }) => (
  <div
    style={{
      flex: 1,
      height: "4px",
      borderRadius: "999px",
      background: "rgba(255,255,255,0.08)",
      overflow: "hidden",
    }}
  >
    <div
      style={{
        height: "100%",
        width: `${Math.min(Math.max(pct || 0, 0), 100)}%`,
        borderRadius: "999px",
        background: color,
        transition: "width 0.8s ease",
      }}
    />
  </div>
);

const parseLocalAssessmentResult = () => {
  try {
    const saved = localStorage.getItem("lastAssessmentResult");
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
};

const getSkillName = (skill) => {
  if (typeof skill === "string") return skill;

  return (
    skill?.skill_name ||
    skill?.name ||
    skill?.skillId ||
    skill?.skill_id ||
    "Skill"
  );
};

const getSkillProgress = (skill, fallback = 0) => {
  if (typeof skill === "string") return fallback;

  if (typeof skill?.progress === "number") return skill.progress;
  if (typeof skill?.score === "number") return skill.score;
  if (typeof skill?.level === "number") return skill.level * 50;

  return fallback;
};

const normalizeSkillItem = (skill, fallbackPct = 0) => ({
  name: getSkillName(skill),
  pct: getSkillProgress(skill, fallbackPct),
  priority: typeof skill === "object" ? skill?.priority : undefined,
  reason: typeof skill === "object" ? skill?.reason : undefined,
  evidence: typeof skill === "object" ? skill?.evidence || [] : [],
  nextTaskId: typeof skill === "object" ? skill?.next_task_id : undefined,
});

const normalizeSkillGapData = (apiData, localData) => {
  const source = apiData || localData || {};

  const ai =
    source.ai ||
    source.rawAi ||
    source.assessmentAi ||
    localData?.ai ||
    {};

  const aiSkillGap = ai.skill_gap || source.skill_gap || {};
  const aiAnalysis =
    ai.validated_context?.validated_analysis ||
    source.analysis ||
    {};

  const targetRole =
    source.targetRole ||
    source.target_role ||
    source.analysis?.role ||
    aiAnalysis.target_role ||
    aiSkillGap.target_role ||
    "Belum ditentukan";

  const confidenceScore =
    source.confidenceScore ||
    source.confidence_score ||
    source.analysis?.confidence ||
    aiAnalysis.confidence_score ||
    0;

  const missingRaw =
    aiSkillGap.missing_skills ||
    source.missingSkills ||
    source.missing_skills ||
    source.skillGap ||
    source.skill_gap ||
    localData?.skillGap ||
    [];

  const weakRaw =
    aiSkillGap.weak_skills ||
    source.weakSkills ||
    source.weak_skills ||
    [];

  const ownedRaw =
    aiSkillGap.owned_skills ||
    source.ownedSkills ||
    source.owned_skills ||
    [];

  const missingSkills = Array.isArray(missingRaw)
    ? missingRaw.map((skill) => normalizeSkillItem(skill, 0))
    : [];

  const weakSkills = Array.isArray(weakRaw)
    ? weakRaw.map((skill) => normalizeSkillItem(skill, 50))
    : [];

  const ownedSkills = Array.isArray(ownedRaw)
    ? ownedRaw.map((skill) => normalizeSkillItem(skill, 100))
    : [];

  return {
    targetRole,
    confidenceScore,
    problemCategory:
      aiSkillGap.problem_category ||
      source.problemCategory ||
      source.problem_category ||
      source.analysis?.problemCategory ||
      "Skill Gap",
    blockerType:
      aiSkillGap.blocker_type ||
      source.analysis?.blockerType ||
      null,
    readinessScore:
      aiSkillGap.readiness_score ??
      source.readinessScore ??
      0,
    priorityGap:
      aiSkillGap.priority_gap ||
      source.priorityGap ||
      null,
    summary:
      source.analysis?.summary ||
      aiAnalysis.summary ||
      "",
    missingSkills,
    weakSkills,
    ownedSkills,
    raw: source,
  };
};

export default function SkillGapPage() {
  const navigate = useNavigate();

  const [skillGapData, setSkillGapData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSkillGap = async () => {
      try {
        const res = await api.get("/skill-gap/me");
        setSkillGapData(res.data.data);
      } catch (error) {
        console.log(error.response?.data || error.message);

        const localResult = parseLocalAssessmentResult();

        if (localResult) {
          setSkillGapData(localResult);
          toast("Menampilkan skill gap dari hasil assessment terakhir.");
        } else {
          toast.error(
            error.response?.data?.message ||
              "Gagal mengambil data skill gap"
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchSkillGap();
  }, []);

  const localAssessmentResult = useMemo(() => {
    return parseLocalAssessmentResult();
  }, []);

  const normalized = useMemo(() => {
    return normalizeSkillGapData(skillGapData, localAssessmentResult);
  }, [skillGapData, localAssessmentResult]);

  const {
    targetRole,
    confidenceScore,
    problemCategory,
    blockerType,
    readinessScore,
    priorityGap,
    summary,
    missingSkills,
    weakSkills,
    ownedSkills,
  } = normalized;

  const handleCreateLearningPath = () => {
    navigate("/action-plan");
  };

  const handleExportPDF = () => {
    toast("Fitur export PDF akan dibuat nanti.");
  };

  const handleBack = () => {
    navigate("/dashboardUser");
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
        Memuat skill gap...
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
            border: "1.5px solid rgba(255,255,255,0.2)",
            background: "rgba(255,255,255,0.07)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.8)",
            fontWeight: 500,
          }}
        >
          Gap Skill Analysis
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
          Kembali
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
            maxWidth: "720px",
            animation: "slideUp 0.6s ease both",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: "28px" }}>
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
                fontSize: "24px",
                margin: "0 auto 14px",
              }}
            >
              🔍
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
                Skill Gap
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
              Ini adalah skill yang perlu diperkuat untuk menjadi{" "}
              <span style={{ color: "#3dba74", fontWeight: 600 }}>
                {targetRole}
              </span>
              .
            </p>

            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "10px",
                flexWrap: "wrap",
                marginTop: "10px",
              }}
            >
              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.45)",
                  background: "rgba(255,255,255,0.06)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "999px",
                  padding: "5px 12px",
                }}
              >
                Confidence: {confidenceScore}%
              </span>

              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.45)",
                  background: "rgba(255,255,255,0.06)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "999px",
                  padding: "5px 12px",
                }}
              >
                Readiness: {readinessScore}%
              </span>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            {[
              {
                icon: "✕",
                label: "MISSING",
                count: missingSkills.length,
                color: "#e05a5a",
              },
              {
                icon: "=",
                label: "WEAK",
                count: weakSkills.length,
                color: "#d4a844",
              },
              {
                icon: "✓",
                label: "OWNED",
                count: ownedSkills.length,
                color: "#3dba74",
              },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  padding: "14px 18px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}
              >
                <div
                  style={{
                    width: "28px",
                    height: "28px",
                    borderRadius: "50%",
                    background: item.color,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "white",
                    fontWeight: 700,
                  }}
                >
                  {item.icon}
                </div>

                <div>
                  <p
                    style={{
                      fontSize: "10px",
                      opacity: 0.5,
                      margin: 0,
                    }}
                  >
                    {item.label}
                  </p>

                  <p
                    style={{
                      margin: 0,
                      color: item.color,
                      fontSize: "22px",
                      fontFamily: "'Playfair Display', serif",
                      fontWeight: 700,
                    }}
                  >
                    {item.count}
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "14px",
              padding: "16px 18px",
              marginBottom: "12px",
            }}
          >
            <p
              style={{
                color: "#3dba74",
                margin: "0 0 8px",
                fontWeight: 700,
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
              }}
            >
              Ringkasan AI
            </p>

            <p
              style={{
                margin: 0,
                color: "rgba(255,255,255,0.58)",
                fontSize: "13px",
                lineHeight: 1.7,
              }}
            >
              Problem Category:{" "}
              <span style={{ color: "rgba(255,255,255,0.82)" }}>
                {problemCategory}
              </span>
              {blockerType ? (
                <>
                  {" "}
                  · Blocker:{" "}
                  <span style={{ color: "rgba(255,255,255,0.82)" }}>
                    {blockerType}
                  </span>
                </>
              ) : null}
              {priorityGap ? (
                <>
                  {" "}
                  · Prioritas:{" "}
                  <span style={{ color: "#3dba74" }}>
                    {priorityGap}
                  </span>
                </>
              ) : null}
            </p>

            {summary && (
              <p
                style={{
                  margin: "8px 0 0",
                  color: "rgba(255,255,255,0.42)",
                  fontSize: "12px",
                  lineHeight: 1.6,
                }}
              >
                {summary}
              </p>
            )}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "12px",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "14px",
                padding: "16px 18px",
              }}
            >
              <p
                style={{
                  color: "#e05a5a",
                  margin: "0 0 10px",
                  fontWeight: 700,
                }}
              >
                Missing Skills
              </p>

              {missingSkills.length > 0 ? (
                missingSkills.map((skill) => (
                  <div key={skill.name} style={{ marginBottom: "14px" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: "10px",
                        fontSize: "13px",
                        marginBottom: "6px",
                      }}
                    >
                      <span>{skill.name}</span>
                      <span>{skill.pct}%</span>
                    </div>

                    <ProgressBar pct={skill.pct} color="#e05a5a" />

                    <div
                      style={{
                        display: "flex",
                        gap: "6px",
                        flexWrap: "wrap",
                        marginTop: "7px",
                      }}
                    >
                      {skill.priority && (
                        <span
                          style={{
                            fontSize: "10px",
                            color: "#e05a5a",
                            background: "rgba(224,90,90,0.12)",
                            border: "1px solid rgba(224,90,90,0.25)",
                            padding: "3px 8px",
                            borderRadius: "999px",
                          }}
                        >
                          {skill.priority}
                        </span>
                      )}

                      {skill.nextTaskId && (
                        <span
                          style={{
                            fontSize: "10px",
                            color: "rgba(255,255,255,0.55)",
                            background: "rgba(255,255,255,0.07)",
                            border: "1px solid rgba(255,255,255,0.12)",
                            padding: "3px 8px",
                            borderRadius: "999px",
                          }}
                        >
                          Next: {skill.nextTaskId}
                        </span>
                      )}
                    </div>

                    {skill.reason && (
                      <p
                        style={{
                          margin: "7px 0 0",
                          fontSize: "11px",
                          lineHeight: 1.5,
                          color: "rgba(255,255,255,0.38)",
                        }}
                      >
                        {skill.reason}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p
                  style={{
                    fontSize: "12px",
                    color: "rgba(255,255,255,0.45)",
                    lineHeight: 1.6,
                  }}
                >
                  Tidak ada missing skill dari hasil AI.
                </p>
              )}
            </div>

            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "14px",
                padding: "16px 18px",
              }}
            >
              <p
                style={{
                  color: "#d4a844",
                  margin: "0 0 10px",
                  fontWeight: 700,
                }}
              >
                Weak Skills
              </p>

              {weakSkills.length > 0 ? (
                weakSkills.map((skill) => (
                  <div key={skill.name} style={{ marginBottom: "14px" }}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: "10px",
                        fontSize: "13px",
                        marginBottom: "6px",
                      }}
                    >
                      <span>{skill.name}</span>
                      <span>{skill.pct}%</span>
                    </div>

                    <ProgressBar pct={skill.pct} color="#d4a844" />

                    {skill.reason && (
                      <p
                        style={{
                          margin: "7px 0 0",
                          fontSize: "11px",
                          lineHeight: 1.5,
                          color: "rgba(255,255,255,0.38)",
                        }}
                      >
                        {skill.reason}
                      </p>
                    )}
                  </div>
                ))
              ) : (
                <p
                  style={{
                    fontSize: "12px",
                    color: "rgba(255,255,255,0.45)",
                    lineHeight: 1.6,
                  }}
                >
                  Belum ada weak skill dari hasil AI. Untuk assessment awal,
                  AI menandai skill sebagai missing sampai task pertama
                  berhasil divalidasi.
                </p>
              )}
            </div>
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(61,186,116,0.2)",
              borderRadius: "14px",
              padding: "16px 18px",
              marginBottom: "24px",
            }}
          >
            <p
              style={{
                color: "#3dba74",
                margin: "0 0 10px",
                fontWeight: 700,
              }}
            >
              Skill yang Sudah Kamu Miliki
            </p>

            {ownedSkills.length > 0 ? (
              ownedSkills.map((skill) => (
                <div
                  key={skill.name}
                  style={{
                    fontSize: "13px",
                    color: "rgba(255,255,255,0.75)",
                    marginBottom: "8px",
                  }}
                >
                  ✓ {skill.name}
                </div>
              ))
            ) : (
              <p
                style={{
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.45)",
                  lineHeight: 1.6,
                  margin: 0,
                }}
              >
                Belum ada owned skill yang tervalidasi. Skill akan masuk ke
                bagian ini setelah task dinilai passed oleh AI.
              </p>
            )}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto",
              gap: "12px",
            }}
          >
            <button
              onClick={handleCreateLearningPath}
              style={{
                padding: "14px 16px",
                borderRadius: "12px",
                border: "1px solid rgba(61,186,116,0.25)",
                background:
                  "linear-gradient(135deg, rgba(61,186,116,0.25), rgba(61,186,116,0.08))",
                color: "#3dba74",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.25s ease",
                letterSpacing: "0.2px",
                textDecoration: "underline",
                textDecorationColor: "rgba(61,186,116,0.25)",
                textUnderlineOffset: "3px",
                boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(61,186,116,0.35), rgba(61,186,116,0.12))";
                e.currentTarget.style.boxShadow =
                  "0 12px 30px rgba(0,0,0,0.25)";
                e.currentTarget.style.color = "white";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.background =
                  "linear-gradient(135deg, rgba(61,186,116,0.25), rgba(61,186,116,0.08))";
                e.currentTarget.style.boxShadow =
                  "0 8px 20px rgba(0,0,0,0.15)";
                e.currentTarget.style.color = "#3dba74";
              }}
            >
              Buka Learning Path →
            </button>

            <button
              onClick={handleExportPDF}
              style={{
                padding: "14px 22px",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.15)",
                background: "rgba(255,255,255,0.05)",
                color: "rgba(255,255,255,0.75)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.25s ease",
                letterSpacing: "0.2px",
                backdropFilter: "blur(8px)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background =
                  "rgba(255,255,255,0.12)";
                e.currentTarget.style.color = "white";
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.boxShadow =
                  "0 10px 25px rgba(0,0,0,0.2)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background =
                  "rgba(255,255,255,0.05)";
                e.currentTarget.style.color = "rgba(255,255,255,0.75)";
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "none";
              }}
            >
              Export PDF
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
          div[style*="grid-template-columns: 1fr 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1fr auto"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}