"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import type { TimelinePoint } from "@/lib/types";

interface Props {
  timeline: TimelinePoint[];
}

const STAGE_COLORS = {
  interview: "#3b82f6",
  oa: "#f97316",
  offer: "#22c55e",
  rejection: "#ef4444",
  question: "#6366f1",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((s: number, p: { value: number }) => s + (p.value || 0), 0);
  return (
    <div style={{
      background: "#111118",
      border: "1px solid #2a2a3a",
      borderRadius: 10,
      padding: "12px 16px",
      fontSize: 12,
    }}>
      <div style={{ color: "#8888aa", marginBottom: 8, fontWeight: 600 }}>{label}</div>
      {payload.map((p: { name: string; value: number; color: string }) => (
        <div key={p.name} style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
          <span style={{ width: 8, height: 8, borderRadius: 2, background: p.color, display: "inline-block" }} />
          <span style={{ color: "#aaaacc", textTransform: "capitalize", minWidth: 70 }}>{p.name}</span>
          <span style={{ color: "#e8e8f0", fontWeight: 600 }}>{p.value}</span>
        </div>
      ))}
      <div style={{ borderTop: "1px solid #2a2a3a", marginTop: 8, paddingTop: 8, color: "#6666aa", display: "flex", justifyContent: "space-between" }}>
        <span>Total</span><span style={{ color: "#e8e8f0", fontWeight: 700 }}>{total}</span>
      </div>
    </div>
  );
}

export default function ActivityTimeline({ timeline }: Props) {
  // Thin out for readability – show every 3rd label
  const data = timeline.map((t, i) => ({
    ...t,
    displayDate: i % 5 === 0 ? t.date.slice(5) : "",
  }));

  return (
    <div style={{
      background: "#111118",
      border: "1px solid #1e1e2e",
      borderRadius: 12,
      padding: "20px 16px 12px",
    }}>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
          <defs>
            {Object.entries(STAGE_COLORS).map(([key, color]) => (
              <linearGradient key={key} id={`grad-${key}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e1e2e" vertical={false} />
          <XAxis dataKey="date" tick={{ fill: "#555577", fontSize: 10 }} tickLine={false} axisLine={false}
            tickFormatter={(v) => v.slice(5)} interval="equidistantPreserveStart" />
          <YAxis tick={{ fill: "#555577", fontSize: 10 }} tickLine={false} axisLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11, color: "#888899", paddingTop: 8 }}
            iconType="circle"
            iconSize={7}
          />
          {(Object.keys(STAGE_COLORS) as (keyof typeof STAGE_COLORS)[]).map((key) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stackId="1"
              stroke={STAGE_COLORS[key]}
              strokeWidth={1.5}
              fill={`url(#grad-${key})`}
              dot={false}
              activeDot={{ r: 3 }}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
