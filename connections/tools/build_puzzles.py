#!/usr/bin/env python3
"""Builds puzzles.js for the Bookshelf Connections game.

Source of truth: the BOOKS and CATEGORIES tables below.
Run:  python3 connections/tools/build_puzzles.py
Every generated puzzle is checked so each tile fits exactly one of its four
groups (counting "also" near-misses), which is what keeps the game fair.
To add books later: add to BOOKS, add the id to any category it fits
(members, or `also` if it's arguable), then re-run.
"""
import json, random, os
from collections import Counter

# id: (title, author, month read, note shown on the results bookshelf)
BOOKS = {
  'seed':          ("Seed", "Bri Lee", "Jan", ""),
  'lastoneout':    ("Last One Out", "Jane Harper", "Jan", "Mystery"),
  'tellingtales':  ("Telling Tales", "Ann Cleeves", "Jan", "Vera mystery · recommended"),
  'saltwater':     ("Salt Water", "Ali Gripper", "Jan", "Short stories"),
  'rip':           ("The Rip", "Mark Brandi", "Jan", ""),
  'landwinter':    ("The Land in Winter", "Andrew Miller", "Jan", "Not very satisfying"),
  'housemaid':     ("The Housemaid", "Freida McFadden", "Jan", "Clever plotted mystery"),
  'visitor':       ("The Visitor", "Rebecca Starford", "Jan", "Tense mystery"),
  'underworld':    ("The Underworld", "Sofie Laguna", "Jan", "Didn't engage"),
  'riders':        ("The Riders", "Tim Winton", "Jan", "Very engaging · recommended"),
  'lastanniv':     ("The Last Anniversary", "Liane Moriarty", "Jan", ""),
  'crowtrap':      ("The Crow Trap", "Ann Cleeves", "Jan", "Vera mystery"),
  'fellowship':    ("Fellowship Point", "Alice Elliott Dark", "Feb", ""),
  'blackout':      ("The Blackout Murders", "Anna Elliott & Charles Veley", "Feb", "Mystery"),
  'killingstones': ("The Killing Stones", "Ann Cleeves", "Feb", "Shetland mystery"),
  'memorial':      ("Memorial Days", "Geraldine Brooks", "Feb", "Memoir"),
  'hidden':        ("Hidden", "Bryan Brown", "Feb", ""),
  'silentvoices':  ("Silent Voices", "Ann Cleeves", "Mar", "Vera mystery"),
  'husbands':      ("The Husband's Secret", "Liane Moriarty", "Mar", ""),
  'exwife':        ("The Ex-Wife", "Tim Sullivan", "Mar", "Short story"),
  'gambler':       ("The Gambler", "J.P. Pomare", "Mar", ""),
  'myfriends':     ("My Friends", "Hisham Matar", "Mar", ""),
  'alice':         ("What Alice Forgot", "Liane Moriarty", "Apr", ""),
  'harry':         ("The Afterlife of Harry Playford", "Steven Carroll", "Mar", ""),
  'flashlight':    ("The Flashlight", "Susan Choi", "Apr", "8/10 · Japan & Korea history"),
  'savelife':      ("This Story Might Save Your Life", "Tiffany Crum", "May", "Different style of mystery"),
  'heir':          ("The Heir Apparent", "Rebecca Armitage", "May", "The royal family thriller"),
  'farflung':      ("A Far-Flung Life", "M.L. Stedman", "May", "9/10 · recommended"),
  'feet':          ("Look After Your Feet", "Rosalie Ham", "May", "About getting old · didn't finish"),
  'theo':          ("Theo of Golden", "Allen Levi", "May", "8/10 · thoughtful ending"),
  'insidious':     ("Insidious Intent", "Val McDermid", "May", "Tony Hill & Carol Jordan"),
  'correspondent': ("The Correspondent", "Virginia Evans", "May", ""),
  'deadspeak':     ("How the Dead Speak", "Val McDermid", "May", "8/10 mystery"),
  'needtoknow':    ("You Need to Know", "Nicola Moriarty", "Jun", ""),
  'lovelane':      ("Love Lane", "Patrick Gale", "Jun", ""),
  'boysea':        ("The Boy from the Sea", "Garrett Carr", "Jun", ""),
  'revenge':       ("Three Reasons for Revenge", "Dervla McTiernan", "Jun", "9/10 mystery"),
  'neversay':      ("Things We Never Say", "Elizabeth Strout", "Jun", "10/10 · recommended"),
  'midnight':      ("The Midnight Train", "Matt Haig", "Jun", ""),
  'girlgreen':     ("The Girl in Green", "Derek B. Miller", "Jul", "Gave up halfway"),
  'whistler':      ("Whistler", "Ann Patchett", "Jul", "10/10 · highly recommended"),
  'labyrinth':     ("Labyrinth", "Amanda Lohrey", "Jul", "7–8/10"),
  'buried':        ("The Book of Buried Pasts", "Sarah Clutton", "Jul", "8/10 · intriguing mystery"),
  'tailor':        ("The Tailor", "Tim Sullivan", "Jul", "DS Cross mystery"),
  'atsea':         ("At Sea", "Yassmin Abdel-Magied", "Jul", "Engineer on an oil rig"),
  'detective':     ("The Detective", "Matthew Reilly", "Jul", "Read a quarter, then dumped"),
  'russian':       ("The Russian", "James Patterson", "Jul", ""),
  'legacy':        ("The Legacy", "Caroline Bond", "Aug", "Recommended"),
  'hunter':        ("The Hunter", "Tim Sullivan", "Aug", "Short story"),
  'wakes':         ("Every Time She Wakes", "Petronella McGovern", "Aug", "Abandoned"),
  'electric':      ("The Electric Hotel", "Dominic Smith", "Aug", "Didn't engage"),
  'lonelymouth':   ("Lonely Mouth", "Jacqueline Maley", "Aug", "Didn't engage"),
  'names':         ("The Names", "Florence Knapp", "Aug", "Sensitively written · recommended"),
  'edenhope':      ("Edenhope", "Louise Le Nay", "Aug", "7–8/10 · family"),
  'gravity':       ("Gravity Let Me Go", "Trent Dalton", "Aug", "Listened to a third"),
  'resurrection':  ("Resurrection Bay", "Emma Viskic", "Aug", "8/10 mystery"),
  'fierceland':    ("Fierceland", "Omar Musa", "Aug", "7–8/10 · Borneo"),
  'librarian':     ("The Librarian", "Marie Benedict & V.C. Murray", "Sep", ""),
  'sea':           ("The Sea", "John Banville", "Sep", "9/10 · recommended"),
  'reportmurder':  ("Report for Murder", "Val McDermid", "Sep", "7/10 crime mystery"),
  'tightlines':    ("Tight Lines", "Allee Richards", "Sep", "Gave up halfway"),
  'wonder':        ("State of Wonder", "Ann Patchett", "Sep", ""),
  'solvemurders':  ("We Solve Murders", "Richard Osman", "Sep", ""),
}

# level: 0 yellow (straightforward) .. 3 purple (trickiest / wordplay / by elimination)
# members: titles that clearly belong.  also: titles someone could argue fit,
# which are therefore never allowed in a puzzle that uses the category unless chosen.
# key: word to underline in the solved bar so the link is obvious after the fact.
# memory: needs you to remember something about the book (max one per puzzle).
CATEGORIES = [
  dict(id='cleeves', level=0, name="Ann Cleeves", memory=False,
       members=['tellingtales','crowtrap','killingstones','silentvoices']),
  dict(id='moriarty', level=0, name="Written by a Moriarty", memory=False,
       members=['lastanniv','husbands','alice','needtoknow']),
  dict(id='murder', level=0, name="Murder or killing in the title", memory=False,
       members=['blackout','reportmurder','solvemurders','killingstones'],
       also=['deadspeak','revenge','detective'],
       key={'blackout':'Murders','reportmurder':'Murder','solvemurders':'Murders','killingstones':'Killing'}),
  dict(id='mysteries', level=0, name="Mysteries & whodunnits", memory=True,
       members=['tellingtales','crowtrap','killingstones','silentvoices','lastoneout','blackout','housemaid',
                'visitor','insidious','deadspeak','revenge','reportmurder','solvemurders','resurrection',
                'gambler','tailor','detective','savelife'],
       also=['exwife','hunter','buried','heir','rip','wakes','hidden','husbands','needtoknow','girlgreen',
             'russian']),
  dict(id='longest', level=0, name="The longest titles (five words or more)", memory=False,
       members=['savelife','harry','buried','boysea']),
  dict(id='anns', level=1, name="Written by an Ann (Cleeves or Patchett)", memory=False,
       members=['tellingtales','crowtrap','killingstones','silentvoices','whistler','wonder'],
       also=['blackout']),
  dict(id='oneword', level=0, name="One-word titles", memory=False,
       members=['seed','hidden','whistler','labyrinth','edenhope','fierceland']),

  dict(id='water', level=1, name="The sea, salt water & surf", memory=False,
       members=['saltwater','rip','boysea','atsea','sea','resurrection'],
       also=['tightlines'],
       key={'saltwater':'Salt Water','rip':'Rip','boysea':'Sea','atsea':'Sea','sea':'Sea','resurrection':'Bay'}),
  dict(id='jobs', level=1, name="“The” + a job", memory=False,
       members=['housemaid','tailor','hunter','detective','librarian','correspondent'],
       also=['gambler','riders','visitor','heir','russian']),
  dict(id='time', level=1, name="Clock & calendar words", memory=False,
       members=['midnight','lastanniv','memorial','landwinter','wakes'],
       key={'midnight':'Midnight','lastanniv':'Anniversary','memorial':'Days','landwinter':'Winter','wakes':'Time'}),
  dict(id='people', level=1, name="Boy, girl, husband, wife", memory=False,
       members=['boysea','girlgreen','exwife','husbands'],
       also=['housemaid','heir','myfriends'],
       key={'boysea':'Boy','girlgreen':'Girl','exwife':'Wife','husbands':'Husband'}),
  dict(id='places', level=1, name="Ends with a place: Point, Lane, Bay, Hotel", memory=False,
       members=['fellowship','lovelane','resurrection','electric'],
       also=['wonder','landwinter','fierceland','edenhope','midnight'],
       key={'fellowship':'Point','lovelane':'Lane','resurrection':'Bay','electric':'Hotel'}),
  dict(id='pronouns', level=1, name="Has you, we, me, my or she in it", memory=False,
       members=['needtoknow','solvemurders','myfriends','neversay','feet','gravity','wakes','savelife'],
       key={'needtoknow':'You','solvemurders':'We','myfriends':'My','neversay':'We','feet':'Your',
            'gravity':'Me','wakes':'She','savelife':'Your'}),

  dict(id='afterlife', level=2, name="Beyond the grave", memory=False,
       members=['harry','underworld','deadspeak','resurrection'],
       also=['memorial','legacy','buried','wakes','edenhope','killingstones','reportmurder','solvemurders',
             'blackout','rip'],
       key={'harry':'Afterlife','underworld':'Underworld','deadspeak':'Dead','resurrection':'Resurrection'}),
  dict(id='funeral', level=2, name="After someone dies", memory=False,
       members=['wakes','memorial','legacy','buried'],
       also=['harry','underworld','deadspeak','resurrection','killingstones','rip'],
       key={'wakes':'Wakes','memorial':'Memorial','legacy':'Legacy','buried':'Buried'}),
  dict(id='sounds', level=2, name="Ways to use your voice", memory=False,
       members=['deadspeak','silentvoices','neversay','tellingtales','whistler'],
       also=['lonelymouth','correspondent','reportmurder','needtoknow','savelife'],
       key={'deadspeak':'Speak','silentvoices':'Voices','neversay':'Say','tellingtales':'Telling','whistler':'Whistler'}),
  dict(id='secrets', level=2, name="Keeping secrets", memory=False,
       members=['husbands','hidden','buried','neversay'],
       also=['alice','needtoknow','silentvoices','insidious','underworld','lonelymouth'],
       key={'husbands':'Secret','hidden':'Hidden','buried':'Buried','neversay':'Never Say'}),
  dict(id='bookish', level=2, name="Story time: story, book, tales, librarian", memory=False,
       members=['savelife','buried','tellingtales','librarian'],
       also=['correspondent','reportmurder','names'],
       key={'savelife':'Story','buried':'Book','tellingtales':'Tales','librarian':'Librarian'}),
  dict(id='light', level=2, name="Lights on, lights off", memory=False,
       members=['flashlight','electric','blackout','midnight'],
       also=['underworld','lastoneout'],
       key={'flashlight':'Flashlight','electric':'Electric','blackout':'Blackout','midnight':'Midnight'}),
  dict(id='feelings', level=2, name="A feeling hides in the title", memory=False,
       members=['lonelymouth','lovelane','wonder','edenhope'],
       also=['revenge','fierceland','insidious'],
       key={'lonelymouth':'Lonely','lovelane':'Love','wonder':'Wonder','edenhope':'hope'}),
  dict(id='named', level=2, name="Names in the title", memory=False,
       members=['alice','theo','harry','names'],
       also=['whistler'],
       key={'alice':'Alice','theo':'Theo','harry':'Harry Playford','names':'Names'}),
  dict(id='tims', level=2, name="Written by a Tim (Winton or Sullivan)", memory=False,
       members=['riders','exwife','tailor','hunter']),

  dict(id='alliteration', level=3, name="Alliteration: Love Lane, Telling Tales…", memory=False,
       members=['lovelane','farflung','tellingtales','insidious','buried'],
       also=['savelife']),
  dict(id='compound', level=3, name="Two words squashed into one", memory=False,
       members=['housemaid','flashlight','underworld','edenhope','fierceland','fellowship','blackout','harry','midnight'],
       gloss={'housemaid':'House·maid','flashlight':'Flash·light','underworld':'Under·world','edenhope':'Eden·hope',
            'fierceland':'Fierce·land','fellowship':'Fellow·ship','blackout':'Black·out','harry':'After·life',
            'midnight':'Mid·night'}),
  dict(id='homophones', level=3, name="Sound like other words", memory=False,
       members=['heir','sea','tailor','russian'],
       also=['seed','rip'],
       gloss={'heir':'air','sea':'see','tailor':'Taylor','russian':'rushin’'}),
  dict(id='dnf', level=3, name="Ones you gave up on", memory=True,
       members=['girlgreen','detective','wakes','gravity','feet','tightlines'],
       also=['underworld','lonelymouth','electric','hidden','saltwater']),
  dict(id='favourites', level=3, name="Your 9s and 10s out of 10", memory=True,
       members=['neversay','whistler','farflung','revenge','sea'],
       also=['riders','flashlight','deadspeak','names','legacy','theo','resurrection','buried','reportmurder',
             'edenhope','labyrinth','fierceland','tellingtales']),
]
CAT = {c['id']: c for c in CATEGORIES}
for c in CATEGORIES:
    c.setdefault('also', []); c.setdefault('key', {}); c.setdefault('gloss', {})
    for b in c['members'] + c['also'] + list(c['key']) + list(c['gloss']):
        assert b in BOOKS, (c['id'], b)
    assert not set(c['members']) & set(c['also']), c['id']
    assert len(c['members']) >= 4, c['id']
    for b, k in c['key'].items():
        assert k.lower() in BOOKS[b][0].lower(), (c['id'], b, k)

def fits(book, cat):
    return book in cat['members'] or book in cat['also']

def valid(groups):
    """groups: list of (cat, [4 ids]). Each tile must fit exactly one chosen category."""
    tiles = [b for _, bs in groups for b in bs]
    if len(set(tiles)) != 16: return False
    for cat, bs in groups:
        for b in bs:
            if sum(fits(b, c) for c, _ in groups) != 1: return False
    # No decoy answers: any other connection may cover at most three of the tiles,
    # unless those four are exactly one of the real groups (e.g. Ann Cleeves inside "Written by an Ann").
    chosen = {c['id'] for c, _ in groups}
    real = [set(bs) for _, bs in groups]
    for c in CATEGORIES:
        if c['id'] in chosen: continue
        hit = set(c['members']) & set(tiles)
        if c['id'] in DECOY_OK:
            # broad genres: fine as a red herring, but only a light one
            inside = set().union(*[g for g in real if g <= hit])
            if len(hit - inside) > (2 if inside else 3): return False
            continue
        if len(hit) > 4 or (len(hit) == 4 and hit not in real): return False
    return True

# How often a category may appear: four-member (identical every time) and memory groups vs the rest.
CAP_SMALL, CAP_BIG = 7, 18

# Broad categories that are allowed to overlap other groups when they aren't in play.
DECOY_OK = {'mysteries'}

def feasible_combos():
    """Every set of four categories that can form a fair puzzle."""
    from itertools import combinations
    out = []
    for combo in combinations(CATEGORIES, 4):
        pick = sorted(combo, key=lambda c: c['level'])
        lv = [c['level'] for c in pick]
        # an easy on-ramp, at most one purple-style group, at most one memory group
        if lv[0] > 1 or lv.count(3) > 1 or lv.count(0) > 2 or lv[3] < 2 or sum(c['memory'] for c in pick) > 1: continue
        pools = []
        for c in pick:
            pool = [b for b in c['members'] if not any(fits(b, o) for o in pick if o is not c)]
            if len(pool) < 4: break
            pools.append(pool)
        else:
            out.append((pick, pools))
    return out

def build(n=56, seed=20261005):
    rng = random.Random(seed)
    combos = feasible_combos()
    cat_use, tile_use, combo_use = Counter(), Counter(), Counter()
    seen, out = set(), []
    cap = lambda c: CAP_SMALL if len(c['members']) == 4 or (c['memory'] and c['id'] != 'mysteries') else CAP_BIG
    while len(out) < n:
        # favour combos made of the least-used categories; mysteries were asked for, so nudge them up
        scored = []
        for ci, (pick, pools) in enumerate(combos):
            if any(cat_use[c['id']] >= cap(c) for c in pick) or combo_use[ci] >= 1: continue
            score = sum(cat_use[c['id']] for c in pick) + rng.random() * 3 - (8 if pick[0]['id'] == 'mysteries' else 0)
            scored.append((score, ci))
        if not scored: raise RuntimeError(f'stuck at {len(out)}')
        scored.sort()
        for _, ci in scored[:400]:
            pick, pools = combos[ci]
            groups = []
            for c, pool in zip(pick, pools):
                w = [1 / (1 + tile_use[b]) ** 2 for b in pool]
                chosen = []
                while len(chosen) < 4:
                    b = rng.choices(pool, weights=w)[0]
                    if b not in chosen: chosen.append(b)
                groups.append((c, chosen))
            sig = frozenset(b for _, bs in groups for b in bs)
            if valid(groups) and sig not in seen: break
        else:
            raise RuntimeError(f'stuck at {len(out)}')
        seen.add(sig); combo_use[ci] += 1
        for c, bs in groups:
            cat_use[c['id']] += 1
            for b in bs: tile_use[b] += 1
        out.append({'cats': frozenset(c['id'] for c in pick), 'groups': [(c['id'], bs) for c, bs in groups]})
    # order the bank so neighbouring days share as little as possible
    ordered = [out.pop(0)]
    while out:
        prev = ordered[-1]['cats']
        prev2 = ordered[-2]['cats'] if len(ordered) > 1 else frozenset()
        out.sort(key=lambda p: (len(p['cats'] & prev) * 3 + len(p['cats'] & prev2), rng.random()))
        ordered.append(out.pop(0))
    return ordered, cat_use, tile_use

def main():
    print(len(feasible_combos()), 'feasible category combos')
    for seed in range(20261005, 20261005 + 50):
        try:
            puzzles, cat_use, tile_use = build(seed=seed)
            break
        except RuntimeError:
            continue
    else:
        raise SystemExit('no seed produced a full bank; loosen caps or add categories')
    print('seed', seed)
    data = {
        'books': {k: {'t': t, 'a': a, 'm': m, 'n': n} for k, (t, a, m, n) in BOOKS.items()},
        'categories': {c['id']: {'name': c['name'], 'level': c['level'], 'key': c['key'], 'gloss': c['gloss']}
                       for c in CATEGORIES},
        'puzzles': [[{'c': cid, 'b': bs} for cid, bs in p['groups']] for p in puzzles],
    }
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, '..', 'puzzles.js')
    with open(path, 'w') as f:
        f.write('// Generated by tools/build_puzzles.py — edit that file, not this one.\n')
        f.write('window.BOOKSHELF = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'{len(puzzles)} puzzles written')
    print('category use:', dict(sorted(cat_use.items(), key=lambda x: -x[1])))
    unused = [b for b in BOOKS if not tile_use[b]]
    print('most used tiles:', [(BOOKS[b][0], n) for b, n in tile_use.most_common(8)])
    print('tile use range:', min(tile_use.values()), max(tile_use.values()), 'unused:', unused)
    return puzzles

if __name__ == '__main__':
    ps = main()
    import sys
    if '-v' in sys.argv:
        for i, p in enumerate(ps, 1):
            print(f'#{i}')
            for cid, bs in p['groups']:
                print(f"  {CAT[cid]['level']} {CAT[cid]['name']:<45} " + ' | '.join(BOOKS[b][0] for b in bs))
