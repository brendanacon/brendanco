// Unsaid core: shared by the app (360/index.html) and the backend (360/worker/worker.js).
// No DOM, no network. Templates, validation, rating stats, the synthesis prompt and
// report clean-up all live here so the browser preview and the live backend behave the same.

export const MIN_THRESHOLD = 3;
export const DEFAULT_THRESHOLD = 5;
export const LIMITS = { questions: 12, invites: 100, text: 2000, title: 120, name: 60, prompt: 240 };
export const SCALE_LABELS = ['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree'];

export const TEMPLATES = [
  {
    id: 'leader',
    name: 'Me as a leader',
    blurb: 'A founder or manager 360. How you set direction, make calls and handle disagreement.',
    title: 'How am I doing as a leader?',
    questions: [
      { type: 'scale', prompt: 'I get clear direction from {name} on what matters most.' },
      { type: 'scale', prompt: 'It feels safe to disagree with {name}.' },
      { type: 'scale', prompt: 'I trust the calls {name} makes.' },
      { type: 'text', prompt: 'What should {name} keep doing?' },
      { type: 'text', prompt: 'What should {name} start or stop doing?' },
      { type: 'text', prompt: "What's something you've wanted to tell {name} but haven't?" },
    ],
  },
  {
    id: 'direction',
    name: 'Our direction',
    blurb: 'Is the strategy landing? Find out whether the team believes in where you are heading.',
    title: 'Are we heading in the right direction?',
    questions: [
      { type: 'scale', prompt: 'I understand where we are heading over the next 12 months.' },
      { type: 'scale', prompt: 'I believe we are focused on the right things.' },
      { type: 'scale', prompt: "I'd recommend working here to a friend." },
      { type: 'text', prompt: 'What are we getting most right?' },
      { type: 'text', prompt: "What's the biggest risk you see that leadership isn't talking about?" },
      { type: 'text', prompt: 'If you ran the company for a week, what would you change first?' },
    ],
  },
  {
    id: 'ideas',
    name: 'Ideas box',
    blurb: 'Surface the ideas people sit on because they worry they sound silly.',
    title: 'What ideas are we missing?',
    questions: [
      { type: 'scale', prompt: 'I feel my ideas are heard here.' },
      { type: 'text', prompt: "What's one idea that would make the biggest difference to how we work?" },
      { type: 'text', prompt: "What's something we do that wastes time?" },
      { type: 'text', prompt: "What's an idea you've had but haven't raised? What stopped you?" },
    ],
  },
  {
    id: 'custom',
    name: 'Start blank',
    blurb: 'Write your own questions. Mix ratings and open answers.',
    title: '',
    questions: [{ type: 'text', prompt: '' }],
  },
];

export function fill(text, name) {
  return String(text || '').replace(/\{name\}/g, name || 'me');
}

function str(v, max) {
  return String(v == null ? '' : v).replace(/\s+/g, ' ').trim().slice(0, max);
}
function bad(msg) {
  return Object.assign(new Error(msg), { status: 400 });
}

// Returns a clean round spec or throws a 400.
export function validateRoundSpec(spec) {
  spec = spec || {};
  const ownerName = str(spec.ownerName, LIMITS.name);
  const title = str(spec.title, LIMITS.title);
  if (!ownerName) throw bad('Add your name so people know who the feedback is for.');
  if (!title) throw bad('Give the round a title.');
  const qs = Array.isArray(spec.questions) ? spec.questions : [];
  const questions = qs
    .map((q, i) => ({ id: 'q' + (i + 1), type: q && q.type === 'scale' ? 'scale' : 'text', prompt: str(q && q.prompt, LIMITS.prompt) }))
    .filter(q => q.prompt)
    .slice(0, LIMITS.questions)
    .map((q, i) => ({ ...q, id: 'q' + (i + 1) }));
  if (!questions.length) throw bad('Add at least one question.');
  if (!questions.some(q => q.type === 'text')) throw bad('Add at least one open question so there is something to synthesise.');
  const threshold = Math.round(Number(spec.threshold) || DEFAULT_THRESHOLD);
  if (threshold < MIN_THRESHOLD || threshold > 20) throw bad('The anonymity threshold must be between ' + MIN_THRESHOLD + ' and 20.');
  const invites = Math.round(Number(spec.invites) || 0);
  if (invites < threshold) throw bad('Invite at least ' + threshold + ' people, or the report can never unlock.');
  if (invites > LIMITS.invites) throw bad('Up to ' + LIMITS.invites + ' invites per round.');
  return { ownerName, title, questions, threshold, invites };
}

// Returns answers keyed by question id, or throws a 400.
export function validateAnswers(questions, answers) {
  answers = answers || {};
  const out = {};
  let wrote = false;
  for (const q of questions) {
    const v = answers[q.id];
    if (q.type === 'scale') {
      const n = Math.round(Number(v));
      if (!(n >= 1 && n <= 5)) throw bad('Please answer every rating question.');
      out[q.id] = n;
    } else {
      const t = String(v == null ? '' : v).trim().slice(0, LIMITS.text);
      if (t) { out[q.id] = t; wrote = true; }
    }
  }
  if (!wrote) throw bad('Answer at least one of the open questions.');
  return out;
}

export function computeStats(questions, responses) {
  return questions.filter(q => q.type === 'scale').map(q => {
    const counts = [0, 0, 0, 0, 0];
    let sum = 0, n = 0;
    for (const r of responses) {
      const v = r[q.id];
      if (v >= 1 && v <= 5) { counts[v - 1]++; sum += v; n++; }
    }
    return { id: q.id, prompt: q.prompt, n, counts, mean: n ? Math.round((sum / n) * 10) / 10 : null };
  });
}

export function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = randomInt(i + 1);
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
function randomInt(max) {
  const b = new Uint32Array(1);
  crypto.getRandomValues(b);
  return b[0] % max;
}

const ALPHABET = 'abcdefghijkmnpqrstuvwxyz23456789';
export function randomId(len) {
  const b = new Uint8Array(len);
  crypto.getRandomValues(b);
  let s = '';
  for (let i = 0; i < len; i++) s += ALPHABET[b[i] % ALPHABET.length];
  return s;
}

export async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf), x => x.toString(16).padStart(2, '0')).join('');
}

const SYSTEM = `You turn anonymous workplace feedback into a written synthesis for the person it is about. Protecting the anonymity of the people who answered matters more than completeness.

Rules:
1. Never quote. Paraphrase everything in your own neutral words. Do not reuse distinctive phrases, slang, metaphors, typos, swearing or unusual words from any response, because writing style can identify people.
2. Remove anything that could identify a respondent: names, roles, teams, projects, clients, dates, places, tenure, personal circumstances, or events only a few people would know about. If a point cannot be made without that, generalise it or leave it out.
3. Report patterns, not people. For each theme give "count": the number of distinct responses that support it. A theme with count 1 is allowed only if it is genuinely useful and stated generically, and include at most two of those in the whole report.
4. Drop abuse, insults and slurs. If an abusive comment contains a real point, keep only that point, rephrased calmly. Put the number of comments that were pure abuse with nothing usable in "removed".
5. Be direct and specific. Do not soften criticism into mush and do not inflate praise. Write to the subject in the second person ("you").
6. Plain English, short sentences, Australian spelling. No em dashes.

Return only JSON in exactly this shape:
{
  "headline": "One or two sentences: the overall read.",
  "strengths": [{ "theme": "3 to 6 words", "detail": "1 or 2 sentences", "count": 0 }],
  "growth": [{ "theme": "3 to 6 words", "detail": "1 or 2 sentences", "count": 0 }],
  "mixed": [{ "theme": "3 to 6 words", "detail": "Where people disagree with each other, 1 or 2 sentences" }],
  "questions": [{ "id": "q4", "summary": "2 or 3 sentences summarising answers to that open question" }],
  "actions": ["A concrete next step, starting with a verb"],
  "removed": 0
}
Give 2 to 4 strengths, 2 to 4 growth areas, 0 to 2 mixed signals, one "questions" entry per open question that received answers, and exactly 3 actions.`;

// Builds the chat messages for the synthesis. Responses are shuffled so their order says nothing.
export function synthesisMessages(round, responses) {
  const qs = round.questions.map(q => ({ ...q, prompt: fill(q.prompt, round.ownerName) }));
  const stats = computeStats(qs, responses);
  const lines = [];
  lines.push('Feedback is about: ' + round.ownerName);
  lines.push('Round: ' + round.title);
  lines.push('Number of responses: ' + responses.length);
  lines.push('');
  lines.push('Questions:');
  for (const q of qs) lines.push(q.id + ' [' + (q.type === 'scale' ? 'rating 1 to 5' : 'open') + ']: ' + q.prompt);
  if (stats.length) {
    lines.push('');
    lines.push('Rating averages (already calculated; refer to them only if useful):');
    for (const s of stats) lines.push(s.id + ': ' + s.mean + ' out of 5');
  }
  lines.push('');
  lines.push('Open answers, in random order:');
  shuffle(responses).forEach((r, i) => {
    lines.push('');
    lines.push('--- Response ' + (i + 1) + ' ---');
    for (const q of qs) if (q.type === 'text' && r[q.id]) lines.push(q.id + ': ' + r[q.id]);
  });
  return [{ role: 'system', content: SYSTEM }, { role: 'user', content: lines.join('\n') }];
}

export function consensusLabel(count, n) {
  if (n && count / n >= 0.6) return 'Most people';
  if (count >= 2) return 'Several people';
  return 'One voice';
}

// Cleans whatever the model returned into a safe, predictable report.
export function normaliseReport(raw, round, n) {
  raw = raw || {};
  const textIds = new Set(round.questions.filter(q => q.type === 'text').map(q => q.id));
  const themes = (list, withCount) => (Array.isArray(list) ? list : []).slice(0, 5).map(t => {
    const count = Math.max(1, Math.min(n, Math.round(Number(t && t.count) || 1)));
    const out = { theme: str(t && t.theme, 80), detail: str(t && t.detail, 400) };
    if (withCount) { out.count = count; out.label = consensusLabel(count, n); }
    return out;
  }).filter(t => t.theme && t.detail);
  return {
    headline: str(raw.headline, 400),
    strengths: themes(raw.strengths, true),
    growth: themes(raw.growth, true),
    mixed: themes(raw.mixed, false).slice(0, 3),
    questions: (Array.isArray(raw.questions) ? raw.questions : [])
      .map(q => ({ id: str(q && q.id, 8), summary: str(q && q.summary, 600) }))
      .filter(q => textIds.has(q.id) && q.summary),
    actions: (Array.isArray(raw.actions) ? raw.actions : []).map(a => str(a, 240)).filter(Boolean).slice(0, 4),
    removed: Math.max(0, Math.min(n, Math.round(Number(raw.removed) || 0))),
    n,
    generatedAt: new Date().toISOString(),
  };
}
