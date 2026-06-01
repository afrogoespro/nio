export const dynamic = 'force-dynamic';

"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

type Prospect = {
  id: string;
  first_name: string;
  last_name: string;
  company: string;
  title: string;
  trigger: string;
  subject: string;
  body: string;
};

type Status = "pending" | "approved" | "skipped";

type MessageState = {
  subject: string;
  body: string;
  originalBody: string;
  status: Status;
  learned: boolean;
};

export default function ReviewPage() {
  const params = useSearchParams();
  const campaignId = params.get("campaign") ?? "demo";

  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [loading, setLoading] = useState(true);
  const [states, setStates] = useState<Record<string, MessageState>>({});
  const [activeId, setActiveId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`http://localhost:8000/review/queue/${campaignId}`)
      .then((r) => r.json())
      .then((data) => {
        const list: Prospect[] = data.prospects;
        setProspects(list);
        setStates(
          Object.fromEntries(
            list.map((p) => [
              p.id,
              { subject: p.subject, body: p.body, originalBody: p.body, status: "pending" as Status, learned: false },
            ])
          )
        );
        if (list.length > 0) setActiveId(list[0].id);
      })
      .finally(() => setLoading(false));
  }, [campaignId]);

  if (loading) return (
    <main style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "inherit" }}>
      <p style={{ color: "#888", fontSize: "14px" }}>loading queue<span className="blink">_</span></p>
    </main>
  );

  if (prospects.length === 0) return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", maxWidth: "600px", margin: "0 auto", padding: "48px 24px" }}>
      <p style={{ color: "#888", fontSize: "12px", marginBottom: "8px" }}>nio / review queue</p>
      <h1 style={{ fontSize: "20px", fontWeight: "700", marginBottom: "8px" }}>nothing to review yet.</h1>
      <p style={{ color: "#888", fontSize: "14px" }}>nio is working on finding prospects. check back soon.</p>
    </main>
  );

  const prospect = prospects.find((p) => p.id === activeId)!;
  const state = activeId ? states[activeId] : null;
  const wasEdited = state ? state.body.trim() !== state.originalBody.trim() : false;

  function updateBody(val: string) {
    if (!activeId) return;
    setStates((s) => ({ ...s, [activeId]: { ...s[activeId], body: val } }));
  }

  function updateSubject(val: string) {
    if (!activeId) return;
    setStates((s) => ({ ...s, [activeId]: { ...s[activeId], subject: val } }));
  }

  async function handleApprove() {
    if (!activeId || !state) return;
    setSaving(true);
    try {
      const res = await fetch("http://localhost:8000/review/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: campaignId,
          prospect_id: activeId,
          subject: state.subject,
          body: state.body,
          original_body: state.originalBody,
        }),
      });
      const data = await res.json();
      setStates((s) => ({ ...s, [activeId]: { ...s[activeId], status: "approved", learned: data.learned } }));
      goNext();
    } catch {
      setStates((s) => ({ ...s, [activeId!]: { ...s[activeId!], status: "approved" } }));
      goNext();
    } finally {
      setSaving(false);
    }
  }

  async function handleSkip() {
    if (!activeId) return;
    setSaving(true);
    try {
      await fetch("http://localhost:8000/review/reject", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ campaign_id: campaignId, prospect_id: activeId }),
      });
    } finally {
      setStates((s) => ({ ...s, [activeId!]: { ...s[activeId!], status: "skipped" } }));
      setSaving(false);
      goNext();
    }
  }

  function goNext() {
    const next = prospects.find((p) => p.id !== activeId && states[p.id]?.status === "pending");
    if (next) setActiveId(next.id);
  }

  const counts = {
    pending: Object.values(states).filter((s) => s.status === "pending").length,
    approved: Object.values(states).filter((s) => s.status === "approved").length,
    skipped: Object.values(states).filter((s) => s.status === "skipped").length,
  };

  const allDone = counts.pending === 0;

  return (
    <main style={{ minHeight: "100vh", maxWidth: "900px", margin: "0 auto", padding: "40px 24px", display: "flex", flexDirection: "column", gap: "24px" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <p style={{ color: "#888", fontSize: "12px", marginBottom: "4px" }}>nio / review queue</p>
          <h1 style={{ fontSize: "20px", fontWeight: "700" }}>review outreach</h1>
          <p style={{ color: "#888", fontSize: "13px", marginTop: "4px" }}>
            edit anything that doesn't sound like you. every change teaches nio.
          </p>
        </div>
        <div style={{ display: "flex", border: "1px solid #1a1a1a" }}>
          {[
            { label: "pending", count: counts.pending },
            { label: "approved", count: counts.approved },
            { label: "skipped", count: counts.skipped },
          ].map((s, i) => (
            <div key={s.label} style={{ padding: "8px 16px", borderRight: i < 2 ? "1px solid #1a1a1a" : "none", textAlign: "center" }}>
              <p style={{ fontSize: "18px", fontWeight: "700" }}>{s.count}</p>
              <p style={{ fontSize: "11px", color: "#888", textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</p>
            </div>
          ))}
        </div>
      </div>

      {allDone ? (
        <div style={{ border: "1px solid #1a1a1a", padding: "40px", textAlign: "center" }}>
          <p style={{ fontSize: "18px", fontWeight: "700", marginBottom: "8px" }}>all done.</p>
          <p style={{ color: "#888", fontSize: "14px" }}>
            {counts.approved} messages queued. nio learned from your edits.
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", border: "1px solid #1a1a1a" }}>

          <div style={{ borderRight: "1px solid #1a1a1a" }}>
            {prospects.map((p) => {
              const s = states[p.id];
              const isActive = p.id === activeId;
              return (
                <button
                  key={p.id}
                  onClick={() => setActiveId(p.id)}
                  style={{
                    display: "block", width: "100%", padding: "14px 16px", textAlign: "left",
                    background: isActive ? "#1a1a1a" : "transparent",
                    color: isActive ? "#f5f0e8" : s?.status !== "pending" ? "#bbb" : "#1a1a1a",
                    fontFamily: "inherit", fontSize: "13px",
                    cursor: "pointer", border: "none", borderBottom: "1px solid " + (isActive ? "#333" : "#ddd"),
                  }}
                >
                  <p style={{ fontWeight: "700", marginBottom: "2px" }}>{p.first_name} {p.last_name}</p>
                  <p style={{ fontSize: "12px", opacity: 0.6 }}>{p.company}</p>
                  {s?.status !== "pending" && (
                    <p style={{ fontSize: "11px", marginTop: "4px", opacity: 0.5, textTransform: "uppercase", letterSpacing: "0.06em" }}>{s?.status}</p>
                  )}
                </button>
              );
            })}
          </div>

          {prospect && state && (
            <div style={{ padding: "24px", display: "flex", flexDirection: "column", gap: "16px" }}>
              <div style={{ background: "#f0ebe0", padding: "10px 14px", fontSize: "13px", color: "#666" }}>
                <span style={{ fontWeight: "700", color: "#1a1a1a" }}>hook: </span>
                {prospect.trigger || "no specific trigger found — message is general"}
              </div>

              <div>
                <p style={{ fontSize: "11px", color: "#888", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "6px" }}>subject</p>
                <input
                  type="text"
                  value={state.subject}
                  onChange={(e) => updateSubject(e.target.value)}
                  style={{ width: "100%", border: "1px solid #ddd", background: "transparent", fontFamily: "inherit", fontSize: "14px", padding: "8px 12px", color: "#1a1a1a", outline: "none" }}
                />
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                  <p style={{ fontSize: "11px", color: "#888", textTransform: "uppercase", letterSpacing: "0.08em" }}>message</p>
                  {wasEdited && <p style={{ fontSize: "11px", color: "#888", fontStyle: "italic" }}>edited — nio will learn from this</p>}
                </div>
                <textarea
                  rows={10}
                  value={state.body}
                  onChange={(e) => updateBody(e.target.value)}
                  style={{
                    width: "100%",
                    border: "1px solid " + (wasEdited ? "#1a1a1a" : "#ddd"),
                    background: "transparent", fontFamily: "inherit", fontSize: "14px",
                    lineHeight: "1.7", padding: "12px", resize: "vertical", color: "#1a1a1a", outline: "none",
                  }}
                />
              </div>

              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                <button
                  onClick={handleApprove}
                  disabled={saving}
                  style={{
                    flex: 1, border: "1px solid #1a1a1a", background: "#1a1a1a", color: "#f5f0e8",
                    fontFamily: "inherit", fontSize: "13px", fontWeight: "700", padding: "11px 20px",
                    cursor: saving ? "default" : "pointer", textTransform: "uppercase", letterSpacing: "0.05em", opacity: saving ? 0.5 : 1,
                  }}
                >
                  {saving ? "saving..." : wasEdited ? "approve + teach nio →" : "approve + send →"}
                </button>
                <button
                  onClick={handleSkip}
                  disabled={saving}
                  style={{
                    border: "1px solid #bbb", background: "transparent", color: "#888",
                    fontFamily: "inherit", fontSize: "13px", padding: "11px 20px",
                    cursor: saving ? "default" : "pointer", textTransform: "uppercase", letterSpacing: "0.05em",
                  }}
                >
                  skip
                </button>
              </div>

              {state.learned && (
                <p style={{ fontSize: "12px", color: "#888", fontStyle: "italic" }}>
                  voice profile updated from your edit.
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </main>
  );
}
