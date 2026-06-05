// src/pages/admin/AdminDashboardPage.jsx

import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { StarField } from "../../components/Shared";
import api from "../../api/axios";
import { logout } from "../../utils/auth";
import toast from "react-hot-toast";

const getBackendBaseUrl = () => {
  const baseURL = api.defaults.baseURL || "http://localhost:5000/api";
  return baseURL.replace(/\/api\/?$/, "");
};

const getFileUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http")) return path;

  return `${getBackendBaseUrl()}${path}`;
};

const formatDate = (value) => {
  if (!value) return "-";

  return new Date(value).toLocaleString("id-ID", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

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
  return user?.username || user?.name || user?.email?.split("@")[0] || "Admin";
};

const StatCard = ({ icon, label, value, desc }) => (
  <div
    style={{
      background: "rgba(255,255,255,0.94)",
      borderRadius: "16px",
      padding: "18px",
      color: "#1a3a2a",
    }}
  >
    <span style={{ fontSize: "22px" }}>{icon}</span>

    <p
      style={{
        margin: "10px 0 2px",
        fontFamily: "'Playfair Display', serif",
        fontSize: "28px",
        fontWeight: 800,
        color: "#1a3a2a",
      }}
    >
      {value}
    </p>

    <p
      style={{
        margin: 0,
        fontSize: "13px",
        fontWeight: 800,
        color: "#2d8c5e",
      }}
    >
      {label}
    </p>

    {desc && (
      <p
        style={{
          margin: "5px 0 0",
          fontSize: "11px",
          color: "rgba(40,70,55,0.55)",
          lineHeight: 1.5,
        }}
      >
        {desc}
      </p>
    )}
  </div>
);

const StatusBadge = ({ status }) => {
  const isPassed = status === "passed";

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "5px",
        padding: "5px 10px",
        borderRadius: "999px",
        background: isPassed
          ? "rgba(61,186,116,0.14)"
          : "rgba(212,168,68,0.14)",
        border: isPassed
          ? "1px solid rgba(61,186,116,0.35)"
          : "1px solid rgba(212,168,68,0.35)",
        color: isPassed ? "#2d8c5e" : "#b87a00",
        fontSize: "11px",
        fontWeight: 800,
        textTransform: "capitalize",
        whiteSpace: "nowrap",
      }}
    >
      {isPassed ? "✓" : "!"} {status || "pending"}
    </span>
  );
};

const EmptyState = ({ title, desc }) => (
  <div
    style={{
      background: "rgba(255,255,255,0.94)",
      borderRadius: "16px",
      padding: "28px",
      textAlign: "center",
      color: "#1a3a2a",
    }}
  >
    <p
      style={{
        margin: "0 0 8px",
        fontSize: "20px",
        fontWeight: 900,
      }}
    >
      {title}
    </p>

    <p
      style={{
        margin: 0,
        fontSize: "13px",
        color: "rgba(40,70,55,0.6)",
        lineHeight: 1.6,
      }}
    >
      {desc}
    </p>
  </div>
);

const DetailList = ({ title, items = [], color = "#2d8c5e" }) => (
  <div
    style={{
      background: "rgba(45,140,94,0.06)",
      border: "1px solid rgba(45,140,94,0.12)",
      borderRadius: "12px",
      padding: "14px",
    }}
  >
    <p
      style={{
        margin: "0 0 10px",
        fontSize: "13px",
        fontWeight: 900,
        color,
      }}
    >
      {title}
    </p>

    {items.length > 0 ? (
      items.map((item, index) => (
        <p
          key={index}
          style={{
            margin: "0 0 8px",
            fontSize: "12px",
            lineHeight: 1.6,
            color: "rgba(40,70,55,0.72)",
          }}
        >
          • {item}
        </p>
      ))
    ) : (
      <p
        style={{
          margin: 0,
          fontSize: "12px",
          color: "rgba(40,70,55,0.52)",
        }}
      >
        Belum ada data.
      </p>
    )}
  </div>
);

export default function AdminDashboardPage() {
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState("submissions");
  const [summary, setSummary] = useState(null);
  const [users, setUsers] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [selectedSubmission, setSelectedSubmission] = useState(null);
  const [loading, setLoading] = useState(true);

  const admin = useMemo(() => getStoredUser(), []);
  const displayName = getDisplayName(admin);

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [summaryResult, usersResult, submissionsResult, feedbackResult] =
          await Promise.allSettled([
            api.get("/admin/summary"),
            api.get("/admin/users"),
            api.get("/admin/submissions"),
            api.get("/admin/feedback"),
          ]);

        if (summaryResult.status === "fulfilled") {
          setSummary(summaryResult.value.data.data);
        }

        if (usersResult.status === "fulfilled") {
          setUsers(usersResult.value.data.data || []);
        }

        if (submissionsResult.status === "fulfilled") {
          setSubmissions(submissionsResult.value.data.data || []);
        }

        if (feedbackResult.status === "fulfilled") {
          setFeedbackList(feedbackResult.value.data.data || []);
        }

        if (
          summaryResult.status === "rejected" &&
          usersResult.status === "rejected" &&
          submissionsResult.status === "rejected" &&
          feedbackResult.status === "rejected"
        ) {
          toast.error("Gagal mengambil data admin");
        }
      } catch (error) {
        console.log(error.response?.data || error.message);
        toast.error("Gagal mengambil data admin");
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  const statCards = [
    {
      icon: "👥",
      label: "Total Users",
      value: summary?.totalUsers ?? 0,
      desc: "User biasa yang terdaftar.",
    },
    {
      icon: "📝",
      label: "Assessments",
      value: summary?.totalAssessments ?? 0,
      desc: "Total assessment yang masuk.",
    },
    {
      icon: "📤",
      label: "Submissions",
      value: summary?.totalSubmissions ?? 0,
      desc: "Total task yang disubmit.",
    },
    {
      icon: "✅",
      label: "Passed",
      value: summary?.totalPassedSubmissions ?? 0,
      desc: "Submission yang lolos.",
    },
    {
      icon: "🔁",
      label: "Revision",
      value: summary?.totalRevisionSubmissions ?? 0,
      desc: "Submission yang perlu revisi.",
    },
    {
      icon: "💬",
      label: "Feedback",
      value: summary?.totalFeedback ?? 0,
      desc: "Feedback yang sudah dibuat.",
    },
  ];

  const filteredSubmissions = useMemo(() => {
    return submissions;
  }, [submissions]);

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
        Memuat admin dashboard...
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
          padding: "20px 34px",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
          background: "rgba(255,255,255,0.035)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "16px",
        }}
      >
        <div>
          <h1
            style={{
              margin: 0,
              fontFamily: "'Playfair Display', serif",
              color: "#3dba74",
              fontSize: "30px",
              textDecoration: "underline",
              textDecorationColor: "rgba(61,186,116,0.35)",
              textUnderlineOffset: "4px",
            }}
          >
            Admin Dashboard
          </h1>

          <p
            style={{
              margin: "6px 0 0",
              fontSize: "13px",
              color: "rgba(255,255,255,0.5)",
            }}
          >
            Halo, {displayName}. Pantau user, submission, feedback, dan file
            task dari sini.
          </p>
        </div>

        <button
          onClick={handleLogout}
          style={{
            padding: "10px 16px",
            borderRadius: "10px",
            border: "1px solid rgba(224,90,90,0.28)",
            background: "rgba(224,90,90,0.09)",
            color: "#ff8a8a",
            fontWeight: 800,
            cursor: "pointer",
          }}
        >
          Logout
        </button>
      </header>

      <main
        style={{
          position: "relative",
          zIndex: 1,
          padding: "28px 34px 48px",
          display: "flex",
          flexDirection: "column",
          gap: "18px",
        }}
      >
        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(6, 1fr)",
            gap: "12px",
          }}
        >
          {statCards.map((item) => (
            <StatCard
              key={item.label}
              icon={item.icon}
              label={item.label}
              value={item.value}
              desc={item.desc}
            />
          ))}
        </section>

        <section
          style={{
            display: "flex",
            gap: "10px",
            flexWrap: "wrap",
          }}
        >
          {[
            {
              id: "submissions",
              label: "Submissions & Feedback",
              count: submissions.length,
            },
            {
              id: "users",
              label: "Users",
              count: users.length,
            },
            {
              id: "feedback",
              label: "Feedback List",
              count: feedbackList.length,
            },
          ].map((tab) => {
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: "10px 14px",
                  borderRadius: "999px",
                  border: isActive
                    ? "1px solid rgba(61,186,116,0.5)"
                    : "1px solid rgba(255,255,255,0.12)",
                  background: isActive
                    ? "rgba(61,186,116,0.14)"
                    : "rgba(255,255,255,0.06)",
                  color: isActive ? "#3dba74" : "rgba(255,255,255,0.65)",
                  fontSize: "13px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                {tab.label} ({tab.count})
              </button>
            );
          })}
        </section>

        {activeTab === "submissions" && (
          <section
            style={{
              background: "rgba(255,255,255,0.94)",
              borderRadius: "18px",
              padding: "18px",
              color: "#1a3a2a",
              overflowX: "auto",
            }}
          >
            <h2
              style={{
                margin: "0 0 14px",
                fontSize: "18px",
                fontWeight: 900,
              }}
            >
              📤 Submissions & Feedback
            </h2>

            {filteredSubmissions.length === 0 ? (
              <EmptyState
                title="Belum ada submission"
                desc="Submission user akan muncul di sini setelah user mengirim task."
              />
            ) : (
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  minWidth: "920px",
                }}
              >
                <thead>
                  <tr>
                    {[
                      "User",
                      "Task",
                      "Status",
                      "Score",
                      "File",
                      "Tanggal",
                      "Aksi",
                    ].map((head) => (
                      <th
                        key={head}
                        style={{
                          textAlign: "left",
                          padding: "12px",
                          fontSize: "12px",
                          color: "rgba(40,70,55,0.58)",
                          borderBottom: "1px solid rgba(0,0,0,0.08)",
                        }}
                      >
                        {head}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {filteredSubmissions.map((item) => {
                    const fileUrl = getFileUrl(item.fileUrl);

                    return (
                      <tr key={item.id}>
                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                            fontSize: "13px",
                            fontWeight: 800,
                          }}
                        >
                          {item.user?.email || "-"}
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                            fontSize: "13px",
                          }}
                        >
                          <strong>{item.task?.title || "-"}</strong>
                          <p
                            style={{
                              margin: "4px 0 0",
                              fontSize: "11px",
                              color: "rgba(40,70,55,0.52)",
                            }}
                          >
                            {item.task?.role || "-"}
                          </p>
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                          }}
                        >
                          <StatusBadge status={item.status} />
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                            fontSize: "13px",
                            fontWeight: 900,
                            color: "#2d8c5e",
                          }}
                        >
                          {item.feedback?.score ?? "-"}
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                            fontSize: "12px",
                          }}
                        >
                          {item.fileUrl ? (
                            <a
                              href={fileUrl}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                color: "#2d8c5e",
                                fontWeight: 900,
                                textDecoration: "none",
                              }}
                            >
                              Lihat File →
                            </a>
                          ) : (
                            <span style={{ color: "rgba(40,70,55,0.45)" }}>
                              Tidak ada
                            </span>
                          )}
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                            fontSize: "12px",
                            color: "rgba(40,70,55,0.62)",
                          }}
                        >
                          {formatDate(item.createdAt)}
                        </td>

                        <td
                          style={{
                            padding: "12px",
                            borderBottom: "1px solid rgba(0,0,0,0.06)",
                          }}
                        >
                          <button
                            onClick={() => setSelectedSubmission(item)}
                            style={{
                              padding: "8px 12px",
                              borderRadius: "9px",
                              border: "none",
                              background: "#2d8c5e",
                              color: "white",
                              fontSize: "12px",
                              fontWeight: 800,
                              cursor: "pointer",
                            }}
                          >
                            Detail
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </section>
        )}

        {activeTab === "users" && (
          <section
            style={{
              background: "rgba(255,255,255,0.94)",
              borderRadius: "18px",
              padding: "18px",
              color: "#1a3a2a",
              overflowX: "auto",
            }}
          >
            <h2
              style={{
                margin: "0 0 14px",
                fontSize: "18px",
                fontWeight: 900,
              }}
            >
              👥 Users
            </h2>

            {users.length === 0 ? (
              <EmptyState
                title="Belum ada user"
                desc="Data user akan muncul setelah ada akun yang terdaftar."
              />
            ) : (
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  minWidth: "760px",
                }}
              >
                <thead>
                  <tr>
                    {["Email", "Role", "Assessment", "Tanggal Daftar"].map(
                      (head) => (
                        <th
                          key={head}
                          style={{
                            textAlign: "left",
                            padding: "12px",
                            fontSize: "12px",
                            color: "rgba(40,70,55,0.58)",
                            borderBottom: "1px solid rgba(0,0,0,0.08)",
                          }}
                        >
                          {head}
                        </th>
                      )
                    )}
                  </tr>
                </thead>

                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td
                        style={{
                          padding: "12px",
                          borderBottom: "1px solid rgba(0,0,0,0.06)",
                          fontWeight: 800,
                          fontSize: "13px",
                        }}
                      >
                        {user.email}
                      </td>

                      <td
                        style={{
                          padding: "12px",
                          borderBottom: "1px solid rgba(0,0,0,0.06)",
                          fontSize: "13px",
                          textTransform: "capitalize",
                        }}
                      >
                        {user.role}
                      </td>

                      <td
                        style={{
                          padding: "12px",
                          borderBottom: "1px solid rgba(0,0,0,0.06)",
                          fontSize: "13px",
                          color: user.isAssessmentDone ? "#2d8c5e" : "#b87a00",
                          fontWeight: 900,
                        }}
                      >
                        {user.isAssessmentDone ? "Selesai" : "Belum"}
                      </td>

                      <td
                        style={{
                          padding: "12px",
                          borderBottom: "1px solid rgba(0,0,0,0.06)",
                          fontSize: "12px",
                          color: "rgba(40,70,55,0.62)",
                        }}
                      >
                        {formatDate(user.createdAt)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        )}

        {activeTab === "feedback" && (
          <section
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: "14px",
            }}
          >
            {feedbackList.length === 0 ? (
              <div style={{ gridColumn: "1 / -1" }}>
                <EmptyState
                  title="Belum ada feedback"
                  desc="Feedback akan muncul setelah user submit task."
                />
              </div>
            ) : (
              feedbackList.map((item) => (
                <div
                  key={item.id}
                  style={{
                    background: "rgba(255,255,255,0.94)",
                    borderRadius: "16px",
                    padding: "18px",
                    color: "#1a3a2a",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      gap: "12px",
                      marginBottom: "12px",
                    }}
                  >
                    <div>
                      <p
                        style={{
                          margin: "0 0 4px",
                          fontSize: "14px",
                          fontWeight: 900,
                        }}
                      >
                        {item.task?.title || "-"}
                      </p>

                      <p
                        style={{
                          margin: 0,
                          fontSize: "12px",
                          color: "rgba(40,70,55,0.55)",
                        }}
                      >
                        {item.user?.email || "-"}
                      </p>
                    </div>

                    <span
                      style={{
                        fontFamily: "'Playfair Display', serif",
                        fontSize: "24px",
                        fontWeight: 900,
                        color: "#2d8c5e",
                      }}
                    >
                      {item.score}
                    </span>
                  </div>

                  <DetailList title="Strengths" items={item.strengths} />
                </div>
              ))
            )}
          </section>
        )}
      </main>

      {selectedSubmission && (
        <div
          onClick={() => setSelectedSubmission(null)}
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 20,
            background: "rgba(0,0,0,0.55)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "24px",
          }}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "100%",
              maxWidth: "760px",
              maxHeight: "88vh",
              overflowY: "auto",
              background: "rgba(255,255,255,0.97)",
              color: "#1a3a2a",
              borderRadius: "18px",
              padding: "22px",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: "12px",
                marginBottom: "16px",
              }}
            >
              <div>
                <h2
                  style={{
                    margin: "0 0 6px",
                    fontFamily: "'Playfair Display', serif",
                    fontSize: "26px",
                  }}
                >
                  Detail Submission
                </h2>

                <p
                  style={{
                    margin: 0,
                    fontSize: "13px",
                    color: "rgba(40,70,55,0.58)",
                  }}
                >
                  {selectedSubmission.user?.email} •{" "}
                  {formatDate(selectedSubmission.createdAt)}
                </p>
              </div>

              <button
                onClick={() => setSelectedSubmission(null)}
                style={{
                  border: "none",
                  background: "rgba(224,90,90,0.12)",
                  color: "#c04040",
                  borderRadius: "10px",
                  padding: "9px 12px",
                  fontWeight: 900,
                  cursor: "pointer",
                  height: "fit-content",
                }}
              >
                Tutup
              </button>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr auto",
                gap: "12px",
                marginBottom: "14px",
              }}
            >
              <div
                style={{
                  background: "rgba(45,140,94,0.07)",
                  border: "1px solid rgba(45,140,94,0.14)",
                  borderRadius: "14px",
                  padding: "14px",
                }}
              >
                <p
                  style={{
                    margin: "0 0 4px",
                    fontSize: "12px",
                    color: "rgba(40,70,55,0.55)",
                  }}
                >
                  Task
                </p>

                <p
                  style={{
                    margin: 0,
                    fontSize: "16px",
                    fontWeight: 900,
                  }}
                >
                  {selectedSubmission.task?.title}
                </p>
              </div>

              <div
                style={{
                  background: "rgba(45,140,94,0.07)",
                  border: "1px solid rgba(45,140,94,0.14)",
                  borderRadius: "14px",
                  padding: "14px",
                  minWidth: "110px",
                  textAlign: "center",
                }}
              >
                <p
                  style={{
                    margin: "0 0 4px",
                    fontSize: "12px",
                    color: "rgba(40,70,55,0.55)",
                  }}
                >
                  Score
                </p>

                <p
                  style={{
                    margin: 0,
                    fontFamily: "'Playfair Display', serif",
                    fontSize: "28px",
                    fontWeight: 900,
                    color: "#2d8c5e",
                  }}
                >
                  {selectedSubmission.feedback?.score ?? "-"}
                </p>
              </div>
            </div>

            <div style={{ marginBottom: "14px" }}>
              <StatusBadge status={selectedSubmission.status} />
            </div>

            <div
              style={{
                background: "rgba(0,0,0,0.035)",
                borderRadius: "14px",
                padding: "14px",
                marginBottom: "14px",
              }}
            >
              <p
                style={{
                  margin: "0 0 8px",
                  fontSize: "13px",
                  fontWeight: 900,
                }}
              >
                Catatan User
              </p>

              <p
                style={{
                  margin: 0,
                  fontSize: "13px",
                  lineHeight: 1.7,
                  color: "rgba(40,70,55,0.72)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {selectedSubmission.content || "Tidak ada catatan."}
              </p>
            </div>

            {selectedSubmission.fileUrl && (
              <div
                style={{
                  background: "rgba(45,140,94,0.08)",
                  border: "1px solid rgba(45,140,94,0.16)",
                  borderRadius: "14px",
                  padding: "14px",
                  marginBottom: "14px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                }}
              >
                <div style={{ minWidth: 0 }}>
                  <p
                    style={{
                      margin: "0 0 4px",
                      fontSize: "13px",
                      fontWeight: 900,
                      wordBreak: "break-word",
                    }}
                  >
                    📎 {selectedSubmission.fileName || "File submission"}
                  </p>

                  <p
                    style={{
                      margin: 0,
                      fontSize: "12px",
                      color: "rgba(40,70,55,0.58)",
                    }}
                  >
                    Bukti file yang dikirim user.
                  </p>
                </div>

                <a
                  href={getFileUrl(selectedSubmission.fileUrl)}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    padding: "9px 13px",
                    borderRadius: "10px",
                    background: "#2d8c5e",
                    color: "white",
                    fontSize: "12px",
                    fontWeight: 900,
                    textDecoration: "none",
                    whiteSpace: "nowrap",
                  }}
                >
                  Lihat File →
                </a>
              </div>
            )}

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr",
                gap: "12px",
              }}
            >
              <DetailList
                title="Strengths"
                items={selectedSubmission.feedback?.strengths || []}
              />

              <DetailList
                title="Weaknesses"
                color="#c04040"
                items={selectedSubmission.feedback?.weaknesses || []}
              />

              <DetailList
                title="Suggestions"
                color="#b87a00"
                items={selectedSubmission.feedback?.suggestions || []}
              />
            </div>
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 1180px) {
          section[style*="grid-template-columns: repeat(6, 1fr)"] {
            grid-template-columns: repeat(3, 1fr) !important;
          }
        }

        @media (max-width: 760px) {
          header {
            flex-direction: column !important;
            align-items: flex-start !important;
          }

          main {
            padding: 22px 18px 42px !important;
          }

          section[style*="grid-template-columns: repeat(6, 1fr)"] {
            grid-template-columns: 1fr !important;
          }

          section[style*="grid-template-columns: repeat(2, 1fr)"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="grid-template-columns: 1fr auto"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}