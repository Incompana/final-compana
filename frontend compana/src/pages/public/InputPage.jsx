import { useState } from "react";
import { Logo, StarField } from "../../components/Shared";
import { useAssessment } from "../../context/AssessmentContext";
import { useNavigate } from "react-router-dom";

const TOPICS = [
  { icon: "🎓", label: "Baru lulus kuliah" },
  { icon: "🔄", label: "Mau ganti karir" },
  { icon: "📊", label: "Ingin naik jabatan" },
];

export default function InputPage() {
  const navigate = useNavigate(); 

  const { draft, setDraft } = useAssessment();

const [text, setText] = useState(
  draft.inputText || ""
);
const handleNext = () => {
  setDraft((prev) => ({
    ...prev,
    inputText: text,
  }));

  navigate("/assessment");
};
  const handleTopicClick = (label) => {
    setText((prev) => prev ? `${prev} ${label.toLowerCase()}.` : `${label}.`);
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a1f12", color: "white", display: "flex", flexDirection: "column" }}>
      {/* Navbar */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "16px 40px",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
      }}>
        <Logo />
        <div style={{
          fontFamily: "'DM Sans', sans-serif", fontSize: "13px",
          color: "rgba(255,255,255,0.45)",
        }}>
          Langkah <span style={{ color: "white", fontWeight: 600 }}>1</span> dari 3
        </div>
        <div style={{ width: "120px" }} />
      </nav>

      {/* Progress bar */}
      <div style={{ height: "3px", background: "rgba(255,255,255,0.08)" }}>
        <div style={{
          width: "33.33%", height: "100%",
          background: "linear-gradient(90deg, #2d8c5e, #3dba74)",
        }} />
      </div>

      {/* Content */}
      <section style={{
        flex: 1, position: "relative",
        display: "flex", flexDirection: "column", alignItems: "center",
        justifyContent: "center", textAlign: "center",
        padding: "48px 24px 32px", overflow: "hidden",
      }}>
        <div className="mesh-bg" />
        <StarField />

        <div style={{ position: "relative", zIndex: 1, width: "100%", maxWidth: "620px" }}>
          <div className="badge-pill" style={{ marginBottom: "20px" }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#4de89a", flexShrink: 0 }} />
            Input kondisimu
          </div>

          <h1 className="hero-title" style={{ fontSize: "clamp(32px, 6vw, 54px)", marginBottom: "12px" }}>
            Ceritakan kondisimu
            <br />
            <span style={{ color: "#3dba74", textDecoration: "underline", textDecorationColor: "rgba(61,186,116,0.4)", textUnderlineOffset: "6px" }}>
              sekarang
            </span>
          </h1>

          <p style={{
            fontFamily: "'DM Sans', sans-serif", fontSize: "14px",
            color: "rgba(255,255,255,0.45)", marginBottom: "28px", lineHeight: 1.6,
          }}>
            Tulis apapun yang kamu rasakan — tidak perlu sempurna, cukup jujur.
          </p>

          {/* Textarea card */}
          <div style={{
            background: "rgba(255,255,255,0.05)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: "14px", padding: "20px",
            textAlign: "left", backdropFilter: "blur(8px)",
          }}>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Saya ingin jadi frontend developer tapi bingung mulai dari mana, sudah coba beberapa course tapi tidak konsisten. Skills saya masih basic HTML/CSS. Saya tidak tahu harus fokus ke mana dulu..."
              rows={6}
              style={{
                width: "100%", background: "transparent",
                border: "none", outline: "none", resize: "none",
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "14px", color: "rgba(255,255,255,0.85)",
                lineHeight: 1.7, caretColor: "#3dba74",
              }}
            />

            <div style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              marginTop: "12px", paddingTop: "12px",
              borderTop: "1px solid rgba(255,255,255,0.07)",
            }}>
              <div style={{
                display: "flex", alignItems: "center", gap: "6px",
                fontFamily: "'DM Sans', sans-serif", fontSize: "12px",
                color: "rgba(255,255,255,0.35)",
              }}>
                <span>💡</span>
                <span>Semakin jujur, semakin akurat</span>
              </div>
              <button
                className="cta-btn"
                style={{ padding: "10px 22px", fontSize: "13px", animation: "none" }}
                disabled={text.trim().length < 5}
                onClick={handleNext}
              >
                Analyze →
              </button>
            </div>
          </div>

          {/* Topic chips */}
          <div style={{ marginTop: "24px" }}>
            <p style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: "12px",
              color: "rgba(255,255,255,0.35)", marginBottom: "12px",
            }}>
              Butuh inspirasi? Coba topik ini:
            </p>
            <div style={{ display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap" }}>
              {TOPICS.map((t) => (
                <button key={t.label} onClick={() => handleTopicClick(t.label)} className="topic-chip">
                  <span>{t.icon}</span>
                  <span>{t.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Bottom nav */}
      <div style={{
        display: "flex", justifyContent: "space-between",
        padding: "16px 40px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
      }}>
       <button
  onClick={() => navigate(-1)}
  className="ghost-btn"
>
  ← Kembali
</button>
        <button className="ghost-btn">Lewati</button>
      </div>
    </div>
  );
}