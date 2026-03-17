"use client";

import { useState, useMemo } from "react";
import type { InternData, Company } from "@/lib/types";
import StatsBar from "./StatsBar";
import ActivityTimeline from "./ActivityTimeline";
import CompanyGrid from "./CompanyGrid";
import CompanyModal from "./CompanyModal";
import RecentFeed from "./RecentFeed";

interface Props {
  data: InternData;
}

export default function Dashboard({ data }: Props) {
  const [selected, setSelected] = useState<Company | null>(null);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"count" | "offers" | "interviews" | "rejections">("count");

  const filtered = useMemo(() => {
    let list = [...data.companies];
    if (search.trim()) {
      list = list.filter((c) =>
        c.name.toLowerCase().includes(search.toLowerCase())
      );
    }
    list.sort((a, b) => {
      if (sortBy === "offers") return b.stages.offer - a.stages.offer;
      if (sortBy === "interviews") return b.stages.interview - a.stages.interview;
      if (sortBy === "rejections") return b.stages.rejection - a.stages.rejection;
      return b.count - a.count;
    });
    return list;
  }, [data.companies, search, sortBy]);

  return (
    <div style={{ background: "#0a0a0f", minHeight: "100vh", color: "#e8e8f0" }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid #1e1e2e",
        background: "linear-gradient(180deg, #111118 0%, #0a0a0f 100%)",
        padding: "24px 32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 12,
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <span style={{ fontSize: 22, fontWeight: 700, letterSpacing: "-0.5px" }}>
              🧑‍💻 2026 Intern Process
            </span>
            <span style={{
              background: "#6366f120",
              border: "1px solid #6366f140",
              color: "#818cf8",
              fontSize: 11,
              fontWeight: 600,
              padding: "2px 8px",
              borderRadius: 20,
              letterSpacing: "0.5px",
            }}>LIVE</span>
          </div>
          <div style={{ color: "#6666aa", fontSize: 13 }}>
            Insights from the Discord process channel · {data.stats.total_process_msgs.toLocaleString()} messages · {data.stats.total_companies_tracked} companies
          </div>
        </div>
        <div style={{ color: "#44445a", fontSize: 12 }}>
          Updated {new Date(data.generated).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>

      <div style={{ padding: "24px 32px", maxWidth: 1400, margin: "0 auto" }}>
        {/* Stats bar */}
        <StatsBar stats={data.stats} />

        {/* Timeline */}
        <div style={{ marginTop: 28 }}>
          <SectionHeader title="Activity Over Time" subtitle="Daily !process messages by stage" />
          <ActivityTimeline timeline={data.timeline} />
        </div>

        {/* Company leaderboard */}
        <div style={{ marginTop: 32, display: "grid", gridTemplateColumns: "1fr 340px", gap: 24, alignItems: "start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, flexWrap: "wrap", gap: 12 }}>
              <SectionHeader title="Companies" subtitle={`${filtered.length} tracked`} />
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search company..."
                  style={{
                    background: "#111118",
                    border: "1px solid #2a2a3a",
                    borderRadius: 8,
                    padding: "7px 12px",
                    color: "#e8e8f0",
                    fontSize: 13,
                    outline: "none",
                    width: 160,
                  }}
                />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
                  style={{
                    background: "#111118",
                    border: "1px solid #2a2a3a",
                    borderRadius: 8,
                    padding: "7px 12px",
                    color: "#e8e8f0",
                    fontSize: 13,
                    outline: "none",
                    cursor: "pointer",
                  }}
                >
                  <option value="count">Sort: Activity</option>
                  <option value="offers">Sort: Offers</option>
                  <option value="interviews">Sort: Interviews</option>
                  <option value="rejections">Sort: Rejections</option>
                </select>
              </div>
            </div>
            <CompanyGrid companies={filtered} onSelect={setSelected} />
          </div>

          {/* Recent feed */}
          <div>
            <SectionHeader title="Recent Activity" subtitle="Latest process msgs" />
            <RecentFeed recent={data.recent} onCompanyClick={(name) => {
              const co = data.companies.find((c) => c.name === name);
              if (co) setSelected(co);
            }} />
          </div>
        </div>
      </div>

      {/* Company modal */}
      {selected && (
        <CompanyModal company={selected} onClose={() => setSelected(null)} />
      )}
    </div>
  );
}

function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 15, fontWeight: 600, color: "#e8e8f0" }}>{title}</div>
      <div style={{ fontSize: 12, color: "#5555aa", marginTop: 2 }}>{subtitle}</div>
    </div>
  );
}
