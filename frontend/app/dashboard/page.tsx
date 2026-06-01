"use client";

export const dynamic = 'force-dynamic';

import { useSearchParams } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Stats {
  campaign_id: string;
  status: string;
  last_run_at: string | null;
  running: boolean;
  total_prospects: number;
  sent: number;
  sent_today: number;
  replied: number;
  leads: number;
  pending_review: number;
  queued: number;
}

interface Activity {
  id: string;
  first_name: string;
  last_name: string | null;
  company: string | null;
  status: string;
  trigger: string | null;
  created_at: string | null;
  sent_at: string | null;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function statusLabel(s: string): string {
  const map: Record<string, string> = {
    queued: "queued",
    message_ready: "ready to review",
    sent: "sent",
    replied: "replied",
    lead: "lead",
    unsubscribed: "skipped",
  };
  return map[s] || s;
}

export default function DashboardPage() {
  const params = useSearchParams();
  const campaignId = params.get("campaign");

  const [stats, setStats] = useState<Stats | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [runTriggered, setRunTriggered] = useState(false);

  const fetchData = useCallback(async () => {
    if (!campaignId) return;
    try {
      const [statsRes, activityRes] = await Promise.all([
        fetch(`${API}/campaign/${campaignId}/stats`),
        fetch(`${API}/campaign/${campaignId}/activity`),
      ]);
      const statsData = await statsRes.json();
      const activityData = await activityRes.json();
      setStats(statsData);
      setActivity(activityData.activity || []);
    } catch {
      /* silent — will retry on next poll */
    } finally {
      setLoading(false);
    }
  }, [campaignId]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10_000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRun = async () => {
    if (!campaignId || runTriggered) return;
    setRunTriggered(true);
    try {
      await fetch(`${API}/campaign/${campaignId}/run`, { method: "POST" });
      setTimeout(fetchData, 2000);
    } catch {
      setRunTriggered(false);
    }
  };

  const handlePauseResume = async () => {
    if (!campaignId || !stats) return;
    const action = stats.status === "paused" ? "resume" : "pause";
    await fetch(`${API}/campaign/${campaignId}/${action}`, { method: "POST" });
    fetchData();
  };

  const isRunning = stats?.running || runTriggered;
  const isPaused = stats?.status === "paused";

  if (!campaignId) {
    return (
      <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "#888" }}>no campaign selected.</p>
      </main>
    );
  }

  return (
    <main style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      padding: "48px 24px",
      maxWidth: "600px",
      margin: "0 auto",
    }}>

      {/* header */}
      <h1 style={{ fontSize: "24px", fontWeight: "700", marginBottom: "4px" }}>
        your campaign
      </h1>
      <p style={{ color: "#888", fontSize: "13px", marginBottom: "32px" }}>
        {isPaused ? "paused." : isRunning ? "finding and emailing prospects right now..." : "ready to go. hit run to start outreach."}
      </p>

      {/* run button */}
      <button
        onClick={handleRun}
        disabled={!!isRunning || isPaused}
        style={{
          width: "100%",
          padding: "16px",
          fontSize: "14px",
          fontWeight: "700",
          fontFamily: "inherit",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          border: "1px solid #1a1a1a",
          background: isRunning ? "#f5f0e8" : "#1a1a1a",
          color: isRunning ? "#888" : "#f5f0e8",
          cursor: isRunning || isPaused ? "default" : "pointer",
          marginBottom: "32px",
        }}
      >
        {isRunning ? "running..." : isPaused ? "campaign paused" : "run now"}
      </button>

      {/* stats */}
      {!loading && stats && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          gap: "0",
          borderTop: "1px solid #1a1a1a",
          borderLeft: "1px solid #1a1a1a",
          marginBottom: "32px",
        }}>
          {[
            { label: "sent today", value: stats.sent_today },
            { label: "total sent", value: stats.sent },
            { label: "replies", value: stats.replied },
          ].map((stat) => (
            <div key={stat.label} style={{
              padding: "16px",
              borderRight: "1px solid #1a1a1a",
              borderBottom: "1px solid #1a1a1a",
            }}>
              <p style={{ fontSize: "28px", fontWeight: "700" }}>{stat.value}</p>
              <p style={{ fontSize: "12px", color: "#888" }}>{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* review nudge */}
      {stats && stats.pending_review > 0 && (
        <Link
          href={`/review?campaign=${campaignId}`}
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            border: "1px solid #1a1a1a",
            padding: "16px 20px",
            marginBottom: "32px",
            textDecoration: "none",
            color: "inherit",
          }}
        >
          <div>
            <p style={{ fontWeight: "700", fontSize: "14px", marginBottom: "2px" }}>
              {stats.pending_review} message{stats.pending_review !== 1 ? "s" : ""} to review
            </p>
            <p style={{ fontSize: "12px", color: "#888" }}>
              edit anything that doesn't sound like you
            </p>
          </div>
          <span style={{
            background: "#1a1a1a",
            color: "#f5f0e8",
            padding: "8px 18px",
            fontSize: "12px",
            fontWeight: "700",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            whiteSpace: "nowrap",
          }}>
            review
          </span>
        </Link>
      )}

      {/* recent activity */}
      {activity.length > 0 && (
        <div style={{
          border: "1px solid #1a1a1a",
          padding: "20px",
          marginBottom: "32px",
        }}>
          <p style={{
            color: "#888",
            fontSize: "12px",
            marginBottom: "16px",
            textTransform: "uppercase",
            letterSpacing: "0.08em",
          }}>
            recent activity
          </p>
          {activity.slice(0, 10).map((item) => (
            <div key={item.id} style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "baseline",
              paddingBottom: "8px",
              marginBottom: "8px",
              borderBottom: "1px solid #eee",
            }}>
              <div>
                <span style={{
                  fontSize: "13px",
                  fontWeight: item.status === "replied" ? "700" : "400",
                }}>
                  {item.first_name} {item.last_name || ""}
                </span>
                {item.company && (
                  <span style={{ fontSize: "12px", color: "#888" }}> at {item.company}</span>
                )}
              </div>
              <div style={{ textAlign: "right", flexShrink: 0, marginLeft: "12px" }}>
                <span style={{
                  fontSize: "11px",
                  color: item.status === "replied" ? "#1a1a1a" : "#888",
                  fontWeight: item.status === "replied" ? "700" : "400",
                }}>
                  {statusLabel(item.status)}
                </span>
                {item.sent_at && (
                  <span style={{ fontSize: "11px", color: "#aaa", marginLeft: "8px" }}>
                    {timeAgo(item.sent_at)}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* empty state */}
      {!loading && activity.length === 0 && (
        <div style={{
          border: "1px solid #ddd",
          padding: "32px 20px",
          textAlign: "center",
          marginBottom: "32px",
        }}>
          <p style={{ fontSize: "14px", color: "#888", marginBottom: "4px" }}>
            no activity yet
          </p>
          <p style={{ fontSize: "12px", color: "#aaa" }}>
            hit "run now" to start finding and emailing prospects
          </p>
        </div>
      )}

      {/* footer controls */}
      <div style={{ fontSize: "13px", color: "#888", display: "flex", gap: "12px" }}>
        <button
          onClick={handlePauseResume}
          style={{
            background: "none",
            border: "none",
            fontFamily: "inherit",
            fontSize: "13px",
            color: "#888",
            cursor: "pointer",
            textDecoration: "underline",
            padding: 0,
          }}
        >
          {isPaused ? "resume campaign" : "pause campaign"}
        </button>
        <span>&middot;</span>
        <Link href={`/review?campaign=${campaignId}`} style={{ color: "#888" }}>
          review queue
        </Link>
        {stats?.last_run_at && (
          <>
            <span>&middot;</span>
            <span>last run {timeAgo(stats.last_run_at)}</span>
          </>
        )}
      </div>
    </main>
  );
}
