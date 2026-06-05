// src/components/Shared.jsx
import React from "react";

export const STARS = Array.from({ length: 120 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 2 + 0.5,
  opacity: Math.random() * 0.6 + 0.2,
  delay: Math.random() * 3,
}));

export const StarField = () => {
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
      {STARS.map((star) => (
        <div
          key={star.id}
          style={{
            position: "absolute",
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.size}px`,
            height: `${star.size}px`,
            borderRadius: "50%",
            backgroundColor: "rgba(255,255,255,0.9)",
            opacity: star.opacity,
            animation: `twinkle ${2 + star.delay}s ease-in-out infinite`,
            animationDelay: `${star.delay}s`,
          }}
        />
      ))}
    </div>
  );
};

export const Logo = () => (
  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
    <div style={{
      width: "28px", height: "28px",
      background: "rgba(45, 140, 94, 0.8)",
      borderRadius: "6px",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: "14px",
    }}>⌘</div>
    <span style={{ fontFamily: "'Playfair Display', serif", fontWeight: 700, fontSize: "17px", color: "white" }}>
      Compana
    </span>
  </div>
);