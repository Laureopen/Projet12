-- Ajoute "commercial" s'il n'existe pas déjà
INSERT INTO department (name)
SELECT 'commercial'
WHERE NOT EXISTS (
    SELECT 1 FROM department WHERE name = 'commercial'
);
-- Ajoute "support" s'il n'existe pas déjà
INSERT INTO department (name)
SELECT 'support'
WHERE NOT EXISTS (
    SELECT 1 FROM department WHERE name = 'support'
);
-- Ajoute "gestion" s'il n'existe pas déjà
INSERT INTO department (name)
SELECT 'gestion'
WHERE NOT EXISTS (
    SELECT 1 FROM department WHERE name = 'gestion'
);