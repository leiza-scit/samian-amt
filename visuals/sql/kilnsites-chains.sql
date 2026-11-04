-- Kiln sites of the three CHNT chains that are not in visuals/data/kilnsites-gaul.csv.
-- Run against the Samian Research database and save the result as visuals/data/kilnsites-extra.csv
-- (CSV with header, comma separated, quoted text; same columns as kilnsites-gaul.csv).
SELECT id, coordinate1, coordinate2, site, tradition, datemin, datemax, wikidataid
FROM cat29.tblkilnsites
WHERE site IN ('Kräherwald', 'Rheinzabern', 'Pfaffenhofen', 'Westerndorf');
