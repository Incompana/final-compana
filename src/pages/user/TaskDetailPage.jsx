// src/pages/user/TaskDetailPage.jsx

import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import api from "../../api/axios";
import toast from "react-hot-toast";

const SectionDot = ({ color = "#3dba74" }) => (
  <span
    style={{
      width: "8px",
      height: "8px",
      borderRadius: "50%",
      background: color,
      display: "inline-block",
      flexShrink: 0,
      marginRight: "8px",
    }}
  />
);

const SectionLabel = ({ children, color = "#3dba74" }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      marginBottom: "12px",
    }}
  >
    <SectionDot color={color} />

    <span
      style={{
        fontFamily: "'DM Sans', sans-serif",
        fontSize: "10px",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        color: "rgba(255,255,255,0.4)",
        fontWeight: 600,
      }}
    >
      {children}
    </span>
  </div>
);

const sectionCard = {
  background: "rgba(255,255,255,0.04)",
  border: "1px solid rgba(255,255,255,0.09)",
  borderRadius: "14px",
  padding: "16px 20px",
  marginBottom: "10px",
};

const getMainSkillFromTitle = (title = "") => {
  return title.replace("Pelajari", "").trim().split(" ")[0] || "Skill";
};

const getFileSizeText = (size) => {
  if (!size) return "";

  const kb = size / 1024;
  const mb = kb / 1024;

  if (mb >= 1) {
    return `${mb.toFixed(2)} MB`;
  }

  return `${Math.round(kb)} KB`;
};

const buildTaskData = (step, totalSteps) => {
  const skill = getMainSkillFromTitle(step?.title);

  return {
    breadcrumb: ["Action Plan", `Langkah ${step?.order || 1}`],
    phase: "ROADMAP PERSONAL",
    title: step?.title || "Task Belajar",
    tags: [skill, "Practice"],
    duration: `${step?.estimatedDays || 3} hari`,
    xp: 80 + (step?.order || 1) * 20,
    currentStep: step?.order || 1,
    totalSteps: totalSteps || 1,
    sections: {
      deskripsi:
        step?.description ||
        "Pelajari skill ini sebagai bagian dari roadmap personalmu.",
      yangHarusDikerjakan: [
        `Pelajari konsep dasar ${skill} dari dokumentasi atau referensi terpercaya.`,
        `Buat latihan kecil atau mini project sederhana menggunakan ${skill}.`,
        "Upload bukti pengerjaan. Untuk project, upload ZIP source code tanpa node_modules.",
        "Catatan tambahan boleh diisi untuk menjelaskan isi file, kendala, atau hasil pengerjaan.",
      ],
      expectedOutput: [
        {
          icon: "🗂️",
          text: "ZIP project/source code untuk bukti paling kuat.",
        },
        {
          icon: "📄",
          text: "PDF/TXT untuk laporan atau catatan pengerjaan.",
        },
        {
          icon: "🖼️",
          text: "Screenshot/gambar untuk bukti visual hasil latihan.",
        },
      ],
      referensiBelajar: [
        {
          icon: "🤖",
          text: "Tanya Compana AI untuk penjelasan yang lebih mudah.",
          isExternal: false,
        },
        {
          icon: "📘",
          text: `Cari dokumentasi resmi atau tutorial dasar ${skill}.`,
          isExternal: true,
        },
        {
          icon: "▶️",
          text: `Cari video pembelajaran ${skill} untuk pemula.`,
          isExternal: true,
        },
      ],
    },
  };
};

export default function TaskDetailPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [actionPlan, setActionPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submittedResult, setSubmittedResult] = useState(null);

  useEffect(() => {
    const fetchActionPlan = async () => {
      try {
        const res = await api.get("/action-plans/me");
        setActionPlan(res.data.data);
      } catch (error) {
        console.log(error.response?.data || error.message);

        toast.error(
          error.response?.data?.message || "Gagal mengambil detail task"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchActionPlan();
  }, []);

  const steps = useMemo(() => {
    return actionPlan?.steps || [];
  }, [actionPlan]);

  const activeStep = useMemo(() => {
    const savedActiveTask = localStorage.getItem("activeTask");

    if (savedActiveTask) {
      try {
        return JSON.parse(savedActiveTask);
      } catch {
        localStorage.removeItem("activeTask");
      }
    }

    return (
      steps.find(
        (step) =>
          step.status === "revision" ||
          step.status === "berjalan" ||
          (!step.isCompleted && !step.isLocked)
      ) ||
      steps.find((step) => !step.isCompleted) ||
      steps[0] ||
      null
    );
  }, [steps]);

  const data = useMemo(() => {
    return buildTaskData(activeStep, steps.length);
  }, [activeStep, steps.length]);

  const validateAndSetFile = (selectedFile) => {
    if (!selectedFile) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
      "application/pdf",
      "text/plain",
      "application/zip",
      "application/x-zip-compressed",
    ];

    const allowedExtensions = [".jpg", ".jpeg", ".png", ".webp", ".pdf", ".txt", ".zip"];

    const lowerName = selectedFile.name.toLowerCase();

    const isAllowedByType = allowedTypes.includes(selectedFile.type);
    const isAllowedByExtension = allowedExtensions.some((ext) =>
      lowerName.endsWith(ext)
    );

    if (!isAllowedByType && !isAllowedByExtension) {
      toast.error("File harus berupa gambar, PDF, TXT, atau ZIP");
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      toast.error("Ukuran file maksimal 10MB");
      return;
    }

    setFile(selectedFile);
  };

  const handleFileDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);

    const selectedFile =
      event.dataTransfer?.files?.[0] || event.target?.files?.[0];

    validateAndSetFile(selectedFile);
  };

  const handleBack = () => {
    navigate("/action-plan");
  };

  const handleSubmit = async () => {
    if (!file && !notes.trim()) {
      toast.error("Tambahkan file atau catatan terlebih dahulu.");
      return;
    }

    try {
      setSubmitting(true);

      const formData = new FormData();

      formData.append("taskTitle", data.title);
      formData.append("taskDescription", data.sections.deskripsi);
      formData.append("targetRole", actionPlan?.targetRole || "");
      formData.append("content", notes.trim());

      if (file) {
        formData.append("file", file);
      }

      const res = await api.post("/submissions/submit", formData);
      const result = res.data.data;
      const submittedStatus = result?.submission?.status;

      localStorage.setItem("lastSubmissionResult", JSON.stringify(result));
      localStorage.removeItem("activeTask");

      setSubmittedResult(result);

      setActionPlan((prev) => {
        if (!prev?.steps) return prev;

        return {
          ...prev,
          steps: prev.steps.map((step) => {
            const isSubmittedStep =
              step.taskId === activeStep?.taskId ||
              step.id === activeStep?.id ||
              step.title === activeStep?.title;

            if (!isSubmittedStep) return step;

            return {
              ...step,
              isCompleted: submittedStatus === "passed",
              status:
                submittedStatus === "passed"
                  ? "selesai"
                  : submittedStatus === "revision"
                  ? "revision"
                  : step.status,
              isLocked: false,
            };
          }),
        };
      });

      setFile(null);
      setNotes("");

      toast.success(
        submittedStatus === "passed"
          ? "Task selesai dan berhasil dinilai AI."
          : "Task berhasil disubmit. Silakan cek feedback revisi."
      );
    } catch (error) {
      console.log(error.response?.data || error.message);

      toast.error(error.response?.data?.message || "Gagal submit task");
    } finally {
      setSubmitting(false);
    }
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
        Memuat detail task...
      </div>
    );
  }

  if (!activeStep) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#0a1f12",
          color: "white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
          gap: "14px",
          fontFamily: "'DM Sans', sans-serif",
        }}
      >
        <p>Belum ada task aktif.</p>

        <button
          onClick={() => navigate("/action-plan")}
          style={{
            padding: "10px 18px",
            borderRadius: "10px",
            border: "none",
            background: "#3dba74",
            color: "white",
            cursor: "pointer",
          }}
        >
          Kembali ke Action Plan
        </button>
      </div>
    );
  }

  if (submittedResult) {
    const submissionStatus = submittedResult?.submission?.status;
    const feedbackScore = submittedResult?.feedback?.score ?? 0;
    const isPassed = submissionStatus === "passed";

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
            onClick={() => navigate("/action-plan")}
            style={{
              background: "transparent",
              border: "none",
              color: "rgba(255,255,255,0.55)",
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "13px",
              cursor: "pointer",
            }}
          >
            Kembali ke Action Plan
          </button>
        </nav>

        <div
          style={{
            position: "relative",
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
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
              background: "rgba(255,255,255,0.06)",
              border: `1px solid ${
                isPassed
                  ? "rgba(61,186,116,0.35)"
                  : "rgba(212,168,68,0.35)"
              }`,
              borderRadius: "18px",
              padding: "28px",
              textAlign: "center",
              boxShadow: "0 20px 60px rgba(0,0,0,0.22)",
            }}
          >
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "50%",
                background: isPassed
                  ? "rgba(61,186,116,0.18)"
                  : "rgba(212,168,68,0.18)",
                border: `1px solid ${
                  isPassed
                    ? "rgba(61,186,116,0.35)"
                    : "rgba(212,168,68,0.35)"
                }`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "30px",
                margin: "0 auto 16px",
              }}
            >
              {isPassed ? "✅" : "📝"}
            </div>

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontSize: "28px",
                margin: "0 0 10px",
                color: isPassed ? "#3dba74" : "#d4a844",
              }}
            >
              {isPassed ? "Task Selesai Disubmit" : "Task Berhasil Disubmit"}
            </h1>

            <p
              style={{
                margin: "0 0 18px",
                color: "rgba(255,255,255,0.68)",
                fontSize: "14px",
                lineHeight: 1.7,
              }}
            >
              {isPassed
                ? "Submission kamu sudah dinilai passed. Status task akan berubah menjadi selesai di Action Plan, Dashboard, dan Profil."
                : "Submission kamu sudah diterima, tetapi masih butuh revisi. Buka Feedback untuk melihat bagian yang perlu diperbaiki."}
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px",
                marginBottom: "18px",
              }}
            >
              <div
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                  padding: "14px",
                }}
              >
                <p
                  style={{
                    margin: "0 0 4px",
                    color: "rgba(255,255,255,0.42)",
                    fontSize: "11px",
                  }}
                >
                  Status
                </p>

                <p
                  style={{
                    margin: 0,
                    color: isPassed ? "#3dba74" : "#d4a844",
                    fontWeight: 800,
                    textTransform: "capitalize",
                  }}
                >
                  {submissionStatus}
                </p>
              </div>

              <div
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                  padding: "14px",
                }}
              >
                <p
                  style={{
                    margin: "0 0 4px",
                    color: "rgba(255,255,255,0.42)",
                    fontSize: "11px",
                  }}
                >
                  Score
                </p>

                <p
                  style={{
                    margin: 0,
                    color: "#3dba74",
                    fontWeight: 800,
                  }}
                >
                  {feedbackScore}
                </p>
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px",
              }}
            >
              <button
                onClick={() => navigate("/feedback")}
                style={{
                  padding: "13px 16px",
                  borderRadius: "12px",
                  border: "none",
                  background: "#2d8c5e",
                  color: "white",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Lihat Feedback
              </button>

              <button
                onClick={() => navigate("/action-plan")}
                style={{
                  padding: "13px 16px",
                  borderRadius: "12px",
                  border: "1px solid rgba(255,255,255,0.14)",
                  background: "rgba(255,255,255,0.06)",
                  color: "rgba(255,255,255,0.75)",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Buka Action Plan
              </button>
            </div>
          </div>
        </div>
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
          flexShrink: 0,
        }}
      >
        <Logo />

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <span
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "13px",
              color: "rgba(255,255,255,0.5)",
            }}
          >
            Langkah {data.currentStep} dari {data.totalSteps}
          </span>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "5px 14px",
              borderRadius: "999px",
              background: "rgba(61,186,116,0.12)",
              border: "1.5px solid rgba(61,186,116,0.35)",
            }}
          >
            <span style={{ fontSize: "13px" }}>⚡</span>

            <span
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                fontWeight: 600,
                color: "#3dba74",
              }}
            >
              +{data.xp} XP
            </span>
          </div>
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
            maxWidth: "640px",
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
                  onClick={() =>
                    index < data.breadcrumb.length - 1 && handleBack()
                  }
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
              ...sectionCard,
              background: "rgba(255,255,255,0.05)",
              border: "1px solid rgba(255,255,255,0.11)",
              marginBottom: "12px",
              padding: "16px 20px",
            }}
          >
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "10px",
                letterSpacing: "0.1em",
                textTransform: "uppercase",
                color: "rgba(255,255,255,0.35)",
                marginBottom: "6px",
              }}
            >
              {data.phase}
            </p>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                marginBottom: "10px",
              }}
            >
              <div
                style={{
                  width: "38px",
                  height: "38px",
                  borderRadius: "10px",
                  background: "rgba(45,140,94,0.2)",
                  border: "1.5px solid rgba(61,186,116,0.3)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "18px",
                  flexShrink: 0,
                }}
              >
                📝
              </div>

              <h1
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "clamp(20px, 3.5vw, 26px)",
                  color: "white",
                  margin: 0,
                }}
              >
                {data.title}
              </h1>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                flexWrap: "wrap",
              }}
            >
              {data.tags.map((tag) => (
                <span
                  key={tag}
                  style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: "11px",
                    color: "rgba(255,255,255,0.65)",
                    background: "rgba(255,255,255,0.08)",
                    border: "1px solid rgba(255,255,255,0.13)",
                    padding: "3px 10px",
                    borderRadius: "6px",
                  }}
                >
                  {tag}
                </span>
              ))}

              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "11px",
                  color: "#3dba74",
                  background: "rgba(61,186,116,0.1)",
                  border: "1px solid rgba(61,186,116,0.25)",
                  padding: "3px 10px",
                  borderRadius: "6px",
                  fontWeight: 600,
                }}
              >
                +{data.xp} XP
              </span>
            </div>
          </div>

          <div style={{ ...sectionCard }}>
            <SectionLabel>Deskripsi</SectionLabel>

            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(255,255,255,0.7)",
                lineHeight: 1.7,
                margin: 0,
              }}
            >
              {data.sections.deskripsi}
            </p>
          </div>

          <div style={{ ...sectionCard }}>
            <SectionLabel color="#3dba74">
              Yang Harus Dikerjakan
            </SectionLabel>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {data.sections.yangHarusDikerjakan.map((item, index) => (
                <div
                  key={index}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                  }}
                >
                  <div
                    style={{
                      width: "22px",
                      height: "22px",
                      borderRadius: "50%",
                      background: "rgba(45,140,94,0.25)",
                      border: "1.5px solid rgba(61,186,116,0.4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: "'DM Sans', sans-serif",
                      fontWeight: 700,
                      fontSize: "11px",
                      color: "#3dba74",
                      flexShrink: 0,
                      marginTop: "1px",
                    }}
                  >
                    {index + 1}
                  </div>

                  <p
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "13px",
                      color: "rgba(255,255,255,0.75)",
                      margin: 0,
                      lineHeight: 1.6,
                    }}
                  >
                    {item}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...sectionCard }}>
            <SectionLabel color="#3dba74">
              Expected Output
            </SectionLabel>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "8px",
              }}
            >
              {data.sections.expectedOutput.map((item, index) => (
                <div
                  key={index}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "8px 12px",
                    background: "rgba(255,255,255,0.03)",
                    border: "1px solid rgba(255,255,255,0.07)",
                    borderRadius: "8px",
                  }}
                >
                  <span style={{ fontSize: "16px", flexShrink: 0 }}>
                    {item.icon}
                  </span>

                  <span
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "13px",
                      color: "rgba(255,255,255,0.7)",
                    }}
                  >
                    {item.text}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ ...sectionCard }}>
            <SectionLabel color="#3dba74">Submit Task</SectionLabel>

            <div
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleFileDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${
                  isDragging
                    ? "rgba(61,186,116,0.6)"
                    : "rgba(255,255,255,0.15)"
                }`,
                borderRadius: "12px",
                padding: "28px 20px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                gap: "6px",
                cursor: "pointer",
                background: isDragging
                  ? "rgba(61,186,116,0.05)"
                  : "rgba(255,255,255,0.02)",
                transition: "all 0.2s",
                marginBottom: "10px",
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".jpg,.jpeg,.png,.webp,.pdf,.txt,.zip"
                style={{ display: "none" }}
                onChange={handleFileDrop}
              />

              <span style={{ fontSize: "24px" }}>📁</span>

              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "13px",
                  color: file ? "#3dba74" : "rgba(255,255,255,0.55)",
                  margin: 0,
                  fontWeight: file ? 600 : 400,
                  textAlign: "center",
                  wordBreak: "break-word",
                }}
              >
                {file
                  ? `✓ ${file.name} (${getFileSizeText(file.size)})`
                  : "Upload file kamu di sini"}
              </p>

              <p
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "11px",
                  color: "rgba(255,255,255,0.3)",
                  margin: 0,
                  textAlign: "center",
                  lineHeight: 1.5,
                }}
              >
                Gambar, PDF, TXT, atau ZIP. Maksimal 10MB.
                <br />
                Untuk project, upload ZIP source code tanpa node_modules.
              </p>
            </div>

            {file && (
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "10px",
                  padding: "10px 12px",
                  borderRadius: "10px",
                  background: "rgba(61,186,116,0.08)",
                  border: "1px solid rgba(61,186,116,0.18)",
                  marginBottom: "10px",
                }}
              >
                <p
                  style={{
                    margin: 0,
                    fontSize: "12px",
                    color: "rgba(255,255,255,0.68)",
                    lineHeight: 1.5,
                  }}
                >
                  File siap dikirim. ZIP project akan memiliki bobot penilaian
                  lebih tinggi dibanding gambar atau dokumen.
                </p>

                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                  style={{
                    border: "none",
                    background: "rgba(224,90,90,0.15)",
                    color: "#ff8a8a",
                    borderRadius: "8px",
                    padding: "8px 10px",
                    fontSize: "11px",
                    fontWeight: 700,
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                  }}
                >
                  Hapus
                </button>
              </div>
            )}

            <textarea
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              placeholder="Catatan tambahan opsional — jelaskan isi file, hasil project, atau kendala yang kamu temui..."
              rows={3}
              style={{
                width: "100%",
                padding: "12px 14px",
                borderRadius: "10px",
                border: "1px solid rgba(255,255,255,0.1)",
                background: "rgba(255,255,255,0.03)",
                color: "rgba(255,255,255,0.7)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                outline: "none",
                resize: "vertical",
              }}
            />
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "auto 1fr",
              gap: "12px",
            }}
          >
            <button
              onClick={handleBack}
              style={{
                padding: "14px 24px",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.15)",
                background: "rgba(255,255,255,0.06)",
                color: "rgba(255,255,255,0.6)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 500,
                cursor: "pointer",
              }}
            >
              Simpan Draft
            </button>

            <button
              onClick={handleSubmit}
              disabled={submitting}
              style={{
                padding: "14px",
                borderRadius: "12px",
                border: "none",
                background: submitting
                  ? "rgba(45,140,94,0.45)"
                  : "rgba(45,140,94,0.9)",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 600,
                cursor: submitting ? "not-allowed" : "pointer",
              }}
            >
              {submitting ? "Mengirim..." : "Submit Task →"}
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
          div[style*="grid-template-columns: auto 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}