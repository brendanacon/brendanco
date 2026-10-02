// Unsaid API: a Cloudflare Worker backed by one KV namespace (binding UNSAID).
// Deploy steps are in README.md next to this file.
//
// Anonymity guarantees enforced here, not in the browser:
//  - Raw answers never leave this worker. The owner only ever gets rating totals and the AI synthesis,
//    and only once the round has at least `threshold` responses.
//  - Invite tokens and the admin key are stored as SHA-256 hashes. The owner's browser keeps the
//    tokens, so the server never learns who was invited.
//  - A response is stored under a random key with no timestamp and no link to the token that sent it.
//    The only thing recorded against a token is "used".

import {
  validateRoundSpec, validateAnswers, computeStats, synthesisMessages, normaliseReport, randomId, sha256,
} from '../core.js';

export default {
  async fetch(req, env) {
    const cors = corsHeaders(req, env);
    if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
    try {
      return json(await route(req, env), 200, cors);
    } catch (e) {
      return json({ error: e.status ? e.message : 'Something went wrong.' }, e.status || 500, cors);
    }
  },
};

function corsHeaders(req, env) {
  const allowed = String(env.ALLOWED_ORIGINS || 'https://brendanco.com').split(',').map(s => s.trim());
  const origin = req.headers.get('Origin') || '';
  return {
    'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : allowed[0],
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), { status, headers: { ...headers, 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });
}

function fail(status, msg) {
  return Object.assign(new Error(msg), { status });
}

async function body(req) {
  try { return await req.json(); } catch (e) { throw fail(400, 'Expected a JSON body.'); }
}

async function route(req, env) {
  const parts = new URL(req.url).pathname.split('/').filter(Boolean);
  const [root, id, kind, secret, action] = parts;
  if (root !== 'rounds') throw fail(404, 'Not found.');

  if (!id && req.method === 'POST') return createRound(env, await body(req));
  if (!id || !secret) throw fail(404, 'Not found.');
  const round = await env.UNSAID.get('r:' + id, 'json');
  if (!round) throw fail(404, 'This round does not exist.');

  if (kind === 'invite') {
    const th = await sha256(secret);
    if (!round.tokens.includes(th)) throw fail(404, 'This invite link is not valid.');
    const used = !!(await env.UNSAID.get('u:' + id + ':' + th));
    if (req.method === 'GET') return { ...publicRound(round), used };
    if (req.method === 'POST') {
      if (used) throw fail(409, 'This link has already been used.');
      const answers = validateAnswers(round.questions, (await body(req)).answers);
      await env.UNSAID.put('resp:' + id + ':' + randomId(20), JSON.stringify(answers));
      await env.UNSAID.put('u:' + id + ':' + th, '1');
      return { ok: true };
    }
  }

  if (kind === 'admin') {
    if ((await sha256(secret)) !== round.adminHash) throw fail(403, 'This admin link is not valid.');
    const responses = await loadResponses(env, id);
    const unlocked = responses.length >= round.threshold;
    if (req.method === 'GET' && !action) {
      return {
        ...publicRound(round),
        invites: round.tokens.length,
        count: responses.length,
        unlocked,
        stats: unlocked ? computeStats(round.questions, responses) : null,
        report: unlocked ? round.report : null,
      };
    }
    if (req.method === 'POST' && action === 'report') {
      if (!unlocked) throw fail(409, 'The report unlocks at ' + round.threshold + ' responses.');
      const raw = await openaiJSON(env, synthesisMessages(round, responses));
      round.report = normaliseReport(raw, round, responses.length);
      await env.UNSAID.put('r:' + id, JSON.stringify(round));
      return { report: round.report };
    }
  }
  throw fail(404, 'Not found.');
}

async function createRound(env, spec) {
  const clean = validateRoundSpec(spec);
  const id = randomId(10);
  const adminKey = randomId(24);
  const tokens = Array.from({ length: clean.invites }, () => randomId(16));
  const round = {
    id,
    ownerName: clean.ownerName,
    title: clean.title,
    questions: clean.questions,
    threshold: clean.threshold,
    created: new Date().toISOString(),
    adminHash: await sha256(adminKey),
    tokens: await Promise.all(tokens.map(sha256)),
    report: null,
  };
  await env.UNSAID.put('r:' + id, JSON.stringify(round));
  return { id, adminKey, tokens };
}

function publicRound(r) {
  return { id: r.id, ownerName: r.ownerName, title: r.title, questions: r.questions, threshold: r.threshold, created: r.created };
}

async function loadResponses(env, id) {
  const keys = [];
  let cursor;
  do {
    const page = await env.UNSAID.list({ prefix: 'resp:' + id + ':', cursor });
    keys.push(...page.keys.map(k => k.name));
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  const values = await Promise.all(keys.map(k => env.UNSAID.get(k, 'json')));
  return values.filter(Boolean);
}

async function openaiJSON(env, messages) {
  if (!env.OPENAI_API_KEY) throw fail(503, 'The AI key is not set up on the server yet.');
  const req = {
    model: env.OPENAI_MODEL || 'gpt-5.5',
    messages,
    response_format: { type: 'json_object' },
    max_completion_tokens: 4000,
    reasoning_effort: 'low',
  };
  const call = b => fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + env.OPENAI_API_KEY },
    body: JSON.stringify(b),
  });
  let r = await call(req);
  if (r.status === 400 && /reasoning_effort/.test(await r.clone().text())) {
    delete req.reasoning_effort;
    r = await call(req);
  }
  if (!r.ok) throw fail(502, 'The AI service returned an error (' + r.status + '). Try again shortly.');
  const j = await r.json();
  const text = j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
  try { return JSON.parse(text); } catch (e) { throw fail(502, 'The AI returned something unreadable. Try again.'); }
}
