#!/usr/bin/env python3
"""Builds tech.js: the Tech edition (Stratechery-reader level).

Same rules and generator as build_puzzles.py: every tile fits exactly one group in its
puzzle, and no other connection covers four of its tiles.
Run:  python3 connections/tools/build_tech.py [-v]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_puzzles as engine

# id: (tile, clue shown with "Show clues", year, note for the results screen)
ITEMS = {
  # big platforms
  'google':      ("Google", "Search", "1998", "The original aggregator of the web"),
  'meta':        ("Meta", "Facebook's parent", "2004", "Renamed from Facebook in 2021"),
  'amazon':      ("Amazon", "Shopping & AWS", "1994", "Named after the river"),
  'netflix':     ("Netflix", "Streaming", "1997", ""),
  'airbnb':      ("Airbnb", "Places to stay", "2008", "Y Combinator, 2009"),
  'uber':        ("Uber", "Rides", "2009", ""),
  'snap':        ("Snap", "Snapchat's parent", "2011", "Renamed from Snapchat Inc. in 2016"),
  'pinterest':   ("Pinterest", "Visual discovery", "2010", ""),
  'reddit':      ("Reddit", "Forums", "2005", "From Y Combinator's very first batch"),
  'twitter':     ("Twitter", "Now called X", "2006", "Elon Musk bought it in 2022"),
  'youtube':     ("YouTube", "Video", "2005", "Founded by PayPal alumni; Google bought it in 2006"),
  'tiktok':      ("TikTok", "Short video", "2016", "Owned by ByteDance"),
  'yelp':        ("Yelp", "Local reviews", "2004", "Founded by PayPal alumni"),
  'instagram':   ("Instagram", "Photos", "2010", "Meta bought it in 2012 for $1B"),
  'alphabet':    ("Alphabet", "Google's parent", "2015", "Google restructured under Alphabet in 2015"),
  'block':       ("Block", "Cash App & Square", "2009", "Renamed from Square in 2021"),
  # Elon
  'zip2':        ("Zip2", "Online city guides", "1995", "Elon Musk's first company"),
  'paypal':      ("PayPal", "Payments", "1998", "Elon's X.com merged with Confinity to become PayPal"),
  'tesla':       ("Tesla", "Electric cars", "2003", "Also the name of an Nvidia GPU architecture (2006)"),
  'spacex':      ("SpaceX", "Rockets", "2002", ""),
  'neuralink':   ("Neuralink", "Brain implants", "2016", ""),
  'boring':      ("The Boring Company", "Tunnels", "2016", ""),
  'xai':         ("xAI", "Grok's maker", "2023", ""),
  'openai':      ("OpenAI", "ChatGPT's maker", "2015", "Elon Musk co-founded it and left in 2018"),
  'solarcity':   ("SolarCity", "Solar panels", "2006", "Elon was chairman; Tesla bought it in 2016"),
  # PayPal alumni
  'linkedin':    ("LinkedIn", "Professional network", "2002", "Founded by Reid Hoffman; Microsoft bought it in 2016"),
  'palantir':    ("Palantir", "Data analytics", "2003", "Co-founded by Peter Thiel; named after Tolkien's seeing stones"),
  'affirm':      ("Affirm", "Buy now, pay later", "2012", "Founded by Max Levchin"),
  'yammer':      ("Yammer", "Workplace social network", "2008", "Founded by David Sacks; Microsoft bought it in 2012"),
  # acquisitions
  'github':      ("GitHub", "Code hosting", "2008", "Microsoft bought it in 2018"),
  'activision':  ("Activision Blizzard", "Video games", "2008", "Microsoft bought it in 2023 for $69B"),
  'skype':       ("Skype", "Video calls", "2003", "Microsoft bought it in 2011 and shut it in 2025"),
  'minecraft':   ("Minecraft", "Block-building game", "2011", "Microsoft bought its maker Mojang in 2014"),
  'nokia':       ("Nokia", "Phones & networks", "1865", "Named after a Finnish town; Microsoft bought its phone business"),
  'whatsapp':    ("WhatsApp", "Messaging", "2009", "Meta bought it in 2014"),
  'oculus':      ("Oculus", "VR headsets", "2012", "Meta bought it in 2014"),
  'giphy':       ("Giphy", "GIFs", "2013", "Meta bought it; UK regulators made it sell"),
  'android':     ("Android", "Phone OS", "2003", "Google bought it in 2005"),
  'doubleclick': ("DoubleClick", "Ad tech", "1996", "Google bought it in 2008"),
  'nest':        ("Nest", "Smart thermostats", "2010", "Google bought it in 2014"),
  'fitbit':      ("Fitbit", "Fitness trackers", "2007", "Google bought it in 2021"),
  'waze':        ("Waze", "Maps", "2006", "Google bought it in 2013"),
  'deepmind':    ("DeepMind", "AI lab", "2010", "Google bought it in 2014"),
  'wholefoods':  ("Whole Foods", "Groceries", "1980", "Amazon bought it in 2017"),
  'twitch':      ("Twitch", "Live streaming", "2011", "Amazon bought it in 2014; began at Y Combinator as Justin.tv"),
  'ring':        ("Ring", "Video doorbells", "2013", "Amazon bought it in 2018"),
  'zappos':      ("Zappos", "Shoes online", "1999", "Amazon bought it in 2009"),
  'mgm':         ("MGM", "Film studio", "1924", "Amazon bought it in 2022"),
  # deals that died
  'figma':       ("Figma", "Design software", "2012", "Adobe's $20B takeover was abandoned in 2023"),
  'irobot':      ("iRobot", "Roomba maker", "1990", "Amazon's takeover was abandoned in 2024"),
  'arm':         ("Arm", "Chip designs", "1990", "Nvidia's takeover was abandoned in 2022"),
  'qualcomm':    ("Qualcomm", "Phone chips", "1985", "Broadcom's hostile bid was blocked in 2018"),
  # chips
  'nvidia':      ("Nvidia", "GPUs", "1993", ""),
  'amd':         ("AMD", "CPUs & GPUs", "1969", ""),
  'intel':       ("Intel", "CPUs & foundry", "1968", ""),
  'tsmc':        ("TSMC", "Chip foundry", "1987", ""),
  'asml':        ("ASML", "Chipmaking machines", "1984", "Makes the EUV lithography machines"),
  'hopper':      ("Hopper", "Named after Grace Hopper", "2022", "Nvidia GPU architecture (H100)"),
  'blackwell':   ("Blackwell", "Named after David Blackwell", "2024", "Nvidia GPU architecture (B200)"),
  'rubin':       ("Rubin", "Named after Vera Rubin", "2026", "Nvidia GPU architecture"),
  'ampere':      ("Ampere", "Named after André-Marie Ampère", "2020", "Nvidia GPU architecture (A100)"),
  'm1':          ("M1", "Mac chip", "2020", "Apple silicon"),
  'r1':          ("R1", "Vision Pro chip", "2024", "Apple silicon (also a DeepSeek model name)"),
  'h2':          ("H2", "AirPods chip", "2022", "Apple silicon"),
  't2':          ("T2", "Mac security chip", "2017", "Apple silicon"),
  # AI
  'anthropic':   ("Anthropic", "Claude's maker", "2021", "Founded by former OpenAI staff"),
  'mistral':     ("Mistral", "French AI lab", "2023", ""),
  'tm':          ("Thinking Machines", "AI lab", "2025", "Founded by Mira Murati, ex-OpenAI CTO"),
  'ssi':         ("SSI", "Safe Superintelligence, an AI lab", "2024", "Founded by Ilya Sutskever, ex-OpenAI chief scientist"),
  'perplexity':  ("Perplexity", "AI search", "2022", "CEO Aravind Srinivas worked at OpenAI"),
  'deepseek':    ("DeepSeek", "Chinese AI lab", "2023", ""),
  'chatgpt':     ("ChatGPT", "OpenAI's chatbot", "2022", ""),
  'claude':      ("Claude", "Anthropic's chatbot", "2023", ""),
  'gemini':      ("Gemini", "Google's chatbot", "2023", ""),
  'grok':        ("Grok", "xAI's chatbot", "2023", ""),
  'copilot':     ("Copilot", "Microsoft's AI assistant", "2023", ""),
  'cursor':      ("Cursor", "AI code editor", "2023", ""),
  'lovable':     ("Lovable", "AI app builder", "2023", ""),
  'replit':      ("Replit", "AI coding platform", "2016", ""),
  'windsurf':    ("Windsurf", "AI code editor", "2024", ""),
  'bolt':        ("Bolt", "AI app builder", "2024", ""),
  'v0':          ("v0", "Vercel's AI app builder", "2023", ""),
  'instinct':    ("Instinct", "AI agent startup", "", ""),
  'poke':        ("Poke", "AI agent startup", "", "An assistant you text"),
  'dots':        ("Dots", "AI agent startup", "", ""),
  'muse':        ("Muse", "AI agent startup", "", ""),
  'manus':       ("Manus", "General-purpose AI agent", "2025", ""),
  'devin':       ("Devin", "AI software engineer", "2024", "Made by Cognition"),
  # China
  'tencent':     ("Tencent", "WeChat's parent", "1998", ""),
  'alibaba':     ("Alibaba", "E-commerce & cloud", "1999", ""),
  'huawei':      ("Huawei", "Phones & telecom gear", "1987", ""),
  'xiaomi':      ("Xiaomi", "Phones — and now cars", "2010", "Launched the SU7 electric car in 2024"),
  'byd':         ("BYD", "Electric cars", "1995", ""),
  'temu':        ("Temu", "Cheap stuff, shipped", "2022", "Owned by PDD Holdings"),
  'wechat':      ("WeChat", "Everything app", "2011", "Owned by Tencent"),
  # cars & space
  'rivian':      ("Rivian", "Electric trucks", "2009", ""),
  'lucid':       ("Lucid", "Electric sedans", "2007", ""),
  'nio':         ("NIO", "Electric cars", "2014", "Chinese EV maker"),
  'blueorigin':  ("Blue Origin", "Rockets", "2000", "Founded by Jeff Bezos"),
  'rocketlab':   ("Rocket Lab", "Small rockets", "2006", "Founded in New Zealand"),
  'kuiper':      ("Kuiper", "Satellite internet", "2019", "Amazon's answer to Starlink"),
  # Y Combinator
  'stripe':      ("Stripe", "Online payments", "2010", "Y Combinator, 2010"),
  'doordash':    ("DoorDash", "Food delivery", "2013", "Y Combinator, 2013"),
  'dropbox':     ("Dropbox", "File storage", "2007", "Y Combinator, 2007"),
  'coinbase':    ("Coinbase", "Crypto exchange", "2012", "Y Combinator, 2012"),
  'instacart':   ("Instacart", "Grocery delivery", "2012", "Y Combinator, 2012"),
  # Google graveyard
  'reader':      ("Google Reader", "RSS reader", "2005", "Shut down 2013"),
  'googleplus':  ("Google+", "Social network", "2011", "Shut down 2019"),
  'stadia':      ("Stadia", "Cloud gaming", "2019", "Google shut it down in 2023"),
  'inbox':       ("Inbox", "Email app", "2014", "Google shut it down in 2019"),
  'allo':        ("Allo", "Messaging app", "2016", "Google shut it down in 2019"),
  # Ben Thompson
  'stratechery': ("Stratechery", "Ben Thompson's newsletter", "2013", ""),
  'dithering':   ("Dithering", "Podcast", "2020", "Ben Thompson & John Gruber"),
  'sharptech':   ("Sharp Tech", "Podcast", "2022", "Ben Thompson & Andrew Sharp"),
  'sharpchina':  ("Sharp China", "Podcast", "2022", "Andrew Sharp & Bill Bishop"),
  'goat':        ("Greatest of All Talk", "Podcast", "2018", "Ben Thompson & Andrew Sharp on the NBA"),
  # subscriptions etc
  'spotify':     ("Spotify", "Music streaming", "2006", ""),
  'substack':    ("Substack", "Newsletters", "2017", ""),
  'adobe':       ("Adobe", "Creative software", "1982", "Named after Adobe Creek, which ran behind a founder's house"),
  'cisco':       ("Cisco", "Networking gear", "1984", "Named after San Francisco"),
  'anduril':     ("Anduril", "Defence tech", "2017", "Named after Aragorn's sword"),
  'erebor':      ("Erebor", "Bank for tech startups", "2025", "Named after Tolkien's Lonely Mountain"),
  'mithril':     ("Mithril Capital", "Peter Thiel's fund", "2012", "Named after Tolkien's precious metal"),
  'bing':        ("Bing", "Microsoft's search", "2009", ""),
  'duckduckgo':  ("DuckDuckGo", "Private search", "2008", "Funded by search ads"),
  'yahoo':       ("Yahoo", "Web portal", "1994", ""),
  'telegram':    ("Telegram", "Messaging", "2013", ""),
  'signal':      ("Signal", "Encrypted messaging", "2014", ""),
  'imessage':    ("iMessage", "Apple's messaging", "2011", ""),
  # people
  'cook':        ("Tim Cook", "Apple CEO", "2011", "Took over from Steve Jobs"),
  'nadella':     ("Satya Nadella", "Microsoft CEO", "2014", "Took over from Steve Ballmer, after Bill Gates"),
  'pichai':      ("Sundar Pichai", "Google CEO", "2015", "Took over from Larry Page"),
  'jassy':       ("Andy Jassy", "Amazon CEO", "2021", "Took over from Jeff Bezos"),
  'jensen':      ("Jensen Huang", "Nvidia CEO", "1993", "Co-founded Nvidia"),
  'zuck':        ("Mark Zuckerberg", "Meta CEO", "2004", "Co-founded Facebook"),
  'chesky':      ("Brian Chesky", "Airbnb CEO", "2008", "Co-founded Airbnb"),
  'collison':    ("Patrick Collison", "Stripe CEO", "2010", "Co-founded Stripe with his brother John"),
  'thiel':       ("Peter Thiel", "Investor", "", "PayPal co-founder"),
  'hoffman':     ("Reid Hoffman", "Investor", "", "PayPal executive, then founded LinkedIn"),
  'levchin':     ("Max Levchin", "Affirm CEO", "", "PayPal co-founder"),
  'sacks':       ("David Sacks", "Investor", "", "PayPal COO, then founded Yammer"),
}

C = lambda id, level, name, members, also=(), key=None, gloss=None, memory=False: dict(
    id=id, level=level, name=name, members=list(members), also=list(also), key=key or {}, gloss=gloss or {}, memory=memory)

CHATBOT_LIKE = ['chatgpt','claude','gemini','grok','copilot','perplexity','deepseek','poke','manus','devin','instinct','dots','muse']

CATEGORIES = [
  C('elon', 0, "Elon Musk companies", ['zip2','paypal','tesla','spacex','neuralink','boring','xai','twitter'],
    also=['openai','solarcity','grok']),
  C('chatbots', 0, "AI chatbots", ['chatgpt','claude','gemini','grok','copilot'],
    also=['perplexity','deepseek','poke','manus','devin','instinct','dots','muse']),
  C('search', 0, "Search engines", ['google','bing','perplexity','duckduckgo','yahoo']),
  C('messaging', 0, "Messaging apps", ['whatsapp','telegram','signal','wechat','imessage'], also=['skype','allo','poke']),
  C('evs', 0, "Make electric cars", ['tesla','byd','rivian','lucid','nio','xiaomi']),
  C('space', 0, "Rocket & satellite companies", ['spacex','blueorigin','rocketlab','kuiper']),

  C('ads', 1, "Make their money from ads", ['google','meta','snap','pinterest','reddit','twitter','youtube','tiktok','yelp',
                                             'instagram','duckduckgo','yahoo','bing'],
    also=['amazon','netflix','linkedin','alphabet','spotify','uber','doordash','instacart','perplexity','waze','doubleclick',
          'giphy','android']),
  C('googleacq', 1, "Bought by Google", ['youtube','android','doubleclick','nest','fitbit','waze','deepmind']),
  C('metaacq', 1, "Bought by Meta", ['instagram','whatsapp','oculus','giphy']),
  C('amazonacq', 1, "Bought by Amazon", ['wholefoods','twitch','ring','zappos','mgm'], also=['irobot']),
  C('msftacq', 1, "Bought by Microsoft", ['linkedin','github','activision','skype','minecraft','nokia','yammer'], also=['openai']),
  C('china', 1, "Chinese tech", ['tiktok','tencent','alibaba','huawei','xiaomi','byd','temu','deepseek','wechat','nio'],
    also=['manus']),
  C('chips', 1, "Semiconductor companies", ['nvidia','amd','intel','tsmc','qualcomm','asml','arm'],
    also=['huawei','m1','r1','h2','t2','hopper','blackwell','rubin','ampere']),
  C('aicoding', 1, "AI coding tools", ['cursor','lovable','replit','windsurf','bolt','v0'],
    also=['devin','copilot','claude','chatgpt','github']),
  C('agents', 1, "AI agent startups", ['instinct','poke','dots','muse','manus','devin'],
    also=['chatgpt','claude','copilot','perplexity']),
  C('labs', 1, "Frontier AI labs", ['openai','anthropic','mistral','deepmind','tm','ssi','xai','deepseek'],
    also=['google','meta','perplexity']),
  C('renamed', 1, "Changed their name", ['meta','alphabet','block','snap'], also=['twitter','paypal'],
    gloss={'meta':'was Facebook','alphabet':'new parent of Google','block':'was Square','snap':'was Snapchat'}),
  C('graveyard', 1, "Killed by Google", ['reader','googleplus','stadia','inbox','allo']),
  C('ben', 1, "Ben Thompson's podcasts", ['dithering','sharptech','sharpchina','goat'], also=['stratechery']),

  C('aggregators', 2, "Aggregators, per Ben Thompson's 2015 essay", ['google','meta','amazon','netflix','airbnb','uber'],
    also=['youtube','tiktok','doordash','spotify','instagram','alphabet','instacart','pinterest','reddit','snap','twitter'],
    memory=True),
  C('paypalcos', 2, "Founded by PayPal alumni", ['linkedin','youtube','yelp','palantir','affirm','yammer'],
    also=['tesla','spacex','xai','neuralink','boring','twitter','paypal','openai','solarcity']),
  C('mafia', 2, "The PayPal Mafia", ['thiel','hoffman','levchin','sacks']),
  C('blocked', 2, "Takeovers that fell through", ['figma','irobot','arm','qualcomm'], also=['tiktok'], memory=True),
  C('oaialumni', 2, "Founded by OpenAI alumni", ['anthropic','ssi','tm','perplexity']),
  C('successors', 2, "Took over from a founder", ['cook','nadella','pichai','jassy']),
  C('founders', 2, "Founders still running the company", ['jensen','zuck','chesky','collison'], also=['levchin']),
  C('nvarch', 2, "Nvidia GPU architectures", ['hopper','blackwell','rubin','ampere'], also=['tesla']),
  C('yc', 2, "Y Combinator alumni", ['airbnb','stripe','doordash','dropbox','reddit','twitch','coinbase','instacart'],
    also=['openai']),
  C('subs', 2, "Mostly subscription revenue", ['netflix','spotify','stratechery','substack','dropbox','adobe'],
    also=['chatgpt','claude','perplexity','cursor','lovable','replit','windsurf','bolt','github','figma','linkedin',
          'dithering','sharptech','sharpchina','goat','v0','activision'], memory=True),

  C('applechips', 3, "Apple chips", ['m1','r1','h2','t2']),
  C('tolkien', 3, "Named from Tolkien", ['palantir','anduril','erebor','mithril'],
    gloss={'palantir':'seeing stone','anduril':'Aragorn’s sword','erebor':'the Lonely Mountain','mithril':'elven metal'}),
  C('places', 3, "Named after a place", ['amazon','nokia','adobe','cisco'], also=['erebor'],
    gloss={'amazon':'the river','nokia':'Finnish town','adobe':'Adobe Creek','cisco':'San Francisco'}),
  C('lowercase', 3, "Starts with a lowercase letter", ['xai','irobot','imessage','v0'],
    key={'xai':'x','irobot':'i','imessage':'i','v0':'v'}),
]

for c in CATEGORIES:
    for b in c['members'] + c['also'] + list(c['key']) + list(c['gloss']):
        assert b in ITEMS, (c['id'], b)
    assert not set(c['members']) & set(c['also']), c['id']
    for b, k in c['key'].items():
        assert ITEMS[b][0].startswith(k) or k.lower() in ITEMS[b][0].lower(), (c['id'], b, k)

def main():
    engine.CATEGORIES = CATEGORIES
    engine.DECOY_OK = set()
    engine.CAP_SMALL, engine.CAP_BIG = 6, 12
    for seed in range(20070109, 20070109 + 50):
        try:
            puzzles, cat_use, tile_use = engine.build(n=60, seed=seed)
            break
        except RuntimeError:
            continue
    else:
        raise SystemExit('no seed produced a full bank')
    data = {
        'books': {k: {'t': t, 'a': a, 'm': m, 'n': n} for k, (t, a, m, n) in ITEMS.items()},
        'categories': {c['id']: {'name': c['name'], 'level': c['level'], 'key': c['key'], 'gloss': c['gloss']} for c in CATEGORIES},
        'puzzles': [[{'c': cid, 'b': bs} for cid, bs in p['groups']] for p in puzzles],
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tech.js')
    with open(path, 'w') as f:
        f.write('// Generated by tools/build_tech.py — edit that file, not this one.\n')
        f.write('window.TECH = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'seed {seed}: {len(puzzles)} puzzles from {len(ITEMS)} items')
    print('category use:', dict(sorted(cat_use.items(), key=lambda x: -x[1])))
    print('unused:', [b for b in ITEMS if not tile_use[b]])
    print('most used:', [(ITEMS[b][0], n) for b, n in tile_use.most_common(6)])
    if '-v' in sys.argv:
        cat = {c['id']: c for c in CATEGORIES}
        for i, p in enumerate(puzzles, 1):
            print(f'#{i}')
            for cid, bs in p['groups']:
                print(f"  {cat[cid]['level']} {cat[cid]['name']:<42} " + ' | '.join(ITEMS[b][0] for b in bs))

if __name__ == '__main__':
    main()
