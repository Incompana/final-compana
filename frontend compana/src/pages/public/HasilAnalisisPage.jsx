// src/pages/HasilAnalisisPage.jsx
import { useState } from "react";
import { Logo, StarField } from "../../components/Shared";
import { useAssessment } from "../../context/AssessmentContext";
import { useNavigate } from "react-router-dom";
import LoginRegisterPrompt from "../../components/LoginRegisterPrompt";
import api from "../../api/axios";
import toast from "react-hot-toast";

export default function HasilAnalisisPage({
  onLihatRoadmap,
  onSimpan,
  onSelesai,
}) {

const [showLoginPrompt, setShowLoginPrompt] = useState(false);
const navigate = useNavigate();

const { draft, clearDraft } = useAssessment();

const answers = draft.answers || {};

const analysis =
  draft.analysisResult || {};

const skillGap =
  draft.skillGap || [];

const recommendedTasks =
  draft.recommendedTasks || [];

const problemCategory =
  analysis.problemCategory ||
  "Skill Gap";

const problemDesc =
  analysis.summary ||
  analysis.problemDescription ||
  "Masih membutuhkan peningkatan skill";

const formatRoleLabel = (role = "Frontend Developer") =>
  role
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

const formatPersonaLabel = (personaValue = "Career Explorer") =>
  personaValue
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());

const persona =
  analysis.personaType ||
  analysis.persona ||
  "Career Explorer";

 const DATA = {
  targetRole:
    formatRoleLabel(analysis.role || "Frontend Developer"),

  level: analysis.currentLevel || "Entry Level",

  problemCategory,
  problemDesc,

  confidenceScore:
    analysis.confidence || 75,

  confidenceLabel:
    "Berdasarkan hasil assessment AI",

  persona: {
    nama: formatPersonaLabel(persona),

    tahapKarir:
      answers[1] ===
      "mahasiswa aktif"
        ? "Mahasiswa"
        : "Pemula",

    skillSaatIni:
      answers[3] ||
      "Belum ditentukan",

    gayaBelajar:
      "Praktek + Video",

    waktuTersedia:
      "1–2 jam / hari",

    target6Bulan:
      "Dapat pekerjaan pertama",
  },

  langkah:
    (recommendedTasks.length
      ? recommendedTasks
      : ["Buka action plan untuk melihat task AI pertama kamu"]
    ).map((task, index) => ({
      no: index + 1,
      text: task,
      badge: "Rekomendasi AI",
      badgeColor: "#2d8c5e",
    })),
};
const card = {
  background: "rgba(255,255,255,0.06)",
  border: "1px solid rgba(255,255,255,0.12)",
  borderRadius: "14px",
  padding: "18px 20px",
};

const label = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "10px",
  letterSpacing: "0.08em",
  color: "rgba(255,255,255,0.4)",
  textTransform: "uppercase",
  marginBottom: "4px",
};

const value = {
  fontFamily: "'Playfair Display', serif",
  fontWeight: 700,
  fontSize: "17px",
  color: "#3dba74",
  textDecoration: "underline",
  textDecorationColor: "rgba(61,186,116,0.35)",
  textUnderlineOffset: "3px",
};

const subValue = {
  fontFamily: "'DM Sans', sans-serif",
  fontSize: "12px",
  color: "rgba(255,255,255,0.5)",
  marginTop: "2px",
};

const pct = DATA.confidenceScore;

const handleNextJourney = async () => {
  if (!draft?.assessmentPayload) {
    toast.error("Data assessment belum tersedia");
    navigate("/assessment");
    return;
  }

  const token = localStorage.getItem("token");

  if (!token || token === "undefined" || token === "null") {
    setShowLoginPrompt(true);
    return;
  }

  try {
    const saveResponse = await api.post(
      "/assessments/save",
      draft.assessmentPayload
    );

    localStorage.setItem(
      "lastAssessmentResult",
      JSON.stringify(saveResponse.data.data)
    );

    const user = JSON.parse(
      localStorage.getItem("user") || "null"
    );

    if (user) {
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...user,
          is_assessment_done: true,
        })
      );
    }

    clearDraft();

    navigate("/skill-gap");
  } catch (error) {
    console.log(error.response?.data || error.message);
    toast.error("Gagal menyimpan hasil assessment");
  }
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
      {/* Nav */}
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
            background: "rgba(61,186,116,0.08)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.8)",
            fontWeight: 500,
          }}
        >
          Hasil Analisis
        </div>
        <button
          onClick={onSelesai}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.55)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            cursor: "pointer",
            transition: "color 0.2s",
          }}
          onMouseEnter={(e) => (e.target.style.color = "rgba(255,255,255,0.95)")}
          onMouseLeave={(e) => (e.target.style.color = "rgba(255,255,255,0.55)")}
        >
          Selesai ✓
        </button>
      </nav>

      {/* Body */}
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
            animation: "slideUp 0.6s ease both",
          }}
        >
          {/* Hero icon + title */}
          <div style={{ textAlign: "center", marginBottom: "28px" }}>
            <div
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "50%",
                background: "rgba(45,140,94,0.25)",
                border: "1.5px solid rgba(61,186,116,0.4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "28px",
                margin: "0 auto 16px",
              }}
            >
              🧠
            </div>
            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(26px, 4vw, 34px)",
                margin: "0 0 10px",
              }}
            >
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "4px",
                }}
              >
                Analisismu
              </span>{" "}
              <span style={{ color: "white" }}>sudah siap!</span>
            </h1>
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(255,255,255,0.5)",
                textDecoration: "underline",
                textDecorationColor: "rgba(255,255,255,0.2)",
              }}
            >
              Berdasarkan jawabanmu, berikut profil karir dan rekomendasi langkah yang bisa diambil hari ini.
            </p>
          </div>

          {/* 3-column top cards */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr 1fr",
              gap: "12px",
              marginBottom: "16px",
            }}
          >
            {/* Target Role */}
            <div
              style={{
                ...card,
                background: "rgba(255,255,255,0.92)",
              }}
            >
              <div
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "rgba(45,140,94,0.18)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  marginBottom: "10px",
                }}
              >
                💻
              </div>
              <p style={{ ...label, color: "rgba(40,60,50,0.5)" }}>Target Role</p>
              <p style={{ ...value, color: "#2d8c5e" }}>{DATA.targetRole}</p>
              <p style={{ ...subValue, color: "rgba(40,60,50,0.55)" }}>{DATA.level}</p>
            </div>

            {/* Problem Category */}
            <div style={{ ...card, background: "rgba(255,255,255,0.92)" }}>
              <div
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "rgba(220,140,80,0.18)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  marginBottom: "10px",
                }}
              >
                😕
              </div>
              <p style={{ ...label, color: "rgba(40,60,50,0.5)" }}>Problem Category</p>
              <p style={{ ...value, color: "#c07030" }}>{DATA.problemCategory}</p>
              <p style={{ ...subValue, color: "rgba(40,60,50,0.55)" }}>{DATA.problemDesc}</p>
            </div>

            {/* Confidence Score */}
            <div style={{ ...card, background: "rgba(255,255,255,0.92)" }}>
              <div
                style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "rgba(45,140,94,0.18)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "16px",
                  marginBottom: "10px",
                }}
              >
                📊
              </div>
              <p style={{ ...label, color: "rgba(40,60,50,0.5)" }}>Confidence Score</p>
              <p
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "26px",
                  color: "#2d8c5e",
                  margin: "0 0 6px",
                }}
              >
                {pct}%
              </p>
              <div
                style={{
                  height: "5px",
                  borderRadius: "999px",
                  background: "rgba(45,140,94,0.15)",
                  marginBottom: "6px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${pct}%`,
                    borderRadius: "999px",
                    background: "linear-gradient(90deg, #2d8c5e, #3dba74)",
                  }}
                />
              </div>
              <p style={{ ...subValue, color: "rgba(40,60,50,0.55)", fontSize: "11px" }}>
                {DATA.confidenceLabel}
              </p>
            </div>
          </div>

          {/* Profil Persona */}
          <div
            style={{
              ...card,
              background: "rgba(255,255,255,0.06)",
              marginBottom: "16px",
            }}
          >
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                fontWeight: 600,
                color: "rgba(255,255,255,0.75)",
                marginBottom: "14px",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              👤{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.35)",
                  textUnderlineOffset: "3px",
                }}
              >
                Profil Persona Kamu
              </span>
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 1fr",
                gap: "10px",
              }}
            >
              {[
                { lbl: "Nama Persona", val: DATA.persona.nama },
                { lbl: "Tahap Karir", val: DATA.persona.tahapKarir },
                { lbl: "Skill Saat Ini", val: DATA.persona.skillSaatIni },
                { lbl: "Gaya Belajar", val: DATA.persona.gayaBelajar },
                { lbl: "Waktu Tersedia", val: DATA.persona.waktuTersedia },
                { lbl: "Target 6 Bulan", val: DATA.persona.target6Bulan },
              ].map(({ lbl, val }) => (
                <div
                  key={lbl}
                  style={{
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.09)",
                    borderRadius: "10px",
                    padding: "10px 12px",
                  }}
                >
                  <p style={label}>{lbl}</p>
                  <p
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "13px",
                      color: "#3dba74",
                      textDecoration: "underline",
                      textDecorationColor: "rgba(61,186,116,0.3)",
                      textUnderlineOffset: "3px",
                      margin: 0,
                    }}
                  >
                    {val}
                  </p>
                </div>
              ))}
            </div>
          </div>
          <div
  style={{
    ...card,
    marginBottom: "16px",
  }}
>
  <p
    style={{
      fontFamily: "'DM Sans', sans-serif",
      fontSize: "13px",
      fontWeight: 600,
      color: "#3dba74",
      marginBottom: "12px",
    }}
  >
    🚀 Skill Gap
  </p>

  <div
    style={{
      display: "flex",
      flexWrap: "wrap",
      gap: "10px",
    }}
  >
    {skillGap.map((skill) => (
      <span
        key={skill}
        style={{
          padding: "8px 14px",
          borderRadius: "999px",
          background:
            "rgba(61,186,116,0.15)",
          border:
            "1px solid rgba(61,186,116,0.3)",
          fontSize: "13px",
        }}
      >
        {skill}
      </span>
    ))}
  </div>
</div>

          {/* 3 Langkah Pertama */}
          <div
            style={{
              ...card,
              background: "rgba(255,255,255,0.06)",
              marginBottom: "24px",
            }}
          >
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                fontWeight: 600,
                color: "rgba(255,255,255,0.75)",
                marginBottom: "14px",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              🎯{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.35)",
                  textUnderlineOffset: "3px",
                }}
              >
                3 Langkah Pertama Kamu
              </span>
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {DATA.langkah.map((item) => (
                <div
                  key={item.no}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    background: "rgba(255,255,255,0.04)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: "10px",
                    padding: "12px 14px",
                  }}
                >
                  <div
                    style={{
                      width: "26px",
                      height: "26px",
                      borderRadius: "50%",
                      background: "rgba(45,140,94,0.3)",
                      border: "1.5px solid rgba(61,186,116,0.4)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: "'DM Sans', sans-serif",
                      fontWeight: 700,
                      fontSize: "12px",
                      color: "#3dba74",
                      flexShrink: 0,
                    }}
                  >
                    {item.no}
                  </div>
                  <p
                    style={{
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "13px",
                      color: "rgba(255,255,255,0.8)",
                      flex: 1,
                      margin: 0,
                      textDecoration: "underline",
                      textDecorationColor: "rgba(255,255,255,0.2)",
                      textUnderlineOffset: "3px",
                    }}
                  >
                    {item.text}
                  </p>
                  <span
                    style={{
                      padding: "4px 10px",
                      borderRadius: "999px",
                      background: item.badgeColor,
                      fontFamily: "'DM Sans', sans-serif",
                      fontSize: "11px",
                      fontWeight: 600,
                      color: "white",
                      flexShrink: 0,
                    }}
                  >
                    {item.badge}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom buttons */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: "12px" }}>
            <button
onClick={handleNextJourney}
              style={{
                padding: "14px",
                borderRadius: "12px",
                border: "1px solid rgba(255,255,255,0.15)",
                background: "rgba(255,255,255,0.07)",
                color: "rgba(255,255,255,0.75)",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 500,
                cursor: "pointer",
                transition: "all 0.2s",
                textDecoration: "underline",
                textDecorationColor: "rgba(255,255,255,0.2)",
                textUnderlineOffset: "3px",
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "rgba(255,255,255,0.12)";
                e.target.style.color = "white";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "rgba(255,255,255,0.07)";
                e.target.style.color = "rgba(255,255,255,0.75)";
              }}
            >
               Lanjut ke Skill Gap →
            </button>
            <button
            onClick={handleNextJourney}
              style={{
                padding: "14px 28px",
                borderRadius: "12px",
                border: "none",
                background: "rgba(61,186,116,0.75)",
                color: "white",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "rgba(61,186,116,1)";
                e.target.style.transform = "translateY(-1px)";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "rgba(61,186,116,0.75)";
                e.target.style.transform = "translateY(0)";
              }}
            >
              Simpan Hasil
            </button>
          </div>
        </div>
      </div>
    {showLoginPrompt && (
  <LoginRegisterPrompt
    onLogin={() => navigate("/login")}
    onRegister={() => navigate("/register")}
    onSkip={() => setShowLoginPrompt(false)}
  />
)}

    </div>
  );
}
