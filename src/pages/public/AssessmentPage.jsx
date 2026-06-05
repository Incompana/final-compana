// src/pages/AssessmentPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo, StarField } from "../../components/Shared";
import { useAssessment } from "../../context/AssessmentContext";
import api from "../../api/axios";

const QUESTIONS = [
  {
    id: 1,
    category: "Situasi",
    question: "Situasi kamu sekarang gimana?",
    options: [
      "mahasiswa aktif",
      "fresh graduate",
      "kerja",
      "ingin berpindah pekerjaan",
    ],
  },
  {
    id: 2,
    category: "Kendala",
    question: "Bagian mana yang paling bikin kamu bingung sekarang?",
    options: [
      "gatau mau mulai dari mana",
      "banyak skill, tapi bingung banget",
      "takut salah jalur",
      "sudah belajar, tapi merasa tidak berkembang",
      "belum punya portfolio",
    ],
  },
  {
    id: 3,
    category: "Target Role",
    question: "Kamu ingin diarahkan ke jalur apa dulu?",
    options: [
      "Frontend Developer",
      "Backend Developer",
      "UI/UX Designer",
      "Machine Learning Engineer",
      "SOC Analyst",
      "Masih bingung",
    ],
  },
  {
    id: 4,
    category: "Level",
    question: "Level skill kamu sekarang menurut kamu gimana?",
    options: [
      "beginner",
      "intermediate",
      "advanced",
    ],
  },
];

const TOTAL_QUESTIONS =
  QUESTIONS.length;

export default function AssessmentPage() {
  const navigate = useNavigate();

  const { draft, setDraft } =
    useAssessment();

  // STATE
  const [currentQ, setCurrentQ] =
    useState(0);

  const [submitting, setSubmitting] =
    useState(false);

  // ANSWERS
  const answers =
    draft.answers || {};

  const q = QUESTIONS[currentQ];

  const selected =
    answers[q.id];

  const answeredCount =
    Object.keys(answers).length;

  const progressPercent = Math.round(
    (answeredCount /
      TOTAL_QUESTIONS) *
      100
  );

  // SELECT ANSWER
  const handleSelect = (option) => {

    setDraft((prev) => ({
      ...prev,

      answers: {
        ...prev.answers,

        [q.id]: option,
      },
    }));
  };

  // NEXT
  const handleNext = async () => {

    const updatedDraft = {
      ...draft,
      answers,
    };

    setDraft(updatedDraft);

    // NEXT QUESTION
    if (
      currentQ <
      QUESTIONS.length - 1
    ) {

      setCurrentQ((prev) => prev + 1);

      return;
    }

    // PREVENT DOUBLE SUBMIT
    if (submitting) return;

    try {

      setSubmitting(true);

      // LOADING PAGE
      navigate("/loading");

const roleAnswer = updatedDraft.answers[3];
const blockerAnswer = updatedDraft.answers[2];
const levelAnswer = updatedDraft.answers[4] || "beginner";

const roleMap = {
  "Frontend Developer": "Frontend Developer",
  "Backend Developer": "Backend Developer",
  "UI/UX Designer": "UI/UX Designer",
  "Machine Learning Engineer": "Machine Learning Engineer",
  "SOC Analyst": "SOC Analyst",
  "Masih bingung": "Frontend Developer",
};

const blockerMap = {
  "gatau mau mulai dari mana": "belum_tahu_mulai",
  "banyak skill, tapi bingung banget": "skill_belum_cukup",
  "takut salah jalur": "takut_salah_pilih",
  "sudah belajar, tapi merasa tidak berkembang": "skill_belum_cukup",
  "belum punya portfolio": "belum_ada_portfolio",
};

const problemCategoryMap = {
  "gatau mau mulai dari mana": "Bingung mulai belajar dari mana",
  "banyak skill, tapi bingung banget": "Skill belum cukup",
  "takut salah jalur": "Takut salah pilih jalur",
  "sudah belajar, tapi merasa tidak berkembang": "Skill belum cukup",
  "belum punya portfolio": "Belum punya portfolio",
};

const payload = {
  targetRole: roleMap[roleAnswer] || "Frontend Developer",
  currentLevel: levelAnswer,
  problemCategory:
    problemCategoryMap[blockerAnswer] ||
    "Bingung mulai belajar dari mana",
  blockerType: blockerMap[blockerAnswer] || "belum_tahu_mulai",
  maxQuestions: 3,
  answers: QUESTIONS.map((questionItem) => ({
    question: questionItem.question,
    answer: updatedDraft.answers[questionItem.id] || "",
  })),
};
      // API
      const response =
        await api.post(
          "/assessments/analyze",
          payload
        );

      console.log("RESPONSE:");
      console.log(response.data);

      // SAVE RESULT
     setDraft((prev) => ({
  ...prev,

  assessmentPayload: payload,

  analysisResult:
    response.data.data.analysis,

  skillGap:
    response.data.data.skillGap,

  recommendedTasks:
    response.data.data.recommendedTasks,

  aiResult:
    response.data.data.ai,
}));
      setSubmitting(false);

      navigate("/hasil-analisis");
    } catch (error) {

      console.log(error);

      setSubmitting(false);

      alert(
        "Gagal analyze assessment"
      );
    }
  };

  // PREVIOUS
  const handlePrev = () => {

    if (currentQ > 0) {

      setCurrentQ((prev) => prev - 1);

    } else {

      navigate("/input");
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
      }}
    >

      {/* NAVBAR */}
      <nav
        style={{
          display: "flex",

          alignItems: "center",

          justifyContent:
            "space-between",

          padding: "16px 40px",

          borderBottom:
            "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <Logo />

        <div
          style={{
            fontFamily:
              "'DM Sans', sans-serif",

            fontSize: "13px",

            color:
              "rgba(255,255,255,0.45)",
          }}
        >
          Pertanyaan{" "}

          <span
            style={{
              color: "white",
              fontWeight: 600,
            }}
          >
            {currentQ + 1}
          </span>{" "}

          dari{" "}

          <span
            style={{
              color: "white",
              fontWeight: 600,
            }}
          >
            {TOTAL_QUESTIONS}
          </span>
        </div>

        <button className="ghost-btn">
          Lewati →
        </button>
      </nav>

      {/* PROGRESS */}
      <div
        style={{
          height: "3px",

          background:
            "rgba(255,255,255,0.08)",
        }}
      >
        <div
          style={{
            width:
              `${progressPercent}%`,

            height: "100%",

            background:
              "linear-gradient(90deg, #2d8c5e, #3dba74)",

            transition:
              "width 0.5s ease",
          }}
        />
      </div>

      {/* CONTENT */}
      <section
        style={{
          flex: 1,

          position: "relative",

          display: "flex",

          flexDirection: "column",

          alignItems: "center",

          justifyContent: "center",

          padding:
            "40px 24px 24px",

          overflow: "hidden",
        }}
      >
        <div className="mesh-bg" />

        <StarField />

        <div
          style={{
            position: "relative",

            zIndex: 1,

            width: "100%",

            maxWidth: "600px",
          }}
        >

          {/* HEADER */}
          <div
            style={{
              display: "flex",

              alignItems: "center",

              justifyContent:
                "space-between",

              marginBottom: "14px",
            }}
          >

            <div
              style={{
                fontFamily:
                  "'DM Sans', sans-serif",

                fontSize: "13px",

                color:
                  "rgba(255,255,255,0.4)",
              }}
            >
              Langkah{" "}

              <span
                style={{
                  color:
                    "rgba(255,255,255,0.8)",

                  fontWeight: 600,
                }}
              >
                {currentQ + 1}
              </span>{" "}

              dari {TOTAL_QUESTIONS}
            </div>

            <div
              style={{
                display: "flex",

                alignItems: "center",

                gap: "28px",
              }}
            >

              <div
                className="badge-pill"
                style={{
                  marginBottom: 0,

                  fontSize: "11px",

                  padding:
                    "4px 12px",
                }}
              >

                <span
                  style={{
                    width: "5px",

                    height: "5px",

                    borderRadius:
                      "50%",

                    background:
                      "#4de89a",

                    flexShrink: 0,
                  }}
                />

                Assessment Karir
              </div>

              <div
                style={{
                  fontFamily:
                    "'DM Sans', sans-serif",

                  fontSize: "12px",

                  color:
                    "rgba(255,255,255,0.35)",
                }}
              >
                {progressPercent}%
              </div>
            </div>
          </div>

          {/* CARD */}
          <div
            style={{
              background:
                "rgba(255,255,255,0.05)",

              border:
                "1px solid rgba(255,255,255,0.1)",

              borderRadius: "16px",

              padding: "28px",

              backdropFilter:
                "blur(8px)",
            }}
          >

            {/* TOP */}
            <div
              style={{
                display: "flex",

                justifyContent:
                  "space-between",

                alignItems: "center",

                marginBottom: "16px",
              }}
            >

              <span
                style={{
                  fontFamily:
                    "'DM Sans', sans-serif",

                  fontSize: "12px",

                  color:
                    "rgba(255,255,255,0.35)",
                }}
              >
                Pertanyaan{" "}
                {currentQ + 1}
              </span>

              <span
                style={{
                  fontFamily:
                    "'DM Sans', sans-serif",

                  fontSize: "11px",

                  color:
                    "rgba(100, 220, 150, 0.8)",

                  background:
                    "rgba(45,140,94,0.15)",

                  border:
                    "1px solid rgba(45,140,94,0.3)",

                  borderRadius:
                    "999px",

                  padding:
                    "3px 10px",
                }}
              >
                {q.category}
              </span>
            </div>

            {/* QUESTION */}
            <h2
              style={{
                fontFamily:
                  "'Playfair Display', serif",

                fontWeight: 700,

                fontSize:
                  "clamp(18px, 3vw, 24px)",

                lineHeight: 1.3,

                marginBottom: "20px",
              }}
            >
              {q.question}
            </h2>

            {/* OPTIONS */}
            <div
              style={{
                display: "flex",

                flexDirection:
                  "column",

                gap: "10px",

                marginBottom: "20px",
              }}
            >

              {q.options.map(
                (option) => {

                  const isSelected =
                    selected ===
                    option;

                  return (
                    <button
                      key={option}

                      onClick={() =>
                        handleSelect(
                          option
                        )
                      }

                      style={{
                        display:
                          "flex",

                        alignItems:
                          "center",

                        gap: "12px",

                        padding:
                          "14px 16px",

                        borderRadius:
                          "10px",

                        border:
                          isSelected
                            ? "1px solid rgba(45,140,94,0.5)"
                            : "1px solid rgba(255,255,255,0.08)",

                        background:
                          isSelected
                            ? "rgba(45,140,94,0.15)"
                            : "rgba(255,255,255,0.03)",

                        cursor:
                          "pointer",

                        textAlign:
                          "left",

                        transition:
                          "all 0.18s",

                        width: "100%",
                      }}
                    >

                      <div
                        style={{
                          width: "18px",

                          height:
                            "18px",

                          borderRadius:
                            "50%",

                          flexShrink: 0,

                          border:
                            isSelected
                              ? "2px solid #3dba74"
                              : "2px solid rgba(255,255,255,0.25)",

                          display:
                            "flex",

                          alignItems:
                            "center",

                          justifyContent:
                            "center",
                        }}
                      >

                        {isSelected && (
                          <div
                            style={{
                              width:
                                "8px",

                              height:
                                "8px",

                              borderRadius:
                                "50%",

                              background:
                                "#3dba74",
                            }}
                          />
                        )}
                      </div>

                      <span
                        style={{
                          fontFamily:
                            "'DM Sans', sans-serif",

                          fontSize:
                            "14px",

                          color:
                            isSelected
                              ? "rgba(255,255,255,0.95)"
                              : "rgba(255,255,255,0.65)",
                        }}
                      >
                        {option}
                      </span>
                    </button>
                  );
                }
              )}
            </div>

            {/* FOOTER */}
            <div
              style={{
                display: "flex",

                justifyContent:
                  "space-between",

                alignItems: "center",
              }}
            >

              <button
                onClick={handlePrev}

                className="ghost-btn"
              >
                ← Sebelumnya
              </button>

              <button
                onClick={handleNext}

                className="cta-btn"

                style={{
                  padding:
                    "10px 24px",

                  fontSize: "13px",

                  animation: "none",
                }}

                disabled={
                  !selected ||
                  submitting
                }
              >
                {submitting
                  ? "Analyzing..."
                  : currentQ ===
                    QUESTIONS.length -
                      1
                  ? "Analisis AI →"
                  : "Selanjutnya →"}
              </button>
            </div>
          </div>

          {/* COUNT */}
          <p
            style={{
              textAlign: "center",

              marginTop: "16px",

              fontFamily:
                "'DM Sans', sans-serif",

              fontSize: "12px",

              color:
                "rgba(255,255,255,0.3)",
            }}
          >
            {answeredCount} dari{" "}
            {TOTAL_QUESTIONS} pertanyaan
            dijawab
          </p>
        </div>
      </section>
    </div>
  );
}