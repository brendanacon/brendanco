#!/usr/bin/env python3
"""Builds architecture.js: the 20th-century international architecture edition.

Same rules and generator as build_puzzles.py (every tile fits exactly one group in its
puzzle); only the items and categories differ.
Run:  python3 connections/tools/build_architecture.py [-v]
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_puzzles as engine

# id: (tile, architect, year, where — and anything worth knowing)
ITEMS = {
  'villasavoye':   ("Villa Savoye", "Le Corbusier", "1931", "Poissy, France"),
  'unite':         ("Unité d'Habitation", "Le Corbusier", "1952", "Marseille, France"),
  'ronchamp':      ("Notre-Dame du Haut", "Le Corbusier", "1955", "Ronchamp, France · chapel"),
  'latourette':    ("La Tourette Priory", "Le Corbusier", "1960", "near Lyon, France · monastery"),
  'lc4':           ("LC4 Chaise Longue", "Le Corbusier, Jeanneret & Perriand", "1928", "Chair"),
  'chandigarh':    ("Chandigarh", "Le Corbusier (master plan)", "1950s", "India · planned capital city"),
  'fallingwater':  ("Fallingwater", "Frank Lloyd Wright", "1937", "Pennsylvania, USA"),
  'guggenheimny':  ("Guggenheim New York", "Frank Lloyd Wright", "1959", "New York · museum"),
  'robie':         ("Robie House", "Frank Lloyd Wright", "1910", "Chicago · built for Frederick Robie"),
  'johnsonwax':    ("Johnson Wax Headquarters", "Frank Lloyd Wright", "1939", "Racine, Wisconsin"),
  'unitytemple':   ("Unity Temple", "Frank Lloyd Wright", "1908", "Oak Park, near Chicago · church"),
  'taliesin':      ("Taliesin West", "Frank Lloyd Wright", "1937", "Arizona · Wright's own winter home & studio"),
  'barcelonapav':  ("Barcelona Pavilion", "Mies van der Rohe & Lilly Reich", "1929", "Barcelona · 1929 International Exposition"),
  'farnsworth':    ("Farnsworth House", "Mies van der Rohe", "1951", "Plano, Illinois · built for Edith Farnsworth"),
  'seagram':       ("Seagram Building", "Mies van der Rohe (with Philip Johnson)", "1958", "New York · whisky company HQ"),
  'neuenational':  ("Neue Nationalgalerie", "Mies van der Rohe", "1968", "Berlin · art museum"),
  'tugendhat':     ("Villa Tugendhat", "Mies van der Rohe", "1930", "Brno, Czechia · built for the Tugendhats"),
  'crownhall':     ("Crown Hall", "Mies van der Rohe", "1956", "Chicago · architecture school"),
  'barcelonachair':("Barcelona Chair", "Mies van der Rohe & Lilly Reich", "1929", "Chair"),
  'paimio':        ("Paimio Sanatorium", "Alvar Aalto", "1933", "Paimio, Finland"),
  'mairea':        ("Villa Mairea", "Alvar Aalto", "1939", "Finland · built for Maire Gullichsen"),
  'finlandia':     ("Finlandia Hall", "Alvar Aalto", "1971", "Helsinki · concert hall"),
  'saynatsalo':    ("Säynätsalo Town Hall", "Alvar Aalto", "1952", "Finland"),
  'paimiochair':   ("Paimio Chair", "Alvar Aalto", "1932", "Chair"),
  'brasiliacath':  ("Brasília Cathedral", "Oscar Niemeyer", "1970", "Brasília, Brazil"),
  'congress':      ("National Congress of Brazil", "Oscar Niemeyer", "1960", "Brasília, Brazil · parliament"),
  'niteroi':       ("Niterói Art Museum", "Oscar Niemeyer", "1996", "Niterói, Brazil"),
  'pampulha':      ("Pampulha Church", "Oscar Niemeyer", "1943", "Belo Horizonte, Brazil"),
  'copan':         ("Copan Building", "Oscar Niemeyer", "1966", "São Paulo, Brazil · apartments"),
  'brasilia':      ("Brasília", "Lúcio Costa & Oscar Niemeyer", "1960", "Brazil · planned capital city"),
  'salk':          ("Salk Institute", "Louis Kahn", "1965", "La Jolla, California"),
  'kimbell':       ("Kimbell Art Museum", "Louis Kahn", "1972", "Fort Worth, Texas"),
  'dhaka':         ("Bangladesh Parliament", "Louis Kahn", "1982", "Dhaka, Bangladesh"),
  'exeter':        ("Exeter Library", "Louis Kahn", "1971", "New Hampshire, USA"),
  'bilbao':        ("Guggenheim Bilbao", "Frank Gehry", "1997", "Bilbao, Spain · museum"),
  'dancinghouse':  ("Dancing House", "Frank Gehry & Vlado Milunić", "1996", "Prague · nicknamed Fred and Ginger"),
  'vitramuseum':   ("Vitra Design Museum", "Frank Gehry", "1989", "Weil am Rhein, Germany"),
  'gehryhouse':    ("Gehry Residence", "Frank Gehry", "1978", "Santa Monica · Gehry's own home"),
  'sydneyopera':   ("Sydney Opera House", "Jørn Utzon", "1973", "Sydney"),
  'bagsvaerd':     ("Bagsværd Church", "Jørn Utzon", "1976", "Copenhagen"),
  'kuwait':        ("Kuwait National Assembly", "Jørn Utzon", "1982", "Kuwait City · parliament"),
  'canlis':        ("Can Lis", "Jørn Utzon", "1972", "Mallorca · Utzon's own home"),
  'louvrepyramid': ("Louvre Pyramid", "I.M. Pei", "1989", "Paris · museum entrance"),
  'bankofchina':   ("Bank of China Tower", "I.M. Pei", "1990", "Hong Kong"),
  'eastwing':      ("National Gallery East Wing", "I.M. Pei", "1978", "Washington DC · art museum"),
  'jfklibrary':    ("JFK Library", "I.M. Pei", "1979", "Boston"),
  'twa':           ("TWA Flight Center", "Eero Saarinen", "1962", "New York · airport terminal at JFK"),
  'gatewayarch':   ("Gateway Arch", "Eero Saarinen", "1965", "St Louis"),
  'dulles':        ("Dulles Airport", "Eero Saarinen", "1962", "Washington DC"),
  'tulipchair':    ("Tulip Chair", "Eero Saarinen", "1957", "Chair"),
  'bauhaus':       ("Bauhaus Dessau", "Walter Gropius", "1926", "Dessau, Germany · art school"),
  'fagus':         ("Fagus Factory", "Walter Gropius & Adolf Meyer", "1913", "Alfeld, Germany"),
  'gropiushouse':  ("Gropius House", "Walter Gropius", "1938", "Massachusetts · Gropius's own home"),
  'panam':         ("Pan Am Building", "Walter Gropius, Pietro Belluschi & Emery Roth", "1963", "New York · airline HQ"),
  'casabatllo':    ("Casa Batlló", "Antoni Gaudí", "1906", "Barcelona · remodelled for Josep Batlló"),
  'casamila':      ("Casa Milà", "Antoni Gaudí", "1912", "Barcelona · built for the Milà family"),
  'parkguell':     ("Park Güell", "Antoni Gaudí", "1914", "Barcelona"),
  'sagrada':       ("Sagrada Família", "Antoni Gaudí", "begun 1882", "Barcelona · basilica"),
  'churchlight':   ("Church of the Light", "Tadao Ando", "1989", "Osaka, Japan"),
  'churchwater':   ("Church on the Water", "Tadao Ando", "1988", "Hokkaido, Japan"),
  'watertemple':   ("Water Temple", "Tadao Ando", "1991", "Awaji Island, Japan · Buddhist temple"),
  'azuma':         ("Azuma House", "Tadao Ando", "1976", "Osaka, Japan · the Row House"),
  'hsbc':          ("HSBC Building", "Norman Foster", "1985", "Hong Kong · bank HQ"),
  'reichstag':     ("Reichstag Dome", "Norman Foster", "1999", "Berlin · parliament"),
  'stansted':      ("Stansted Airport", "Norman Foster", "1991", "London"),
  'cheklapkok':    ("Chek Lap Kok Airport", "Norman Foster", "1998", "Hong Kong"),
  'glasshouse':    ("Glass House", "Philip Johnson", "1949", "Connecticut · Johnson's own home"),
  'att':           ("AT&T Building", "Philip Johnson & John Burgee", "1984", "New York · phone company HQ"),
  'crystal':       ("Crystal Cathedral", "Philip Johnson & John Burgee", "1980", "California · church"),
  'lipstick':      ("Lipstick Building", "Philip Johnson & John Burgee", "1986", "New York"),
  'rothko':        ("Rothko Chapel", "Philip Johnson, Howard Barnstone & Eugene Aubry", "1971", "Houston"),
  'yoyogi':        ("Yoyogi National Gymnasium", "Kenzo Tange", "1964", "Tokyo · 1964 Olympics"),
  'hiroshima':     ("Hiroshima Peace Museum", "Kenzo Tange", "1955", "Hiroshima, Japan"),
  'nakagin':       ("Nakagin Capsule Tower", "Kisho Kurokawa", "1972", "Tokyo"),
  'kansai':        ("Kansai Airport", "Renzo Piano", "1994", "Osaka, Japan"),
  'pompidou':      ("Centre Pompidou", "Renzo Piano & Richard Rogers", "1977", "Paris · art centre"),
  'lloyds':        ("Lloyd's Building", "Richard Rogers", "1986", "London · insurance market HQ"),
  'schroder':      ("Schröder House", "Gerrit Rietveld", "1924", "Utrecht · built for Truus Schröder"),
  'redblue':       ("Red and Blue Chair", "Gerrit Rietveld", "1923", "Chair"),
  'einstein':      ("Einstein Tower", "Erich Mendelsohn", "1921", "Potsdam, Germany · observatory"),
  'chrysler':      ("Chrysler Building", "William Van Alen", "1930", "New York · car company HQ"),
  'empirestate':   ("Empire State Building", "Shreve, Lamb & Harmon", "1931", "New York"),
  'rockefeller':   ("Rockefeller Center", "Raymond Hood & others", "1939", "New York"),
  'flatiron':      ("Flatiron Building", "Daniel Burnham", "1902", "New York"),
  'sears':         ("Sears Tower", "SOM (Bruce Graham & Fazlur Khan)", "1973", "Chicago · now Willis Tower"),
  'hancock':       ("John Hancock Center", "SOM (Bruce Graham & Fazlur Khan)", "1969", "Chicago"),
  'lever':         ("Lever House", "SOM (Gordon Bunshaft)", "1952", "New York · soap company HQ"),
  'marinacity':    ("Marina City", "Bertrand Goldberg", "1964", "Chicago · the 'corn cob' towers"),
  'wtc':           ("World Trade Center", "Minoru Yamasaki", "1973", "New York"),
  'habitat67':     ("Habitat 67", "Moshe Safdie", "1967", "Montreal · built for Expo 67"),
  'biosphere':     ("Montreal Biosphère", "Buckminster Fuller", "1967", "Montreal · US pavilion at Expo 67"),
  'atomium':       ("Atomium", "André Waterkeyn", "1958", "Brussels · built for Expo 58"),
  'spaceneedle':   ("Space Needle", "John Graham & Edward Carlson", "1962", "Seattle · 1962 World's Fair"),
  'cntower':       ("CN Tower", "John Andrews & WZMH", "1976", "Toronto"),
  'tvtower':       ("Berlin TV Tower", "Hermann Henselmann & others", "1969", "Berlin"),
  'sydneytower':   ("Sydney Tower", "Donald Crone", "1981", "Sydney"),
  'philharmonie':  ("Berlin Philharmonie", "Hans Scharoun", "1963", "Berlin · concert hall"),
  'festivalhall':  ("Royal Festival Hall", "Leslie Martin & Robert Matthew", "1951", "London · concert hall"),
  'barbican':      ("Barbican Estate", "Chamberlin, Powell & Bon", "1982", "London"),
  'trellick':      ("Trellick Tower", "Ernő Goldfinger", "1972", "London"),
  'nationaltheatre':("National Theatre", "Denys Lasdun", "1976", "London"),
  'bostoncityhall':("Boston City Hall", "Kallmann McKinnell & Knowles", "1968", "Boston"),
  'masp':          ("MASP", "Lina Bo Bardi", "1968", "São Paulo · São Paulo Museum of Art"),
  'barragan':      ("Casa Barragán", "Luis Barragán", "1948", "Mexico City · Barragán's own home"),
  'whitney':       ("Whitney Museum", "Marcel Breuer", "1966", "New York"),
  'wassily':       ("Wassily Chair", "Marcel Breuer", "1925", "Chair"),
  'egg':           ("Egg Chair", "Arne Jacobsen", "1958", "Chair"),
  'eameschair':    ("Eames Lounge Chair", "Charles & Ray Eames", "1956", "Chair"),
  'eameshouse':    ("Eames House", "Charles & Ray Eames", "1949", "Los Angeles · the Eameses' own home"),
  'roseseidler':   ("Rose Seidler House", "Harry Seidler", "1950", "Sydney · built for his mother Rose"),
  'ausquare':      ("Australia Square", "Harry Seidler", "1967", "Sydney"),
  'muller':        ("Villa Müller", "Adolf Loos", "1930", "Prague · built for František Müller"),
  'stoclet':       ("Palais Stoclet", "Josef Hoffmann", "1911", "Brussels · built for Adolphe Stoclet"),
  'imarabe':       ("Institut du Monde Arabe", "Jean Nouvel", "1987", "Paris"),
  'grandearche':   ("La Grande Arche", "Johan Otto von Spreckelsen", "1989", "Paris"),
  'pentagon':      ("The Pentagon", "George Bergstrom", "1943", "Virginia, USA"),
  'aph':           ("Parliament House, Canberra", "Mitchell/Giurgola & Thorp", "1988", "Canberra"),
  'canberra':      ("Canberra", "Walter Burley Griffin & Marion Mahony Griffin", "1913", "Australia · planned capital city"),
  'islamabad':     ("Islamabad", "Constantinos Doxiadis", "1960s", "Pakistan · planned capital city"),
  # --- added for variety ---
  'petronas':    ("Petronas Towers", "César Pelli", "1998", "Kuala Lumpur · world's tallest 1998–2004"),
  'pennstation': ("Penn Station", "McKim, Mead & White", "1910", "New York · demolished 1963"),
  'imperial':    ("Imperial Hotel, Tokyo", "Frank Lloyd Wright", "1923", "Tokyo · demolished 1968"),
  'pruittigoe':  ("Pruitt-Igoe", "Minoru Yamasaki", "1954", "St Louis · demolished 1972"),
  'e1027':       ("E-1027", "Eileen Gray", "1929", "Roquebrune-Cap-Martin, France"),
  'vitrafire':   ("Vitra Fire Station", "Zaha Hadid", "1993", "Weil am Rhein, Germany"),
  'munich':      ("Munich Olympic Stadium", "Günter Behnisch & Frei Otto", "1972", "Munich · 1972 Olympics"),
  'montrealoly': ("Montreal Olympic Stadium", "Roger Taillibert", "1976", "Montreal · 1976 Olympics"),
  'palazzetto':  ("Palazzetto dello Sport", "Pier Luigi Nervi", "1957", "Rome · 1960 Olympics"),
  'viipuri':     ("Viipuri Library", "Alvar Aalto", "1935", "Vyborg, now Russia"),
  'stockholmlib':("Stockholm Public Library", "Gunnar Asplund", "1928", "Stockholm"),
  'hollyhock':   ("Hollyhock House", "Frank Lloyd Wright", "1921", "Los Angeles"),
}

C = lambda id, level, name, members, also=(), key=None, gloss=None, memory=False: dict(
    id=id, level=level, name=name, members=list(members), also=list(also), key=key or {}, gloss=gloss or {}, memory=memory)

CATEGORIES = [
  # who designed it — the famous five are yellow, the rest green
  C('wright', 0, "Frank Lloyd Wright", ['fallingwater','guggenheimny','robie','johnsonwax','unitytemple','taliesin','hollyhock','imperial']),
  C('mies', 0, "Mies van der Rohe", ['barcelonapav','farnsworth','seagram','neuenational','tugendhat','crownhall','barcelonachair']),
  C('corbu', 0, "Le Corbusier", ['villasavoye','unite','ronchamp','latourette','lc4'], also=['chandigarh']),
  C('gaudi', 0, "Gaudí", ['casabatllo','casamila','parkguell','sagrada']),
  C('gehry', 0, "Frank Gehry", ['bilbao','dancinghouse','vitramuseum','gehryhouse']),
  C('aalto', 1, "Alvar Aalto", ['paimio','mairea','finlandia','saynatsalo','paimiochair','viipuri']),
  C('niemeyer', 1, "Oscar Niemeyer", ['brasiliacath','congress','niteroi','pampulha','copan'], also=['brasilia']),
  C('kahn', 1, "Louis Kahn", ['salk','kimbell','dhaka','exeter']),
  C('pei', 1, "I.M. Pei", ['louvrepyramid','bankofchina','eastwing','jfklibrary']),
  C('saarinen', 1, "Eero Saarinen", ['twa','gatewayarch','dulles','tulipchair']),
  C('gropius', 1, "Walter Gropius", ['bauhaus','fagus','gropiushouse','panam']),
  C('utzon', 1, "Jørn Utzon", ['sydneyopera','bagsvaerd','kuwait','canlis']),
  C('ando', 1, "Tadao Ando", ['churchlight','churchwater','watertemple','azuma']),
  C('foster', 1, "Norman Foster", ['hsbc','reichstag','stansted','cheklapkok']),
  C('johnson', 1, "Philip Johnson", ['glasshouse','att','crystal','lipstick'], also=['seagram','rothko']),

  # where it is
  C('nyc', 0, "In New York", ['guggenheimny','seagram','chrysler','empirestate','rockefeller','flatiron','twa','lever','wtc',
                              'panam','att','whitney','lipstick','pennstation']),
  C('chicago', 1, "In Chicago", ['robie','crownhall','sears','hancock','marinacity'], also=['unitytemple','farnsworth']),
  C('london', 1, "In London", ['lloyds','barbican','trellick','nationaltheatre','festivalhall'], also=['stansted']),
  C('paris', 1, "In Paris", ['pompidou','louvrepyramid','imarabe','grandearche'], also=['villasavoye']),
  C('berlin', 1, "In Berlin", ['neuenational','reichstag','tvtower','philharmonie'], also=['einstein']),
  C('barcelona', 1, "In Barcelona", ['casabatllo','casamila','parkguell','sagrada','barcelonapav'], also=['barcelonachair']),
  C('japan', 1, "In Japan", ['yoyogi','nakagin','churchlight','churchwater','watertemple','azuma','hiroshima','kansai','imperial']),
  C('brazil', 1, "In Brazil", ['brasiliacath','congress','niteroi','pampulha','copan','masp'], also=['brasilia']),
  C('australia', 1, "In Australia", ['sydneyopera','roseseidler','ausquare','sydneytower','aph','canberra']),

  # what it is
  C('chairs', 0, "Chairs, not buildings", ['barcelonachair','wassily','tulipchair','redblue','paimiochair','egg','lc4','eameschair']),
  C('airports', 0, "Airports", ['twa','dulles','stansted','kansai','cheklapkok'], key={'dulles':'Airport','stansted':'Airport','kansai':'Airport','cheklapkok':'Airport'}),
  C('villa', 0, "Villa ___", ['villasavoye','tugendhat','mairea','muller'], key={'villasavoye':'Villa','tugendhat':'Villa','mairea':'Villa','muller':'Villa'}),
  C('worship', 1, "Places of worship", ['ronchamp','latourette','brasiliacath','pampulha','churchlight','churchwater','watertemple',
                                         'bagsvaerd','unitytemple','crystal','rothko','sagrada']),
  C('museums', 1, "Art museums", ['guggenheimny','bilbao','pompidou','kimbell','neuenational','masp','niteroi','vitramuseum','eastwing',
                                   'whitney','louvrepyramid'], also=['jfklibrary','hiroshima','imarabe']),
  C('music', 1, "Concert halls & opera houses", ['sydneyopera','philharmonie','finlandia','festivalhall'], also=['nationaltheatre','barbican']),
  C('towers', 1, "Observation towers", ['spaceneedle','cntower','tvtower','sydneytower'],
    also=['atomium','empirestate','sears','gatewayarch','hancock','wtc']),
  C('capitals', 2, "Planned capital cities", ['canberra','brasilia','chandigarh','islamabad']),
  C('parliaments', 2, "Parliament buildings", ['congress','dhaka','kuwait','reichstag','aph'], also=['chandigarh','canberra','brasilia']),
  C('company', 2, "Named after a company", ['seagram','chrysler','lever','panam','att','hsbc','lloyds','johnsonwax','bankofchina','sears'],
    also=['twa','hancock','rockefeller'],
    gloss={'seagram':'whisky','chrysler':'cars','lever':'soap','panam':'airline','att':'phones','hsbc':'bank','lloyds':'insurance',
           'johnsonwax':'cleaning products','bankofchina':'bank','sears':'department stores'}),
  C('ownhome', 2, "Architects' own homes", ['gropiushouse','eameshouse','gehryhouse','barragan','glasshouse','taliesin','canlis'],
    gloss={'glasshouse':'Philip Johnson','taliesin':'Frank Lloyd Wright','canlis':'Jørn Utzon'}),
  C('clients', 2, "Homes named after their owners", ['villasavoye','robie','farnsworth','schroder','tugendhat','roseseidler','muller',
                                                      'stoclet','casabatllo','casamila','mairea'],
    also=['gropiushouse','eameshouse','gehryhouse','barragan']),
  C('expo', 2, "Built for a World's Fair", ['barcelonapav','habitat67','biosphere','atomium','spaceneedle'], memory=True,
    gloss={'barcelonapav':'1929','habitat67':'Expo 67','biosphere':'Expo 67','atomium':'Expo 58','spaceneedle':'1962'}),
  C('brutalism', 2, "Brutalist concrete", ['barbican','trellick','nationaltheatre','bostoncityhall'], memory=True,
    also=['unite','habitat67','masp','salk','dhaka','exeter','yoyogi','kimbell','latourette']),
  C('hightech', 2, "High-tech: the workings on show", ['pompidou','lloyds','hsbc','stansted'], memory=True,
    also=['kansai','cheklapkok','reichstag']),

  # wordplay
  C('shapes', 3, "A shape hides in the name", ['louvrepyramid','gatewayarch','ausquare','biosphere','pentagon','grandearche'],
    also=['egg','atomium'],
    key={'louvrepyramid':'Pyramid','gatewayarch':'Arch','ausquare':'Square','biosphere':'sphère','pentagon':'Pentagon','grandearche':'Arche'}),
  C('initials', 3, "Initials in the name", ['twa','att','masp','hsbc','jfklibrary','cntower','lc4'],
    key={'twa':'TWA','att':'AT&T','masp':'MASP','hsbc':'HSBC','jfklibrary':'JFK','cntower':'CN','lc4':'LC4'}),
  C('lookslike', 3, "Named for what it looks like", ['lipstick','egg','tulipchair','flatiron'],
    also=['dancinghouse','louvrepyramid','biosphere','atomium','gatewayarch','pentagon','marinacity','spaceneedle'],
    key={'lipstick':'Lipstick','egg':'Egg','tulipchair':'Tulip','flatiron':'Flatiron'}),
  # --- added for variety ---
  C('tallest', 2, "Once the world's tallest building", ['chrysler','empirestate','wtc','sears','petronas'], memory=True),
  C('demolished', 2, "Demolished or destroyed", ['wtc','nakagin','pennstation','imperial','pruittigoe']),
  C('women', 2, "Designed by a woman", ['e1027','vitrafire','masp','canberra'], also=['barcelonapav','barcelonachair','lc4']),
  C('olympic', 1, "Olympic venues", ['yoyogi','munich','montrealoly','palazzetto']),
  C('libraries', 1, "Libraries", ['exeter','jfklibrary','viipuri','stockholmlib']),
  C('nordic', 1, "In the Nordics", ['finlandia','paimio','mairea','saynatsalo','bagsvaerd','stockholmlib'], also=['viipuri']),
  C('california', 1, "In California", ['salk','eameshouse','gehryhouse','crystal','hollyhock']),
  C('famous', 3, "Named after someone famous (who didn't live there)", ['einstein','jfklibrary','pompidou','rothko','salk'],
    also=['guggenheimny','bilbao','whitney','kimbell','villasavoye','robie','farnsworth','schroder','tugendhat','roseseidler',
          'muller','stoclet','casabatllo','casamila','mairea','gropiushouse','eameshouse','gehryhouse','barragan']),
  C('nothome', 3, "A 'House' that isn't a home", ['lever','sydneyopera','aph','dancinghouse']),
]

for c in CATEGORIES:
    for b in c['members'] + c['also'] + list(c['key']) + list(c['gloss']):
        assert b in ITEMS, (c['id'], b)
    assert not set(c['members']) & set(c['also']), c['id']
    for b, k in c['key'].items():
        assert k.lower() in ITEMS[b][0].lower(), (c['id'], b, k)

def main():
    engine.CATEGORIES = CATEGORIES  # the generator reads its tables from the module
    engine.DECOY_OK = set()
    engine.CAP_SMALL, engine.CAP_BIG = 4, 6
    engine.WINDOW, engine.REPEAT_GAP = 7, 10**6
    engine.POOL_TRIES = 2
    for seed in range(1, 6):
        try:
            puzzles, cat_use, tile_use = engine.build(n=50, seed=seed)
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
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'architecture.js')
    with open(path, 'w') as f:
        f.write('// Generated by tools/build_architecture.py — edit that file, not this one.\n')
        f.write('window.ARCHITECTURE = ' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(f'seed {seed}: {len(puzzles)} puzzles from {len(ITEMS)} items')
    print('category use:', dict(sorted(cat_use.items(), key=lambda x: -x[1])))
    print('unused:', [b for b in ITEMS if not tile_use[b]])
    print('most used:', [(ITEMS[b][0], n) for b, n in tile_use.most_common(6)])
    if '-v' in sys.argv:
        cat = {c['id']: c for c in CATEGORIES}
        for i, p in enumerate(puzzles, 1):
            print(f'#{i}')
            for cid, bs in p['groups']:
                print(f"  {cat[cid]['level']} {cat[cid]['name']:<36} " + ' | '.join(ITEMS[b][0] for b in bs))

if __name__ == '__main__':
    main()
