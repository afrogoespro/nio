"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

type Message = {
  role: "ai" | "user";
  text: string;
};

const FIRST_MESSAGE = "hey — before i start writing on your behalf, i want to learn how you actually talk. just be yourself here, no need to be formal.\n\nhow would you describe what you do to someone you just met?";

export default function VoicePage() {
  const router = useRouter();
  const params = useSearchParams();
  const campaignId = params.get("campaign");

  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", text: FIRST_MESSAGE },
  ]);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<{ role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [voiceProfile, setVoiceProfile] = useState<Record<string, unknown> | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend() {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    setInput("");
    setMessages((m) => [...m, { role: "user", text: userText }]);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/voice/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: campaignId,
          message: userText,
          history,
        }),
      });

      const data = await res.json();

      setHistory(data.history);
      setMessages((m) => [...m, { role: "ai", text: data.reply }]);

      if (data.training_complete) {
        setDone(true);
        setVoiceProfile(data.voice_profile);
      }
    } catch {
      setMessages((m) => [...m, { role: "ai", text: "something went wrong, try again." }]);
    } finally {
      setLoading(false);
    }
  }

  function handleLaunch() {
    router.push(`/dashboard?campaign=${campaignId}`);
  }

  return (
    <main style={{
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      maxWidth: "600px",
      margin: "0 auto",
      padding: "48px 24px 24px",
    }}>
      <p style={{ color: "#888", fontSize: "12px", marginBottom: "8px" }}>
        voice training / {campaignId}
      </p>
      <h2 style={{ fontSize: "18px", fontWeight: "700", marginBottom: "4px" }}>
        teach me how you talk.
      </h2>
      <p style={{ color: "#888", fontSize: "13px", marginBottom: "32px" }}>
        a few questions. answer like you'd text a friend.
      </p>

      {/* chat window */}
      <div style={{
        border: "1px solid #1a1a1a",
        padding: "20px",
        flex: 1,
        minHeight: "360px",
        maxHeight: "460px",
        overflowY: "auto",
        marginBottom: "16px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: "flex",
            flexDirection: "column",
            alignItems: msg.role === "user" ? "flex-end" : "flex-start",
          }}>
            <p style={{
              fontSize: "11px",
              color: "#888",
              marginBottom: "4px",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
            }}>
              {msg.role === "ai" ? "ai" : "you"}
            </p>
            <div style={{
              maxWidth: "85%",
              background: msg.role === "user" ? "#1a1a1a" : "transparent",
              color: msg.role === "user" ? "#f5f0e8" : "#1a1a1a",
              border: msg.role === "ai" ? "1px solid #ddd" : "none",
              padding: "10px 14px",
              fontSize: "14px",
              lineHeight: "1.6",
              whiteSpace: "pre-wrap",
            }}>
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ alignSelf: "flex-start" }}>
            <p style={{ fontSize: "11px", color: "#888", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "0.08em" }}>ai</p>
            <div style={{ border: "1px solid #ddd", padding: "10px 14px", fontSize: "14px", color: "#888" }}>
              <span className="blink">_</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* voice profile preview */}
      {done && voiceProfile && (
        <div style={{
          border: "1px solid #1a1a1a",
          padding: "16px",
          marginBottom: "16px",
          background: "#1a1a1a",
          color: "#f5f0e8",
        }}>
          <p style={{ fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "10px", color: "#aaa" }}>
            voice profile locked in
          </p>
          <p style={{ fontSize: "13px", marginBottom: "6px" }}>
            vibe: <strong>{voiceProfile.overall_vibe as string}</strong>
          </p>
          <p style={{ fontSize: "13px", marginBottom: "6px" }}>
            energy: {voiceProfile.energy as string} &nbsp;&middot;&nbsp; tone: {voiceProfile.formality as string}
          </p>
          {voiceProfile.example_opener && (
            <p style={{ fontSize: "13px", marginTop: "10px", borderTop: "1px solid #333", paddingTop: "10px", color: "#ccc", fontStyle: "italic" }}>
              example opener: "{voiceProfile.example_opener as string}"
            </p>
          )}
        </div>
      )}

      {/* input */}
      {!done ? (
        <div style={{ display: "flex", gap: "8px" }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleSend(); }}
            placeholder="type your answer..."
            autoFocus
            style={{
              flex: 1,
              border: "1px solid #1a1a1a",
              background: "transparent",
              fontFamily: "inherit",
              fontSize: "14px",
              padding: "10px 14px",
              color: "#1a1a1a",
            }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{
              border: "1px solid #1a1a1a",
              background: input.trim() && !loading ? "#1a1a1a" : "transparent",
              color: input.trim() && !loading ? "#f5f0e8" : "#bbb",
              borderColor: input.trim() && !loading ? "#1a1a1a" : "#bbb",
              fontFamily: "inherit",
              fontSize: "13px",
              fontWeight: "700",
              padding: "10px 20px",
              cursor: input.trim() && !loading ? "pointer" : "default",
              textTransform: "uppercase",
              letterSpacing: "0.05em",
            }}
          >
            send
          </button>
        </div>
      ) : (
        <button
          onClick={handleLaunch}
          style={{
            border: "1px solid #1a1a1a",
            background: "#1a1a1a",
            color: "#f5f0e8",
            fontFamily: "inherit",
            fontSize: "13px",
            fontWeight: "700",
            padding: "12px 24px",
            cursor: "pointer",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            width: "100%",
          }}
        >
          start outreach &rarr;
        </button>
      )}
    </main>
  );
}
