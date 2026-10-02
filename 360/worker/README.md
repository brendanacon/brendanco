# Unsaid API (Cloudflare Worker)

Without this, brendanco.com/360 runs in **preview mode**: rounds live in one browser, so invite links only work on the device that created them. Deploying the worker makes links work for anyone, anywhere. It takes about five minutes and fits in Cloudflare's free tier.

```sh
cd 360/worker
npx wrangler login
npx wrangler kv namespace create UNSAID      # copy the id it prints into wrangler.toml
npx wrangler secret put OPENAI_API_KEY        # paste the OpenAI key
npx wrangler deploy                           # prints https://unsaid-api.<you>.workers.dev
```

Then set `API_BASE` near the top of the script in `360/index.html` to that URL and push.

To test against a deployed worker before changing the code, open the browser console on brendanco.com/360 and run
`localStorage.setItem('unsaid-api', 'https://unsaid-api.<you>.workers.dev')`, then reload.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| POST | `/rounds` | Create a round. Returns `id`, `adminKey` and the invite `tokens` (shown once, never stored in plain text). |
| GET | `/rounds/:id/invite/:token` | Questions for a respondent, plus whether the link is used. |
| POST | `/rounds/:id/invite/:token` | Submit answers. One response per token. |
| GET | `/rounds/:id/admin/:key` | Progress. Rating totals and the report appear only once the threshold is met. |
| POST | `/rounds/:id/admin/:key/report` | Generate (or refresh) the AI synthesis. |

## Known limits before this is a real product

- KV is eventually consistent, so two submits on one token within a second or so could both land. A Durable Object per round fixes that.
- No rate limiting yet. Put Cloudflare's rate-limiting rule on `POST /rounds` before promoting it publicly.
- No accounts. The admin link is the login, so losing it means losing the round.
