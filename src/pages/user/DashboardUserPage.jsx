// src/pages/user/DashboardUserPage.jsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { StarField } from "../../components/Shared";
import { logout } from "../../utils/auth";
import api from "../../api/axios";
import toast from "react-hot-toast";
import LogoutConfirmModal from "../../components/LogoutConfirmModal";

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

const NAV_ITEMS = [
  {
    id: "dashboard",
    icon: "📊",
    label: "Dashboard",
    path: "/dashboardUser",
  },
  {
    id: "profile",
    icon: "👤",
    label: "Profil",
    path: "/profile",
  },
  {
    id: "skill-gap",
    icon: "🔍",
    label: "Skill Gap",
    path: "/skill-gap",
  },
  {
    id: "action-plan",
    icon: "🗺️",
    label: "Action Plan",
    path: "/action-plan",
  },
  {
    id: "tasks",
    icon: "📋",
    label: "Task",
    path: "/task-detail",
  },
  {
    id: "feedback",
    icon: "💬",
    label: "Feedback",
    path: "/feedback",
  },
];

const QUICK_ACTIONS = [
  {
    icon: "🔍",
    title: "Skill Gap",
    desc: "Lihat kemampuan yang perlu kamu tingkatkan.",
    path: "/skill-gap",
  },
  {
    icon: "🗺️",
    title: "Action Plan",
    desc: "Ikuti roadmap belajar personalmu.",
    path: "/action-plan",
  },
  {
    icon: "💬",
    title: "Feedback",
    desc: "Lihat hasil evaluasi task terakhir.",
    path: "/feedback",
  },
];

export default function DashboardUserPage() {
  const routerNavigate = useNavigate();

  const [activeNav, setActiveNav] = useState("dashboard");
  const [actionPlan, setActionPlan] = useState(null);
  const [progressData, setProgressData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const user = useMemo(() => getStoredUser(), []);
  const displayName = getDisplayName(user);

  const avatarUrl = useMemo(() => {
    return getFileUrl(user?.avatarUrl || user?.avatar_url);
  }, [user]);

  useEffect(() => {
    const fetchDashboardData = async () => {
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
          toast.error("Gagal mengambil data dashboard");
        }
      } catch (error) {
        console.log(error.response?.data || error.message);
        toast.error("Gagal mengambil data dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const steps = useMemo(() => {
    return actionPlan?.steps || [];
  }, [actionPlan]);

  const completedSteps = steps.filter(
    (step) => step.isCompleted || step.status === "selesai"
  ).length;

  const totalSteps = steps.length;

  const overallPct =
    totalSteps > 0
      ? Math.round((completedSteps / totalSteps) * 100)
      : progressData?.progressPercentage || 0;

  const totalXp = completedSteps * 120;

  const allCompleted = totalSteps > 0 && completedSteps === totalSteps;

  const activeTask = useMemo(() => {
    if (allCompleted) {
      return null;
    }

    return (
      steps.find(
        (step) =>
          step.status === "revision" ||
          step.status === "berjalan" ||
          (!step.isCompleted && !step.isLocked)
      ) ||
      steps.find((step) => !step.isCompleted) ||
      null
    );
  }, [allCompleted, steps]);

  const handleNavigate = (item) => {
    setActiveNav(item.id);
    routerNavigate(item.path);
  };

  const handleOpenLogoutModal = () => {
  setShowLogoutModal(true);
};

const handleConfirmLogout = () => {
  logout();
  setShowLogoutModal(false);
  routerNavigate("/", { replace: true });
};

  const handleContinueTask = () => {
    if (allCompleted) {
      toast.success("Semua task sudah selesai. Keren!");
      return;
    }

    if (!activeTask) {
      toast.error("Belum ada task aktif.");
      return;
    }

    localStorage.setItem("activeTask", JSON.stringify(activeTask));

    routerNavigate("/task-detail");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a1f12",
        display: "flex",
        overflowX: "hidden",
        fontFamily: "'DM Sans', sans-serif",
      }}
    >
      {/* Sidebar */}
      <aside
        style={{
          width: "205px",
          minWidth: "205px",
          background: "rgba(255,255,255,0.04)",
          borderRight: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          flexDirection: "column",
          padding: "20px 12px",
          position: "sticky",
          top: 0,
          height: "100vh",
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            padding: "0 8px",
            marginBottom: "28px",
          }}
        >
          <span style={{ fontSize: "16px" }}>⌘</span>

          <span
            style={{
              fontFamily: "'Playfair Display', serif",
              fontWeight: 700,
              fontSize: "16px",
              color: "#3dba74",
              textDecoration: "underline",
              textDecorationColor: "rgba(61,186,116,0.35)",
              textUnderlineOffset: "3px",
            }}
          >
            Compana
          </span>
        </div>

        {/* Nav */}
        <nav
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            gap: "4px",
          }}
        >
          {NAV_ITEMS.map((item) => {
            const isActive = activeNav === item.id;

            return (
              <button
                key={item.id}
                onClick={() => handleNavigate(item)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  padding: "10px 12px",
                  borderRadius: "9px",
                  border: "none",
                  background: isActive
                    ? "rgba(61,186,116,0.15)"
                    : "transparent",
                  color: isActive
                    ? "#3dba74"
                    : "rgba(255,255,255,0.55)",
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: "13px",
                  fontWeight: isActive ? 600 : 400,
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.18s",
                  borderLeft: isActive
                    ? "2px solid #3dba74"
                    : "2px solid transparent",
                }}
              >
                <span style={{ fontSize: "15px" }}>{item.icon}</span>
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* User Mini + Logout */}
        <div
          style={{
            borderTop: "1px solid rgba(255,255,255,0.08)",
            paddingTop: "16px",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "8px 10px",
              marginBottom: "10px",
            }}
          >
            <div
              style={{
                width: "34px",
                height: "34px",
                borderRadius: "50%",
                background: "rgba(61,186,116,0.2)",
                border: "1.5px solid rgba(61,186,116,0.4)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "13px",
                color: "#3dba74",
                flexShrink: 0,
                overflow: "hidden",
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
                displayName.charAt(0).toUpperCase()
              )}
            </div>

            <div style={{ minWidth: 0 }}>
              <p
                style={{
                  fontSize: "13px",
                  fontWeight: 600,
                  color: "rgba(255,255,255,0.85)",
                  margin: 0,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {displayName}
              </p>

              <p
                style={{
                  fontSize: "11px",
                  color: "rgba(255,255,255,0.35)",
                  margin: 0,
                  textTransform: "capitalize",
                }}
              >
                {user?.role || "user"}
              </p>
            </div>
          </div>

          <button
  onClick={handleOpenLogoutModal}
  style={{
    width: "100%",
    padding: "10px 12px",
    borderRadius: "9px",
    border: "1px solid rgba(224,90,90,0.25)",
    background: "rgba(224,90,90,0.08)",
    color: "#ff8a8a",
    fontFamily: "'DM Sans', sans-serif",
    fontSize: "13px",
    fontWeight: 600,
    cursor: "pointer",
    textAlign: "left",
  }}
>
  🚪 Logout
</button>
        </div>
      </aside>

      {/* Main */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          position: "relative",
        }}
      >
        <div className="mesh-bg" />
        <StarField />

        <div
          style={{
            position: "relative",
            zIndex: 1,
            padding: "28px 32px 44px",
            display: "flex",
            flexDirection: "column",
            gap: "18px",
          }}
        >
          {/* Header */}
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "space-between",
              gap: "16px",
            }}
          >
            <div>
              <h1
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "clamp(24px, 3vw, 32px)",
                  color: "#3dba74",
                  margin: "0 0 6px",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(61,186,116,0.3)",
                  textUnderlineOffset: "4px",
                }}
              >
                Hi, {displayName}
              </h1>

              <p
                style={{
                  fontSize: "13px",
                  color: "rgba(255,255,255,0.48)",
                  margin: 0,
                  lineHeight: 1.6,
                }}
              >
                Lanjutkan perjalanan kariermu dari skill gap, action plan,
                sampai task aktif.
              </p>
            </div>

            <button
              onClick={handleContinueTask}
              disabled={allCompleted}
              style={{
                padding: "10px 22px",
                borderRadius: "10px",
                border: "none",
                background: allCompleted
                  ? "rgba(45,140,94,0.35)"
                  : "#3dba74",
                color: "white",
                fontSize: "14px",
                fontWeight: 700,
                cursor: allCompleted
                  ? "not-allowed"
                  : "pointer",
              }}
            >
              {allCompleted
                ? "Selesai Semua ✓"
                : "Lanjut Task →"}
            </button>
          </div>

          {/* Stats */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, 1fr)",
              gap: "12px",
            }}
          >
            {[
              {
                icon: "🏆",
                value: `${overallPct}%`,
                label: "Overall Progress",
              },
              {
                icon: "✓",
                value: `${completedSteps}/${totalSteps || 0}`,
                label: "Task Selesai",
              },
              {
                icon: "⚡",
                value: `${totalXp} XP`,
                label: "Total XP",
              },
            ].map((stat) => (
              <div
                key={stat.label}
                style={{
                  background: "rgba(255,255,255,0.93)",
                  borderRadius: "14px",
                  padding: "16px 18px",
                }}
              >
                <span style={{ fontSize: "20px" }}>{stat.icon}</span>

                <p
                  style={{
                    fontFamily: "'Playfair Display', serif",
                    fontWeight: 700,
                    fontSize: "24px",
                    color: "#1a3a2a",
                    margin: "8px 0 2px",
                  }}
                >
                  {loading ? "..." : stat.value}
                </p>

                <p
                  style={{
                    fontSize: "12px",
                    color: "rgba(40,70,55,0.55)",
                    margin: 0,
                  }}
                >
                  {stat.label}
                </p>
              </div>
            ))}
          </div>

          {/* Progress card */}
          <div
            style={{
              background: "rgba(255,255,255,0.93)",
              borderRadius: "14px",
              padding: "18px 20px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "10px",
              }}
            >
              <p
                style={{
                  fontSize: "14px",
                  fontWeight: 700,
                  color: "#1a3a2a",
                  margin: 0,
                }}
              >
                🚀 Perjalanan Karier
              </p>

              <span
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "16px",
                  color: "#2d8c5e",
                }}
              >
                {loading ? "..." : `${overallPct}%`}
              </span>
            </div>

            <div
              style={{
                height: "8px",
                borderRadius: "999px",
                background: "rgba(45,140,94,0.12)",
                overflow: "hidden",
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${overallPct}%`,
                  borderRadius: "999px",
                  background: "linear-gradient(90deg,#2d8c5e,#3dba74)",
                  transition: "width 0.5s ease",
                }}
              />
            </div>

            <p
              style={{
                fontSize: "12px",
                color: "rgba(40,70,55,0.55)",
                margin: 0,
                lineHeight: 1.5,
              }}
            >
              {allCompleted
                ? "Semua task dalam action plan sudah selesai. Mantap!"
                : totalSteps > 0
                ? `${completedSteps} dari ${totalSteps} task sudah selesai.`
                : "Progress belum tersedia. Mulai action plan untuk membuka task pertamamu."}
            </p>
          </div>

          {/* Main Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.5fr 1fr",
              gap: "14px",
              alignItems: "start",
            }}
          >
            {/* Active task */}
            <div
              style={{
                background: "rgba(255,255,255,0.93)",
                borderRadius: "14px",
                padding: "22px",
              }}
            >
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "4px 12px",
                  borderRadius: "999px",
                  background: allCompleted
                    ? "rgba(61,186,116,0.13)"
                    : activeTask?.status === "revision"
                    ? "rgba(212,168,68,0.13)"
                    : "rgba(61,186,116,0.1)",
                  border: allCompleted
                    ? "1px solid rgba(61,186,116,0.35)"
                    : activeTask?.status === "revision"
                    ? "1px solid rgba(212,168,68,0.35)"
                    : "1px solid rgba(61,186,116,0.3)",
                  marginBottom: "12px",
                }}
              >
                <span style={{ fontSize: "11px" }}>
                  {allCompleted ? "✓" : "▷"}
                </span>

                <span
                  style={{
                    fontSize: "11px",
                    fontWeight: 700,
                    color: allCompleted
                      ? "#2d8c5e"
                      : activeTask?.status === "revision"
                      ? "#b87a00"
                      : "#2d8c5e",
                  }}
                >
                  {allCompleted
                    ? "Selesai Semua"
                    : activeTask?.status === "revision"
                    ? "Need Revision"
                    : "Progress Sekarang"}
                </span>
              </div>

              <p
                style={{
                  fontFamily: "'Playfair Display', serif",
                  fontWeight: 700,
                  fontSize: "22px",
                  color: "#1a3a2a",
                  margin: "0 0 8px",
                  textDecoration: "underline",
                  textDecorationColor: "rgba(45,140,94,0.3)",
                  textUnderlineOffset: "3px",
                }}
              >
                {activeTask?.title || "Semua task selesai 🎉"}
              </p>

              <p
                style={{
                  fontSize: "13px",
                  color: "rgba(40,70,55,0.65)",
                  margin: "0 0 14px",
                  lineHeight: 1.7,
                }}
              >
                {activeTask?.description ||
                  "Kamu sudah menyelesaikan semua task di action plan ini. Mantap!"}
              </p>

              {activeTask && (
                <div
                  style={{
                    display: "flex",
                    gap: "8px",
                    flexWrap: "wrap",
                    marginBottom: "16px",
                  }}
                >
                  <span
                    style={{
                      fontSize: "11px",
                      color: "rgba(40,70,55,0.65)",
                      background: "rgba(45,140,94,0.1)",
                      border: "1px solid rgba(45,140,94,0.2)",
                      padding: "4px 10px",
                      borderRadius: "6px",
                    }}
                  >
                    Step {activeTask.order}
                  </span>

                  <span
                    style={{
                      fontSize: "11px",
                      color: "rgba(40,70,55,0.65)",
                      background: "rgba(45,140,94,0.1)",
                      border: "1px solid rgba(45,140,94,0.2)",
                      padding: "4px 10px",
                      borderRadius: "6px",
                    }}
                  >
                    ⏱ {activeTask.estimatedDays} hari
                  </span>
                </div>
              )}

              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  onClick={handleContinueTask}
                  disabled={allCompleted}
                  style={{
                    flex: 1,
                    padding: "12px",
                    borderRadius: "10px",
                    border: "none",
                    background: allCompleted
                      ? "rgba(45,140,94,0.35)"
                      : "#2d8c5e",
                    color: "white",
                    fontSize: "14px",
                    fontWeight: 700,
                    cursor: allCompleted
                      ? "not-allowed"
                      : "pointer",
                  }}
                >
                  {allCompleted
                    ? "Selesai Semua ✓"
                    : "Lanjutkan →"}
                </button>

                <button
                  onClick={() => routerNavigate("/action-plan")}
                  style={{
                    padding: "12px 18px",
                    borderRadius: "10px",
                    border: "1px solid rgba(45,140,94,0.3)",
                    background: "transparent",
                    color: "#2d8c5e",
                    fontSize: "13px",
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                >
                  Roadmap
                </button>
              </div>
            </div>

            {/* Quick Actions */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "12px",
              }}
            >
              {QUICK_ACTIONS.map((action) => (
                <button
                  key={action.title}
                  onClick={() => routerNavigate(action.path)}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    background: "rgba(255,255,255,0.93)",
                    border: "none",
                    borderRadius: "14px",
                    padding: "16px 18px",
                    cursor: "pointer",
                  }}
                >
                  <p
                    style={{
                      fontSize: "13px",
                      fontWeight: 700,
                      color: "#1a3a2a",
                      margin: "0 0 6px",
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <span>{action.icon}</span>
                    {action.title}
                  </p>

                  <p
                    style={{
                      fontSize: "12px",
                      color: "rgba(40,70,55,0.55)",
                      margin: 0,
                      lineHeight: 1.5,
                    }}
                  >
                    {action.desc}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>

<LogoutConfirmModal
  open={showLogoutModal}
  onCancel={() => setShowLogoutModal(false)}
  onConfirm={handleConfirmLogout}
/>
      <style>{`
        @media (max-width: 900px) {
          aside {
            display: none !important;
          }

          div[style*="grid-template-columns: repeat(3, 1fr)"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1.5fr 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}