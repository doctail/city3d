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
