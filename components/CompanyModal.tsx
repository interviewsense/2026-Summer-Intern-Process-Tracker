"use client";

import { useEffect, useState } from "react";
import {
  RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from "recharts";
import type { Company } from "@/lib/types";

interface Props {
  company: Company;
  onClose: () => void;
}

const STAGE_COLORS = {
  offer: "#22c55e",
  interview: "#3b82f6",
  oa: "#f97316",
  rejection: "#ef4444",
  question: "#6366f1",
};

const STAGE_ICONS: Record<string, string> = {
  offer: "🎉",
  rejection: "💀",
  interview: "🎙️",
  oa: "📝",
  question: "❓",
};

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

type Tab = "overview" | "messages" | "threads";

export default function CompanyModal({ company: co, onClose }: Props) {
  const [tab, setTab] = useState<Tab>("overview");

  // Close on Escape
  useEffect(() => {
    const h = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  const stages = co.stages;
  const total = co.count;

  const radarData = [
    { axis: "Questions", value: stages.question },
    { axis: "Interviews", value: stages.interview },
    { axis: "OAs", value: stages.oa },
    { axis: "Offers", value: stages.offer },
    { axis: "Rejections", value: stages.rejection },
  ];

  const barData = Object.entries(STAGE_COLORS).map(([key, color]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value: stages[key as keyof typeof stages],
    color,
  }));

  const offerRate = total > 0 ? ((stages.offer / total) * 100).toFixed(1) : "0";
  const rejRate = total > 0 ? ((stages.rejection / total) * 100).toFixed(1) : "0";
  const intRate = total > 0 ? ((stages.interview / total) * 100).toFixed(1) : "0";

  const emoji = COMPANY_EMOJIS[co.name] ?? "🏢";

  return (
    <div
      style={{
        position: "fixed", inset: 0, zIndex: 1000,
        background: "rgba(0,0,0,0.8)",
        backdropFilter: "blur(4px)",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: 24,
      }}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div style={{
        background: "#0d0d16",
        border: "1px solid #2a2a3a",
        borderRadius: 16,
        width: "100%",
        maxWidth: 860,
        maxHeight: "90vh",
        overflow: "hidden",
        display: "flex",
        flexDirection: "column",
      }}>
        {/* Modal header */}
        <div style={{
          padding: "20px 24px",
          borderBottom: "1px solid #1e1e2e",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}>
          <span style={{ fontSize: 28 }}>{emoji}</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 20, fontWeight: 700, textTransform: "capitalize" }}>{co.name}</div>
            <div style={{ fontSize: 12, color: "#5555aa", marginTop: 2 }}>
              {total} total discussions · {co.threads.length} saved threads
            </div>
          </div>
          {/* Key rates */}
          <div style={{ display: "flex", gap: 12 }}>
            <Pill label="Offer rate" value={`${offerRate}%`} color="#22c55e" />
            <Pill label="Interview rate" value={`${intRate}%`} color="#3b82f6" />
            <Pill label="Rej rate" value={`${rejRate}%`} color="#ef4444" />
          </div>
          <button
            onClick={onClose}
            style={{
              background: "#1e1e2e", border: "1px solid #2a2a3a", borderRadius: 8,
              color: "#888899", fontSize: 18, width: 32, height: 32,
              display: "flex", alignItems: "center", justifyContent: "center",
              cursor: "pointer", marginLeft: 8,
            }}
          >×</button>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid #1e1e2e", padding: "0 24px" }}>
          {(["overview", "messages", "threads"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: "12px 16px",
                background: "none",
                border: "none",
                borderBottom: tab === t ? "2px solid #6366f1" : "2px solid transparent",
                color: tab === t ? "#818cf8" : "#555577",
                fontSize: 13,
                fontWeight: tab === t ? 600 : 400,
                cursor: "pointer",
                textTransform: "capitalize",
                marginBottom: -1,
              }}
            >
              {t} {t === "messages" ? `(${co.messages.length})` : t === "threads" ? `(${co.threads.length})` : ""}
            </button>
          ))}
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: "auto", padding: "20px 24px" }}>
          {tab === "overview" && (
            <OverviewTab co={co} radarData={radarData} barData={barData} />
          )}
          {tab === "messages" && <MessagesTab messages={co.messages} />}
          {tab === "threads" && <ThreadsTab threads={co.threads} />}
        </div>
      </div>
    </div>
  );
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{
      background: `${color}12`,
      border: `1px solid ${color}30`,
      borderRadius: 8,
      padding: "6px 12px",
      textAlign: "center",
    }}>
      <div style={{ fontSize: 16, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 10, color: "#55556a" }}>{label}</div>
    </div>
  );
}

// ── Overview tab ─────────────────────────────────────────────────────────────
function OverviewTab({ co, radarData, barData }: {
  co: Company;
  radarData: { axis: string; value: number }[];
  barData: { name: string; value: number; color: string }[];
}) {
  const stages = co.stages;

  // Recent activity last 14 days of daily data
  const recentDaily = co.daily.slice(-30);

  return (
    <div>
      {/* Stage breakdown */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10, marginBottom: 24 }}>
        {(Object.entries(STAGE_COLORS) as [keyof typeof STAGE_COLORS, string][]).map(([key, color]) => (
          <div key={key} style={{
            background: "#111118",
            border: "1px solid #1e1e2e",
            borderRadius: 10,
            padding: "12px",
            textAlign: "center",
          }}>
            <div style={{ fontSize: 18, marginBottom: 6 }}>{STAGE_ICONS[key]}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color }}>{stages[key]}</div>
            <div style={{ fontSize: 10, color: "#44445a", textTransform: "capitalize", marginTop: 4 }}>{key}s</div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>
        {/* Bar chart */}
        <div style={{ background: "#111118", border: "1px solid #1e1e2e", borderRadius: 10, padding: "16px 12px" }}>
          <div style={{ fontSize: 12, color: "#5555aa", marginBottom: 12, fontWeight: 600 }}>Stage Breakdown</div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={barData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "#555577", fontSize: 10 }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fill: "#555577", fontSize: 10 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "#111118", border: "1px solid #2a2a3a", borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: "#8888aa" }}
                itemStyle={{ color: "#e8e8f0" }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {barData.map((entry) => <Cell key={entry.name} fill={entry.color} fillOpacity={0.8} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Radar */}
        <div style={{ background: "#111118", border: "1px solid #1e1e2e", borderRadius: 10, padding: "16px 12px" }}>
          <div style={{ fontSize: 12, color: "#5555aa", marginBottom: 4, fontWeight: 600 }}>Process Shape</div>
          <ResponsiveContainer width="100%" height={168}>
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="65%">
              <PolarGrid stroke="#2a2a3a" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#555577", fontSize: 10 }} />
              <Radar name="count" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.25} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Activity sparkline */}
      {recentDaily.length > 0 && (
        <div style={{ background: "#111118", border: "1px solid #1e1e2e", borderRadius: 10, padding: "14px 16px" }}>
          <div style={{ fontSize: 12, color: "#5555aa", marginBottom: 10, fontWeight: 600 }}>Daily Activity (last 30 days)</div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 48 }}>
            {recentDaily.map((d) => {
              const max = Math.max(...recentDaily.map((x) => x.count));
              const h = max > 0 ? Math.max(3, (d.count / max) * 44) : 3;
              return (
                <div key={d.date} title={`${d.date}: ${d.count}`} style={{
                  flex: 1,
                  height: h,
                  background: "#6366f1",
                  borderRadius: 2,
                  opacity: 0.7,
                  transition: "opacity 0.1s",
                }} />
              );
            })}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
            <span style={{ fontSize: 10, color: "#33334a" }}>{recentDaily[0]?.date}</span>
            <span style={{ fontSize: 10, color: "#33334a" }}>{recentDaily[recentDaily.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Messages tab ──────────────────────────────────────────────────────────────
function MessagesTab({ messages }: { messages: Company["messages"] }) {
  const [filter, setFilter] = useState<string>("all");
  const filtered = filter === "all" ? messages : messages.filter((m) => m.stage === filter);

  return (
    <div>
      <div style={{ display: "flex", gap: 6, marginBottom: 14, flexWrap: "wrap" }}>
        {["all", "offer", "interview", "oa", "rejection", "question"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            style={{
              padding: "4px 12px",
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 600,
              cursor: "pointer",
              background: filter === s ? "#6366f120" : "transparent",
              border: `1px solid ${filter === s ? "#6366f140" : "#2a2a3a"}`,
              color: filter === s ? "#818cf8" : "#555577",
              textTransform: "capitalize",
            }}
          >
            {s === "all" ? "All" : `${STAGE_ICONS[s]} ${s}`}
          </button>
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {filtered.map((msg, i) => {
          const color = STAGE_COLORS[msg.stage as keyof typeof STAGE_COLORS] ?? "#6366f1";
          return (
            <div key={i} style={{
              background: "#111118",
              border: "1px solid #1e1e2e",
              borderRadius: 8,
              padding: "10px 14px",
              borderLeft: `3px solid ${color}`,
            }}>
              <div style={{ fontSize: 13, color: "#ccccee", lineHeight: 1.5 }}>
                {msg.content.replace(/^!process\s*/i, "")}
              </div>
              <div style={{ display: "flex", gap: 10, marginTop: 6, alignItems: "center" }}>
                <span style={{ fontSize: 10, color, fontWeight: 600, textTransform: "capitalize" }}>
                  {STAGE_ICONS[msg.stage]} {msg.stage}
                </span>
                <span style={{ fontSize: 10, color: "#33334a" }}>{msg.author}</span>
                <span style={{ fontSize: 10, color: "#33334a", marginLeft: "auto" }}>{msg.date}</span>
              </div>
            </div>
          );
        })}
        {filtered.length === 0 && (
          <div style={{ color: "#33334a", fontSize: 13, textAlign: "center", padding: 32 }}>No messages for this filter.</div>
        )}
      </div>
    </div>
  );
}

// ── Threads tab ───────────────────────────────────────────────────────────────
function ThreadsTab({ threads }: { threads: Company["threads"] }) {
  const [open, setOpen] = useState<number | null>(0);

  if (threads.length === 0) {
    return (
      <div style={{ color: "#33334a", fontSize: 13, textAlign: "center", padding: 48 }}>
        No saved thread conversations for this company.
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {threads.map((thread, i) => (
        <div key={i} style={{
          background: "#111118",
          border: "1px solid #1e1e2e",
          borderRadius: 10,
          overflow: "hidden",
        }}>
          <button
            onClick={() => setOpen(open === i ? null : i)}
            style={{
              width: "100%",
              background: "none",
              border: "none",
              padding: "12px 16px",
              display: "flex",
              alignItems: "center",
              gap: 10,
              cursor: "pointer",
              textAlign: "left",
            }}
          >
            <span style={{ fontSize: 14, color: "#6366f1" }}>{open === i ? "▾" : "▸"}</span>
            <span style={{ fontSize: 13, fontWeight: 600, color: "#ccccee", flex: 1 }}>{thread.title}</span>
            <span style={{ fontSize: 11, color: "#33334a" }}>{thread.messages.length} msgs</span>
          </button>

          {open === i && (
            <div style={{ borderTop: "1px solid #1e1e2e", padding: "12px 16px 16px", display: "flex", flexDirection: "column", gap: 8 }}>
              {thread.messages.map((msg, j) => (
                <div key={j} style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: "50%",
                    background: `hsl(${(msg.author.charCodeAt(0) * 50) % 360}, 50%, 30%)`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 11, fontWeight: 700, color: "#e8e8f0", flexShrink: 0,
                  }}>
                    {(msg.author || "?")[0].toUpperCase()}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 3 }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: "#8888cc" }}>{msg.author || "unknown"}</span>
                      <span style={{ fontSize: 10, color: "#33334a" }}>{msg.date}</span>
                    </div>
                    <div style={{ fontSize: 13, color: "#bbbbdd", lineHeight: 1.6 }}>{msg.content}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
