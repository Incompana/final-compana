import { useNavigate } from "react-router-dom";
import {
  getUser,
  getUserDisplayName,
  logout,
} from "../utils/auth";

export default function UserMenu({
  variant = "dark",
  showRole = true,
}) {
  const navigate = useNavigate();

  const user = getUser();
  const username = getUserDisplayName();

  const handleLogout = () => {
    logout();
    navigate("/", { replace: true });
  };

  if (!user) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
        }}
      >
        <button
          onClick={() => navigate("/login")}
          style={{
            padding: "8px 16px",
            borderRadius: "999px",
            border: "1px solid rgba(61,186,116,0.4)",
            background: "transparent",
            color: variant === "dark" ? "white" : "#1a3a2a",
            cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
          }}
        >
          Login
        </button>

        <button
          onClick={() => navigate("/register")}
          style={{
            padding: "8px 16px",
            borderRadius: "999px",
            border: "none",
            background: "#3dba74",
            color: "white",
            cursor: "pointer",
            fontFamily: "'DM Sans', sans-serif",
            fontSize: "13px",
            fontWeight: 600,
          }}
        >
          Register
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "10px",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "7px 12px",
          borderRadius: "999px",
          background:
            variant === "dark"
              ? "rgba(255,255,255,0.06)"
              : "rgba(45,140,94,0.08)",
          border:
            variant === "dark"
              ? "1px solid rgba(255,255,255,0.12)"
              : "1px solid rgba(45,140,94,0.18)",
        }}
      >
        <div
          style={{
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            background: "rgba(61,186,116,0.2)",
            border: "1.5px solid rgba(61,186,116,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#3dba74",
            fontSize: "12px",
            fontWeight: 700,
          }}
        >
          {username.charAt(0).toUpperCase()}
        </div>

        <div>
          <p
            style={{
              margin: 0,
              fontFamily: "'DM Sans', sans-serif",
              fontSize: "13px",
              fontWeight: 600,
              color: variant === "dark" ? "white" : "#1a3a2a",
              lineHeight: 1.2,
            }}
          >
            {username}
          </p>

          {showRole && (
            <p
              style={{
                margin: 0,
                fontFamily: "'DM Sans', sans-serif",
                fontSize: "10px",
                color:
                  variant === "dark"
                    ? "rgba(255,255,255,0.45)"
                    : "rgba(40,70,55,0.55)",
                lineHeight: 1.2,
              }}
            >
              {user.role || "user"}
            </p>
          )}
        </div>
      </div>

      <button
        onClick={handleLogout}
        style={{
          padding: "8px 14px",
          borderRadius: "999px",
          border: "1px solid rgba(224,90,90,0.3)",
          background: "rgba(224,90,90,0.08)",
          color: "#ff8a8a",
          cursor: "pointer",
          fontFamily: "'DM Sans', sans-serif",
          fontSize: "12px",
          fontWeight: 600,
        }}
      >
        Logout
      </button>
    </div>
  );
}