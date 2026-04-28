-- Drop tables to reset schema (safe re-run)
DROP TABLE IF EXISTS phones   CASCADE;
DROP TABLE IF EXISTS contacts CASCADE;
DROP TABLE IF EXISTS groups   CASCADE;

-- Groups table: stores categories like Family, Work, etc.
CREATE TABLE groups (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Insert default groups
INSERT INTO groups (name) VALUES
    ('Family'),
    ('Work'),
    ('Friend'),
    ('Other');

-- Main contacts table (one row = one person)
CREATE TABLE contacts (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL UNIQUE, -- unique full name
    email      VARCHAR(100),                 -- optional email
    birthday   DATE,                         -- optional birthday
    group_id   INTEGER REFERENCES groups(id) ON DELETE SET NULL, -- link to group
    created_at TIMESTAMP DEFAULT NOW()       -- auto timestamp
);

-- Phones table: multiple numbers per contact (1-to-many)
CREATE TABLE phones (
    id         SERIAL PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE, -- link to contact
    phone      VARCHAR(20) NOT NULL,  -- phone number
    type       VARCHAR(10) NOT NULL DEFAULT 'mobile'
               CHECK (type IN ('home', 'work', 'mobile')) -- restrict type
);