"use client";

interface Props {
  stats: {
    total_process_msgs: number;
    total_companies_tracked: number;
    total_offers: number;
    total_rejections: number;
    total_interviews: number;
    total_oas: number;
  };
}

const STATS = [
  { key: "total_process_msgs", label: "Total Discussions", icon: "💬", color: "#6366f1" },
  { key: "total_companies_tracked", label: "Companies Tracked", icon: "🏢", color: "#8b5cf6" },
  { key: "total_interviews", label: "Interviews Reported", icon: "🎙️", color: "#3b82f6" },
  { key: "total_oas", label: "OAs Mentioned", icon: "📝", color: "#f97316" },
  { key: "total_offers", label: "Offers Reported", icon: "🎉", color: "#22c55e" },
  { key: "total_rejections", label: "Rejections Reported", icon: "💀", color: "#ef4444" },
] as const;

export default function StatsBar({ stats }: Props) {
  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
      gap: 12,
    }}>
      {STATS.map(({ key, label, icon, color }) => (
        <div key={key} style={{
          background: "#111118",
          border: "1px solid #1e1e2e",
          borderRadius: 12,
          padding: "16px 18px",
          position: "relative",
          overflow: "hidden",
        }}>
          <div style={{
            position: "absolute",
            top: 0, left: 0, right: 0,
            height: 2,
            background: `linear-gradient(90deg, ${color}80, transparent)`,
          }} />
          <div style={{ fontSize: 20, marginBottom: 8 }}>{icon}</div>
          <div style={{ fontSize: 22, fontWeight: 700, color, fontVariantNumeric: "tabular-nums" }}>
            {(stats[key] as number).toLocaleString()}
          </div>
          <div style={{ fontSize: 11, color: "#555577", marginTop: 4, fontWeight: 500 }}>
            {label}
          </div>
        </div>
      ))}
    </div>
  );
}
