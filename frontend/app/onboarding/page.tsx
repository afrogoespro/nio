"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

type FormData = {
  business_description: string;
  target_description: string;
  goal: string;
  tone: string;
};

const STEPS = [
  {
    id: "business",
    label: "01 / your business",
    question: "describe your business.",
    sub: "what do you do, what do you sell, what makes you different.",
    placeholder: "e.g. i own a record store in brooklyn. we sell vinyl, host listening parties, and have a small online shop...",
    field: "business_description" as keyof FormData,
  },
  {
    id: "target",
    label: "02 / your people",
    question: "who do you want to reach?",
    sub: "describe them like you'd describe them to a friend.",
    placeholder: "e.g. young music fans 18-30, into indie or hip-hop, the kind who actually buy records not just stream...",
    field: "target_description" as keyof FormData,
  },
  {
    id: "goal",
    label: "03 / the goal",
    question: "what do you want to happen?",
    sub: "what counts as a win for you.",
    placeholder: "e.g. come into the store, show up to an event, follow us online, buy something...",
    field: "goal" as keyof FormData,
  },
  {
    id: "tone",
    label: "04 / your voice",
    question: "how do you talk to people?",
    sub: "what tone fits your brand. the messages will sound like you.",
    placeholder: "e.g. casual and genuine, like a friend who loves music. never salesy. short. real.",
    field: "tone" as keyof FormData,
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    business_description: "",
    target_description: "",
    goal: "",
    tone: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const value = formData[current.field];

  function handleChange(val: string) {
    setFormData((prev) => ({ ...prev, [current.field]: val }));
  }

  async function handleNext() {
    if (!value.trim()) return;
    if (!isLast) { setStep((s) => s + 1); return; }

    setLoading(true);
    setError("");
    try {
      const res = await fetch("http://localhost:8000/onboarding/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "demo", ...formData }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      router.push(`/voice?campaign=${data.campaign_id}`);
    } catch {
      setError("something went wrong. try again.");
    } finally {
      setLoading(false);
    }
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

      {/* progress bar */}
      <div style={{ display: "flex", gap: "4px", marginBottom: "40px" }}>
        {STEPS.map((s, i) => (
          <div key={s.id} style={{
            flex: 1,
            height: "2px",
            background: i <= step ? "#1a1a1a" : "#ddd",
          }} />
        ))}
      </div>

      <p style={{ color: "#888", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "12px" }}>
        {current.label}
      </p>

      <h2 style={{ fontSize: "24px", fontWeight: "700", marginBottom: "8px" }}>
        {current.question}
      </h2>
      <p style={{ color: "#888", marginBottom: "24px", fontSize: "14px" }}>
        {current.sub}
      </p>

      <textarea
        key={current.id}
        rows={5}
        placeholder={current.placeholder}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && e.metaKey) handleNext(); }}
        autoFocus
        style={{
          width: "100%",
          background: "transparent",
          border: "1px solid #1a1a1a",
          padding: "14px",
          fontFamily: "inherit",
          fontSize: "14px",
          lineHeight: "1.6",
          color: "#1a1a1a",
          resize: "none",
          marginBottom: "16px",
        }}
      />

      {error && (
        <p style={{ color: "#cc0000", fontSize: "13px", marginBottom: "12px" }}>
          ! {error}
        </p>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        {step > 0 ? (
          <button
            onClick={() => setStep((s) => s - 1)}
            style={{
              background: "none",
              border: "none",
              fontFamily: "inherit",
              fontSize: "13px",
              color: "#888",
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            &larr; back
          </button>
        ) : <span />}

        <button
          onClick={handleNext}
          disabled={!value.trim() || loading}
          style={{
            border: "1px solid #1a1a1a",
            background: !value.trim() || loading ? "transparent" : "#1a1a1a",
            color: !value.trim() || loading ? "#bbb" : "#f5f0e8",
            borderColor: !value.trim() || loading ? "#bbb" : "#1a1a1a",
            fontFamily: "inherit",
            fontSize: "13px",
            fontWeight: "700",
            letterSpacing: "0.05em",
            textTransform: "uppercase",
            padding: "10px 24px",
            cursor: !value.trim() || loading ? "default" : "pointer",
          }}
        >
          {loading ? "working..." : isLast ? "launch &rarr;" : "continue &rarr;"}
        </button>
      </div>

      <p style={{ marginTop: "32px", color: "#bbb", fontSize: "12px" }}>
        cmd+enter to continue
      </p>
    </main>
  );
}
