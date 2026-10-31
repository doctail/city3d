// Dati del montaggio per citta': anni della timeline, popolazione, epoche, schede evento.
// EVENTS: [anno inizio, anno fine scheda, titolo, testo, sobria?]  (sobria = barra grigia, per tragedie)

// New York City (prima del 1898 solo Manhattan) — censimenti USA e stime coloniali
export const NYC = {
  Y0: 1600, Y1: 2026, POPMAX: 9e6, TICKS: [1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000],
  popLabel: (y) => (y >= 1898 ? 'FIVE BOROUGHS' : 'MANHATTAN'),
  POP: [[1600, 0], [1624, 30], [1628, 270], [1664, 1500], [1698, 4937], [1712, 5840], [1737, 10664], [1756, 13046], [1771, 21863], [1776, 25000], [1783, 12000], [1790, 33131], [1800, 60515], [1810, 96373], [1820, 123706], [1830, 202589], [1840, 312710], [1850, 515547], [1860, 813669], [1870, 942292], [1880, 1164673], [1890, 1441216], [1897, 1900000], [1898, 3300000], [1900, 3437202], [1910, 4766883], [1920, 5620048], [1930, 6930446], [1940, 7454995], [1950, 7891957], [1960, 7781984], [1970, 7894862], [1980, 7071639], [1990, 7322564], [2000, 8008278], [2010, 8175133], [2020, 8804190], [2026, 8480000]],
  ERAS: [[1600, 'Lenapehoking', '#7FA36B'], [1624, 'New Netherland', '#E07A3F'], [1664, 'British Colony', '#B8473A'], [1783, 'Young Republic', '#4F7FB8'], [1825, 'Port City', '#3E9AA0'], [1865, 'Gilded Age', '#C9A227'], [1898, 'Greater New York', '#8E6BBF'], [1945, 'Postwar City', '#6C8A9E'], [1990, 'Global City', '#D96C8A']],
  EVENTS: [
    [1609, 1615, 'Henry Hudson', 'An English captain sailing for the Dutch enters the harbor.'],
    [1625, 1631, 'Fort Amsterdam', 'The Dutch West India Company builds a fort at the tip of Manhattan.'],
    [1653, 1659, 'The wall', 'A timber wall guards the north edge of town. Wall Street follows its line.'],
    [1664, 1670, 'New Amsterdam becomes New York', 'English warships take the colony without a fight.'],
    [1776, 1783, 'Occupation', 'British troops hold the city for the whole Revolutionary War.'],
    [1825, 1831, 'The Erie Canal opens', 'Grain from the Great Lakes now flows to the port of New York.'],
    [1857, 1863, 'Central Park', 'Work begins on 843 acres in the middle of Manhattan.'],
    [1883, 1889, 'Brooklyn Bridge', 'The longest suspension bridge in the world links two cities.'],
    [1898, 1904, 'Five boroughs, one city', 'Manhattan, Brooklyn, Queens, the Bronx and Staten Island unite.'],
    [1904, 1909, 'The subway', 'The first underground line opens with 28 stations.'],
    [1931, 1936, 'Empire State Building', 'At 1,250 feet, the tallest building on Earth for 40 years.'],
    [2001, 2006, 'September 11, 2001', 'The World Trade Center is destroyed in a terrorist attack. 2,753 people are killed in New York.', true],
    [2014, 2019, 'One World Trade Center', 'The new tower opens at 1,776 feet.'],
  ],
};

// Madrid (comune). Prima del 1857: stime storiche (historylab.es: ~90.000 nel 1597, oltre 130.000 nel 1630,
// ~109.000 nel 1710-14, 201.000 nel 1825); prima del 1561 stime approssimative. Dal 1857: censimenti (INE).
export const MADRID = {
  Y0: 1480, Y1: 2026, POPMAX: 4e6, TICKS: [1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000],
  popLabel: () => 'CITY OF MADRID',
  POP: [[1480, 8000], [1530, 12000], [1561, 20000], [1597, 90000], [1630, 130000], [1670, 125000], [1712, 109000], [1735, 130000], [1787, 156000], [1825, 201000], [1857, 281170], [1877, 400917], [1900, 540109], [1910, 556958], [1920, 728937], [1930, 863958], [1940, 1096466], [1950, 1527894], [1960, 2177123], [1970, 3120941], [1981, 3158818], [1991, 2909792], [2001, 2938723], [2011, 3198645], [2021, 3277451], [2026, 3450000]],
  ERAS: [[1480, 'Castilian Town', '#9C8B5E'], [1561, 'Habsburg Capital', '#B8473A'], [1700, 'Bourbon Madrid', '#4F7FB8'], [1808, 'War & Revolution', '#7A5C8E'], [1860, 'The Ensanche', '#C9A227'], [1936, 'Civil War', '#6E6E6E'], [1939, 'Dictatorship', '#6C8A9E'], [1975, 'Democracy', '#D96C8A']],
  EVENTS: [
    [1561, 1567, 'The court arrives', 'Philip II makes Madrid the seat of the royal court.'],
    [1601, 1606, 'Capital lost and regained', 'Philip III moves the court to Valladolid. It returns in 1606.'],
    [1619, 1625, 'Plaza Mayor', 'The great arcaded square opens in the heart of town.'],
    [1625, 1631, 'The last wall', 'A new wall of brick and adobe marks the city limits for the next 240 years.'],
    [1632, 1638, 'Buen Retiro', 'Philip IV builds a palace and gardens east of town. The gardens are today\'s Retiro Park.'],
    [1734, 1740, 'The Alcázar burns', 'On Christmas Eve 1734 the old royal fortress burns. The Royal Palace rises in its place.'],
    [1808, 1814, '2 May 1808', 'Madrid rises against Napoleon\'s army.'],
    [1860, 1866, 'The Ensanche', 'A new grid of districts is planned north and east of the old town.'],
    [1910, 1916, 'Gran Vía', 'Work begins on a new boulevard cut through the old center.'],
    [1919, 1925, 'The Metro', 'The first line runs from Sol to Cuatro Caminos.'],
    [1936, 1939, 'Siege of Madrid', 'The city holds out under siege for almost three years of civil war.', true],
    [1948, 1954, 'Greater Madrid', 'The city absorbs the towns around it.'],
    [1975, 1981, 'Democracy returns', 'Franco dies. Spain begins its transition to democracy.'],
    [2004, 2008, '11 March 2004', 'Bombs on four commuter trains kill 193 people.', true],
    [2008, 2014, 'Cuatro Torres', 'Four skyscrapers rise on Real Madrid\'s old training ground. The tallest are about 250 meters high.'],
  ],
};

// Rotterdam (comune). Prima del 1795 stime storiche approssimative (1622: ~19.500); dal 1795 censimenti e CBS.
// Le schede evento di Rotterdam sono a TEMPO (secondi del video), in rotterdam_overlay.jsx: EVENTS qui resta vuoto.
export const ROTTERDAM = {
  Y0: 1340, Y1: 2026, POPMAX: 1e6, TICKS: [1400, 1500, 1600, 1700, 1800, 1900, 2000],
  popLabel: () => 'CITY OF ROTTERDAM',
  POP: [[1340, 2000], [1400, 3000], [1514, 5500], [1600, 13000], [1622, 19500], [1650, 30000], [1700, 45000], [1795, 53200], [1830, 72300], [1850, 90000], [1869, 116200], [1880, 148100], [1900, 318500], [1910, 417900], [1920, 510000], [1930, 587000], [1939, 620000], [1941, 598000], [1950, 680000], [1965, 731000], [1984, 555000], [2000, 593000], [2010, 610000], [2020, 651000], [2026, 680000]],
  ERAS: [[1340, 'Town on the Rotte', '#9C8B5E'], [1572, 'Dutch Revolt', '#B8473A'], [1590, 'Golden Age', '#C9A227'], [1700, 'Quiet Centuries', '#7A8B6E'], [1850, 'Port City', '#3E9AA0'], [1940, 'War & Ruins', '#6E6E6E'], [1946, 'Rebuilding', '#4F7FB8'], [1985, 'Manhattan on the Maas', '#D96C8A']],
  EVENTS: [],
};

// Copenaghen (comune). Prima del 1769 stime storiche (1728: ~70.000 secondo la voce sull'incendio); 1769 82.086,
// 1801 ~101.000, 1840 120.819, 1870 202.327, 1901 ~400.000 (comune), picco ~768.000 nel 1950, ~467.000 nel 1990, ~670.000 oggi.
// Le schede di Copenaghen sono a TEMPO (secondi del video), in copenhagen_overlay.jsx: EVENTS qui resta vuoto.
export const COPENHAGEN = {
  Y0: 1167, Y1: 2026, POPMAX: 1e6, TICKS: [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000],
  popLabel: () => 'CITY OF COPENHAGEN',
  POP: [[1167, 300], [1254, 2000], [1370, 4000], [1443, 6000], [1500, 10000], [1600, 20000], [1650, 30000], [1700, 60000], [1711, 65000], [1712, 45000], [1728, 70000], [1769, 82086], [1801, 101000], [1840, 120819], [1860, 155000], [1870, 202327], [1890, 312000], [1901, 400000], [1921, 561000], [1940, 700000], [1950, 768000], [1960, 721000], [1970, 623000], [1980, 492000], [1990, 467000], [2000, 495000], [2010, 540000], [2020, 633000], [2026, 670000]],
  ERAS: [[1167, "Absalon's Harbor", '#9C8B5E'], [1443, 'Royal Capital', '#B8473A'], [1588, 'Christian IV', '#C9A227'], [1660, 'Absolute Monarchy', '#7A5C8E'], [1728, 'Fire & Rebuilding', '#D9652B'], [1807, 'War & Recovery', '#6E6E6E'], [1852, 'Beyond the Walls', '#3E9AA0'], [1940, 'Occupation', '#5C5C5C'], [1945, 'Welfare City', '#4F7FB8'], [1990, 'Harbor City', '#D96C8A']],
  EVENTS: [],
};

// Siviglia (comune). Scheda di validazione storica, sezione D: 1248-1800 stime orientative (bassa/media affidabilita', da mostrare con "~");
// dal 1842 INE (1842 di diritto; 1857-1991 di fatto; dal 2001 residenti). 2026: ordine di grandezza (~690.000, non e' nella scheda).
export const SEVILLE = {
  Y0: 1248, Y1: 2026, POPMAX: 1e6, TICKS: [1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000], EST_UNTIL: 1842,
  popLabel: () => 'CITY OF SEVILLE',
  POP: [[1248, 50000], [1300, 50000], [1400, 30000], [1500, 60000], [1600, 120000], [1700, 70000], [1800, 75000], [1842, 100498], [1857, 112529], [1860, 118298], [1877, 134318], [1887, 143182], [1897, 146205], [1900, 148315], [1910, 158287], [1920, 205529], [1930, 228729], [1940, 312123], [1950, 376627], [1960, 442300], [1970, 548072], [1981, 653833], [1991, 704857], [2001, 684633], [2011, 698042], [2021, 684340], [2026, 690000]],
  ERAS: [[1248, 'Castilian Seville', '#9C8B5E'], [1503, 'Gateway to the Indies', '#C9A227'], [1717, 'Quiet Centuries', '#7A8B6E'], [1858, 'Beyond the Walls', '#3E9AA0'], [1936, 'Civil War', '#6E6E6E'], [1939, 'Dictatorship', '#6C8A9E'], [1975, 'Democracy', '#D96C8A'], [1992, 'After Expo 92', '#4F7FB8']],
  EVENTS: [],
};

// Parigi (comune). Scheda di validazione, sezione D: 1190-1790 stime (bassa affidabilita', mostrate con "~"); dal 1801 serie INSEE
// (perimetro dei 12 arrondissement fino al 1859, poi annessione: salto 1856 -> 1861). 2025: 2.065.560 (INSEE).
export const PARIS = {
  Y0: 1190, Y1: 2026, POPMAX: 4e6, TICKS: [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000], EST_UNTIL: 1801,
  popLabel: () => 'CITY OF PARIS',
  POP: [[1190, 25000], [1240, 50000], [1290, 120000], [1340, 200000], [1390, 100000], [1440, 100000], [1490, 200000], [1540, 350000], [1590, 400000], [1640, 450000], [1690, 500000], [1740, 550000], [1790, 600000], [1801, 547756], [1807, 580609], [1811, 622636], [1817, 713966], [1831, 785862], [1836, 909126], [1841, 935261], [1846, 1053897], [1851, 1053262], [1856, 1174346], [1861, 1696141], [1866, 1825274], [1872, 1851792], [1876, 1988806], [1881, 2269023], [1886, 2344550], [1891, 2447957], [1896, 2536834], [1901, 2714068], [1906, 2763393], [1911, 2888110], [1921, 2906472], [1926, 2871429], [1931, 2891020], [1936, 2829746], [1946, 2725374], [1954, 2850189], [1962, 2790091], [1968, 2590771], [1975, 2299830], [1982, 2176243], [1990, 2152423], [1999, 2125246], [2006, 2181371], [2011, 2249975], [2016, 2190327], [2021, 2133111], [2025, 2065560], [2026, 2065560]],
  ERAS: [[1190, 'Capetian Paris', '#9C8B5E'], [1328, 'Valois Kings', '#7A8B6E'], [1589, 'Bourbon Kings', '#C9A227'], [1789, 'Revolution & Empire', '#B8473A'], [1815, 'Restoration', '#7A5C8E'], [1852, 'Haussmann', '#3E9AA0'], [1871, 'Belle Époque', '#D9A441'], [1914, 'World Wars', '#6E6E6E'], [1945, 'Postwar Paris', '#4F7FB8'], [1975, 'Modern Paris', '#D96C8A']],
  EVENTS: [],
};
