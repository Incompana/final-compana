import { Logo, StarField } from "../../components/Shared";

const FITUR = [
  {
    icon: "🧠",
    title: "Analisis Karir dengan AI",
    desc: "Compana menganalisis kondisi dan tujuan karirmu menggunakan AI, lalu menghasilkan profil persona dan rekomendasi yang personal.",
  },
  {
    icon: "🗺️",
    title: "Action Plan Terstruktur",
    desc: "Dapatkan roadmap belajar step-by-step berdasarkan skill gap-mu. Setiap langkah dibuat agar progresmu lebih terarah.",
  },
  {
    icon: "🔍",
    title: "Skill Gap Analysis",
    desc: "Compana mengidentifikasi skill yang kamu miliki, yang perlu diperkuat, dan yang belum ada sama sekali.",
  },
  {
    icon: "📊",
    title: "Dashboard Progres",
    desc: "Pantau perjalanan karirmu dari satu tempat: XP yang terkumpul, task aktif, progress, dan feedback terbaru.",
  },
  {
    icon: "💬",
    title: "Feedback Task",
    desc: "Setiap task yang kamu submit akan dinilai dengan strengths, weaknesses, saran perbaikan, dan skor evaluasi.",
  },
  {
    icon: "🎯",
    title: "Gratis untuk Semua",
    desc: "Mulai analisis, buat action plan, dan akses dashboard tanpa biaya. Compana dibuat agar karir tech lebih mudah dimulai.",
  },
];

const STEPS = [
  {
    no: 1,
    label: "Isi Input Profil",
    desc: "Ceritakan kondisimu sekarang — apakah kamu mahasiswa, fresh graduate, atau sedang ingin pindah jalur karir.",
    icon: "📝",
    color: "#3dba74",
  },
  {
    no: 2,
    label: "Jawab Assessment",
    desc: "Jawab beberapa pertanyaan singkat tentang situasi, pengalaman, dan tujuan karirmu.",
    icon: "✏️",
    color: "#3dba74",
  },
  {
    no: 3,
    label: "Lihat Hasil Analisis",
    desc: "AI memproses jawabanmu dan menghasilkan profil persona, confidence score, dan langkah awal yang bisa kamu ambil.",
    icon: "📊",
    color: "#3dba74",
  },
  {
    no: 4,
    label: "Buat Akun atau Login",
    desc: "Simpan hasil analisis dan akses fitur lanjutan dengan mendaftar atau login.",
    icon: "🔐",
    color: "#d4a844",
  },
  {
    no: 5,
    label: "Jalankan Action Plan",
    desc: "Buka task satu per satu sesuai urutan. Kerjakan, upload hasilmu, lalu dapatkan feedback.",
    icon: "🚀",
    color: "#3dba74",
  },
  {
    no: 6,
    label: "Pantau dari Dashboard",
    desc: "Lihat progres karirmu, total XP, task aktif, dan feedback terbaru dari satu halaman dashboard.",
    icon: "🎯",
    color: "#3dba74",
  },
];

const CONNECTOR_COLOR = "rgba(61,186,116,0.25)";

function Badge({ children }) {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        padding: "6px 18px",
        borderRadius: "999px",
        border: "1.5px solid rgba(61,186,116,0.4)",
        background: "rgba(61,186,116,0.08)",
        fontSize: "12px",
        color: "rgba(255,255,255,0.75)",
        fontWeight: 600,
        marginBottom: "24px",
      }}
    >
      <span
        style={{
          width: "6px",
          height: "6px",
          borderRadius: "50%",
          background: "#3dba74",
          boxShadow: "0 0 6px #3dba74",
          display: "inline-block",
        }}
      />
      {children}
    </div>
  );
}

function FeatureBox({ item }) {
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "14px",
        padding: "20px 22px",
      }}
    >
      <div
        style={{
          width: "40px",
          height: "40px",
          borderRadius: "10px",
          background: "rgba(45,140,94,0.15)",
          border: "1px solid rgba(61,186,116,0.2)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "18px",
          marginBottom: "12px",
        }}
      >
        {item.icon}
      </div>

      <p
        style={{
          fontFamily: "'Playfair Display', serif",
          fontWeight: 700,
          fontSize: "15px",
          color: "rgba(255,255,255,0.9)",
          margin: "0 0 8px",
        }}
      >
        {item.title}
      </p>

      <p
        style={{
          fontSize: "13px",
          color: "rgba(255,255,255,0.5)",
          lineHeight: 1.7,
          margin: 0,
        }}
      >
        {item.desc}
      </p>
    </div>
  );
}

function StepItem({ step, index }) {
  const isGold = step.color === "#d4a844";

  return (
    <div
      style={{
        display: "flex",
        gap: "20px",
        alignItems: "flex-start",
        position: "relative",
        zIndex: 1,
        animation: `slideUp ${0.4 + index * 0.08}s ease both`,
      }}
    >
      <div
        style={{
          width: "54px",
          height: "54px",
          borderRadius: "50%",
          border: isGold
            ? "2px solid rgba(212,168,68,0.5)"
            : "2px solid rgba(61,186,116,0.4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          fontSize: "20px",
          position: "relative",
          background: isGold ? "rgba(212,168,68,0.12)" : "rgba(45,140,94,0.12)",
        }}
      >
        {step.icon}

        <span
          style={{
            position: "absolute",
            top: "-4px",
            right: "-4px",
            width: "18px",
            height: "18px",
            borderRadius: "50%",
            background: step.color,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "10px",
            fontWeight: 700,
            color: "white",
            border: "2px solid #0a1f12",
          }}
        >
          {step.no}
        </span>
      </div>

      <div
        style={{
          flex: 1,
          background: "rgba(255,255,255,0.04)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: "14px",
          padding: "16px 20px",
        }}
      >
        <p
          style={{
            fontFamily: "'Playfair Display', serif",
            fontWeight: 700,
            fontSize: "15px",
            color: step.color,
            margin: "0 0 6px",
            textDecoration: "underline",
            textDecorationColor: isGold
              ? "rgba(212,168,68,0.3)"
              : "rgba(61,186,116,0.3)",
            textUnderlineOffset: "3px",
          }}
        >
          {step.label}
        </p>

        <p
          style={{
            fontSize: "13px",
            color: "rgba(255,255,255,0.55)",
            lineHeight: 1.7,
            margin: 0,
          }}
        >
          {step.desc}
        </p>
      </div>
    </div>
  );
}

export default function TentangPage({ onBack, onMulai }) {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a1f12",
        color: "white",
        display: "flex",
        flexDirection: "column",
        fontFamily: "'DM Sans', sans-serif",
        overflowX: "hidden",
      }}
    >
      <nav
        className="subpage-nav"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "16px 48px",
          position: "sticky",
          top: 0,
          zIndex: 10,
          background: "rgba(10,31,18,0.88)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <Logo />

        <div
          className="subpage-nav-actions"
          style={{ display: "flex", gap: "16px", alignItems: "center" }}
        >
          <button
            onClick={onBack}
            style={{
              background: "transparent",
              border: "none",
              color: "rgba(255,255,255,0.55)",
              fontSize: "13px",
              cursor: "pointer",
            }}
          >
            ← Kembali
          </button>

          <button
            onClick={onMulai}
            style={{
              padding: "8px 22px",
              borderRadius: "999px",
              border: "none",
              background: "#2d8c5e",
              color: "white",
              fontSize: "13px",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Mulai Sekarang
          </button>
        </div>
      </nav>

      <div style={{ position: "relative" }}>
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            maxWidth: "840px",
            margin: "0 auto",
            padding: "64px 24px 80px",
          }}
        >
          <section
            style={{
              textAlign: "center",
              marginBottom: "72px",
              animation: "slideUp 0.6s ease both",
            }}
          >
            <Badge>AI Career Companion</Badge>

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(32px, 5vw, 52px)",
                lineHeight: 1.15,
                margin: "0 0 20px",
              }}
            >
              Tentang{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "6px",
                }}
              >
                Compana
              </span>
            </h1>

            <p
              style={{
                fontSize: "16px",
                color: "rgba(255,255,255,0.55)",
                lineHeight: 1.8,
                maxWidth: "590px",
                margin: "0 auto",
              }}
            >
              Compana adalah platform AI yang membantu kamu merencanakan dan
              menjalankan perjalanan karir di dunia teknologi — dari titik mana
              pun kamu berada sekarang.
            </p>
          </section>

          <section style={{ marginBottom: "72px" }}>
            <div
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.09)",
                borderRadius: "20px",
                padding: "36px 40px",
              }}
            >
              <h2
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "24px",
                  color: "white",
                  margin: "0 0 16px",
                }}
              >
                Apa itu Compana?
              </h2>

              <p
                style={{
                  fontSize: "15px",
                  color: "rgba(255,255,255,0.6)",
                  lineHeight: 1.85,
                  margin: "0 0 16px",
                }}
              >
                Banyak orang ingin masuk ke dunia tech, tapi bingung harus mulai
                dari mana. Ada yang sudah belajar lama tapi tetap merasa stuck.
                Ada juga yang punya banyak skill, tapi tidak tahu mana yang
                relevan untuk karir yang dituju.
              </p>

              <p
                style={{
                  fontSize: "15px",
                  color: "rgba(255,255,255,0.6)",
                  lineHeight: 1.85,
                  margin: 0,
                }}
              >
                <span style={{ color: "#3dba74", fontWeight: 700 }}>
                  Compana hadir untuk menjawab itu.
                </span>{" "}
                Dengan menganalisis kondisi, skill, dan tujuanmu, Compana
                membuatkan roadmap belajar yang personal — lengkap dengan task,
                feedback, dan dashboard progres.
              </p>
            </div>
          </section>

          <section style={{ marginBottom: "72px" }}>
            <h2
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "28px",
                color: "white",
                margin: "0 0 8px",
                textAlign: "center",
              }}
            >
              Apa yang bisa{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "4px",
                }}
              >
                Compana
              </span>{" "}
              lakukan?
            </h2>

            <p
              style={{
                textAlign: "center",
                fontSize: "14px",
                color: "rgba(255,255,255,0.4)",
                margin: "0 0 36px",
              }}
            >
              Semua fitur dirancang untuk satu tujuan: membantumu bergerak maju.
            </p>

            <div
              className="tentang-feature-grid"
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "14px",
              }}
            >
              {FITUR.map((item) => (
                <FeatureBox key={item.title} item={item} />
              ))}
            </div>
          </section>

          <section style={{ marginBottom: "64px" }}>
            <h2
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "28px",
                color: "white",
                margin: "0 0 8px",
                textAlign: "center",
              }}
            >
              Cara{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "4px",
                }}
              >
                menggunakan
              </span>{" "}
              Compana
            </h2>

            <p
              style={{
                textAlign: "center",
                fontSize: "14px",
                color: "rgba(255,255,255,0.4)",
                margin: "0 0 44px",
              }}
            >
              Ikuti 6 langkah sederhana ini untuk memulai perjalanan karirmu.
            </p>

            <div style={{ position: "relative" }}>
              <div
                className="step-connector"
                style={{
                  position: "absolute",
                  left: "27px",
                  top: "44px",
                  bottom: "44px",
                  width: "2px",
                  background: `linear-gradient(to bottom, ${CONNECTOR_COLOR}, ${CONNECTOR_COLOR})`,
                  zIndex: 0,
                }}
              />

              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                {STEPS.map((step, index) => (
                  <StepItem key={step.no} step={step} index={index} />
                ))}
              </div>
            </div>
          </section>

          <section
            style={{
              textAlign: "center",
              background: "rgba(61,186,116,0.08)",
              border: "1px solid rgba(61,186,116,0.2)",
              borderRadius: "20px",
              padding: "44px 32px",
            }}
          >
            <p
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(22px, 4vw, 30px)",
                margin: "0 0 12px",
                color: "white",
              }}
            >
              Siap memulai{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "4px",
                }}
              >
                perjalananmu?
              </span>
            </p>

            <p
              style={{
                fontSize: "14px",
                color: "rgba(255,255,255,0.5)",
                margin: "0 0 28px",
                lineHeight: 1.7,
              }}
            >
              Analisis karirmu sekarang — gratis, cepat, dan langsung bisa
              dipakai.
            </p>

            <button
              onClick={onMulai}
              style={{
                padding: "14px 40px",
                borderRadius: "12px",
                border: "none",
                background: "#2d8c5e",
                color: "white",
                fontSize: "15px",
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              Mulai Sekarang →
            </button>
          </section>
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

        button {
          transition: all 0.2s ease;
        }

        button:hover {
          transform: translateY(-1px);
        }

        .subpage-nav-actions button:first-child:hover {
          color: rgba(255,255,255,0.9) !important;
        }

        .subpage-nav-actions button:last-child:hover,
        section button:hover {
          background: #3dba74 !important;
          box-shadow: 0 8px 24px rgba(61,186,116,0.25);
        }

        @media (max-width: 760px) {
          .subpage-nav {
            padding: 14px 22px !important;
            flex-direction: column;
            align-items: flex-start !important;
          }

          .subpage-nav-actions {
            width: 100%;
            justify-content: space-between;
          }

          .tentang-feature-grid {
            grid-template-columns: 1fr !important;
          }

          .step-connector {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}