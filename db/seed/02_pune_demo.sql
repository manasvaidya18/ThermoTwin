-- Pune district demo fleet (matches the UI). sort_order fixes the simulation order of the demo scenario.
INSERT OR REPLACE INTO facilities (id, name, taluka, district) VALUES
  ('phc-wagholi',   'PHC Wagholi',  'Haveli',   'Pune'),
  ('junnar-phc2',   'Junnar PHC-2', 'Junnar',   'Pune'),
  ('baramati-sdh',  'Baramati SDH', 'Baramati', 'Pune'),
  ('khed-phc',      'Khed PHC',     'Khed',     'Pune'),
  ('shirur-rh',     'Shirur RH',    'Shirur',   'Pune'),
  ('phc-lonikand',  'PHC Lonikand', 'Haveli',   'Pune');

INSERT OR REPLACE INTO fridges (id, facility_id, label, cls, sort_order) VALUES
  ('wagholi-ilr1',  'phc-wagholi',  'ILR-1',  'ILR',      0),
  ('junnar-ilr01',  'junnar-phc2',  'ILR-01', 'DOMESTIC', 1),
  ('baramati-df01', 'baramati-sdh', 'FR-01',  'DOMESTIC', 2),
  ('khed-ilr03',    'khed-phc',     'ILR-03', 'ILR',      3),
  ('shirur-ilr01',  'shirur-rh',    'ILR-01', 'ILR',      4),
  ('lonikand-ilr2', 'phc-lonikand', 'ILR-2',  'ILR',      5);

INSERT OR REPLACE INTO fridge_stock (fridge_id, vaccine, position) VALUES
  ('wagholi-ilr1',  'Pentavalent', 0), ('wagholi-ilr1', 'Hepatitis B', 1), ('wagholi-ilr1', 'OPV', 2), ('wagholi-ilr1', 'MR', 3),
  ('junnar-ilr01',  'Pentavalent', 0), ('junnar-ilr01', 'BCG', 1),
  ('baramati-df01', 'PCV', 0),         ('baramati-df01', 'IPV', 1),
  ('khed-ilr03',    'Td', 0),          ('khed-ilr03', 'MR', 1),
  ('shirur-ilr01',  'OPV', 0),         ('shirur-ilr01', 'MR', 1), ('shirur-ilr01', 'BCG', 2),
  ('lonikand-ilr2', 'Pentavalent', 0), ('lonikand-ilr2', 'Rotavirus', 1);
