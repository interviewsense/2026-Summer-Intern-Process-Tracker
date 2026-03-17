"use client";

import type { RecentMessage } from "@/lib/types";

const STAGE_COLORS: Record<string, string> = {
  offer: "#22c55e",
  rejection: "#ef4444",
  interview: "#3b82f6",
  oa: "#f97316",
  question: "#6366f1",
};

const STAGE_ICONS: Record<string, string> = {
  offer: "🎉",
  rejection: "💀",
  interview: "🎙️",
  oa: "📝",
  question: "❓",
};

interface Props {
  recent: RecentMessage[];
  onCompanyClick: (name: string) => void;
}

export default function RecentFeed({ recent, onCompanyClick }: Props) {
  return (
    <div style={{
      background: "#111118",
      border: "1px solid #1e1e2e",
      borderRadius: 12,
      overflow: "hidden",
      maxHeight: 680,
      overflowY: "auto",
    }}>
      {recent.map((msg, i) => {
        const color = STAGE_COLORS[msg.stage] ?? "#6366f1";
        const icon = STAGE_ICONS[msg.stage] ?? "💬";
        return (
          <div key={i} style={{
            padding: "12px 14px",
            borderBottom: "1px solid #181826",
            display: "flex",
            gap: 10,
          }}>
            <span style={{ fontSize: 14, marginTop: 1 }}>{icon}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: 12,
                color: "#ccccee",
                lineHeight: 1.5,
                overflow: "hidden",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
              }}>
                {msg.content.replace(/^!process\s*/i, "")}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 5 }}>
                {msg.company && (
                  <button
                    onClick={() => onCompanyClick(msg.company!)}
                    style={{
                      background: `${color}15`,
                      border: `1px solid ${color}30`,
                      color: color,
                      fontSize: 10,
                      fontWeight: 600,
                      padding: "1px 7px",
                      borderRadius: 20,
                      cursor: "pointer",
                      textTransform: "capitalize",
                    }}
                  >
                    {msg.company}
                  </button>
                )}
                <span style={{
                  fontSize: 10,
                  fontWeight: 600,
                  color,
                  textTransform: "capitalize",
                  opacity: 0.7,
                }}>
                  {msg.stage}
                </span>
                <span style={{ fontSize: 10, color: "#33334a", marginLeft: "auto" }}>
                  {msg.date}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
