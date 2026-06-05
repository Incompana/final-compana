// src/components/LogoutConfirmModal.jsx

export default function LogoutConfirmModal({
  open,
  onCancel,
  onConfirm,
}) {
  if (!open) return null;

  return (
    <div
      onClick={onCancel}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "rgba(0,0,0,0.58)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        backdropFilter: "blur(6px)",
      }}
    >
      <div
        onClick={(event) => event.stopPropagation()}
        style={{
          width: "100%",
          maxWidth: "430px",
          background: "rgba(255,255,255,0.97)",
          borderRadius: "20px",
          padding: "26px",
          color: "#1a3a2a",
          boxShadow: "0 24px 80px rgba(0,0,0,0.35)",
          animation: "logoutModalUp 0.22s ease both",
        }}
      >
        <div
          style={{
            width: "56px",
            height: "56px",
            borderRadius: "50%",
            background: "rgba(224,90,90,0.12)",
            border: "1.5px solid rgba(224,90,90,0.25)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "25px",
            marginBottom: "16px",
          }}
        >
          🚪
        </div>

        <h2
          style={{
            fontFamily: "'Playfair Display', serif",
            fontSize: "26px",
            fontWeight: 800,
            margin: "0 0 8px",
            color: "#1a3a2a",
          }}
        >
          Keluar dari akun?
        </h2>

        <p
          style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "14px",
            lineHeight: 1.7,
            color: "rgba(40,70,55,0.68)",
            margin: "0 0 22px",
          }}
        >
          Apakah kamu yakin ingin keluar? Kamu perlu login kembali untuk
          melanjutkan perjalanan belajarmu.
        </p>

        <div
          className="logout-modal-actions"
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "10px",
          }}
        >
          <button
            onClick={onCancel}
            style={{
              padding: "12px 16px",
              borderRadius: "12px",
              border: "1px solid rgba(45,140,94,0.22)",
              background: "transparent",
              color: "#2d8c5e",
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "14px",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            Batal
          </button>

          <button
            onClick={onConfirm}
            style={{
              padding: "12px 16px",
              borderRadius: "12px",
              border: "none",
              background: "#e05a5a",
              color: "white",
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "14px",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            Ya, Keluar
          </button>
        </div>
      </div>

      <style>{`
        @keyframes logoutModalUp {
          from {
            opacity: 0;
            transform: translateY(14px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        @media (max-width: 520px) {
          .logout-modal-actions {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}