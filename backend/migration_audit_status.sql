-- Migration: plainbi_audit Erweiterung um Status/Laufzeit/Fehlermeldung
-- Für bestehende Installationen ausführen (einmalig)

-- MSSQL
ALTER TABLE plainbi_audit ADD status varchar(10);
ALTER TABLE plainbi_audit ADD error_msg varchar(2000);
ALTER TABLE plainbi_audit ADD duration_ms int;

-- PostgreSQL
-- ALTER TABLE plainbi_audit ADD COLUMN status varchar(10);
-- ALTER TABLE plainbi_audit ADD COLUMN error_msg varchar(2000);
-- ALTER TABLE plainbi_audit ADD COLUMN duration_ms integer;

-- SQLite
-- ALTER TABLE plainbi_audit ADD COLUMN status varchar;
-- ALTER TABLE plainbi_audit ADD COLUMN error_msg varchar;
-- ALTER TABLE plainbi_audit ADD COLUMN duration_ms integer;

-- Oracle
-- ALTER TABLE plainbi_audit ADD (status varchar2(10), error_msg varchar2(2000), duration_ms number(10));

-- View neu erstellen (DB-spezifisch anpassen):
-- DROP VIEW plainbi_audit_adhoc; -- dann aus repo_init_<db>.json neu ausführen
