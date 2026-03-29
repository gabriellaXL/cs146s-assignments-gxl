CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

CREATE TABLE IF NOT EXISTS action_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT NOT NULL,
  completed BOOLEAN NOT NULL DEFAULT 0,
  project_id INTEGER,
  created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL,
  updated_at DATETIME DEFAULT (STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')) NOT NULL
);

INSERT INTO projects (name, description, created_at, updated_at) VALUES
  (
    'Platform Refresh',
    'Cross-team operational work for improving the starter app.',
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  ),
  (
    'Course Ops',
    'Small tasks for grading and course workflow support.',
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  );

INSERT INTO notes (title, content, created_at, updated_at) VALUES
  (
    'Welcome',
    'This is a starter note. TODO: explore the app!',
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  ),
  (
    'Demo',
    'Click around and add a note. Ship feature!',
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  );

INSERT INTO action_items (description, completed, project_id, created_at, updated_at) VALUES
  (
    'Try pre-commit',
    0,
    1,
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  ),
  (
    'Run tests',
    0,
    2,
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now'),
    STRFTIME('%Y-%m-%dT%H:%M:%fZ','now')
  );
