// src/pages/FiturPage.jsx

import { Logo, StarField } from "../../components/Shared";

const HERO_STATS = [
  {
    value: "5 menit",
    label: "untuk setup analisis",
  },
  {
    value: "AI-powered",
    label: "rekomendasi personal",
  },
  {
    value: "100% gratis",
    label: "tanpa kartu kredit",
  },
];

const FITUR_UTAMA = [
  {
    id: "analisis",
    icon: "🧠",
    tag: "ANALISIS AI",
    title: "Profil Karir Personal",
    desc: "AI menganalisis kondisimu secara mendalam — latar belakang, skill yang dimiliki, gaya belajar, dan tujuan karir — lalu menghasilkan profil persona yang unik untukmu.",
    highlights: [
      "Confidence score dan target role yang akurat",
      "Identifikasi problem category seperti beginner lost dan skill mismatch",
      "Profil persona yang membantu memahami posisi karirmu",
      "Rekomendasi langkah pertama yang bisa diambil hari ini",
    ],
    color: "#3dba74",
    bg: "rgba(61,186,116,0.06)",
    border: "rgba(61,186,116,0.15)",
  },
  {
    id: "skillgap",
    icon: "🔍",
    tag: "SKILL GAP",
    title: "Analisis Kesenjangan Skill",
    desc: "Compana memetakan skill yang kamu punya, yang perlu diperkuat, dan yang belum ada — sehingga energi belajarmu tidak terbuang ke arah yang salah.",
    highlights: [
      "Skill gap berdasarkan target role",
      "Daftar skill yang perlu dipelajari lebih dulu",
      "Prioritas belajar yang lebih terarah",
      "Hasil analisis mudah dibaca dan dipahami",
    ],
    color: "#d4a844",
    bg: "rgba(212,168,68,0.05)",
    border: "rgba(212,168,68,0.18)",
  },
  {
    id: "actionplan",
    icon: "🗺️",
    tag: "ACTION PLAN",
    title: "Roadmap Belajar Bertahap",
    desc: "Bukan sekadar daftar materi — Compana membuatkan roadmap terstruktur dengan urutan langkah, estimasi waktu, dan task yang bisa dikerjakan satu per satu.",
    highlights: [
      "Roadmap belajar personal",
      "Langkah belajar berurutan",
      "Estimasi waktu per task",
      "Progress terlihat setelah task diselesaikan",
    ],
    color: "#3dba74",
    bg: "rgba(61,186,116,0.06)",
    border: "rgba(61,186,116,0.15)",
  },
  {
    id: "task",
    icon: "📋",
    tag: "TASK & SUBMIT",
    title: "Task dengan Panduan Lengkap",
    desc: "Setiap langkah dilengkapi deskripsi tugas, daftar yang harus dikerjakan, expected output, dan tempat submit file hasil pengerjaan.",
    highlights: [
      "Instruksi task yang jelas",
      "Upload file hasil kerja langsung dari browser",
      "Mendukung gambar, PDF, TXT, dan ZIP project",
      "Catatan tambahan untuk menjelaskan proses belajar",
    ],
    color: "#7c6fe0",
    bg: "rgba(124,111,224,0.05)",
    border: "rgba(124,111,224,0.18)",
  },
  {
    id: "feedback",
    icon: "💬",
    tag: "FEEDBACK AI",
    title: "Evaluasi Task Otomatis",
    desc: "Setelah submit, sistem mengevaluasi pekerjaanmu, memberikan status passed atau revision, serta saran perbaikan yang bisa langsung ditindaklanjuti.",
    highlights: [
      "Status passed atau need revision",
      "Daftar strengths dan weaknesses",
      "Saran perbaikan yang jelas",
      "Skor evaluasi berdasarkan hasil submission",
    ],
    color: "#e05a5a",
    bg: "rgba(224,90,90,0.05)",
    border: "rgba(224,90,90,0.15)",
  },
  {
    id: "dashboard",
    icon: "📊",
    tag: "DASHBOARD",
    title: "Pantau Progres dari Satu Tempat",
    desc: "Dashboard personal menampilkan progress belajar, task aktif, total XP, dan langkah berikutnya supaya perjalanan karirmu lebih mudah dipantau.",
    highlights: [
      "Overall progress belajar",
      "Jumlah task selesai",
      "Total XP dari task",
      "Akses cepat ke skill gap, action plan, dan feedback",
    ],
    color: "#3dba74",
    bg: "rgba(61,186,116,0.06)",
    border: "rgba(61,186,116,0.15)",
  },
];

const PERBANDINGAN = [
  {
    label: "Analisis kondisi dan tujuan karir",
    compana: true,
    manual: false,
  },
  {
    label: "Roadmap belajar yang personal",
    compana: true,
    manual: false,
  },
  {
    label: "Skill gap analysis terstruktur",
    compana: true,
    manual: false,
  },
  {
    label: "Task dengan panduan lengkap",
    compana: true,
    manual: true,
  },
  {
    label: "Feedback otomatis",
    compana: true,
    manual: false,
  },
  {
    label: "Dashboard progres terpadu",
    compana: true,
    manual: false,
  },
  {
    label: "Gratis tanpa kartu kredit",
    compana: true,
    manual: true,
  },
  {
    label: "Bisa mulai dalam 5 menit",
    compana: true,
    manual: false,
  },
];

const pageStyle = {
  minHeight: "100vh",
  background: "#0a1f12",
  color: "white",
  display: "flex",
  flexDirection: "column",
  fontFamily: "'DM Sans', sans-serif",
  overflowX: "hidden",
};

const sectionContainerStyle = {
  position: "relative",
  zIndex: 1,
  maxWidth: "920px",
  margin: "0 auto",
  padding: "64px 24px 88px",
};

function CheckIcon({ active = true, strong = false }) {
  const color = active
    ? strong
      ? "#3dba74"
      : "rgba(61,186,116,0.65)"
    : "rgba(224,90,90,0.55)";

  return (
    <div
      style={{
        width: "22px",
        height: "22px",
        borderRadius: "50%",
        background: active
          ? "rgba(61,186,116,0.12)"
          : "rgba(224,90,90,0.08)",
        border: active
          ? "1.5px solid rgba(61,186,116,0.3)"
          : "1.5px solid rgba(224,90,90,0.22)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <span
        style={{
          color,
          fontSize: "11px",
          fontWeight: 800,
        }}
      >
        {active ? "✓" : "✕"}
      </span>
    </div>
  );
}

function HighlightItem({ text, color }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: "10px",
      }}
    >
      <div
        style={{
          width: "18px",
          height: "18px",
          borderRadius: "50%",
          background: `${color}22`,
          border: `1.5px solid ${color}55`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginTop: "2px",
        }}
      >
        <span
          style={{
            color,
            fontSize: "10px",
            fontWeight: 800,
          }}
        >
          ✓
        </span>
      </div>

      <span
        style={{
          fontSize: "13px",
          color: "rgba(255,255,255,0.66)",
          lineHeight: 1.6,
        }}
      >
        {text}
      </span>
    </div>
  );
}

function HeroBadge() {
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
      Semua Fitur Compana
    </div>
  );
}

function HeroStats() {
  return (
    <div
      className="hero-stats"
      style={{
        display: "inline-flex",
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.09)",
        borderRadius: "16px",
        overflow: "hidden",
      }}
    >
      {HERO_STATS.map((stat, index) => (
        <div
          key={stat.label}
          style={{
            padding: "16px 28px",
            borderRight:
              index < HERO_STATS.length - 1
                ? "1px solid rgba(255,255,255,0.08)"
                : "none",
            textAlign: "center",
          }}
        >
          <p
            style={{
              fontFamily: "'Playfair Display', serif",
              fontWeight: 700,
              fontSize: "18px",
              color: "#3dba74",
              margin: "0 0 3px",
            }}
          >
            {stat.value}
          </p>

          <p
            style={{
              fontSize: "11px",
              color: "rgba(255,255,255,0.4)",
              margin: 0,
            }}
          >
            {stat.label}
          </p>
        </div>
      ))}
    </div>
  );
}

function FeatureCard({ feature, index }) {
  const reverse = index % 2 !== 0;

  return (
    <div
      className="feature-card"
      style={{
        display: "grid",
        gridTemplateColumns: "1fr 1fr",
        background: feature.bg,
        border: `1px solid ${feature.border}`,
        borderRadius: "20px",
        overflow: "hidden",
        animation: `slideUp ${0.35 + index * 0.06}s ease both`,
      }}
    >
      <div
        className="feature-text"
        style={{
          padding: "36px 40px",
          order: reverse ? 2 : 1,
          borderRight: reverse ? "none" : `1px solid ${feature.border}`,
          borderLeft: reverse ? `1px solid ${feature.border}` : "none",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: "16px",
        }}
      >
        <span
          style={{
            fontSize: "10px",
            letterSpacing: "0.12em",
            fontWeight: 800,
            color: feature.color,
            opacity: 0.9,
          }}
        >
          {feature.tag}
        </span>

        <h3
          style={{
            fontFamily: "'Playfair Display', serif",
            fontWeight: 700,
            fontSize: "23px",
            color: "white",
            margin: 0,
            lineHeight: 1.25,
          }}
        >
          {feature.title}
        </h3>

        <p
          style={{
            fontSize: "14px",
            color: "rgba(255,255,255,0.56)",
            lineHeight: 1.75,
            margin: 0,
          }}
        >
          {feature.desc}
        </p>
      </div>

      <div
        className="feature-highlight"
        style={{
          padding: "36px 40px",
          order: reverse ? 1 : 2,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "52px",
            height: "52px",
            borderRadius: "14px",
            background: `${feature.color}18`,
            border: `1.5px solid ${feature.color}40`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "24px",
            marginBottom: "20px",
          }}
        >
          {feature.icon}
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "12px",
          }}
        >
          {feature.highlights.map((highlight) => (
            <HighlightItem
              key={highlight}
              text={highlight}
              color={feature.color}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function ComparisonTable() {
  return (
    <div
      className="comparison-table"
      style={{
        background: "rgba(255,255,255,0.03)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: "16px",
        overflow: "hidden",
      }}
    >
      <div
        className="comparison-row comparison-head"
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 140px 140px",
          padding: "14px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <span
          style={{
            fontSize: "11px",
            color: "rgba(255,255,255,0.3)",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          Fitur
        </span>

        <span
          style={{
            fontSize: "12px",
            fontWeight: 800,
            color: "#3dba74",
            textAlign: "center",
          }}
        >
          Compana
        </span>

        <span
          style={{
            fontSize: "12px",
            fontWeight: 700,
            color: "rgba(255,255,255,0.35)",
            textAlign: "center",
          }}
        >
          Belajar Sendiri
        </span>
      </div>

      {PERBANDINGAN.map((row, index) => (
        <div
          key={row.label}
          className="comparison-row"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 140px 140px",
            padding: "13px 24px",
            borderBottom:
              index < PERBANDINGAN.length - 1
                ? "1px solid rgba(255,255,255,0.05)"
                : "none",
            alignItems: "center",
          }}
        >
          <span
            style={{
              fontSize: "13px",
              color: "rgba(255,255,255,0.66)",
              lineHeight: 1.5,
            }}
          >
            {row.label}
          </span>

          <div style={{ display: "flex", justifyContent: "center" }}>
            <CheckIcon active={row.compana} strong />
          </div>

          <div style={{ display: "flex", justifyContent: "center" }}>
            <CheckIcon active={row.manual} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function FiturPage({ onBack, onMulai }) {
  return (
    <div style={pageStyle}>
      <nav
        className="fitur-nav"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "18px",
          padding: "16px 48px",
          position: "sticky",
          top: 0,
          zIndex: 10,
          background: "rgba(10,31,18,0.9)",
          backdropFilter: "blur(12px)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <Logo />

        <div
          className="fitur-nav-actions"
          style={{
            display: "flex",
            gap: "14px",
            alignItems: "center",
          }}
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

        <div style={sectionContainerStyle}>
          <section
            style={{
              textAlign: "center",
              marginBottom: "64px",
              animation: "slideUp 0.5s ease both",
            }}
          >
            <HeroBadge />

            <h1
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 700,
                fontSize: "clamp(32px, 5vw, 52px)",
                lineHeight: 1.15,
                margin: "0 0 20px",
              }}
            >
              Satu platform,{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "6px",
                }}
              >
                semua yang kamu butuhkan
              </span>
            </h1>

            <p
              style={{
                fontSize: "16px",
                color: "rgba(255,255,255,0.52)",
                lineHeight: 1.8,
                maxWidth: "560px",
                margin: "0 auto 40px",
              }}
            >
              Dari analisis awal sampai task harian dan feedback otomatis,
              Compana membantu perjalanan belajar karirmu jadi lebih jelas,
              terarah, dan mudah dipantau.
            </p>

            <HeroStats />
          </section>

          <section style={{ marginBottom: "80px" }}>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "20px",
              }}
            >
              {FITUR_UTAMA.map((feature, index) => (
                <FeatureCard
                  key={feature.id}
                  feature={feature}
                  index={index}
                />
              ))}
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
              Compana vs{" "}
              <span
                style={{
                  color: "rgba(255,255,255,0.42)",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(255,255,255,0.15)",
                  textUnderlineOffset: "4px",
                }}
              >
                Belajar Sendiri
              </span>
            </h2>

            <p
              style={{
                textAlign: "center",
                fontSize: "14px",
                color: "rgba(255,255,255,0.42)",
                margin: "0 0 36px",
              }}
            >
              Compana membantu kamu belajar dengan arah yang lebih jelas.
            </p>

            <ComparisonTable />
          </section>

          <section
            style={{
              textAlign: "center",
              background: "rgba(61,186,116,0.08)",
              border: "1px solid rgba(61,186,116,0.2)",
              borderRadius: "20px",
              padding: "48px 32px",
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
              Coba semua fitur{" "}
              <span
                style={{
                  color: "#3dba74",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.4)",
                  textUnderlineOffset: "4px",
                }}
              >
                gratis sekarang
              </span>
            </p>

            <p
              style={{
                fontSize: "14px",
                color: "rgba(255,255,255,0.48)",
                margin: "0 0 28px",
                lineHeight: 1.7,
              }}
            >
              Tidak perlu kartu kredit. Mulai analisis karirmu dalam beberapa
              menit.
            </p>

            <button
              onClick={onMulai}
              style={{
                padding: "14px 44px",
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

        .fitur-nav-actions button:first-child:hover {
          color: rgba(255,255,255,0.9) !important;
        }

        .fitur-nav-actions button:last-child:hover,
        section button:hover {
          background: #3dba74 !important;
          box-shadow: 0 8px 24px rgba(61,186,116,0.25);
        }

        .comparison-row:hover {
          background: rgba(255,255,255,0.025);
        }

        @media (max-width: 820px) {
          .fitur-nav {
            padding: 14px 22px !important;
          }

          .feature-card {
            grid-template-columns: 1fr !important;
          }

          .feature-text,
          .feature-highlight {
            order: initial !important;
            border-left: none !important;
            border-right: none !important;
            padding: 28px 26px !important;
          }

          .feature-text {
            border-bottom: 1px solid rgba(255,255,255,0.08) !important;
          }

          .hero-stats {
            display: grid !important;
            grid-template-columns: 1fr !important;
            width: 100%;
          }

          .hero-stats > div {
            border-right: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.08);
          }

          .hero-stats > div:last-child {
            border-bottom: none !important;
          }

          .comparison-table {
            overflow-x: auto;
          }

          .comparison-row {
            grid-template-columns: minmax(220px, 1fr) 110px 110px !important;
            min-width: 440px;
          }
        }

        @media (max-width: 560px) {
          .fitur-nav {
            flex-direction: column;
            align-items: flex-start !important;
          }

          .fitur-nav-actions {
            width: 100%;
            justify-content: space-between;
          }
        }
      `}</style>
    </div>
  );
}