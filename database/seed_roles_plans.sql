-- Initial role and plan seeds for KURGIN Backend Auth Contract V1.

INSERT INTO roles (id, description) VALUES
('guest', 'Unauthenticated user, no persisted private data'),
('buyer', 'Consumer buyer'),
('jeweler', 'Jeweler / retail advisor'),
('designer', 'Jewelry designer'),
('gemologist', 'Gemology expert'),
('partner', 'B2B partner'),
('support', 'Support operator'),
('admin', 'System administrator')
ON CONFLICT (id) DO UPDATE SET description = EXCLUDED.description;

INSERT INTO plans (id, name, price_minor, currency, features) VALUES
('free', 'Free', 0, 'RUB', '["public_catalog", "basic_score_info"]'),
('single_report', 'Single Report', 99000, 'RUB', '["single_score_report"]'),
('pro', 'Professional', 490000, 'RUB', '["excel_batch", "saved_reports", "workspace_preview"]'),
('partner', 'Partner', 0, 'RUB', '["partner_prices", "workspace", "team_access"]')
ON CONFLICT (id) DO UPDATE SET
name = EXCLUDED.name,
price_minor = EXCLUDED.price_minor,
currency = EXCLUDED.currency,
features = EXCLUDED.features;
