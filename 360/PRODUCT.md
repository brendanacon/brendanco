# Unsaid: product notes

**One line:** anonymous 360 feedback for founders and managers. Ask 5+ people, get an AI synthesis of the patterns. No quotes, no names.

## The call: B2B wedge first, social later (maybe)

Two ideas were on the table:

1. **Workplace feedback** (founders and managers asking their team). Clear buyer, clear budget, and a clear price anchor: consultant-run 360s cost tens of thousands. Software at $1k–5k a year is an easy story.
2. **A social network for honest feedback between friends** (starting with uni business students). Big top-of-funnel potential, but ad-only revenue, a heavy moderation burden, and the real risk it turns into a pile-on app. Anonymous-feedback-to-friends apps have a history of blowing up and then being shut down over bullying (Sarahah, Yik Yak, Secret).

**Build #1.** Keep the good part of #2, its growth loop, without the risk: every respondent sees "Want honest feedback of your own?" after they submit. Each round puts the product in front of 5+ new people who now trust the anonymity because they just used it. Uni business societies can still be a launch channel ("get feedback on your first impression before grad interviews") on the *same* product, with rounds you start yourself, not a feed.

## What makes it work

Anonymity is the product. If people don't believe it, they write the safe answer and the report is worthless. So the rules are enforced by the system, not promised:

| Rule | How |
| --- | --- |
| Nothing until N (default 5, floor 3) | Server refuses stats and report below threshold |
| No quotes, ever | Owner never receives raw answers, only the AI synthesis. Prompt forbids quoting or reusing distinctive phrasing |
| We don't know who you asked | Invite tokens stored hashed; labels and links live only on the owner's device |
| No linking answer to person | Responses stored under random keys, no timestamps, no token reference |
| One person, one voice | Each link works once |
| Abuse out, signal in | AI drops pure abuse, keeps the constructive kernel; respondents get a gentle nudge as they type |

Consensus labels (Most people / Several people / One voice) are computed in code from the AI's per-theme counts, so the AI can't overstate agreement.

## Structure

```
360/
  index.html        App: landing, round builder, dashboard + report, respondent flow
  core.js           Shared: templates, validation, stats, synthesis prompt, report clean-up
  worker/           Backend: Cloudflare Worker + KV (deploy steps in worker/README.md)
```

Routes: `#/` landing · `#/new` build a round · `#/r/:id/:adminKey` dashboard · `#/a/:id/:token` answer · `#/sample` demo round · `#/rounds` rounds on this device.

The admin link is the login for now. No accounts until there's a reason (recurring rounds, teams).

## Roadmap, in order

1. **Deploy the worker** so links work across devices. (Blocker for real users.)
2. **Email/Slack sending and nudges** from the dashboard, instead of copy-paste links.
3. **Recurring pulse**: same questions monthly, trend lines between rounds. This is the subscription.
4. **Team accounts**: every manager runs rounds; HR sees aggregate themes only, never individual reports.
5. Durable Objects for strict one-response-per-link, rate limiting, SSO.

## Pricing hypothesis

Starter free (1 open round, 10 people) → Startup $49/mo (unlimited, pulse, trends) → Company ~$4.8k/yr (everyone, digests, SSO). Validate by asking 10 founders to run a free round, then asking whether they'd pay for it monthly.
