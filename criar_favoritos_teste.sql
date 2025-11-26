-- Script para criar favoritos de teste
-- Insere alguns favoritos para eventos existentes

-- Favoritos para o primeiro evento (se existir)
INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 1, id, NOW() FROM agenda_event WHERE id = 1 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 1 AND event_id = 1);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 2, id, NOW() FROM agenda_event WHERE id = 1 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 2 AND event_id = 1);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 3, id, NOW() FROM agenda_event WHERE id = 1 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 3 AND event_id = 1);

-- Favoritos para o segundo evento (se existir)
INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 1, id, NOW() FROM agenda_event WHERE id = 2 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 1 AND event_id = 2);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 2, id, NOW() FROM agenda_event WHERE id = 2 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 2 AND event_id = 2);

-- Favoritos para o terceiro evento (se existir) - com mais favoritos
INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 1, id, NOW() FROM agenda_event WHERE id = 3 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 1 AND event_id = 3);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 2, id, NOW() FROM agenda_event WHERE id = 3 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 2 AND event_id = 3);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 3, id, NOW() FROM agenda_event WHERE id = 3 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 3 AND event_id = 3);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 4, id, NOW() FROM agenda_event WHERE id = 3 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 4 AND event_id = 3);

INSERT INTO agenda_useragenda (user_id, event_id, added_at)
SELECT 5, id, NOW() FROM agenda_event WHERE id = 3 
AND NOT EXISTS (SELECT 1 FROM agenda_useragenda WHERE user_id = 5 AND event_id = 3);
