# NIO — Landing Page, App Redesign & Copy Rules

## Overview

NIO is an AI outreach tool that automates cold email outreach. Users pick a personality-driven AI agent, have a voice/text conversation about their business, review a plan, preview sample emails, and launch. The agent then finds prospects, researches them, writes personalized emails, and sends them on autopilot.

This spec covers three deliverables:
1. Marketing landing page
2. Full app redesign (5 screens)
3. Email copy rules for AI agents

## Target User

Solo founders, freelancers, agency owners, and salespeople who need clients but don't want to spend hours on cold outreach. Non-technical. The product should feel like talking to a person, not configuring software.

---

## 1. Landing Page

### Style & Design System

- **Font:** DM Sans (humanist sans-serif, warm and readable)
- **Background:** Sage green (#f4f9f0)
- **Primary accent:** Soft green (#a8d5a2)
- **Text:** Near-black (#1a1a1a)
- **Supporting colors:** Muted tan (#d4c5a9), lavender (#b8a9d4)
- **Surfaces:** White (#fff) cards with subtle shadows, 16-20px border radius
- **Buttons:** Pill-style (24-28px border radius), dark primary, green secondary
- **Overall feel:** Web 2.0 / early Basecamp era — soft gradients, rounded corners, friendly, approachable. Not the typical modern SaaS look.

### Navbar

- Floating pill-style dark navbar, centered
- Logo "nio" on the left
- Links: How it works, Features, FAQ
- Green rounded CTA button: "Book a demo"
- Sticky on scroll

### Section 1: Hero

- Centered layout
- Headline: "Outreach that sounds like you wrote it."
- Subtext: "NIO finds the right people, writes personalized emails in your voice, and sends them on autopilot. You just close the deals."
- CTA: "Book a demo →" (dark pill button)
- Sub-CTA note: "No credit card. 15-minute setup."

### Section 2: How It Works

- Label: "How it works"
- Title: "Three steps. Then autopilot."
- Three white cards side by side, numbered 1-2-3 with green circle indicators:
  1. "Tell us about your business" — Answer a few questions about what you do and who you're looking for. NIO figures out the rest.
  2. "We find and write" — NIO researches real people, finds something relevant about them, and writes a personal email in your voice.
  3. "You review, we send" — Approve the messages you like, edit anything that feels off. NIO learns from every change you make.

### Section 3: Features

- Label: "Why NIO"
- Title: "Not another spam tool."
- Three cards with tinted backgrounds (green, tan, lavender):
  1. "Learns your voice" (green bg) — NIO trains on how you actually talk through a short conversation. Every edit you make teaches it more.
  2. "Real research, not templates" (tan bg) — Each email references something real — a recent post, a job change, a shared interest. Not "I came across your profile."
  3. "Runs while you sleep" (lavender bg) — Set it once. NIO finds new prospects daily, writes and sends emails, and pings you when someone replies.

### Section 4: FAQ

- Label: "FAQ"
- Title: "The obvious questions."
- Stacked Q&A with divider lines:
  - "Will this spam people?" — No. Every email is unique and personalized. NIO caps sends at about 30 per day and spaces them out to feel natural. This isn't a blast tool — it's one-to-one outreach, automated.
  - "Does it sound like a robot?" — NIO learns your writing style through a short training chat. It picks up your tone, your word choices, even phrases you like. Most people can't tell the difference.
  - "What do I need to get started?" — A description of your business and about 15 minutes. NIO handles the rest — finding prospects, researching them, and writing the first batch of emails for you to review.
  - "How do replies work?" — When someone replies, you get an email notification with their info. From there, you take the conversation — NIO hands it off to you once the door is open.

### Section 5: Final CTA

- Dark rounded block (#1a1a1a) with centered text
- Headline: "Stop writing cold emails. Start getting replies."
- Subtext: "15 minutes to set up. Runs on autopilot from there."
- CTA: "Book a demo →" (green pill button)

### Section 6: Footer

- Minimal, centered
- "© 2026 NIO. All rights reserved."

### CTA Destination

All "Book a demo" buttons link to a Calendly-style booking page (external link, configured via env var).

---

## 2. App Redesign

The app uses the same design system as the landing page: DM Sans, sage green palette, rounded corners, soft shadows. The brutalist/terminal aesthetic (Courier Prime, dark borders) is being replaced entirely.

### Screen 1: Agent Selection

**URL:** `/agents` (or `/` after auth)

**Layout:** Centered container, max-width 860px

**Heading:** "Who do you want working for you?"
**Subtext:** "Pick an agent that matches your style. They handle outreach, research, follow-ups — whatever you need."

**Agent grid:** 4 cards in a single row, equal width:

1. **Sally** — 25, Marketing Creative. "Casual, energetic, and fresh. Great for startups and creative industries." Vibe tag: "casual & energetic"
2. **David** — 35, SDR Veteran. "Polished, professional, strategic. Built for B2B and enterprise outreach." Vibe tag: "corporate & polished"
3. **Jessica** — 47, Communications Expert. "Direct, real, efficient. Gets to the point and gets stuff done. No fluff." Vibe tag: "direct & no-nonsense"
4. **Hans** — Friendly Realist. "Talks like a friend. Warm, honest, real. Cold outreach that feels genuine." Vibe tag: "friendly & real"

**Below the grid, centered (max-width 320px):**

5. **Build Your Own** — Custom Agent. "Train an agent on your voice, your style, your personality. Make a copy of yourself." Vibe tag: "your voice, your rules." Dashed border card style.

**Each agent card has:**
- Realistic avatar photo (circular, 80px)
- Name, age/role subtitle
- 1-2 sentence description
- Vibe tag (green pill)

**Interaction:**
- Click a card to select it (green border + checkmark badge top-right)
- Only one selection at a time
- "Continue →" button fades in after selection

**Agent capabilities:** All agents can perform all tasks (outreach, research, follow-up, lead nurture, inbound response). The agent selection is purely about communication style and tone. The selected agent's personality shapes the conversation, the emails, and the plan presentation.

**Agent types available (task selection happens after agent pick, during voice conversation):**
1. Research — find and profile who'd be a good fit, no emailing
2. Outreach — find people, write personalized emails, send on autopilot
3. Follow-up — re-engage people who didn't reply
4. Lead nurture — warm leads over time with ongoing touches
5. Inbound responder — handle replies, qualify leads

### Screen 2: Voice Setup

**URL:** `/setup?agent={agentName}&campaign={id}`

**Layout:** Centered, max-width 560px

**Heading:** "Talk to {AgentName}"
**Subtext:** "Tell {pronoun} about your business. {pronoun} will figure out the rest."

**Chat container:** White card with rounded corners (24px radius)

**Chat header:**
- Agent's avatar (40px, circular)
- Agent name
- Status indicator: "● listening" (green)

**Input area:**
- Text input field (rounded, placeholder: "Type or tap the mic to talk...")
- Mic button (green circle, 48px) — primary input method
- Speech-to-text for voice input, text as fallback

**Conversation flow:**
The agent asks questions naturally based on their personality. Core information to extract:
1. What the business does
2. Who they're trying to reach
3. What the goal is (meetings, sales, awareness)
4. What task they need (outreach, research, etc.)

The agent's personality affects how they ask. Sally is casual and uses emoji. Jessica is direct and efficient. Hans is warm and conversational.

**Completion:** When the agent has enough information, they transition to the plan screen. No explicit "done" button — the agent says something like "Got it, let me put a plan together for you" and the UI transitions.

### Screen 3: Your Plan

**URL:** `/plan?campaign={id}`

**Layout:** Centered, max-width 640px

**Heading:** "Here's what {AgentName} put together."
**Subtext:** "Review your plan. Tap anything to edit it."

**Three stacked white cards:**

**Card 1 — Your Business:**
- Label: "YOUR BUSINESS" (uppercase, small, muted)
- Editable text block showing NIO's summary of their business
- "tap to edit" hint

**Card 2 — Ideal Customer:**
- Label: "IDEAL CUSTOMER"
- ICP displayed as colored tags:
  - Green tags: job titles (Founders, Head of Product)
  - Tan tags: company attributes (Series A-B, 11-50 employees)
  - Purple tags: industry/signals (Tech/SaaS, Recently funded)
- "tap any tag to edit" hint

**Card 3 — The Plan:**
- Label: "THE PLAN"
- Text summary of what the agent will do
- Two adjustable knobs:
  - Emails per day (slider, default 12)
  - Sending window (slider, default 9am-12pm)

**CTA:** "Looks good — show me examples →" (dark pill button)

### Screen 4: Email Preview

**URL:** `/preview?campaign={id}`

**Layout:** Centered, max-width 640px

**Heading:** "Here's what {AgentName} would send."
**Subtext:** "Edit anything that doesn't sound right. {pronoun} learns from every change."

**2-3 email preview cards, stacked:**

Each card shows:
- **Header:** Prospect name, company info, research trigger tag (purple pill)
- **Subject line:** Bold, displayed as typed
- **Email body:** In a light inset box, showing the full email
- **Actions:** "Edit" (outline button) and "Looks good" (green button)

Emails follow all copy rules defined in Section 3 below.

**CTA:** "Launch {AgentName} →" (dark pill button, larger, centered)

### Screen 5: Dashboard

**URL:** `/dashboard?campaign={id}`

**Layout:** Centered, max-width 640px

**Agent status bar:** White card showing:
- Agent avatar (44px)
- "{AgentName} is working" / "{AgentName} is paused"
- Current activity description ("Researching prospects · sent 8 emails today")
- Green pulse indicator (animated) when active

**Stats grid:** Three cards in a row:
- Sent today (number)
- Total sent (number)
- Replies (number, highlighted green background when > 0)

**Action buttons:** Centered row:
- "Run now" (dark button)
- "Pause {AgentName}" (outline button)
- "Review queue (N)" (outline button, shows count)

**Notification feed:** Stacked white cards showing recent events:
- Green dot: replies ("Priya Sharma replied to your email · 2h ago")
- Tan dot: review needed ("3 messages ready for your review · 4h ago")
- Grey dot: status updates ("Sally sent 12 emails yesterday — 1 reply · 1d ago")

**Polling:** Dashboard auto-refreshes every 10 seconds for live stats.

---

## 3. Email Copy Rules

These rules govern how all AI agents write outreach emails. They are non-negotiable defaults. The agent's personality affects tone and word choice, but these structural rules always apply.

### Subject Lines
- Lowercase always
- 3-5 words max
- Should look like something a friend typed
- No clickbait
- Banned: "Quick question", "Reaching out", "Following up", "Opportunity"

### Opening Line
- Lead with something about the recipient — the research trigger IS the opener
- Banned: "I hope this finds you well", "I came across your profile", "I noticed that..."

### Body
- 3-5 sentences max
- 3rd-5th grade reading level
- Exception: academic, scholarly, or professor targets — match their register
- One idea, one ask per email
- No hyphens or em dashes, ever. Use periods or commas instead.
- Write like texting a professional acquaintance
- No bullet points or feature lists

### Banned Words & Phrases
- leverage, synergy, utilize, reach out, touch base
- "I'd love to", "I'm sure you're busy", "Just checking in"
- Any corporate buzzwords that a normal human wouldn't say out loud

### CTA
- Soft ask only: "Would it be worth a chat?" not "Book a call Tuesday at 3pm"
- One CTA per email, never multiple
- Include an easy out ("If not, no worries" or similar)

### Tone Rules
- Match the selected agent's personality
- No exclamation marks (one absolute max)
- No fake urgency ("limited spots", "this week only", "before it's too late")
- No name-dropping unless genuinely relevant and natural

### Hard Rules (Never Break)
- Never fabricate or exaggerate research ("I saw your post" when no post exists)
- Never pretend to know them ("We met at...", "A mutual friend suggested...")
- Never weaponize pain points ("I noticed your site looks outdated")
- Never send without a real, verified research trigger — skip the prospect entirely
- No spammy unsubscribe footers or tracking pixel language

### Follow-Up Rules
- One light bump, two max total follow-ups
- Short and casual: "floating this back up" energy
- Each follow-up must be shorter than the previous email
- No guilt tripping ("I'm sure you're busy", "Just wanted to make sure you saw this")
- If no reply after 2 follow-ups, move on permanently

### Agent Personality Modifiers

The rules above are the foundation. Each agent layers their personality on top:

- **Sally:** More casual, might use an emoji (one max), shorter sentences, conversational closers
- **David:** More structured, professional phrasing, industry-aware language, confident tone
- **Jessica:** Extremely concise, no filler words at all, direct ask, no small talk
- **Hans:** Warm, personal, might reference something human/relatable, feels like a friend reaching out
- **Custom:** Matches whatever voice profile was extracted during the Build Your Own training

---

## Technical Notes

### Design System Tokens
```
--bg: #f4f9f0
--bg-surface: #ffffff
--bg-surface-alt: #fafcf8
--text: #1a1a1a
--text-muted: #666666
--text-faint: #999999
--accent-green: #a8d5a2
--accent-green-hover: #96c88f
--accent-tan: #d4c5a9
--accent-lavender: #b8a9d4
--tag-green-bg: #eef6e9
--tag-green-text: #4a7a42
--tag-tan-bg: #f0ebe0
--tag-tan-text: #8a7550
--tag-purple-bg: #ede8f4
--tag-purple-text: #6b5b8a
--radius-sm: 12px
--radius-md: 16px
--radius-lg: 20px
--radius-pill: 24px
--radius-card: 20px
--shadow-card: 0 2px 8px rgba(0,0,0,0.04)
--shadow-card-hover: 0 12px 32px rgba(0,0,0,0.1)
--font: 'DM Sans', sans-serif
```

### Pages to Build/Redesign
1. `/` — Landing page (new)
2. `/agents` — Agent selection (new, replaces onboarding entry point)
3. `/setup` — Voice/text conversation (redesign of `/onboarding` + `/voice`)
4. `/plan` — Plan review (new)
5. `/preview` — Email preview (new, incorporates review queue approval)
6. `/dashboard` — Campaign dashboard (redesign)
7. `/review` — Review queue (reskin only, accessed from dashboard)

### Voice Input
- Speech-to-text via Web Speech API (browser native) or a third-party service
- Text input always available as fallback
- Agent responses are text-based (TTS is a future enhancement)

### Agent Avatars
- Realistic photos, not illustrations or emoji
- Stored as static assets or loaded from a CDN
- Consistent across all screens (selection, chat, plan, dashboard)

### Mockup Reference
Interactive mockups are saved in `.superpowers/brainstorm/` for reference during implementation:
- `landing-full.html` — Landing page
- `app-flow-v2.html` — Full 5-screen app flow
- `color-palette.html` — Color direction reference
- `visual-direction.html` — Style direction reference
