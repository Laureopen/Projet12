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
INSERT INTO users (name, email, password, department_id)
SELECT 'Epic admin', 'admin@epicevents.com', '$2b$12$jKTdI8J6dJ9BL2NH4k2or.Hyn3J5hRP3NfLvkE0iE4qa8/uW12vo6', d.id
FROM departments d WHERE d.name = 'gestion'AND NOT EXISTS (
    SELECT 1 FROM users WHERE email = 'admin@epicevents.com');