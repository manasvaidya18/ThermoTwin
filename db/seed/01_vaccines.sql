-- Freeze sensitivity of UIP vaccines. Aluminium-adjuvanted and some liquid vaccines are damaged by freezing;
-- OPV, MR and BCG tolerate it. Compiled from WHO guidance; verify against current WHO documents and inserts.
INSERT OR REPLACE INTO vaccines (name, freeze_sensitive, note) VALUES
  ('Pentavalent', 1, 'aluminium adjuvant'),
  ('Hepatitis B', 1, 'aluminium adjuvant'),
  ('DTP',         1, 'aluminium adjuvant'),
  ('Td',          1, 'aluminium adjuvant'),
  ('PCV',         1, 'aluminium adjuvant'),
  ('IPV',         1, 'liquid, freeze-sensitive'),
  ('Rotavirus',   1, 'liquid, freeze-sensitive'),
  ('HPV',         1, 'aluminium adjuvant'),
  ('OPV',         0, 'stored frozen at higher levels'),
  ('MR',          0, 'freeze-dried'),
  ('BCG',         0, 'freeze-dried');
