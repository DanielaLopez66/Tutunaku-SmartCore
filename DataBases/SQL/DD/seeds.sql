-- ============================================================
-- TUTUNAKUN - Datos iniciales (Seeds)
-- Ejecutar DESPUÉS de schema.sql
-- ============================================================

USE tutunakun_db;

-- ============================================================
-- ADMIN USER
-- Contraseña: Admin1234!  (hash bcrypt)
-- ============================================================
INSERT INTO users (id, email, username, hashed_password, full_name, role, is_active, is_email_verified, xp_total, level, hearts)
VALUES (
    'usr-admin-000-0000-000000000001',
    'admin@tutunakun.mx',
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBahzNtAT6cNVi',  -- Admin1234!
    'Administrador Tutunakun',
    'admin',
    TRUE, TRUE, 5000, 10, 5
);

-- DEMO USER
-- Contraseña: Demo1234!
INSERT INTO users (id, email, username, hashed_password, full_name, role, is_active, is_email_verified, xp_total, level, hearts, current_streak)
VALUES (
    'usr-demo-0000-0000-000000000002',
    'demo@tutunakun.mx',
    'totonaco_aprendiz',
    '$2b$12$K8V9X2mN4pQ7rS1tU3wY5eA6bC0dE9fG1hI2jL3kM4nO5pR6sT7u',  -- Demo1234!
    'Aprendiz Totonaco',
    'user',
    TRUE, TRUE, 350, 4, 5, 7
);

-- ============================================================
-- CURSO PRINCIPAL
-- ============================================================
INSERT INTO courses (id, title, description, difficulty, is_published, order_index, created_by) VALUES
(
    'crs-toto-0001-0000-000000000001',
    'Totonaco para Principiantes',
    'Aprende las bases de la lengua totonaca: saludos, números, colores y vocabulario cotidiano con ejercicios interactivos y contenido cultural.',
    'beginner',
    TRUE,
    1,
    'usr-admin-000-0000-000000000001'
),
(
    'crs-toto-0002-0000-000000000002',
    'Conversación Totonaca',
    'Aprende a mantener conversaciones básicas en totonaco sobre familia, comida y vida diaria.',
    'intermediate',
    FALSE,
    2,
    'usr-admin-000-0000-000000000001'
);

-- ============================================================
-- UNIDADES
-- ============================================================
INSERT INTO units (id, course_id, title, description, icon_emoji, color_hex, order_index, is_locked, xp_reward) VALUES
('unt-0001', 'crs-toto-0001-0000-000000000001', 'Saludos y Presentaciones', 'Aprende cómo saludar y presentarte en totonaco', '👋', '#FF6B6B', 1, FALSE, 100),
('unt-0002', 'crs-toto-0001-0000-000000000001', 'Los Números', 'Del uno al veinte en totonaco', '🔢', '#4ECDC4', 2, TRUE, 100),
('unt-0003', 'crs-toto-0001-0000-000000000001', 'Colores y Naturaleza', 'Los colores y el mundo natural en totonaco', '🌈', '#45B7D1', 3, TRUE, 150),
('unt-0004', 'crs-toto-0001-0000-000000000001', 'La Familia', 'Vocabulario de parentesco en totonaco', '👨‍👩‍👧‍👦', '#96CEB4', 4, TRUE, 150),
('unt-0005', 'crs-toto-0001-0000-000000000001', 'Comida y Bebida', 'Alimentos tradicionales totonacos', '🌽', '#FFEAA7', 5, TRUE, 200);

-- ============================================================
-- LECCIONES (con contenido educativo)
-- ============================================================
INSERT INTO lessons (id, unit_id, title, description, order_index, xp_reward, content_type, content_data, is_published) VALUES
(
    'les-0001', 'unt-0001', 'Hola y Adiós', 'Aprende los saludos básicos', 1, 30, 'mixed',
    JSON_ARRAY(
        JSON_OBJECT('type', 'text', 'content', 'En totonaco, los saludos son fundamentales para mostrar respeto. La lengua totonaca se habla principalmente en la Sierra Norte de Puebla y en la costa norte de Veracruz.', 'language', 'es'),
        JSON_OBJECT('type', 'example', 'content', 'Lakgtsukut', 'language', 'toto', 'caption', 'Buenas tardes'),
        JSON_OBJECT('type', 'example', 'content', 'Lakgsnanat', 'language', 'toto', 'caption', 'Buenos días'),
        JSON_OBJECT('type', 'example', 'content', 'Kiwi', 'language', 'toto', 'caption', 'Adiós')
    ),
    TRUE
),
(
    'les-0002', 'unt-0001', '¿Cómo te llamas?', 'Presentaciones personales', 2, 30, 'mixed',
    JSON_ARRAY(
        JSON_OBJECT('type', 'text', 'content', 'Para presentarte en totonaco, usamos estas expresiones básicas:', 'language', 'es'),
        JSON_OBJECT('type', 'example', 'content', 'Chu kin chichi?', 'language', 'toto', 'caption', '¿Cómo te llamas?'),
        JSON_OBJECT('type', 'example', 'content', 'Kin chichi...', 'language', 'toto', 'caption', 'Me llamo...')
    ),
    TRUE
),
(
    'les-0003', 'unt-0002', 'Del 1 al 5', 'Los primeros números', 1, 25, 'text',
    JSON_ARRAY(
        JSON_OBJECT('type', 'text', 'content', 'Los números del 1 al 5 en totonaco son la base para contar.', 'language', 'es'),
        JSON_OBJECT('type', 'example', 'content', 'Tum = 1', 'language', 'toto', 'caption', 'Uno'),
        JSON_OBJECT('type', 'example', 'content', 'Tsa = 2', 'language', 'toto', 'caption', 'Dos'),
        JSON_OBJECT('type', 'example', 'content', 'Tomu = 3', 'language', 'toto', 'caption', 'Tres'),
        JSON_OBJECT('type', 'example', 'content', 'Tsatsa = 4', 'language', 'toto', 'caption', 'Cuatro'),
        JSON_OBJECT('type', 'example', 'content', 'Qalhtum = 5', 'language', 'toto', 'caption', 'Cinco')
    ),
    TRUE
);

-- ============================================================
-- EJERCICIOS
-- ============================================================
INSERT INTO exercises (id, lesson_id, type, question, correct_answer, options, hint, explanation, xp_reward, order_index) VALUES
-- Lección 1: Saludos
('exc-0001', 'les-0001', 'translation', '¿Cómo se dice "Buenos días" en totonaco?', 'Lakgsnanat',
    JSON_ARRAY('Lakgtsukut', 'Lakgsnanat', 'Kiwi', 'Tum'),
    'Es el saludo para la mañana', 'Lakgsnanat es el saludo de la mañana en totonaco. Lakgtsukut se usa en la tarde.', 10, 1),

('exc-0002', 'les-0001', 'translation', '¿Qué significa "Kiwi" en español?', 'Adiós',
    JSON_ARRAY('Hola', 'Buenas noches', 'Adiós', 'Gracias'),
    'Es para despedirse', 'Kiwi es la despedida más común en totonaco.', 10, 2),

('exc-0003', 'les-0001', 'multiple_choice', 'Selecciona el saludo de "Buenas tardes" en totonaco:', 'Lakgtsukut',
    JSON_ARRAY('Lakgsnanat', 'Lakgtsukut', 'Kiwi', 'Kin chichi'),
    NULL, 'Lakgtsukut se usa en la tarde, mientras Lakgsnanat es para las mañanas.', 10, 3),

('exc-0004', 'les-0001', 'writing', 'Escribe cómo se dice "Adiós" en totonaco:', 'Kiwi',
    NULL, 'Empieza con la letra K', 'Kiwi es la despedida más sencilla y común en totonaco.', 15, 4),

-- Lección 2: Presentaciones
('exc-0005', 'les-0002', 'translation', '¿Cómo se pregunta "¿Cómo te llamas?" en totonaco?', 'Chu kin chichi?',
    JSON_ARRAY('Kin chichi', 'Chu kin chichi?', 'Lakgsnanat', 'Kiwi'),
    'Es una pregunta', 'Chu es el marcador de pregunta en totonaco. Kin chichi significa "me llamo".', 10, 1),

('exc-0006', 'les-0002', 'writing', 'Escribe "Me llamo" en totonaco:', 'Kin chichi',
    NULL, 'Empieza con "Kin"', 'Kin chichi literalmente significa "mi nombre es".', 15, 2),

-- Lección 3: Números
('exc-0007', 'les-0003', 'translation', '¿Cuánto es "Tum" en español?', 'Uno',
    JSON_ARRAY('Cero', 'Uno', 'Dos', 'Tres'),
    'Es el primer número', 'Tum es el número uno en totonaco.', 10, 1),

('exc-0008', 'les-0003', 'multiple_choice', '¿Cómo se dice "Dos" en totonaco?', 'Tsa',
    JSON_ARRAY('Tum', 'Tsa', 'Tomu', 'Tsatsa'),
    NULL, 'Tsa es el número dos. Tomu es tres.', 10, 2),

('exc-0009', 'les-0003', 'writing', 'Escribe el número "Cinco" en totonaco:', 'Qalhtum',
    NULL, 'Empieza con Q', 'Qalhtum es cinco en totonaco.', 15, 3),

('exc-0010', 'les-0003', 'translation', '¿Qué número es "Tsatsa"?', 'Cuatro',
    JSON_ARRAY('Tres', 'Cuatro', 'Cinco', 'Dos'),
    'Tsatsa parece una repetición de Tsa', 'Tsatsa (cuatro) es como decir "dos veces dos" en la lógica numérica totonaca.', 10, 4);

-- ============================================================
-- LOGROS / INSIGNIAS
-- ============================================================
INSERT INTO achievements (id, title, description, icon_emoji, badge_color, xp_reward, condition_type, condition_value) VALUES
('ach-0001', 'Primera Palabra', 'Completaste tu primer ejercicio correctamente', '🌱', '#4CAF50', 50, 'xp', 10),
('ach-0002', 'Racha de Fuego', 'Mantuviste una racha de 3 días consecutivos', '🔥', '#FF5722', 100, 'streak', 3),
('ach-0003', 'Semana Constante', 'Estudiaste 7 días seguidos', '⚡', '#FFC107', 200, 'streak', 7),
('ach-0004', 'Explorador Cultural', 'Completaste tu primera unidad', '🗺️', '#9C27B0', 150, 'xp', 100),
('ach-0005', 'Corazón Totonaco', 'Llegaste al nivel 5', '🫀', '#E91E63', 300, 'level', 5),
('ach-0006', 'Maestro de Saludos', 'Completaste la unidad de Saludos', '👋', '#03A9F4', 100, 'xp', 200),
('ach-0007', 'Cien XP', 'Acumulaste 100 puntos de experiencia', '💯', '#FF9800', 50, 'xp', 100),
('ach-0008', 'Mil XP', 'Acumulaste 1000 puntos de experiencia', '🌟', '#FFD700', 200, 'xp', 1000),
('ach-0009', 'Racha Legendaria', '30 días de racha consecutiva', '👑', '#FFD700', 500, 'streak', 30),
('ach-0010', 'Nivel 10', 'Alcanzaste el nivel 10', '🏆', '#FF6B6B', 500, 'level', 10);

-- Otorgar un logro al usuario demo
INSERT INTO user_achievements (id, user_id, achievement_id, earned_at) VALUES
('ua-demo-001', 'usr-demo-0000-0000-000000000002', 'ach-0001', NOW()),
('ua-demo-002', 'usr-demo-0000-0000-000000000002', 'ach-0007', NOW());

-- Progreso del usuario demo
INSERT INTO user_progress (id, user_id, lesson_id, is_completed, completion_percentage, score, xp_earned, completed_at) VALUES
('prg-demo-001', 'usr-demo-0000-0000-000000000002', 'les-0001', TRUE, 100.0, 90.0, 30, NOW()),
('prg-demo-002', 'usr-demo-0000-0000-000000000002', 'les-0002', TRUE, 100.0, 85.0, 25, NOW());

-- Racha del usuario demo
INSERT INTO daily_streaks (user_id, streak_date, xp_earned_today, lessons_completed_today) VALUES
('usr-demo-0000-0000-000000000002', NOW(), 55, 2);

SELECT 'Seeds cargados exitosamente ✅' AS resultado;
