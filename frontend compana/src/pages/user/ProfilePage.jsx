// src/pages/user/ProfilePage.jsx

import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { StarField } from "../../components/Shared";
import api from "../../api/axios";
import { logout } from "../../utils/auth";
import toast from "react-hot-toast";

const getStoredUser = () => {
  const savedUser = localStorage.getItem("user");

  if (!savedUser) return null;

  try {
    return JSON.parse(savedUser);
  } catch {
    return null;
  }
};

const getDisplayName = (user) => {
  return (
    user?.username ||
    user?.name ||
    user?.email?.split("@")[0] ||
    "User"
  );
};

const getBackendBaseUrl = () => {
  const baseURL = api.defaults.baseURL || "http://localhost:5000/api";

  return baseURL.replace(/\/api\/?$/, "");
};

const getFileUrl = (path) => {
  if (!path) return "";

  if (path.startsWith("http")) return path;

  return `${getBackendBaseUrl()}${path}`;
};

const InfoRow = ({ label, value, color = "#1a3a2a" }) => (
  <div
    style={{
      padding: "12px 0",
      borderBottom: "1px solid rgba(0,0,0,0.06)",
    }}
  >
    <p
      style={{
        margin: "0 0 4px",
        fontSize: "12px",
        color: "rgba(40,70,55,0.55)",
      }}
    >
      {label}
    </p>

    <p
      style={{
        margin: 0,
        fontSize: "14px",
        fontWeight: 800,
        color,
        wordBreak: "break-word",
      }}
    >
      {value || "-"}
    </p>
  </div>
);

const StatCard = ({ icon, label, value }) => (
  <div
    style={{
      background: "rgba(255,255,255,0.93)",
      borderRadius: "14px",
      padding: "16px 18px",
    }}
  >
    <span style={{ fontSize: "22px" }}>{icon}</span>

    <p
      style={{
        fontFamily: "'Playfair Display', serif",
        fontWeight: 700,
        fontSize: "24px",
        color: "#1a3a2a",
        margin: "8px 0 2px",
      }}
    >
      {value}
    </p>

    <p
      style={{
        fontSize: "12px",
        color: "rgba(40,70,55,0.55)",
        margin: 0,
      }}
    >
      {label}
    </p>
  </div>
);

export default function ProfilePage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [actionPlan, setActionPlan] = useState(null);
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);

  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(() =>
    getFileUrl(currentUser?.avatarUrl || currentUser?.avatar_url)
  );
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  const displayName = getDisplayName(currentUser);

  const isAssessmentDone =
    currentUser?.is_assessment_done ||
    currentUser?.isAssessmentDone ||
    false;

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const [actionPlanResult, progressResult] =
          await Promise.allSettled([
            api.get("/action-plans/me"),
            api.get("/progress/me"),
          ]);

        if (actionPlanResult.status === "fulfilled") {
          setActionPlan(actionPlanResult.value.data.data);
        }

        if (progressResult.status === "fulfilled") {
          setProgressData(progressResult.value.data.data);
        }

        if (
          actionPlanResult.status === "rejected" &&
          progressResult.status === "rejected"
        ) {
          toast.error("Gagal mengambil data profil");
        }
      } catch (error) {
        console.log(error.response?.data || error.message);
        toast.error("Gagal mengambil data profil");
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, []);

  const steps = actionPlan?.steps || [];

  const completedTasks = steps.filter(
    (step) => step.isCompleted || step.status === "selesai"
  ).length;

  const totalTasks = steps.length;

  const progressPercentage =
    totalTasks > 0
      ? Math.round((completedTasks / totalTasks) * 100)
      : progressData?.progressPercentage ?? 0;

  const totalXp = completedTasks * 120;

  const allCompleted = totalTasks > 0 && completedTasks === totalTasks;

  const currentTask = allCompleted
    ? null
    : steps.find(
        (step) =>
          step.status === "revision" ||
          step.status === "berjalan" ||
          (!step.isCompleted && !step.isLocked)
      ) ||
      steps.find((step) => !step.isCompleted) ||
      progressData?.currentTask ||
      null;

  const handleLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  const handleChooseAvatar = (event) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

    if (!allowedTypes.includes(file.type)) {
      toast.error("Foto harus JPG, PNG, atau WEBP");
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      toast.error("Ukuran foto maksimal 2MB");
      return;
    }

    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleUploadAvatar = async () => {
    if (!avatarFile) {
      toast.error("Pilih foto terlebih dahulu");
      return;
    }

    try {
      setUploadingAvatar(true);

      const formData = new FormData();
      formData.append("avatar", avatarFile);

      const res = await api.post("/uploads/avatar", formData);

      const updatedUser = res.data.data.user;

      const mergedUser = {
        ...currentUser,
        ...updatedUser,
        avatarUrl: updatedUser.avatarUrl || updatedUser.avatar_url,
        avatar_url: updatedUser.avatar_url || updatedUser.avatarUrl,
        is_assessment_done:
          updatedUser.is_assessment_done ??
          updatedUser.isAssessmentDone ??
          currentUser?.is_assessment_done,
        isAssessmentDone:
          updatedUser.isAssessmentDone ??
          updatedUser.is_assessment_done ??
          currentUser?.isAssessmentDone,
      };

      localStorage.setItem("user", JSON.stringify(mergedUser));

      setCurrentUser(mergedUser);
      setAvatarPreview(
        getFileUrl(mergedUser.avatarUrl || mergedUser.avatar_url)
      );
      setAvatarFile(null);

      toast.success("Foto profil berhasil diperbarui");
    } catch (error) {
      console.log(error.response?.data || error.message);

      toast.error(
        error.response?.data?.message ||
          "Gagal upload foto profil"
      );
    } finally {
      setUploadingAvatar(false);
    }
  };

  const userInitial = displayName.charAt(0).toUpperCase();

  const avatarUrl = useMemo(() => {
    return avatarPreview || getFileUrl(currentUser?.avatarUrl || currentUser?.avatar_url);
  }, [avatarPreview, currentUser]);

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
        Memuat profil...
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a1f12",
        color: "white",
        fontFamily: "'DM Sans', sans-serif",
        overflowX: "hidden",
      }}
    >
      <div className="mesh-bg" />
      <StarField />

      <header
        style={{
          position: "relative",
          zIndex: 1,
          padding: "20px 36px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        <div>
          <h1
            style={{
              margin: 0,
              fontFamily: "'Playfair Display', serif",
              fontSize: "28px",
              color: "#3dba74",
              textDecoration: "underline",
              textDecorationColor: "rgba(61,186,116,0.35)",
              textUnderlineOffset: "4px",
            }}
          >
            Profil Kamu
          </h1>

          <p
            style={{
              margin: "6px 0 0",
              fontSize: "13px",
              color: "rgba(255,255,255,0.5)",
            }}
          >
            Ringkasan akun dan perjalanan belajar kamu di Compana.
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <button
            onClick={() => navigate("/dashboardUser")}
            style={{
              padding: "10px 16px",
              borderRadius: "10px",
              border: "1px solid rgba(61,186,116,0.3)",
              background: "rgba(61,186,116,0.1)",
              color: "#3dba74",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            ← Dashboard
          </button>

          <button
            onClick={handleLogout}
            style={{
              padding: "10px 16px",
              borderRadius: "10px",
              border: "1px solid rgba(224,90,90,0.3)",
              background: "rgba(224,90,90,0.09)",
              color: "#ff8a8a",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
      </header>

      <main
        style={{
          position: "relative",
          zIndex: 1,
          padding: "28px 36px 48px",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        <section
          style={{
            background: "rgba(255,255,255,0.93)",
            borderRadius: "18px",
            padding: "24px",
            color: "#1a3a2a",
            display: "grid",
            gridTemplateColumns: "auto 1fr auto",
            gap: "18px",
            alignItems: "center",
          }}
        >
          <div
            style={{
              width: "82px",
              height: "82px",
              borderRadius: "50%",
              background: "rgba(61,186,116,0.16)",
              border: "2px solid rgba(61,186,116,0.35)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              overflow: "hidden",
              flexShrink: 0,
            }}
          >
            {avatarUrl ? (
              <img
                src={avatarUrl}
                alt="Avatar"
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }}
              />
            ) : (
              <span
                style={{
                  color: "#2d8c5e",
                  fontWeight: 900,
                  fontSize: "30px",
                }}
              >
                {userInitial}
              </span>
            )}
          </div>

          <div style={{ minWidth: 0 }}>
            <h2
              style={{
                margin: "0 0 6px",
                fontFamily: "'Playfair Display', serif",
                fontSize: "28px",
              }}
            >
              {displayName}
            </h2>

            <p
              style={{
                margin: 0,
                fontSize: "13px",
                color: "rgba(40,70,55,0.6)",
                wordBreak: "break-word",
              }}
            >
              {currentUser?.email || "-"}
            </p>

            <div
              style={{
                display: "flex",
                gap: "8px",
                flexWrap: "wrap",
                marginTop: "12px",
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                style={{ display: "none" }}
                onChange={handleChooseAvatar}
              />

              <button
                onClick={() => fileInputRef.current?.click()}
                style={{
                  padding: "9px 13px",
                  borderRadius: "10px",
                  border: "1px solid rgba(45,140,94,0.28)",
                  background: "rgba(45,140,94,0.08)",
                  color: "#2d8c5e",
                  fontWeight: 800,
                  cursor: "pointer",
                  fontSize: "12px",
                }}
              >
                Pilih Foto
              </button>

              <button
                onClick={handleUploadAvatar}
                disabled={!avatarFile || uploadingAvatar}
                style={{
                  padding: "9px 13px",
                  borderRadius: "10px",
                  border: "none",
                  background:
                    !avatarFile || uploadingAvatar
                      ? "rgba(45,140,94,0.35)"
                      : "#2d8c5e",
                  color: "white",
                  fontWeight: 800,
                  cursor:
                    !avatarFile || uploadingAvatar
                      ? "not-allowed"
                      : "pointer",
                  fontSize: "12px",
                }}
              >
                {uploadingAvatar ? "Mengupload..." : "Upload Foto"}
              </button>
            </div>
          </div>

          <div
            style={{
              padding: "8px 14px",
              borderRadius: "999px",
              background: isAssessmentDone
                ? "rgba(61,186,116,0.13)"
                : "rgba(212,168,68,0.16)",
              border: isAssessmentDone
                ? "1px solid rgba(61,186,116,0.28)"
                : "1px solid rgba(212,168,68,0.3)",
              color: isAssessmentDone ? "#2d8c5e" : "#b87a00",
              fontSize: "12px",
              fontWeight: 800,
              whiteSpace: "nowrap",
            }}
          >
            {isAssessmentDone ? "Assessment Selesai" : "Belum Assessment"}
          </div>
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "12px",
          }}
        >
          <StatCard
            icon="🏆"
            label="Progress"
            value={`${progressPercentage}%`}
          />

          <StatCard
            icon="✓"
            label="Task Selesai"
            value={`${completedTasks}/${totalTasks}`}
          />

          <StatCard
            icon="⚡"
            label="Total XP"
            value={`${totalXp}`}
          />

          <StatCard
            icon="🎯"
            label="Confidence"
            value={`${actionPlan?.confidenceScore ?? 0}%`}
          />
        </section>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "14px",
            alignItems: "start",
          }}
        >
          <div
            style={{
              background: "rgba(255,255,255,0.93)",
              color: "#1a3a2a",
              borderRadius: "16px",
              padding: "20px 22px",
            }}
          >
            <h3
              style={{
                margin: "0 0 12px",
                fontSize: "16px",
                fontWeight: 900,
              }}
            >
              👤 Informasi Akun
            </h3>

            <InfoRow label="Nama" value={displayName} />
            <InfoRow label="Email" value={currentUser?.email || "-"} />
            <InfoRow label="Role Akun" value={currentUser?.role || "user"} />
            <InfoRow
              label="Status Assessment"
              value={isAssessmentDone ? "Selesai" : "Belum selesai"}
              color={isAssessmentDone ? "#2d8c5e" : "#b87a00"}
            />
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.93)",
              color: "#1a3a2a",
              borderRadius: "16px",
              padding: "20px 22px",
            }}
          >
            <h3
              style={{
                margin: "0 0 12px",
                fontSize: "16px",
                fontWeight: 900,
              }}
            >
              🎯 Informasi Karier
            </h3>

            <InfoRow
              label="Target Role"
              value={actionPlan?.targetRole || "Belum ditentukan"}
              color="#2d8c5e"
            />

            <InfoRow
              label="Confidence Score"
              value={`${actionPlan?.confidenceScore ?? 0}%`}
            />

            <InfoRow
              label="Jumlah Langkah"
              value={`${actionPlan?.steps?.length || totalTasks || 0} langkah`}
            />

            <InfoRow
              label="Status Journey"
              value={
                allCompleted
                  ? "Semua task selesai"
                  : currentTask?.title
                  ? "Sedang berjalan"
                  : "Belum ada task aktif"
              }
              color={allCompleted ? "#2d8c5e" : "#b87a00"}
            />
          </div>
        </section>

        <section
          style={{
            background: "rgba(255,255,255,0.93)",
            color: "#1a3a2a",
            borderRadius: "16px",
            padding: "20px 22px",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px",
              marginBottom: "12px",
            }}
          >
            <div>
              <h3
                style={{
                  margin: "0 0 4px",
                  fontSize: "16px",
                  fontWeight: 900,
                }}
              >
                🚀 Progress Belajar
              </h3>

              <p
                style={{
                  margin: 0,
                  fontSize: "12px",
                  color: "rgba(40,70,55,0.58)",
                }}
              >
                {allCompleted
                  ? "Semua task dalam action plan sudah selesai."
                  : currentTask?.title
                  ? `Task sekarang: ${currentTask.title}`
                  : "Belum ada task aktif."}
              </p>
            </div>

            <span
              style={{
                fontFamily: "'Playfair Display', serif",
                fontWeight: 800,
                fontSize: "24px",
                color: "#2d8c5e",
              }}
            >
              {progressPercentage}%
            </span>
          </div>

          <div
            style={{
              height: "9px",
              borderRadius: "999px",
              background: "rgba(45,140,94,0.12)",
              overflow: "hidden",
              marginBottom: "12px",
            }}
          >
            <div
              style={{
                height: "100%",
                width: `${progressPercentage}%`,
                borderRadius: "999px",
                background: "linear-gradient(90deg,#2d8c5e,#3dba74)",
                transition: "width 0.5s ease",
              }}
            />
          </div>

          <p
            style={{
              margin: 0,
              fontSize: "13px",
              color: "rgba(40,70,55,0.65)",
              lineHeight: 1.6,
            }}
          >
            {completedTasks} dari {totalTasks} task sudah selesai. Total XP
            kamu saat ini adalah {totalXp} XP.
          </p>
        </section>

        <section
          style={{
            background: "rgba(255,255,255,0.93)",
            color: "#1a3a2a",
            borderRadius: "16px",
            padding: "20px 22px",
          }}
        >
          <h3
            style={{
              margin: "0 0 12px",
              fontSize: "16px",
              fontWeight: 900,
            }}
          >
            📋 Task Sekarang
          </h3>

          {allCompleted ? (
            <div>
              <p
                style={{
                  margin: "0 0 12px",
                  fontSize: "14px",
                  color: "rgba(40,70,55,0.68)",
                  lineHeight: 1.6,
                }}
              >
                Semua task sudah selesai. Kamu bisa kembali ke dashboard atau
                melihat ulang roadmap belajar kamu.
              </p>

              <button
                onClick={() => navigate("/dashboardUser")}
                style={{
                  padding: "11px 18px",
                  borderRadius: "10px",
                  border: "none",
                  background: "#2d8c5e",
                  color: "white",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Kembali ke Dashboard
              </button>
            </div>
          ) : currentTask ? (
            <div>
              <p
                style={{
                  margin: "0 0 6px",
                  fontFamily: "'Playfair Display', serif",
                  fontSize: "22px",
                  fontWeight: 800,
                  color: "#1a3a2a",
                }}
              >
                {currentTask.title}
              </p>

              <p
                style={{
                  margin: "0 0 14px",
                  fontSize: "13px",
                  color: "rgba(40,70,55,0.68)",
                  lineHeight: 1.7,
                }}
              >
                {currentTask.description}
              </p>

              <button
                onClick={() => {
                  localStorage.setItem(
                    "activeTask",
                    JSON.stringify(currentTask)
                  );
                  navigate("/task-detail");
                }}
                style={{
                  padding: "11px 18px",
                  borderRadius: "10px",
                  border: "none",
                  background: "#2d8c5e",
                  color: "white",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Lanjutkan Task →
              </button>
            </div>
          ) : (
            <p
              style={{
                margin: 0,
                fontSize: "13px",
                color: "rgba(40,70,55,0.68)",
              }}
            >
              Belum ada task aktif. Buka Action Plan untuk memulai.
            </p>
          )}
        </section>
      </main>

      <style>{`
        @media (max-width: 900px) {
          section[style*="grid-template-columns: repeat(4, 1fr)"] {
            grid-template-columns: repeat(2, 1fr) !important;
          }

          section[style*="grid-template-columns: 1fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }

        @media (max-width: 640px) {
          header {
            flex-direction: column !important;
            align-items: flex-start !important;
          }

          section[style*="grid-template-columns: repeat(4, 1fr)"] {
            grid-template-columns: 1fr !important;
          }

          section[style*="grid-template-columns: auto 1fr auto"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}