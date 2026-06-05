// src/pages/LoadingScreen.jsx
import { useState, useEffect } from "react";
import { Logo, StarField } from "../../components/Shared";

const QUOTES = [
  {
    text: '"Jangan takut gagal. Semua orang pernah gagal, yang terpenting adalah tidak pernah berhenti mencoba."',
    author: "– person",
  },
  {
    text: '"Kesuksesan bukan tentang seberapa jauh kamu melangkah, tapi seberapa keras kamu bangkit setiap kali jatuh."',
    author: "– person",
  },
  {
    text: '"Mulailah dari mana kamu berada, gunakan apa yang kamu punya, lakukan apa yang kamu bisa."',
    author: "– Arthur Ashe",
  },
];

export default function LoadingScreen({
  currentQuestion = 2,
  totalQuestions = 8,
  currentStep = 2,
  totalSteps = 3,
  progress = 25,
  onSkip,
  onDone,
}) {
  const [activeQuote, setActiveQuote] = useState(0);
  const [fade, setFade] = useState(true);

  // Auto-rotate quotes
  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setActiveQuote((prev) => (prev + 1) % QUOTES.length);
        setFade(true);
      }, 400);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  // Auto-advance after all quotes shown (optional — calls onDone)
  useEffect(() => {
    if (!onDone) return;
    const timeout = setTimeout(() => {
      onDone();
    }, QUOTES.length * 4000 + 600);
    return () => clearTimeout(timeout);
  }, [onDone]);

  const handleDotClick = (idx) => {
    setFade(false);
    setTimeout(() => {
      setActiveQuote(idx);
      setFade(true);
    }, 300);
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
      {/* Navbar */}
      <nav
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "14px 40px",
        }}
      >
        <Logo />

        {/* Centre: Pertanyaan x dari y */}
        <div
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            color: "rgba(255,255,255,0.55)",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          Pertanyaan{" "}
          <span style={{ color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
            {currentQuestion}
          </span>{" "}
          dari{" "}
          <span style={{ color: "rgba(255,255,255,0.85)", fontWeight: 600 }}>
            {totalQuestions}
          </span>
        </div>

        {/* Right: Lewati */}
        <button
          onClick={onSkip}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.6)",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "4px",
            transition: "color 0.2s",
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.color = "rgba(255,255,255,0.95)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.color = "rgba(255,255,255,0.6)")
          }
        >
          Lewati →
        </button>
      </nav>

      {/* Main */}
      <div
        style={{
          flex: 1,
          position: "relative",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "flex-start",
          paddingTop: "16px",
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
            padding: "0 24px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {/* Badge */}
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "7px",
              padding: "6px 18px",
              borderRadius: "999px",
              border: "1.5px solid rgba(61, 186, 116, 0.5)",
              background: "rgba(61, 186, 116, 0.08)",
              marginBottom: "18px",
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
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(255,255,255,0.8)",
                fontWeight: 500,
              }}
            >
              Assessment Karir
            </span>
          </div>

          {/* Progress bar */}
          <div style={{ width: "100%", marginBottom: "28px" }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.45)",
                }}
              >
                Langkah {currentStep} dari {totalSteps}
              </span>
              <span
                style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "12px",
                  color: "rgba(255,255,255,0.45)",
                }}
              >
                {progress}%
              </span>
            </div>

            {/* Track */}
            <div
              style={{
                width: "100%",
                height: "5px",
                borderRadius: "999px",
                background: "rgba(255,255,255,0.1)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${progress}%`,
                  borderRadius: "999px",
                  background:
                    "linear-gradient(90deg, #2d8c5e 0%, #3dba74 100%)",
                  transition: "width 0.8s ease",
                }}
              />
            </div>
          </div>

          {/* Quote Card */}
          <div
            style={{
              width: "100%",
              background: "rgba(255,255,255,0.95)",
              borderRadius: "20px",
              padding: "32px 40px 40px",
              boxShadow:
                "0 8px 40px rgba(0,0,0,0.35), 0 0 0 1px rgba(255,255,255,0.08)",
              minHeight: "320px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
            }}
          >
            {/* Label */}
            <p
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "13px",
                color: "rgba(60,80,70,0.5)",
                marginBottom: "0",
              }}
            >
              Quote Of The Day
            </p>

            {/* Quote text */}
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "32px 0 16px",
                opacity: fade ? 1 : 0,
                transition: "opacity 0.4s ease",
              }}
            >
              <p
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "clamp(18px, 3vw, 22px)",
                  color: "#2d8c5e",
                  textAlign: "center",
                  lineHeight: 1.55,
                  textDecoration: "underline",
                  textDecorationColor: "rgba(45,140,94,0.35)",
                  textUnderlineOffset: "4px",
                  margin: 0,
                }}
              >
                {QUOTES[activeQuote].text}
              </p>
            </div>

            {/* Author */}
            <p
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "18px",
                color: "#2d8c5e",
                textAlign: "right",
                margin: 0,
                opacity: fade ? 1 : 0,
                transition: "opacity 0.4s ease 0.05s",
                textDecoration: "underline",
                textDecorationColor: "rgba(45,140,94,0.35)",
                textUnderlineOffset: "4px",
              }}
            >
              {QUOTES[activeQuote].author}
            </p>
          </div>

          {/* Dots */}
          <div
            style={{
              display: "flex",
              gap: "10px",
              marginTop: "24px",
              alignItems: "center",
            }}
          >
            {QUOTES.map((_, idx) => (
              <button
                key={idx}
                onClick={() => handleDotClick(idx)}
                style={{
                  width: idx === activeQuote ? "10px" : "9px",
                  height: idx === activeQuote ? "10px" : "9px",
                  borderRadius: "50%",
                  background:
                    idx === activeQuote
                      ? "#3dba74"
                      : "rgba(255,255,255,0.3)",
                  border: "none",
                  cursor: "pointer",
                  padding: 0,
                  transition: "all 0.3s",
                  transform: idx === activeQuote ? "scale(1.15)" : "scale(1)",
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
