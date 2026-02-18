BEGIN;

-- 1) Clear existing data (order matters due to FK constraints)
TRUNCATE TABLE task_tags;
TRUNCATE TABLE tasks RESTART IDENTITY CASCADE;
TRUNCATE TABLE tags RESTART IDENTITY CASCADE;

-- 2) Insert tags
INSERT INTO tags (name) VALUES
  ('work'),
  ('urgent'),
  ('personal'),
  ('health'),
  ('finance'),
  ('study'),
  ('shopping')
ON CONFLICT (name) DO NOTHING;

-- 3) Insert tasks (due_date always in the future)
INSERT INTO tasks (title, description, priority, due_date, completed, is_deleted, created_at, updated_at)
VALUES
  ('Finish MediVue assessment', 'Implement endpoints, filtering, tests, and Docker.', 5, CURRENT_DATE + 3, FALSE, FALSE, NOW(), NOW()),
  ('Pay electricity bill', 'Pay before due date to avoid late fees.', 3, CURRENT_DATE + 5, FALSE, FALSE, NOW(), NOW()),
  ('Gym session', 'Push day. Warm up properly.', 2, CURRENT_DATE + 1, FALSE, FALSE, NOW(), NOW()),
  ('Buy groceries', 'Eggs, chicken, rice, veggies.', 2, CURRENT_DATE + 2, FALSE, FALSE, NOW(), NOW()),
  ('Study AWS SAA recap', 'Review VPC, IAM, S3, CloudFront, RDS, SQS/SNS.', 4, CURRENT_DATE + 7, FALSE, FALSE, NOW(), NOW()),
  ('Call parents', NULL, 1, CURRENT_DATE + 4, FALSE, FALSE, NOW(), NOW()),
  ('Lodge tax documents', 'Collect invoices and submit to accountant.', 3, CURRENT_DATE + 10, FALSE, FALSE, NOW(), NOW()),
  ('Old deleted task', 'This should be hidden by API queries.', 2, CURRENT_DATE + 6, FALSE, TRUE, NOW(), NOW());

-- 4) Map tasks to tags (many-to-many via task_tags)
-- Finish MediVue assessment -> work, urgent, study
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('work', 'urgent', 'study')
WHERE t.title = 'Finish MediVue assessment';

-- Pay electricity bill -> personal, finance, urgent
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('personal', 'finance', 'urgent')
WHERE t.title = 'Pay electricity bill';

-- Gym session -> health, personal
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('health', 'personal')
WHERE t.title = 'Gym session';

-- Buy groceries -> personal, shopping
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('personal', 'shopping')
WHERE t.title = 'Buy groceries';

-- Study AWS SAA recap -> study
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('study')
WHERE t.title = 'Study AWS SAA recap';

-- Call parents -> personal
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('personal')
WHERE t.title = 'Call parents';

-- Lodge tax documents -> finance, personal
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('finance', 'personal')
WHERE t.title = 'Lodge tax documents';

-- Old deleted task -> work
INSERT INTO task_tags (task_id, tag_id)
SELECT t.id, tg.id
FROM tasks t
JOIN tags tg ON tg.name IN ('work')
WHERE t.title = 'Old deleted task';

COMMIT;

