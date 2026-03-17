"use client";

import type { Company } from "@/lib/types";

interface Props {
  companies: Company[];
  onSelect: (c: Company) => void;
}

const STAGE_COLORS = {
  offer: "#22c55e",
  interview: "#3b82f6",
  oa: "#f97316",
  rejection: "#ef4444",
  question: "#6366f1",
};

const STAGE_LABELS = {
  offer: "Offers",
  interview: "Interviews",
  oa: "OAs",
  rejection: "Rejections",
  question: "Questions",
};

function MiniBar({ stages, total }: { stages: Company["stages"]; total: number }) {
  const order = ["offer", "interview", "oa", "rejection", "question"] as const;
  return (
    <div style={{ display: "flex", height: 4, borderRadius: 2, overflow: "hidden", gap: 1 }}>
      {order.map((s) => {
        const w = total > 0 ? (stages[s] / total) * 100 : 0;
        if (w < 1) return null;
        return (
          <div key={s} style={{
            width: `${w}%`,
            background: STAGE_COLORS[s],
            borderRadius: 2,
          }} title={`${STAGE_LABELS[s]}: ${stages[s]}`} />
        );
      })}
    </div>
  );
}

const COMPANY_EMOJIS: Record<string, string> = {
  amazon: "📦", google: "🔍", microsoft: "🪟", meta: "👾", apple: "🍎",
  openai: "🤖", nvidia: "💚", ibm: "🔵", visa: "💳", citadel: "🏰",
  tesla: "⚡", stripe: "💜", "capital one": "💰", ramp: "🚀", coinbase: "₿",
  oracle: "🔴", snapchat: "👻", shopify: "🛍️", tiktok: "🎵", palantir: "👁️",
  "jane street": "🌊", optiver: "📊", "two sigma": "∑", akuna: "🦅",
  bridgewater: "🌉", intuit: "📈", dropbox: "📂", snowflake: "❄️",
  uber: "🚗", airbnb: "🏠", lyft: "🩷", linkedin: "🔗", salesforce: "☁️",
  doordash: "🍔", robinhood: "🏹", figma: "🎨", cloudflare: "🌐",
  "scale ai": "⚖️", "riot games": "⚔️", xai: "✖️", "modal labs": "🔮",
  anthropic: "🧬", "los alamos": "⚛️",
};

export default function CompanyGrid({ companies, onSelect }: Props) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {companies.map((co, i) => {
        const total = co.count;
        const offerRate = total > 0 ? ((co.stages.offer / total) * 100).toFixed(0) : "0";
        const rejRate = total > 0 ? ((co.stages.rejection / total) * 100).toFixed(0) : "0";
        const emoji = COMPANY_EMOJIS[co.name] ?? "🏢";

        return (
          <button
            key={co.name}
            onClick={() => onSelect(co)}
            style={{
              background: "#111118",
              border: "1px solid #1e1e2e",
              borderRadius: 10,
              padding: "12px 14px",
              cursor: "pointer",
              textAlign: "left",
              transition: "border-color 0.15s, background 0.15s",
              width: "100%",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "#6366f140";
              (e.currentTarget as HTMLButtonElement).style.background = "#15151f";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLButtonElement).style.borderColor = "#1e1e2e";
              (e.currentTarget as HTMLButtonElement).style.background = "#111118";
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              {/* Rank */}
              <span style={{ color: "#333355", fontSize: 11, fontWeight: 700, minWidth: 22, fontVariantNumeric: "tabular-nums" }}>
                #{i + 1}
              </span>
              {/* Emoji */}
              <span style={{ fontSize: 16 }}>{emoji}</span>
              {/* Name */}
              <span style={{ fontWeight: 600, fontSize: 14, color: "#e8e8f0", textTransform: "capitalize", flex: 1 }}>
                {co.name}
              </span>
              {/* Total count */}
              <span style={{ color: "#6366f1", fontWeight: 700, fontSize: 14, fontVariantNumeric: "tabular-nums" }}>
                {total}
              </span>
            </div>

            {/* Stage bar */}
            <MiniBar stages={co.stages} total={total} />

            {/* Mini stats row */}
            <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
              {([
                ["🎉", co.stages.offer, "#22c55e", `${offerRate}% offers`],
                ["🎙️", co.stages.interview, "#3b82f6", "interviews"],
                ["📝", co.stages.oa, "#f97316", "OAs"],
                ["💀", co.stages.rejection, "#ef4444", `${rejRate}% rej`],
              ] as [string, number, string, string][]).map(([icon, val, color, label]) => (
                <div key={label} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <span style={{ fontSize: 11 }}>{icon}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color, fontVariantNumeric: "tabular-nums" }}>{val}</span>
                  <span style={{ fontSize: 10, color: "#44445a" }}>{label}</span>
                </div>
              ))}
            </div>
          </button>
        );
      })}
    </div>
  );
}
