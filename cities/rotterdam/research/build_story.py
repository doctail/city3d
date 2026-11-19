#!/usr/bin/env python3
"""Rotterdam story.json generator (yb-historian + yb-modeler). Every quote is a sentence found by regex in a fetched text file."""
import json, re, math, os, sys
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sources_fetched')
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
FETCHED = '2026-11-19'
LAT0, LON0 = 51.9221, 4.4795
KX = math.cos(math.radians(LAT0)) * 111320.0; KY = 110540.0
def ll(x, y): return [round(LAT0 + y / KY, 5), round(LON0 + x / KX, 5)]
def lx(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def circle(cx, cy, r, n=12): return [ll(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
def poly(pts): return [ll(x, y) for x, y in pts]

SRC = {  # id: (url, title, file)
 'S1': ('https://en.wikipedia.org/wiki/Rotterdam', 'Wikipedia EN, Rotterdam', 'en_Rotterdam.txt'),
 'S2': ('https://en.wikipedia.org/wiki/Timeline_of_Rotterdam', 'Wikipedia EN, Timeline of Rotterdam (History of Rotterdam)', 'en_History_of_Rotterdam.txt'),
 'S3': ('https://nl.wikipedia.org/wiki/Geschiedenis_van_Rotterdam', 'Wikipedia NL, Geschiedenis van Rotterdam', 'nl_Geschiedenis_van_Rotterdam.txt'),
 'S4': ('https://nl.wikipedia.org/wiki/Hoogstraat_(Rotterdam)', 'Wikipedia NL, Hoogstraat (Rotterdam)', 'nl_Hoogstraat_(Rotterdam).txt'),
 'S5': ('https://en.wikipedia.org/wiki/Rotterdam_Blitz', 'Wikipedia EN, Rotterdam Blitz', 'en_Rotterdam_Blitz.txt'),
 'S6': ('https://nl.wikipedia.org/wiki/Bombardement_op_Rotterdam', 'Wikipedia NL, Bombardement op Rotterdam', 'nl_Bombardement_op_Rotterdam.txt'),
 'S7': ('https://en.wikipedia.org/wiki/Laurenskerk', 'Wikipedia EN, Laurenskerk', 'en_Laurenskerk.txt'),
 'S9': ('https://en.wikipedia.org/wiki/Rotterdam_City_Hall', 'Wikipedia EN, Rotterdam City Hall', 'en_Rotterdam_City_Hall.txt'),
 'S10': ('https://nl.wikipedia.org/wiki/Stadhuis_van_Rotterdam', 'Wikipedia NL, Stadhuis van Rotterdam', 'nl_Stadhuis_van_Rotterdam.txt'),
 'S11': ('https://en.wikipedia.org/wiki/Euromast', 'Wikipedia EN, Euromast', 'en_Euromast.txt'),
 'S12': ('https://nl.wikipedia.org/wiki/Euromast', 'Wikipedia NL, Euromast', 'nl_Euromast.txt'),
 'S13': ('https://en.wikipedia.org/wiki/Delfshaven', 'Wikipedia EN, Delfshaven', 'en_Delfshaven.txt'),
 'S14': ('https://en.wikipedia.org/wiki/Pilgrim_Fathers_Church', "Wikipedia EN, Old or Pilgrim Fathers' Church (Delfshaven)", 'en_Pilgrim_Fathers_Church.txt'),
 'S15': ('https://en.wikipedia.org/wiki/Nieuwe_Waterweg', 'Wikipedia EN, Nieuwe Waterweg', 'en_Nieuwe_Waterweg.txt'),
 'S16': ('https://en.wikipedia.org/wiki/Witte_Huis', 'Wikipedia EN, Witte Huis (White House)', 'en_Witte_Huis.txt'),
 'S17': ('https://nl.wikipedia.org/wiki/Witte_Huis_(Rotterdam)', 'Wikipedia NL, Witte Huis (Rotterdam)', 'nl_Witte_Huis_(Rotterdam).txt'),
 'S18': ('https://en.wikipedia.org/wiki/Rotterdam_Hofplein_railway_station', 'Wikipedia EN, Rotterdam Hofplein railway station', 'en_Rotterdam_Hofplein_railway_station.txt'),
 'S19': ('https://en.wikipedia.org/wiki/Van_Nelle_Factory', 'Wikipedia EN, Van Nelle Factory', 'en_Van_Nelle_Factory.txt'),
 'S20': ('https://en.wikipedia.org/wiki/Lijnbaan', 'Wikipedia EN, Lijnbaan', 'en_Lijnbaan.txt'),
 'S21': ('https://en.wikipedia.org/wiki/Groothandelsgebouw', 'Wikipedia EN, Groothandelsgebouw', 'en_Groothandelsgebouw.txt'),
 'S22': ('https://en.wikipedia.org/wiki/Rotterdam_Centraal_railway_station', 'Wikipedia EN, Rotterdam Centraal railway station', 'en_Rotterdam_Centraal_railway_station.txt'),
 'S23': ('https://en.wikipedia.org/wiki/Port_of_Rotterdam', 'Wikipedia EN, Port of Rotterdam', 'en_Port_of_Rotterdam.txt'),
 'S24': ('https://en.wikipedia.org/wiki/Waalhaven', 'Wikipedia EN, Waalhaven', 'en_Waalhaven.txt'),
 'S26': ('https://en.wikipedia.org/wiki/Erasmus_Bridge', 'Wikipedia EN, Erasmus Bridge', 'en_Erasmus_Bridge.txt'),
 'S27': ('https://en.wikipedia.org/wiki/Kop_van_Zuid', 'Wikipedia EN, Kop van Zuid', 'en_Kop_van_Zuid.txt'),
 'S28': ('https://en.wikipedia.org/wiki/Markthal', 'Wikipedia EN, Markthal', 'en_Markthal.txt'),
 'S29': ('https://en.wikipedia.org/wiki/Maastoren', 'Wikipedia EN, Maastoren', 'en_Maastoren.txt'),
 'S30': ('https://en.wikipedia.org/wiki/De_Rotterdam', 'Wikipedia EN, De Rotterdam', 'en_De_Rotterdam.txt'),
 'S31': ('https://en.wikipedia.org/wiki/Zalmhaven', 'Wikipedia EN, Zalmhaven', 'en_Zalmhaven.txt'),
 'S32': ('https://en.wikipedia.org/wiki/Delftse_Poort', 'Wikipedia EN, Delftse Poort', 'en_Delftse_Poort.txt'),
 'S33': ('https://en.wikipedia.org/wiki/Maasvlakte', 'Wikipedia EN, Maasvlakte', 'en_Maasvlakte.txt'),
 'S34': ('https://en.wikipedia.org/wiki/Willemsbrug', 'Wikipedia EN, Willemsbrug', 'en_Willemsbrug.txt'),
 'S35': ('https://en.wikipedia.org/wiki/Schielandshuis', 'Wikipedia EN, Schielandshuis', 'en_Schielandshuis.txt'),
 'S36': ('https://en.wikipedia.org/wiki/County_of_Holland', 'Wikipedia EN, County of Holland', 'en_County_of_Holland.txt'),
 'S37': ('https://en.wikipedia.org/wiki/Burgundian_Netherlands', 'Wikipedia EN, Burgundian Netherlands', 'en_Burgundian_Netherlands.txt'),
 'S38': ('https://en.wikipedia.org/wiki/Dutch_Republic', 'Wikipedia EN, Dutch Republic', 'en_Dutch_Republic.txt'),
 'S39': ('https://en.wikipedia.org/wiki/Batavian_Republic', 'Wikipedia EN, Batavian Republic', 'en_Batavian_Republic.txt'),
 'S40': ('https://en.wikipedia.org/wiki/Kingdom_of_Holland', 'Wikipedia EN, Kingdom of Holland', 'en_Kingdom_of_Holland.txt'),
 'S41': ('https://en.wikipedia.org/wiki/Kingdom_of_the_Netherlands', 'Wikipedia EN, Kingdom of the Netherlands', 'en_Kingdom_of_the_Netherlands.txt'),
 'S42': ('https://en.wikipedia.org/wiki/German_occupation_of_the_Netherlands', 'Wikipedia EN, German occupation of the Netherlands', 'en_German_occupation_of_the_Netherlands.txt'),
 'S43': ('https://en.wikipedia.org/wiki/Rotte_(river)', 'Wikipedia EN, Rotte (river)', 'en_Rotte_(river).txt'),
 'S44': ('https://www.wikidata.org/wiki/Q34370', 'Wikidata Q34370 (Rotterdam), population P1082', 'wd_pop.txt'),
 'S45': ('https://nl.wikipedia.org/wiki/Oude_Haven_(Rotterdam)', 'Wikipedia NL, Oude Haven (Rotterdam)', 'nl_Oude_Haven_(Rotterdam).txt'),
}
_text = {}
def sents(sid):
    if sid not in _text:
        t = open(os.path.join(HERE, SRC[sid][2])).read()
        _text[sid] = [s.strip() for chunk in t.split('\n') for s in re.split(r'(?<=[.!?])\s+', chunk) if s.strip()]
    return _text[sid]
QUOTES = {k: [] for k in SRC}
LOG = []
def C(sid, pat, cut=None):
    """cite: find first sentence matching regex in the source text; register it as a quote; return sid"""
    for s in sents(sid):
        if re.search(pat, s):
            q = s[:300]
            if cut: q = s[:s.index(cut) + len(cut)] if cut in s else q
            if q not in QUOTES[sid]: QUOTES[sid].append(q)
            LOG.append(f'{sid} | {q[:170]}')
            return sid
    raise SystemExit(f'NOT FOUND {sid}: {pat}')
def cites(*pairs):
    out = []
    for p in pairs:
        s = C(*p) if isinstance(p, tuple) else p
        if s not in out: out.append(s)
    return out

cards = []
def card(y, title, lines, src, hold=5.4, conf='high', labels=None, sober=False, note=None, chapter=None):
    d = {'y': y, 'title': title, 'lines': lines if isinstance(lines, list) else [lines], 'hold_s': hold, 'src': src, 'conf': conf}
    if labels: d['labels'] = labels
    if sober: d['sober'] = True
    if note: d['note'] = note
    cards.append(d)

# ============================================================== CARDS (sourced sentences; title/lines in American English)
card(1270, 'A dam on the Rotte', ['Around 1270 a dam closes the Rotte, a muddy fen stream.', 'The town takes its name from it.'],
     cites(('S4', r'Rond 1270 werd de dam in de Rotte voltooid'), ('S43', r'eponym of the city of Rotterdam'), ('S1', r'A dam on the Rotte was built in the 1260s')), 5.8, 'medium',
     note='S1 says the 1260s, S3/S4 say around 1270: year 1270 kept, conf medium.')
card(1275, 'The first wooden houses', ['Houses rise on top of the dam.', 'This is the start of today\'s Hoogstraat.'],
     cites(('S3', r'rond 1275 de eerste houten huizen gebouwd'), ('S4', r'Vlak na voltooiing werden de eerste houten huizen')), 5.2)
card(1283, 'Rotterdam on the record', ['The name Rotterdam is written down for the first time.'], cites(('S3', r'In 1283 is de eerste vermelding')), 4.8)
card(1299, 'A charter, then withdrawn', ['Count John I grants town rights in March.', 'They are revoked before the year ends.'],
     cites(('S3', r'Op 17 maart 1299 krijgt Rotterdam stadsrechten'), ('S3', r'Na september 1299 worden de Rotterdamse stadsrechten weer ingetrokken')), 5.4)
card(1340, 'City rights', ['Count William IV grants Rotterdam city rights.', 'It still has only a few thousand people.'],
     cites(('S1', r'granted city rights to Rotterdam, which then had a population of only a few thousand'), ('S3', r'verleent graaf Willem IV van Holland Rotterdam definitief stadsrechten')), 5.6, 'high',
     note='S1 says 7 July 1340, S3 says 7 June 1340: only the year is shown.')
card(1350, 'A canal to the north', ['The Rotterdamse Schie links the town with Delft and Leiden.'],
     cites(('S3', r'Rotterdamse Schie pas rond 1350 voltooid'), ('S1', r'Around the year 1350, a shipping canal')), 5.0, 'medium')
card(1358, 'Moats and palisades', ['The count allows defenses around the town.', 'The moats follow today\'s Coolsingel and Blaak.'],
     cites(('S3', r'In 1358 geeft graaf Albrecht van Beieren toestemming'), ('S3', r'De vestingsingels liepen langs de huidige Coolsingel')), 5.4)
card(1389, 'Delft digs a harbor', ['To avoid Rotterdam\'s tolls, Delft builds a harbor of its own.', 'The settlement is called Delfshaven.'],
     cites(('S13', r'in 1389 a harbour was created')), 5.6, 'high')
card(1449, 'A church for the town', ['Work starts on the late-Gothic Laurenskerk.', 'Rotterdam has about 1,200 houses.'],
     cites(('S3', r'Tussen 1449 en 1525 bouwt men de laat-gotische Laurenskerk'), ('S3', r'Rotterdam bestaat in die tijd uit ongeveer 1200 huizen'), ('S7', r'built as a Roman Catholic Church between 1449 and 1525')), 5.4, 'high', labels=['Laurenskerk'])
card(1466, 'Erasmus is born', ['Erasmus, a philosopher and one of Rotterdam\'s most famous sons, is born.'],
     cites(('S2', r'1466 - Erasmus, philosopher'), ('S3', r'een van Rotterdams beroemdste zonen, Erasmus')), 5.0, 'medium', note='S2 gives the year; S3 calls him one of Rotterdam\'s most famous sons (it does not give the birthplace).')
card(1489, 'A siege', ['Forces of Frans van Brederode besiege the town in the Hook and Cod wars.'],
     cites(('S2', r'1489 - Rotterdam besieged'), ('S3', r'Hoekse en Kabeljauwse twisten')), 5.0, 'medium', note='S2 gives 1489, S3 gives 1488-1490.')
card(1500, 'Walled at last', ['The town wall is complete.', 'The walled area shrinks: the Goudsesingel becomes the northeast edge.'],
     cites(('S3', r'Begin 1500 is de stadsmuur rondom Rotterdam voltooid'), ('S3', r'Rond 1500 wordt het ommuurde stadsgebied verkleind')), 5.6, 'high')
card(1563, 'The east burns', ['A great fire ravages the eastern part of the town.'], cites(('S3', r'In 1563 valt het oosten van de stad ten prooi aan een grote stadsbrand'), ('S2', r'1563 - Fire')), 5.2, 'high', sober=True)
card(1572, 'The Spanish sack the town', ['Troops of the Spanish governor storm in through the Oostpoort.', 'Rotterdam is plundered.'],
     cites(('S3', r'In 1572 werd Rotterdam geplunderd door troepen'), ('S3', r'De Bestorming van Rotterdam werd geleid door Bossu')), 6.0, 'high', sober=True)
card(1573, 'Rotterdam joins the Revolt', ['The town chooses the side of the Dutch Revolt.', 'It has about 10,000 people.'],
     cites(('S3', r'In 1573 kiest de stad de kant van de Opstand'), ('S3', r'De stad had toen ongeveer 10\.000 inwoners')), 5.4, 'high')
card(1575, 'The Water Town', ['The walled town grows south toward the river.', 'The Water Town fills the area between the Hoogstraat and the Maas.'],
     cites(('S3', r'Vanaf 1575 wordt de ommuurde stad weer uitgebreid'), ('S3', r'Het gebied tussen Hoogstraat, Schiedamse Singel en de Nieuwe Maas')), 5.6, 'high')
card(1579, 'Ships sail on to Rotterdam', ['Dordrecht loses its staple right.', 'Ships no longer have to unload there.'],
     cites(('S3', r'in 1579 bij de Staten van Holland gedaan, dat het middeleeuwse stapelrecht van Dordrecht werd ingetrokken')), 5.4, 'high')
card(1581, 'A seat in the States', ['Rotterdam is admitted to the States of Holland.'], cites(('S3', r'In 1581 kreeg de stad zelf zitting in de Staten')), 4.8, 'high')
card(1600, 'A company port', ['Rotterdam becomes the seat of a chamber of the Dutch East India Company and of the West India Company.'],
     cites(('S1', r'Rotterdam became the seat of one of the six chambers')), 5.6, 'medium', note='S1 gives no year for the chambers; the card year 1600 follows S1 "Beginning in the 1600s ... the port ... grew". Approximate.')
card(1610, 'The slave trade', ['From the 1600s until 1814, Dutch slave ships sail from Rotterdam.', 'Rotterdam merchants are pioneers of the trade.'],
     cites(('S1', r'Beginning in the 1600s, Rotterdam was involved in the Atlantic slave trade'), ('S1', r'According to historian Gerhard de Kok'), ('S1', r'From the 17th century until 1814')), 6.0, 'medium', sober=True,
     note='Year 1610 is a placement inside "beginning in the 1600s"; no exact start year in the source.')
card(1620, 'The Pilgrims leave Delfshaven', ['English Dissenters sail on the Speedwell for America.'],
     cites(('S13', r'On 1 August 1620 the Pilgrim fathers left Delfshaven'), ('S14', r'The Speedwell left Delfshaven, on 21 July 1620')), 5.4, 'medium', labels=['Pilgrim Fathers Church'],
     note='S13 says 1 August 1620, S14 says 21 July 1620: only the year is shown.')
card(1622, 'Erasmus in bronze', ['A bronze statue of Erasmus is set up by the Laurenskerk.', 'Rotterdam has about 20,000 people.'],
     cites(('S3', r'Door het plaatsen van een standbeeld van Hendrick de Keyser wordt in 1622'), ('S3', r'staat nog altijd naast de Laurenskerk'), ('S3', r'Bij de volkstelling van 1622')), 5.4, 'high')
card(1665, 'The Schielandshuis', ['A grand house is finished on the Rotte side of town.', 'It will be one of only two old buildings to survive 1940.'],
     cites(('S35', r'The Schielandshuis was built in 1662', 'was built in 1662'), ('S5', r'Only two buildings prior to the 19th century survived')), 5.6, 'medium',
     note='"on the Rotte side of town" is not sourced and is dropped from the line below.')
cards[-1]['lines'] = ['A grand house is finished in 1665.', 'It will be one of only two pre-19th-century buildings to survive 1940.']
card(1740, 'The sea route silts up', ['The old routes around Rozenburg become impassable.', 'Ships need a long detour to reach Rotterdam.'],
     cites(('S3', r'De directe vaarroutes van Rotterdam naar zee liepen tot de jaren 1740'), ('S3', r'Na 1740 verzandde deze routes en werden ze onbevaarbaar')), 5.6, 'high')
card(1795, 'Revolution', ['French troops arrive and the pro-Orange council is removed.', 'For the first time the city holds public elections.'],
     cites(('S3', r'Tijdens de Franse inval in 1795 wordt het prinsgezinde stadsbestuur afgezet'), ('S3', r'Voor het eerst komen er openbare verkiezingen')), 5.6, 'high')
card(1823, 'Steam', ['The first Dutch steamboat company starts regular lines from Rotterdam.', 'A shipyard follows on the south bank in 1825.'],
     cites(('S3', r'In 1823 is de oprichting van de Nederlandsche Stoomboot Maatschappij'), ('S3', r'Vanuit Rotterdam pioniert die met stoomaangedreven lijndiensten'), ('S3', r'In 1825 richt de NSbM het Etablissement Fijenoord op')), 5.6, 'medium',
     note='"first Dutch steamboat company" is not literally in the source; reworded below.')
cards[-1]['lines'] = ['A steamboat company starts regular lines from Rotterdam.', 'In 1825 it opens a shipyard on the south bank.']
card(1825, 'Beyond the walls', ['The town fills about 140 hectares and is crowded.', 'Only after 1825 does it start to grow outside its walls.'],
     cites(('S3', r'Desondanks breidde de stad zich niet uit buiten zijn wallen en singels'), ('S3', r'Pas na 1825 zou zij zich buiten deze enge grenzen gaan uitbreiden')), 5.6, 'high')
card(1847, 'The first train', ['The first railway reaches Rotterdam, toward The Hague and Amsterdam.'],
     cites(('S3', r'In 1847 krijgt Rotterdam een eerste treinverbinding'), ('S2', r'1847 - Delftsche Poort railway station opens')), 5.0, 'high')
card(1858, 'The river is full', ['The Oosterkade quay is finished.', 'All usable space in the city and along the river is taken.'],
     cites(('S3', r'Als laatste wordt in 1858 de Oosterkade voltooid'), ('S3', r'Hiermee is alle geschikte ruimte in de stad en langs de rivier gebruikt')), 5.6, 'high')
card(1863, 'A new road to the sea', ['A law approves a canal for ocean ships.', 'Engineer Pieter Caland designs it.'],
     cites(('S15', r'In 1863, a law was passed that allowed'), ('S15', r'Hydraulic engineer Pieter Caland was commissioned')), 5.4, 'high')
card(1869, 'The south bank joins', ['Rotterdam annexes parts of IJsselmonde, Katendrecht and Charlois.'],
     cites(('S3', r'In 1869 annexeert Rotterdam delen van gemeenten IJsselmonde, Katendrecht en Charlois'), ('S2', r'1869 - Feijenoord becomes part of city')), 5.2, 'high')
card(1872, 'The New Waterway opens', ['A canal through the Hook of Holland gives ocean ships a straight way to the city.'],
     cites(('S15', r'In 1872, the Nieuwe Waterweg was completed and Rotterdam was easily accessible'), ('S1', r'The greatest spurt of growth, both in port activity and population')), 5.6, 'high')
card(1877, 'Trains cross the river', ['A railway bridge and an elevated line carry trains through the city.', 'The Willemsbrug opens for city traffic a year later.'],
     cites(('S3', r'In 1877 opent de spoorverbinding van Antwerpen naar Rotterdam'), ('S3', r'Via de Willemsspoorbrug, Station Beurs en het Luchtspoor'), ('S3', r'In 1878 opent de Willemsbrug'), ('S2', r'1878 - Willemsbrug opens')), 5.8, 'medium', note='S34 says the first bridge opened in 1879; S3 and S2 say 1878.')
card(1879, 'A harbor on borrowed money', ['The new south-bank harbors open.', 'Their financier, Lodewijk Pincoffs, flees the country with a huge debt.'],
     cites(('S3', r'In 1879 openen de havenfaciliteiten van de RHV'), ('S3', r'Halsoverkop ontvlucht Pincoffs Nederland')), 5.8, 'high')
card(1886, 'Delfshaven joins the city', ['Delfshaven asks to be annexed by Rotterdam.'],
     cites(('S13', r'Delfshaven was annexed by Rotterdam in 1886 at its own request'), ('S2', r'1886 - Delfshaven becomes part of city')), 5.0, 'high', labels=['Pilgrim Fathers Church'])
card(1895, 'Kralingen and Charlois join', ['Two more neighbors are annexed.', 'Between 1880 and 1900 the population doubles, from 160,000 to 315,000.'],
     cites(('S3', r'Ten oosten van de stad wordt in 1895 Kralingen geannexeerd'), ('S3', r'In dat jaar worden ook Charlois'), ('S3', r'Tussen 1880 en 1900 is de bevolking snel gegroeid')), 5.8, 'high')
card(1913, 'A canal becomes a boulevard', ['The Coolvest moat is filled in and the Zandstraat quarter, home to about 2,400 people, is torn down.', 'The Coolsingel boulevard takes shape.'],
     cites(('S3', r'Tussen 1913 en 1922 wordt de Coolvest gedempt en de Zandstraatbuurt gesloopt'), ('S10', r'Voor de uitvoering werd de Coolvest gedempt'), ('S9', r'an entire neighborhood, Zandstraat, where about 2,400 people lived')), 5.8, 'high')
card(1914, 'A neutral city', ['In the First World War Rotterdam is a center of spying.', 'About 25,000 Belgian refugees live here.'],
     cites(('S1', r"During World War I, the city was the world's largest spy centre"), ('S1', r'an average of 25,000 Belgian refugees')), 5.6, 'high')
card(1920, 'Waalhaven Airport', ['The second civilian airport in the Netherlands opens next to the Waalhaven harbor.'],
     cites(('S24', r'It was the second civilian airport in the Netherlands and was opened in 1920')), 5.2, 'high')
card(1926, 'The Van Nelle Factory', ['A glass-and-steel factory goes up on the Schie.', 'Since 2014 it is a World Heritage Site.'],
     cites(('S19', r'Built between 1925 and 1931'), ('S19', r'a poem in steel and glass'), ('S19', r'designated UNESCO World Heritage Site since 2014')), 5.6, 'high', labels=['Van Nelle Factory'])
card(1930, 'A department store draws a crowd', ['The Bijenkorf opens on the Coolsingel.', 'About 70,000 people come to see it.'],
     cites(('S3', r'De opening van warenhuis de Bijenkorf in 1930')), 5.4, 'high')
card(1936, 'A lively, modern city', ['Revues, cinemas and jazz fill the evenings around the Schiedamsedijk.', 'A new Beurs is built, finished in 1940.'],
     cites(('S3', r'Het bruisende uitgaansleven rond de Schiedamsedijk'), ('S3', r'tussen 1936 en 1940 wordt het modernistische nieuwe Beurs gebouw gerealiseerd')), 5.6, 'high')
card(1940.37, 'Fifteen minutes', ['German bombers destroy the historic center in a raid of about fifteen minutes.', 'Around 80,000 people lose their homes.'],
     cites(('S6', r'Het bombardement van een kwartier vernietigde bijna de gehele historische binnenstad'), ('S1', r'Some 80,000 civilians were made homeless')), 6.5, 'high', sober=True)
card(1940.4, 'What survived', ['Only two buildings from before the 19th century survive: the Laurenskerk, heavily damaged, and the Schielandshuis.', 'The City Hall also stands.'],
     cites(('S5', r'Only two buildings prior to the 19th century survived'), ('S7', r'the Laurenskerk was heavily damaged, with only the tower and walls surviving'), ('S1', r'The City Hall survived the bombing')), 6.5, 'high', sober=True, labels=['Laurenskerk', 'City Hall'])
card(1940.45, 'Surrender', ['The Dutch army capitulates the next day.', 'Germany had threatened to bomb Utrecht the same way.'],
     cites(('S1', r'The Dutch army was forced to capitulate on 15 May 1940'), ('S5', r'threaten to destroy the city of Utrecht')), 6.0, 'high', sober=True)
card(1942.6, 'Deportations', ['Between July 1942 and April 1943, 6,790 people are deported from Rotterdam in 8 transports.'],
     cites(('S1', r'Between 30 July 1942 and 22 April 1943, 6,790 people were deported')), 6.0, 'high', sober=True)
card(1943.25, 'A bombing by mistake', ['Allied bombers destroy part of Delfshaven on 31 March 1943.', 'At least 417 people die.'],
     cites(('S3', r'Op 31 maart 1943 bombarderen de geallieerden bij vergissing een deel van Delfshaven'), ('S13', r'destroyed by Allied bombing on 31 March 1943')), 6.0, 'high', sober=True)
card(1944.86, 'The razzia', ['On 10 and 11 November 1944 about 50,000 men between 17 and 40 are taken away.'],
     cites(('S3', r'Op 10 en 11 november 1944 wordt er een grote razzia gehouden')), 6.0, 'high', sober=True)
card(1945.34, 'Liberation', ['Germany surrenders on 5 May 1945.', 'The occupation of the Netherlands ends.'],
     cites(('S42', r'On 5 May 1945, the German surrender at L')), 5.6, 'medium', note='S42 is about the whole country; the exact day Rotterdam itself was freed is not in the fetched texts.')
card(1946, 'Start from scratch', ['The city adopts a plan for rebuilding the center.', 'It chooses a modern city over the old street plan.'],
     cites(('S2', r'Plan for the Reconstruction of Rotterdam adopted'), ('S5', r'There seemed to be no thought of nostalgically rebuilding the old city')), 5.8, 'high')
card(1948.05, 'Stronger through effort', ['Queen Wilhelmina presents the motto "Sterker door strijd" for Rotterdam\'s coat of arms.'],
     cites(('S1', r"In January 1948, Queen Wilhelmina presented the motto")), 5.4, 'high')
card(1952, 'The church is rebuilt', ['Queen Juliana lays the foundation stone for restoring the Laurenskerk.', 'It is finished in 1968.'],
     cites(('S7', r'In 1952, Queen Juliana laid the foundation stone')), 5.4, 'high', labels=['Laurenskerk'])
card(1953, 'A warehouse of the future', ['The Groothandelsgebouw opens, one of the first major buildings after the bombing.'],
     cites(('S21', r'Completed in 1953 it is one of the first major buildings built after the bombing')), 5.2, 'high')
card(1957, 'A new Central Station', ['Rotterdam Centraal opens, replacing the bombed Delftsche Poort station.'],
     cites(('S22', r'completed on 13 March 1957'), ('S22', r'Delftsche Poort station was badly damaged by bombing')), 5.2, 'high')
card(1965, 'The population peaks', ['Rotterdam reaches 731,564 people.'], cites(('S1', r'Its population peaked at 731,564 in 1965')), 5.0, 'high')
card(1968, 'The first metro in the Netherlands', ['Princess Beatrix opens the line at Centraal station.'],
     cites(('S22', r'On 9 February 1968 Princess Beatrix opened the first metro line')), 5.2, 'high')
card(1970, 'The Euromast grows', ['A Space Tower is added on top.', 'The Euromast is now 185 meters tall.'],
     cites(('S3', r'In 1970 maakt men de Euromast')), 5.2, 'high', labels=['Euromast'])
card(1973, 'The port moves to sea', ['The Maasvlakte is built from sand in the North Sea.', 'The first company starts working there in 1973.'],
     cites(('S33', r'In 1973 EMO started as the first company at Maasvlakte'), ('S33', r'The Maasvlakte was created in the 1960s by reclaiming land from the North Sea'), ('S23', r'In the 1970s the port was extended into the sea')), 6.0, 'high',
     note='The Maasvlakte is about 30 km west of the center (Wikidata 51.9525 N, 4.0464 E): outside the 9 km data radius, so it is a card without a target.')
card(1981, 'A new Willemsbrug', ['A new bridge replaces the old one, designed to spare the Oude Haven.'],
     cites(('S34', r'The bridge was completed in 1981'), ('S3', r'In 1981 opent de nieuwe Willemsbrug')), 5.2, 'high')
card(1991, 'Delftse Poort', ['Twin office towers rise above the station.', 'They were built between 1988 and 1991.'],
     cites(('S32', r'It was constructed between 1988 and 1991'), ('S32', r'Both towers are built over a four-storey multifunctional podium')), 5.2, 'high', labels=['Delftse Poort'])
card(1994, 'Manhattan on the Maas', ['The Kop van Zuid project turns the south bank into a new business district.'],
     cites(('S3', r'Een ander megaproject \(uitgevoerd vanaf 1994\) is de Kop van Zuid'), ('S1', r'In the 1990s, the Kop van Zuid was built')), 5.4, 'high')
card(2009, 'Maastoren', ['A 44-floor office tower rises on the Kop van Zuid.', 'Built between 2006 and 2009.'],
     cites(('S29', r'The Maastoren was built between 2006 and 2009'), ('S29', r'The Maastoren has a total of 44 above ground floors')), 5.2, 'high', labels=['Maastoren'])
card(2013.4, 'A bigger port', ['Maasvlakte 2 opens: about 2,000 hectares of new land from the sea.'],
     cites(('S33', r'This project extended the port of Rotterdam by about 2,000 hectares'), ('S33', r'This new part of the Maasvlakte opened in 2013')), 5.4, 'high', note='Outside the data radius, card only.')
card(2013.9, 'De Rotterdam', ['Three interconnected towers rise from a shared base.', 'The complex is finished at the end of 2013.'],
     cites(('S30', r'was finalized at the end of 2013'), ('S30', r'The building consists of three interconnected towers')), 5.2, 'high', labels=['De Rotterdam'])
card(2014.2, 'The new Centraal', ['The rebuilt Rotterdam Centraal is reopened by the king on 13 March 2014.'],
     cites(('S22', r'The full completion of the station was on 13 March 2014')), 5.2, 'high')
card(2022.3, 'The tallest in the Netherlands', ['The Zalmhaven towers are completed in April 2022.'],
     cites(('S31', r'the entire project was completed in April 2022'), ('S31', r'the tallest building in the Netherlands')), 5.4, 'high', labels=['Zalmhaven'])
cards.sort(key=lambda c: c['y'])
# chapter openers must be existing card years
CHAPTERS = [(1270, 'The Dam Town'), (1340, 'A Chartered Town'), (1575, 'The Water Town'), (1795, 'Revolution and Steam'), (1872, 'A Port for the World'),
            (1940.37, 'Fire and Occupation'), (1946, 'Reconstruction'), (1994, 'Manhattan on the Maas')]
for y, _ in CHAPTERS: assert any(abs(c['y'] - y) < 1e-6 for c in cards), y

# ============================================================== SOSTE
def soste():
    S = []
    def so(y0, y1, dur, cap, target, shot, fx, w, src, conf='high', note=None):
        d = {'y0': y0, 'y1': y1, 'dur': dur, 'caption': cap, 'shot': shot, 'target': target, 'fx': fx, 'weight': w, 'src': src, 'conf': conf}
        if note: d['note'] = note
        S.append(d)
    A = lambda x, y, r: 'area:[%.5f,%.5f,%d]' % (ll(x, y)[0], ll(x, y)[1], r)
    D = (500, -130)   # dam in the Rotte at the east end of the Hoogstraat (hand estimate, +-100 m)
    so(1270.0, 1276.0, 6.0, 'A dam on the Rotte (1270)', A(*D, 260), 'wide', 'water', 7,
       cites(('S4', r'Rond 1270 werd de dam in de Rotte voltooid'), ('S3', r'rond 1275 de eerste houten huizen gebouwd')), 'medium',
       'Area on the Hoogstraat dam site; coordinate is a hand estimate (Hoogstraat runs between Beursplein and Binnenrotte, S4).')
    so(1340.0, 1346.0, 5.0, 'Rotterdam receives city rights (1340)', A(400, -100, 450), 'wide', 'crowd', 5,
       cites(('S1', r'In 1340, Rotterdam was granted city rights by William IV'), ('S3', r'verleent graaf Willem IV van Holland Rotterdam definitief stadsrechten')))
    so(1389.0, 1396.0, 5.5, 'Delft digs its own harbor (1389)', A(-2108, -1481, 400), 'wide', 'water', 4, cites(('S13', r'in 1389 a harbour was created')),
       'high', 'Area at the Delfshaven harbor (Wikidata coordinates of the Pilgrim Fathers Church 51.90861, 4.44917).')
    so(1449.0, 1525.0, 7.0, 'The Laurenskerk rises (1449-1525)', 'Laurenskerk', 'medium', 'hammer', 6,
       cites(('S3', r'Tussen 1449 en 1525 bouwt men de laat-gotische Laurenskerk'), ('S7', r'built as a Roman Catholic Church between 1449 and 1525')))
    so(1575.0, 1620.0, 6.0, 'The Water Town grows south (1575)', A(450, -600, 450), 'wide', 'water', 4,
       cites(('S3', r'Vanaf 1575 wordt de ommuurde stad weer uitgebreid')), 'high', 'Area between the Hoogstraat and the Maas (S3).')
    so(1872.0, 1879.0, 7.0, 'A new waterway to the sea (1872)', A(800, -1500, 900), 'wide', 'horn', 6,
       cites(('S15', r'In 1872, the Nieuwe Waterweg was completed and Rotterdam was easily accessible'), ('S3', r'In 1879 openen de havenfaciliteiten van de RHV')), 'high',
       'The canal itself is 20 km west, outside the data; the hover shows the south-bank harbors it made possible (Kop van Zuid, S3, S27).')
    so(1897.2, 1898.8, 5.0, 'The White House (1898)', 'Witte Huis', 'medium', 'hammer', 5,
       cites(('S1', r'The Witte Huis, or White House skyscraper'), ('S16', r'It was the first hoogbouw')), 'medium', 'S16 says 1898, S17 says 1897.')
    so(1907.8, 1908.9, 4.5, 'Hofplein station and the Hofbogen (1908)', A(-116, 400, 300), 'wide', 'horn', 4,
       cites(('S18', r'Hofplein station was opened on 1 October 1908')), 'high')
    so(1914.5, 1920.7, 6.5, 'City Hall opens on the Coolsingel (1920)', 'City Hall', 'medium', 'bell', 6,
       cites(('S10', r'De eerste paal werd geslagen op 12 augustus 1914'), ('S10', r'Op 1 september 1920 werd het gebouw'), ('S9', r'Rotterdam City Hall was built between 1914 and 1920')))
    so(1940.30, 1940.46, 9.0, 'The bombing of Rotterdam (14 May 1940)', 'fire:Bombing of 14 May 1940', 'wide', 'boom', 'max',
       cites(('S6', r'Het bombardement op Rotterdam werd op 14 mei 1940 tussen 13\.27 en ongeveer 13\.40 uur uitgevoerd'), ('S5', r'642 acres'), ('S1', r'The heart of Rotterdam was almost completely destroyed by the Luftwaffe')))
    so(1946.0, 1950.0, 6.0, 'The center is redesigned (1946)', A(450, -300, 700), 'wide', 'hammer', 6,
       cites(('S2', r'Plan for the Reconstruction of Rotterdam adopted'), ('S5', r'adopted in 1946')))
    so(1951.5, 1953.8, 5.0, 'The Lijnbaan opens (1953)', A(-185, -66, 300), 'wide', 'crowd', 5,
       cites(('S20', r'opened on 9 October 1953'), ('S20', r'The street opened on 9 October 1953 to such crowds')), 'high', 'Wikidata coordinates of the Lijnbaan 51.92111, 4.47667.')
    so(1959.5, 1960.4, 5.0, 'The Euromast opens (1960)', 'Euromast', 'medium', 'peal', 5,
       cites(('S11', r'constructed between 1958 and 1960'), ('S12', r'Het gebouw werd officieel geopend door prinses Beatrix op 25 maart 1960')))
    so(1961.5, 1962.8, 5.0, 'The busiest port in the world (1962)', A(700, -2100, 800), 'wide', 'horn', 4,
       cites(('S23', r'From 1962 until 2004, it was the world'), ('S3', r"De havenactiviteiten groeien nu zo snel dat de Rotterdamse haven in 1962")), 'high',
       'Area on the south-bank harbors (Rijnhaven/Maashaven complex, S23); the western ports (Europoort, Maasvlakte) are outside the data.')
    so(1982.0, 1984.9, 5.0, 'The Cube Houses (1984)', 'Cube Houses', 'medium', 'hammer', 4,
       cites(('S3', r'Tussen 1982 en 1984 openen de kubuswoningen van Piet Blom'), ('S2', r'Cube houses built near Oude Haven')))
    so(1994.0, 1996.8, 5.5, 'Kop van Zuid and the Erasmus Bridge (1996)', A(618, -1503, 700), 'wide', 'horn', 6,
       cites(('S26', r'Construction began in 1986 and was completed in 1996'), ('S3', r'Een ander megaproject \(uitgevoerd vanaf 1994\)'), ('S26', r'officially opened by Queen Beatrix on September 6, 1996')))
    so(2012.5, 2014.9, 5.5, 'The Markthal opens (2014)', 'Markthal', 'medium', 'crowd', 5,
       cites(('S28', r'The building was opened on October 1, 2014')), 'high', 'Hover start 2012.5 is a placement (start of construction not sourced).')
    so(2019.0, 2022.3, 5.0, 'The Zalmhaven towers (2022)', 'Zalmhaven', 'medium', 'hammer', 3,
       cites(('S31', r'construction started on 25 October 2018'), ('S31', r'the entire project was completed in April 2022')))
    return S

# ============================================================== LANDMARKS
def landmarks():
    L = []
    def lm(name, kind, at, params, phases, src, conf, note, fp='auto'):
        d = {'name': name, 'kind': kind, 'at': at, 'footprint': fp, 'params': params, 'phases': phases, 'label': True, 'src': src, 'conf': conf, 'note': note}
        L.append(d)
    lm('Laurenskerk', 'church', [51.92159, 4.48563], {'nave_h': 28, 'aisle_h': 18, 'facade_towers': 0, 'apse': True, 'transept': True},
       [{'y': 1449, 'y1': 1525}], cites(('S7', r'built as a Roman Catholic Church between 1449 and 1525'), ('S3', r'Tussen 1449 en 1525 bouwt men de laat-gotische Laurenskerk')), 'medium',
       'Dates from S7/S3 (high). Preset approximation: church on the cadastre footprint of the NAVE (the 62 m tower stays the cadastre building, BAG year 1640). Heights are [Guessing]; the legacy point was the tower (51.921476, 4.484948).')
    lm('Witte Huis', 'skyscraper', [51.918816, 4.491706], {'h': 42.9, 'podium_h': 0, 'crown': 'flat'}, [{'y': 1897, 'y1': 1898}],
       cites(('S16', r'built in 1898 in the Art Nouveau style'), ('S17', r'Het Witte Huis is in 1897 in Rotterdam gebouwd')), 'medium',
       'S16 says 1898, S17 says 1897. Height 42.9 m is the cadastre value (the floor counts in S16/S17 conflict: 10 vs 11). Footprint auto may pick a sub-block (34 m2 at the legacy point): check at the first render.')
    lm('City Hall', 'generic_footprint', [51.922797, 4.479529], {'h': 69.9, 'roof': 'hip'}, [{'y': 1914.62, 'y1': 1920.67}],
       cites(('S10', r'De eerste paal werd geslagen op 12 augustus 1914'), ('S10', r'Op 1 september 1920 werd het gebouw'), ('S9', r'Rotterdam City Hall was built between 1914 and 1920')), 'medium',
       'Phase: first pile 12 Aug 1914 to inauguration 1 Sep 1920 (S10). Geometry [Guessing]: footprint at the legacy point is the clock tower only.')
    lm('Euromast', 'tower_round', [51.905445, 4.466639], {'rad': 5, 'h': 107.6, 'top': 'lantern', 'c': 'concrete'}, [{'y': 1958, 'y1': 1960.23}],
       cites(('S11', r'constructed between 1958 and 1960'), ('S12', r'Het gebouw werd officieel geopend door prinses Beatrix op 25 maart 1960')), 'medium',
       'Height 107.6 m is the cadastre value; the Space Tower (1970, S12: 185 m total) is not modeled. Radius is [Guessing].')
    lm('Cube Houses', 'generic_footprint', [51.920508, 4.489507], {'h': 25.0, 'roof': 'hip', 'c': 'ochre'}, [{'y': 1982, 'y1': 1984}],
       cites(('S3', r'Tussen 1982 en 1984 openen de kubuswoningen van Piet Blom'), ('S2', r'Cube houses built near Oude Haven')), 'medium',
       'Tilted cubes approximated by hip roofs on the cadastre footprint; geometry [Guessing].')
    lm('Markthal', 'generic_footprint', [51.92011, 4.486958], {'h': 41.8, 'roof': 'dome', 'roof_h': 12, 'c': 'concrete'}, [{'y': 2011.5, 'y1': 2014.75}],
       cites(('S28', r'The building was opened on October 1, 2014')), 'low',
       'Opening 1 Oct 2014 (S28). Start 2011.5 is a placement: the start of construction is not in the fetched text. The horseshoe arch is not modeled (preset approximation).')
    lm('De Rotterdam', 'skyscraper', [51.906893, 4.488633], {'h': 151.5, 'podium_h': 8, 'crown': 'flat'}, [{'y': 2009, 'y1': 2013.9}],
       cites(('S30', r'Construction began in 2009'), ('S30', r'was finalized at the end of 2013')), 'medium', 'Three towers merged into one block by the preset; height from the cadastre.')
    lm('Maastoren', 'skyscraper', [51.908702, 4.493381], {'h': 165.2, 'podium_h': 10, 'crown': 'flat'}, [{'y': 2006, 'y1': 2009}],
       cites(('S29', r'The Maastoren was built between 2006 and 2009')), 'high', 'Legacy year 2011 (cadastre) replaced by 2006-2009 (S29).')
    lm('Zalmhaven', 'skyscraper', [51.910222, 4.480796], {'h': 203.0, 'podium_h': 10, 'crown': 'flat'}, [{'y': 2018.82, 'y1': 2022.3}],
       cites(('S31', r'construction started on 25 October 2018'), ('S31', r'the entire project was completed in April 2022')), 'medium',
       'Height 203 m is the cadastre value; S1 says 215 m for the tallest tower: not changed without a measured source.')
    lm('Delftse Poort', 'skyscraper', [51.924353, 4.472159], {'h': 150.0, 'podium_h': 12, 'crown': 'flat'}, [{'y': 1988, 'y1': 1991}],
       cites(('S32', r'It was constructed between 1988 and 1991')), 'high', 'Two towers on a podium (S32); merged by the preset.')
    lm('Van Nelle Factory', 'generic_footprint', [51.923149, 4.433385], {'h': 37.3, 'roof': 'flat', 'c': 'white'}, [{'y': 1925, 'y1': 1931}],
       cites(('S19', r'Built between 1925 and 1931')), 'high', 'Dates from S19; geometry [Guessing] (cadastre footprint at the legacy point, 76 m2).')
    lm('Pilgrim Fathers Church', 'church', [51.90861, 4.44917], {'nave_h': 13, 'facade_towers': 0, 'apse': False, 'transept': False}, [{'y': 1417, 'y1': 1418}],
       cites(('S14', r'goes back as far as 1417')), 'medium',
       'Church of St Anthony consecrated 1417 (S14), rebuilt 1761. Coordinates from Wikidata. Cadastre footprint not verified (nearest buildings are BAG 1876).')
    return L

# ============================================================== MAIN
def main():
    base = json.load(open(os.path.join(WT, 'cities/rotterdam/story.json')))
    story = base
    # ---------------- city
    c = story['city']
    c.update({'country': 'Netherlands', 'start_year': 1270, 'end_year': 2026, 'style_preset': 'nordic',
              'title': 'EVOLUTION OF ROTTERDAM | 3D City Timelapse (1270-NOW) | No AI', 'data_source': 'custom', 'data_dir': 'data_rotterdam'})
    P = lambda y, v, k, s, conf: ([y, v, k], s, conf)
    pops = [
     ([1340, 3000, 'rough estimate'], 'S1', 'low', 'S1: "only a few thousand"; 3,000 is a [Guessing] reading.'),
     ([1573, 10000, 'rough estimate'], 'S3', 'medium', ''), ([1622, 20000, 'historical estimate'], 'S3', 'medium', 'S2 timeline says 20,000 for 1632 (approximate).'),
     ([1675, 30000, 'rough estimate'], 'S1', 'low', 'S1: around 30,000 by the 1670s.'),
     ([1699, 50000, 'rough estimate'], 'S3', 'low', 'S3: "almost 50,000" toward the end of the 17th century; conflicts with the 1670s figure only if read as growth of 20,000 in 25 years.'),
     ([1750, 56000, 'rough estimate'], 'S3', 'low', 'S3: about 56,000 in the middle of the 18th century (S2: 53,212 in 1796).'),
     ([1796, 53212, 'historical estimate'], 'S2', 'medium', ''), ([1838, 72000, 'historical estimate'], 'S2', 'medium', ''),
     ([1866, 115277, 'historical estimate'], 'S2', 'medium', ''), ([1880, 160000, 'historical estimate'], 'S3', 'medium', ''),
     ([1891, 203500, 'historical estimate'], 'S2', 'medium', ''), ([1900, 315000, 'historical estimate'], 'S3', 'medium', 'Includes the 1895 annexations of Kralingen and Charlois (S3).'),
     ([1905, 379017, 'historical estimate'], 'S2', 'medium', ''), ([1920, 500000, 'historical estimate'], 'S3', 'low', 'S3: "slightly above 500,000".'),
     ([1965, 731564, 'historical estimate'], 'S1', 'medium', 'Peak. No figure for 1930-1960 in the fetched texts: the HUD interpolates between 1920 and 1965.'),
     ([1985, 560000, 'historical estimate'], 'S1', 'medium', ''), ([2000, 592673, 'census'], 'S44', 'medium', ''),
     ([2010, 603425, 'census'], 'S44', 'medium', ''), ([2022, 655468, 'census'], 'S44', 'high', ''), ([2023, 664311, 'census'], 'S44', 'medium', 'Wikidata preferred rank.')]
    cites(('S1', r'Its population peaked at 731,564 in 1965'), ('S1', r'reaching 560,000 by 1985'), ('S1', r'In 2022, Rotterdam had a population of 655,468'),
          ('S1', r'by the 1670s, its population was around 30,000'), ('S3', r'Bij de volkstelling van 1622'), ('S3', r'In 1573 kiest de stad'),
          ('S3', r'Tegen het eind van de 17e eeuw zouden het er zelfs bijna 50\.000 zijn'), ('S3', r'groeide het inwonertal van Rotterdam tot zo.n 56\.000'),
          ('S3', r'In 1920 zal de bevolking zelfs al iets boven de 500\.000'), ('S3', r'van 160\.000 naar 315\.000 inwoners'),
          ('S2', r'1796 - Population: 53,212'), ('S2', r'1838 - Population: 72,000'), ('S2', r'1866 - Population: 115,277'), ('S2', r'1891 - Population: 203,500'), ('S2', r'Population: 379,017'),
          ('S44', r'2000: 592673'), ('S44', r'2010: 603425'), ('S44', r'2022: 655468'), ('S44', r'2023: 664311'))
    c['population'] = [p[0] for p in pops]
    c['pop_src'] = ['S1', 'S2', 'S3', 'S44']
    c['pop_conf'] = [p[2] for p in pops]
    c['pop_point_src'] = [p[1] for p in pops]
    c['pop_note'] = ' | '.join(f'{p[0][0]}: {p[3]}' for p in pops if p[3])
    c['data_reliable_from'] = 1900
    c['data_reliable_note'] = ('[Guessing] 1900: the cadastre (3DBAG) holds only surviving buildings: 8,417 with a year in 1850-1899 against 70,364 in 1900-1949 and almost none before 1850 '
                              '(counted on data_rotterdam_src/buildings.json.gz, 2026-11-19); the 1940 center is all post-1945. Before 1900 the city is generated from zones.')
    flags = {'hol': ['#f2c200', '#c8102e'], 'bur': ['#c8102e', '#f2c200'], 'hab': ['#f2c200', '#1a1a1a'], 'rev': ['#ff7f00', '#ffffff', '#21468b'],
             'nl': ['#ae1c28', '#ffffff', '#21468b'], 'fr': ['#21468b', '#ffffff', '#e1000f'], 'occ': ['#2b2b2b', '#8c8c8c']}
    c['polities'] = [
     {'y': 1270, 'name': 'County of Holland', 'flag_colors': flags['hol'], 'src': cites(('S36', r'state of the Holy Roman Empire from its inception until 1433')), 'conf': 'high'},
     {'y': 1433, 'name': 'Burgundian Netherlands', 'flag_colors': flags['bur'], 'src': cites(('S36', r'From 1433 onward it was part of the Burgundian Netherlands')), 'conf': 'high'},
     {'y': 1482, 'name': 'Habsburg Netherlands', 'flag_colors': flags['hab'], 'src': cites(('S36', r'from 1482 part of the Habsburg Netherlands')), 'conf': 'high'},
     {'y': 1573, 'name': 'Dutch Revolt · Holland against Spain', 'flag_colors': flags['rev'], 'src': cites(('S3', r'In 1573 kiest de stad de kant van de Opstand')), 'conf': 'high',
      'note': 'The chip changes when Rotterdam itself joins the Revolt (S3, 1573); the Republic proper is dated 1581.'},
     {'y': 1581, 'name': 'Dutch Republic', 'flag_colors': flags['nl'], 'src': cites(('S38', r'declaring their independence in 1581'), ('S3', r'In 1581 kreeg de stad zelf zitting in de Staten')), 'conf': 'high'},
     {'y': 1795.05, 'name': 'Batavian Republic', 'flag_colors': flags['nl'], 'src': cites(('S39', r'It was proclaimed on 19 January 1795')), 'conf': 'high'},
     {'y': 1806.43, 'name': 'Kingdom of Holland', 'flag_colors': flags['nl'], 'src': cites(('S40', r"installed as 'King of Holland' on 5 June 1806")), 'conf': 'high'},
     {'y': 1810.0, 'name': 'French Empire', 'flag_colors': flags['fr'], 'src': cites(('S40', r'the kingdom was dissolved in 1810, after which the Netherlands were annexed by France until 1813')), 'conf': 'medium', 'note': 'Year only in S40; month not used.'},
     {'y': 1813.0, 'name': 'United Netherlands', 'flag_colors': flags['nl'], 'src': cites(('S41', r'regained its independence from France in 1813')), 'conf': 'medium', 'note': 'Year only in S41.'},
     {'y': 1815.2, 'name': 'Kingdom of the Netherlands', 'flag_colors': flags['nl'], 'src': cites(('S41', r'In March 1815, amidst the turmoil of the Hundred Days')), 'conf': 'high'},
     {'y': 1940.38, 'name': 'German occupation', 'flag_colors': flags['occ'], 'src': cites(('S1', r'The Dutch army was forced to capitulate on 15 May 1940'), ('S42', r'assuming power on 29 May 1940')), 'conf': 'medium',
      'note': 'Capitulation 15 May 1940 (S1); the Reichskommissariat takes power 29 May 1940 (S42).'},
     {'y': 1945.34, 'name': 'Kingdom of the Netherlands', 'flag_colors': flags['nl'], 'src': cites(('S42', r'On 5 May 1945, the German surrender at L')), 'conf': 'medium',
      'note': '5 May 1945 is the national liberation date (S42); Rotterdam\'s own date is not in the fetched texts.'}]
    c['eras'] = [[1270, 'Dam town on the Rotte', '#c9a24a'], [1340, 'Chartered town', '#b5654a'], [1575, 'The Water Town', '#6aa0c8'], [1795, 'Revolution and empire', '#8a6aa0'],
                 [1872, 'World port', '#7cb06a'], [1940.38, 'Bombing and occupation', '#8c8c8c'], [1945.34, 'Reconstruction', '#c98a4b'], [1990, 'Manhattan on the Maas', '#5fb0a8']]
    c['eras_note'] = 'Display eras; boundaries follow the sourced events: 1340 charter, 1575 Water Town (S3), 1795 (S3), 1872 Nieuwe Waterweg (S1), 1940 bombing (S1), 1945 liberation (S42), 1990s Kop van Zuid (S3).'
    c['style_note'] = '[Guessing] nordic (brick walls, red roofs, green-blue water) as the closest preset for Dutch brick; no render done to check.'
    # ---------------- history
    cites(('S1', r'In 1340, Rotterdam was granted city rights'), ('S5', r'642 acres'), ('S6', r'De Duitse bommen vielen in een brede strook in het centrum'))
    H = story['history']
    H['zones'] = [
     {'name': 'Dam settlement on the Rotte', 'ring': circle(500, -130, 300), 'born': [1270, 1300], 'seed': ll(500, -130), 'era_height': [5, 8],
      'src': cites(('S4', r'Rond 1270 werd de dam in de Rotte voltooid'), ('S3', r'rond 1275 de eerste houten huizen gebouwd'), ('S3', r'Daaromheen groeit bedrijvigheid en een nederzetting')), 'conf': 'low',
      'note': 'Dam c. 1270, first houses c. 1275 (S3, S4). Ring/seed are a HAND SKETCH (+-150 m) at the east end of the Hoogstraat; born window 1270-1300 is a [Guessing]; heights 5-8 m [Guessing].'},
     {'name': 'Walled town between Coolsingel, Goudsesingel and the Hoogstraat', 'ring': poly([(-290, 300), (1240, -290), (1150, -172), (500, -120), (-50, -76)]), 'born': [1300, 1500], 'seed': ll(500, -130),
      'era_height': [7, 11],
      'src': cites(('S3', r'De vestingsingels liepen langs de huidige Coolsingel'), ('S3', r'Rond 1500 wordt het ommuurde stadsgebied verkleind'), ('S3', r'Rotterdam bestaat in die tijd uit ongeveer 1200 huizen')), 'conf': 'low',
      'note': 'Boundaries from S3 (moats along Coolsingel, Warande/Goudsesingel, Blaak, Nieuwehaven; walled area c. 140 ha, S3). Ring converted from the legacy triangle in hist_rotterdam.py (hand sketch). Growth 1300-1500 ramps outward from the dam: [Guessing].'},
     {'name': 'The Water Town', 'ring': poly([(-50, -76), (500, -120), (1150, -172), (1300, -720), (700, -1050), (80, -1000), (-50, -300)]), 'born': [1575, 1650], 'seed': ll(450, -600), 'era_height': [8, 12],
      'src': cites(('S3', r'Het gebied tussen Hoogstraat, Schiedamse Singel en de Nieuwe Maas'), ('S3', r'bedroeg niet meer dan 140 hectare')), 'conf': 'low',
      'note': 'Expansion starts 1575 (S3); the end of the build-out (1650) is the legacy value, not sourced.'},
     {'name': 'Delfshaven harbor town', 'ring': circle(-2108, -1481, 380), 'born': [1389, 1650], 'seed': ll(-2108, -1481), 'era_height': [6, 10],
      'src': cites(('S13', r'in 1389 a harbour was created'), ('S14', r'goes back as far as 1417')), 'conf': 'low',
      'note': 'Harbor created 1389 (S13); growth window and ring are a hand sketch around the Pilgrim Fathers Church.'},
     {'name': 'Schiedam', 'ring': circle(-5469, -607, 700), 'born': [1275, 1500], 'seed': ll(-5469, -607), 'era_height': [6, 10],
      'src': cites(('S3', r'Allen havensteden die zich ontwikkelen')), 'conf': 'low',
      'note': 'City rights 1275 (S3: "Gouda (1272), Schiedam (1275)"); ring is a hand sketch around Wikidata 51.91667, 4.40; growth window [Guessing].'}]
    # The S3 city-rights line for Schiedam
    cites(('S3', r'Net als Gouda \(1272\), Schiedam \(1275\) en Brielle \(1330\)'))
    H['walls'] = [
     {'name': 'Moats and town wall', 'ring': poly([(-290, 300), (1240, -290), (1150, -172), (500, -120), (-50, -76)]), 'built': [1358, 1500], 'demolished': 1850, 'height': 8, 'width': 2.5, 'towers_every_m': 80,
      'src': cites(('S3', r'In 1358 geeft graaf Albrecht van Beieren toestemming'), ('S3', r'Begin 1500 is de stadsmuur rondom Rotterdam voltooid')), 'conf': 'low',
      'note': 'Built 1358-1500 (S3). DEMOLISHED 1850 is a placeholder [Guessing]: S3 only says the walls were taken down "some time ago" before 1913 and that the city grew beyond them only after 1825. Ring = same hand sketch as the walled town.'},
     {'name': 'Rotte dam and sea dike (Hoogstraat)', 'line': poly([(330, -112), (500, -125), (700, -150)]), 'built': [1268, 1272], 'demolished': 1946, 'height': 3, 'width': 9, 'towers_every_m': 0,
      'src': cites(('S4', r'De dam was onderdeel van het traject van een middeleeuwse zeewering'), ('S5', r'main dike of the city alongside the riverbank')), 'conf': 'low',
      'note': 'Dam in the Rotte c. 1270, part of Schielands Hoge Zeedijk (S3, S4); S4: the Hoogstraat is no longer part of the dike since the reconstruction. 1946 is the year of the Basisplan, which moved the dike to the riverbank (S5): [Likely], not an exact date.'}]
    H['gutting'] = [
     {'name': 'Zandstraat quarter (City Hall site)', 'ring': poly([(-60, 160), (110, 160), (110, 0), (-60, 0)]), 'from': 1825, 'until': 1914.5,
      'src': cites(('S9', r'an entire neighborhood, Zandstraat, where about 2,400 people lived, was demolished'), ('S10', r'Voor de uitvoering werd de Coolvest gedempt')), 'conf': 'low',
      'note': 'Demolished from 1913-14 for the City Hall (S9, S10). Ring is a hand sketch at the Coolsingel; "from" 1825 is a [Guessing] (S3: growth outside the walls only after 1825).'}]
    H['fires'] = [
     {'name': 'Bombing of 14 May 1940', 'ring': poly([(-620, 710), (35, 820), (1065, 490), (1440, -120), (1130, -785), (380, -950), (-380, -895), (-650, -230)]),
      'y': 1940.366, 'y1': 1940.385, 'destroy': True, 'rebuild_years': 5, 'flames': 60, 'smoke': 10, 'origin': ll(500, 100),
      'src': cites(('S6', r'Het bombardement op Rotterdam werd op 14 mei 1940 tussen 13\.27 en ongeveer 13\.40 uur uitgevoerd'), ('S5', r'642 acres'), ('S6', r'De Duitse bommen vielen in een brede strook in het centrum')), 'conf': 'medium',
      'note': '14 May 1940, 13:27-13:40 (S6); about 2.6 km2 of the center destroyed (S5: 642 acres). Ring = legacy damage-map polygon (hist_rotterdam.py BOMB, hand estimate, c. 3 km2) from Hofplein to Kralingen (S6). Fire window to 1940.385 (about 5 days of fire) and rebuild_years 5 are [Guessing]; the origin is an arbitrary point in the center.'}]
    H['water'] = []; H['bridges'] = []
    # ---------------- landmarks, soste
    story['landmarks'] = landmarks()
    R = story['regia']
    R['soste'] = soste()
    R['open'] = {'year': 2026, 'rewind_to': 1270}
    R['music'] = 'waking_monument'
    # ---------------- sources
    story['sources'] = {sid: {'url': SRC[sid][0], 'title': SRC[sid][1], 'quote': ' … '.join(QUOTES[sid]), 'fetched': FETCHED} for sid in SRC if QUOTES[sid]}
    # ---------------- montaggio
    m = story['montaggio']
    for k in ('cards',): m.pop(k, None)
    m['open'] = ['ROTTERDAM TODAY', '664,311 people', '756 YEARS', 'Open data, reconstruction before 1900']
    m['title'] = ['ROTTERDAM', '1270 TO NOW']
    m['end'] = ['ROTTERDAM · 756 YEARS', 'WHICH CITY NEXT?']
    m['style'] = 'mattia'; m['label_years'] = True
    m['cards'] = cards
    m['chapters'] = [{'y': y, 'title': t} for y, t in CHAPTERS]
    m['events'] = []
    m['cta'] = 'Which city should grow next? Tell me in the comments'
    m['sources_card'] = {'seconds': 8, 'max': 14, 'no_ai': 'NO AI: every frame is rendered from open data', 'items': [
        'Buildings, streets, water, parks: © OpenStreetMap contributors (ODbL); building years: BAG / 3DBAG',
        'Terrain: AHN / Copernicus GLO-30 DEM',
        'History: Wikipedia NL and EN (Geschiedenis van Rotterdam, Rotterdam Blitz, Laurenskerk, City Hall and others)',
        'Population: Wikipedia EN and NL, Wikidata',
        'Music: Unicorn Heads, TrackTribe (YouTube Audio Library)']}
    m.pop('legacy_date', None)
    story['legacy']['data_package'] = {'dir': 'data_rotterdam_src', 'present': ['buildings.json.gz', 'dem.npz.gz', 'harbours.json.gz', 'land.json.gz', 'parks.json.gz', 'roads.json.gz'], 'missing_for_kit': [], 'complete': True}
    story.pop('_legacy_gaps', None)
    story['qa'] = {'accept': []}
    story['_filled_by'] = ('yb-historian + yb-modeler, 2026-11-19: story rebuilt from fetched texts (Wikipedia NL/EN, Wikidata); every source quote is a verbatim sentence of the fetched text '
                           '(checked by verify_quotes.py). No kit build or render was run. Items marked conf low or [Guessing] in notes are estimates.')
    out = os.path.join(WT, 'cities/rotterdam/story.json')
    json.dump(story, open(out, 'w'), indent=1, ensure_ascii=False)
    
    print('cards', len(cards), 'soste', len(story['regia']['soste']), 'sources', len(story['sources']), 'landmarks', len(story['landmarks']))
main()
