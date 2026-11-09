CREATE TABLE members (
  email TEXT PRIMARY KEY,
  user_id TEXT UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('owner','editor','reviewer','publisher'))
);
--> statement-breakpoint
CREATE TABLE publication_batches (
  id TEXT PRIMARY KEY,
  state TEXT NOT NULL,
  run_id INTEGER,
  created_by TEXT NOT NULL,
  created_at TEXT NOT NULL
);
--> statement-breakpoint
CREATE TABLE proposals (
  id TEXT PRIMARY KEY,
  author TEXT NOT NULL,
  body TEXT NOT NULL,
  state TEXT NOT NULL,
  submitted_at TEXT NOT NULL,
  reviewer TEXT,
  reviewed_at TEXT,
  review_note TEXT,
  batch_id TEXT REFERENCES publication_batches(id)
);
--> statement-breakpoint
CREATE INDEX proposals_by_state ON proposals(state, submitted_at);
--> statement-breakpoint
CREATE INDEX proposals_by_author ON proposals(author, submitted_at);
