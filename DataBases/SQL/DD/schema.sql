-- ============================================================
-- TUTUNAKUN - Schema MySQL 8
-- Plataforma educativa gamificada de lengua totonaca
-- ============================================================

CREATE DATABASE IF NOT EXISTS tutunakun_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tutunakun_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- TABLA: users
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id            VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    email         VARCHAR(255) NOT NULL,
    username      VARCHAR(50)  NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150),
    avatar_url    VARCHAR(500),
    role          ENUM('admin','user','visitor') NOT NULL DEFAULT 'user',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Gamificación
    xp_total      INT          NOT NULL DEFAULT 0,
    level         SMALLINT     NOT NULL DEFAULT 1,
    hearts        SMALLINT     NOT NULL DEFAULT 5,
    current_streak INT         NOT NULL DEFAULT 0,
    longest_streak INT         NOT NULL DEFAULT 0,
    last_activity_date DATETIME,

    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_username (username),
    INDEX idx_users_role (role),
    INDEX idx_users_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: courses
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    id            VARCHAR(36) NOT NULL DEFAULT (UUID()),
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    cover_image_url VARCHAR(500),    color_hex       VARCHAR(7)  DEFAULT '#FF6B6B',    difficulty    ENUM('beginner','intermediate','advanced') NOT NULL DEFAULT 'beginner',
    is_published  BOOLEAN NOT NULL DEFAULT FALSE,
    order_index   SMALLINT NOT NULL DEFAULT 0,
    created_by    VARCHAR(36),

    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_courses_published (is_published),
    INDEX idx_courses_order (order_index),
    CONSTRAINT fk_courses_creator FOREIGN KEY (created_by)
        REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: units
-- ============================================================
CREATE TABLE IF NOT EXISTS units (
    id          VARCHAR(36) NOT NULL DEFAULT (UUID()),
    course_id   VARCHAR(36) NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    icon_emoji  VARCHAR(10) DEFAULT '📚',
    color_hex   VARCHAR(7)  DEFAULT '#FF6B6B',
    order_index SMALLINT    NOT NULL DEFAULT 0,
    is_locked   BOOLEAN     NOT NULL DEFAULT TRUE,
    xp_reward   INT         NOT NULL DEFAULT 50,

    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_units_course (course_id),
    CONSTRAINT fk_units_course FOREIGN KEY (course_id)
        REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: lessons
-- ============================================================
CREATE TABLE IF NOT EXISTS lessons (
    id           VARCHAR(36) NOT NULL DEFAULT (UUID()),
    unit_id      VARCHAR(36) NOT NULL,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    order_index  SMALLINT    NOT NULL DEFAULT 0,
    xp_reward    INT         NOT NULL DEFAULT 20,

    -- Contenido educativo (clase)
    content_type VARCHAR(50),           -- text, video, audio, mixed
    content_data JSON,                  -- bloques de contenido estructurado

    is_published BOOLEAN NOT NULL DEFAULT FALSE,

    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_lessons_unit (unit_id),
    INDEX idx_lessons_published (is_published),
    CONSTRAINT fk_lessons_unit FOREIGN KEY (unit_id)
        REFERENCES units(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: exercises
-- ============================================================
CREATE TABLE IF NOT EXISTS exercises (
    id             VARCHAR(36) NOT NULL DEFAULT (UUID()),
    lesson_id      VARCHAR(36) NOT NULL,
    type           ENUM('translation','multiple_choice','writing','audio') NOT NULL,
    question       TEXT        NOT NULL,
    correct_answer TEXT        NOT NULL,
    options        JSON,               -- opciones para selección múltiple
    hint           TEXT,
    explanation    TEXT,               -- explicación de la respuesta
    audio_url      VARCHAR(500),
    image_url      VARCHAR(500),
    xp_reward      INT         NOT NULL DEFAULT 5,
    order_index    SMALLINT    NOT NULL DEFAULT 0,

    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_exercises_lesson (lesson_id),
    INDEX idx_exercises_type (type),
    CONSTRAINT fk_exercises_lesson FOREIGN KEY (lesson_id)
        REFERENCES lessons(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: exercise_attempts
-- ============================================================
CREATE TABLE IF NOT EXISTS exercise_attempts (
    id                 VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id            VARCHAR(36) NOT NULL,
    exercise_id        VARCHAR(36) NOT NULL,
    user_answer        TEXT        NOT NULL,
    is_correct         BOOLEAN     NOT NULL,
    xp_earned          INT         NOT NULL DEFAULT 0,
    time_spent_seconds INT,

    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_attempts_user (user_id),
    INDEX idx_attempts_exercise (exercise_id),
    INDEX idx_attempts_correct (is_correct),
    CONSTRAINT fk_attempts_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_attempts_exercise FOREIGN KEY (exercise_id)
        REFERENCES exercises(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: user_progress
-- ============================================================
CREATE TABLE IF NOT EXISTS user_progress (
    id                    VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id               VARCHAR(36) NOT NULL,
    lesson_id             VARCHAR(36) NOT NULL,
    is_completed          BOOLEAN     NOT NULL DEFAULT FALSE,
    completion_percentage FLOAT       NOT NULL DEFAULT 0.0,
    score                 FLOAT       NOT NULL DEFAULT 0.0,
    attempts_count        INT         NOT NULL DEFAULT 0,
    xp_earned             INT         NOT NULL DEFAULT 0,
    completed_at          DATETIME,

    created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_user_lesson_progress (user_id, lesson_id),
    INDEX idx_progress_user (user_id),
    INDEX idx_progress_completed (is_completed),
    CONSTRAINT fk_progress_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_progress_lesson FOREIGN KEY (lesson_id)
        REFERENCES lessons(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: achievements (insignias disponibles)
-- ============================================================
CREATE TABLE IF NOT EXISTS achievements (
    id               VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    title            VARCHAR(150) NOT NULL,
    description      TEXT,
    icon_url         VARCHAR(500),
    icon_emoji       VARCHAR(10)  DEFAULT '🏆',
    badge_color      VARCHAR(7)   DEFAULT '#FFD700',
    xp_reward        INT          NOT NULL DEFAULT 100,
    condition_type   VARCHAR(50),    -- streak, xp, lessons, perfect_score, level
    condition_value  INT,

    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_achievements_condition (condition_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: user_achievements
-- ============================================================
CREATE TABLE IF NOT EXISTS user_achievements (
    id             VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id        VARCHAR(36) NOT NULL,
    achievement_id VARCHAR(36) NOT NULL,
    earned_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_user_achievement (user_id, achievement_id),
    CONSTRAINT fk_ua_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_ua_achievement FOREIGN KEY (achievement_id)
        REFERENCES achievements(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: daily_streaks
-- ============================================================
CREATE TABLE IF NOT EXISTS daily_streaks (
    id                       VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id                  VARCHAR(36) NOT NULL,
    streak_date              DATETIME    NOT NULL,
    xp_earned_today          INT         NOT NULL DEFAULT 0,
    lessons_completed_today  INT         NOT NULL DEFAULT 0,

    created_at               DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_user_streak_date (user_id, streak_date),
    INDEX idx_streaks_user (user_id),
    CONSTRAINT fk_streaks_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: refresh_tokens
-- ============================================================
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id         VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    user_id    VARCHAR(36)  NOT NULL,
    token      VARCHAR(500) NOT NULL,
    is_revoked BOOLEAN      NOT NULL DEFAULT FALSE,
    expires_at DATETIME     NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_refresh_token (token),
    INDEX idx_refresh_user (user_id),
    CONSTRAINT fk_refresh_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: password_resets
-- ============================================================
CREATE TABLE IF NOT EXISTS password_resets (
    id         VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    user_id    VARCHAR(36)  NOT NULL,
    token      VARCHAR(255) NOT NULL,
    is_used    BOOLEAN      NOT NULL DEFAULT FALSE,
    expires_at DATETIME     NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_password_reset_token (token),
    CONSTRAINT fk_pr_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: email_verifications
-- ============================================================
CREATE TABLE IF NOT EXISTS email_verifications (
    id         VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    user_id    VARCHAR(36)  NOT NULL,
    token      VARCHAR(255) NOT NULL,
    is_used    BOOLEAN      NOT NULL DEFAULT FALSE,
    expires_at DATETIME     NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_ev_token (token),
    CONSTRAINT fk_ev_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: notifications
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id         VARCHAR(36)  NOT NULL DEFAULT (UUID()),
    user_id    VARCHAR(36)  NOT NULL,
    type       ENUM('reminder','achievement','progress','system') NOT NULL,
    title      VARCHAR(200) NOT NULL,
    message    TEXT,
    icon_emoji VARCHAR(10),
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    action_url VARCHAR(500),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_notif_user_unread (user_id, is_read),
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLA: reminders
-- ============================================================
CREATE TABLE IF NOT EXISTS reminders (
    id           VARCHAR(36) NOT NULL DEFAULT (UUID()),
    user_id      VARCHAR(36) NOT NULL,
    hour         TINYINT     NOT NULL COMMENT '0-23',
    minute       TINYINT     NOT NULL COMMENT '0-59',
    timezone     VARCHAR(50) NOT NULL DEFAULT 'America/Mexico_City',
    is_active    BOOLEAN     NOT NULL DEFAULT TRUE,
    message      VARCHAR(300) NOT NULL DEFAULT '¡Es hora de estudiar totonaco! 🫀',
    days_of_week JSON        COMMENT '[0,1,2,3,4,5,6] lunes=0 domingo=6',
    last_sent_at DATETIME,

    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_reminders_user (user_id),
    INDEX idx_reminders_time (hour, minute, is_active),
    CONSTRAINT fk_reminders_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_hour CHECK (hour BETWEEN 0 AND 23),
    CONSTRAINT chk_minute CHECK (minute BETWEEN 0 AND 59)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- VISTA: user_learning_summary (útil para dashboard)
-- ============================================================
CREATE OR REPLACE VIEW user_learning_summary AS
SELECT
    u.id,
    u.username,
    u.email,
    u.xp_total,
    u.level,
    u.current_streak,
    COUNT(DISTINCT up.lesson_id) AS lessons_completed,
    COUNT(DISTINCT ua.achievement_id) AS achievements_earned,
    SUM(CASE WHEN ea.is_correct = TRUE THEN 1 ELSE 0 END) AS correct_answers,
    COUNT(ea.id) AS total_attempts,
    ROUND(
        100.0 * SUM(CASE WHEN ea.is_correct = TRUE THEN 1 ELSE 0 END)
        / NULLIF(COUNT(ea.id), 0), 2
    ) AS accuracy_pct
FROM users u
LEFT JOIN user_progress up ON up.user_id = u.id AND up.is_completed = TRUE
LEFT JOIN user_achievements ua ON ua.user_id = u.id
LEFT JOIN exercise_attempts ea ON ea.user_id = u.id
GROUP BY u.id;

SELECT 'Schema Tutunakun creado exitosamente ✅' AS resultado;
