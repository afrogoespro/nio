import Link from "next/link";

export default function Home() {
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
      <p style={{ color: "#888", marginBottom: "4px", fontSize: "12px", textTransform: "uppercase", letterSpacing: "0.1em" }}>
        nio / natural intelligent outreach
      </p>

      <h1 style={{
        fontSize: "32px",
        fontWeight: "700",
        lineHeight: "1.25",
        marginBottom: "6px",
      }}>
        outreach that sounds<br />
        <span style={{ fontWeight: "400" }}>like you wrote it.</span>
      </h1>

      <p style={{ color: "#888", fontSize: "14px", marginBottom: "32px", lineHeight: "1.6" }}>
        nio learns how you talk, finds the right people,<br />
        and reaches out — a few at a time, every day.
      </p>

      <div style={{
        borderTop: "1px solid #ccc",
        borderBottom: "1px solid #ccc",
        padding: "20px 0",
        marginBottom: "32px",
      }}>
        {[
          ["01", "you describe your business + who you want"],
          ["02", "nio learns your voice in a short chat"],
          ["03", "it finds people and researches each one"],
          ["04", "writes real messages. sends them slowly."],
          ["05", "you get a ping when someone replies"],
        ].map(([num, text]) => (
          <div key={num} style={{ display: "flex", gap: "16px", marginBottom: "10px", alignItems: "baseline" }}>
            <span style={{ color: "#bbb", fontSize: "12px", minWidth: "20px" }}>{num}</span>
            <span style={{ fontSize: "14px", color: "#444" }}>{text}</span>
          </div>
        ))}
      </div>

      <Link
        href="/onboarding"
        style={{
          display: "inline-block",
          border: "1px solid #1a1a1a",
          padding: "11px 28px",
          textDecoration: "none",
          fontWeight: "700",
          fontSize: "13px",
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          width: "fit-content",
          background: "#1a1a1a",
          color: "#f5f0e8",
        }}
      >
        get started →
      </Link>

      <p style={{ marginTop: "40px", color: "#bbb", fontSize: "12px" }}>
        setup takes 2 minutes.
      </p>
    </main>
  );
}
