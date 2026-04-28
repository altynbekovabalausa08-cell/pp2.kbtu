-- Function: search by name, email or any phone
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    contact_id  INTEGER,
    name        VARCHAR,
    email       VARCHAR,
    birthday    DATE,
    group_name  VARCHAR,
    phone       VARCHAR,
    phone_type  VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT ON (c.id, ph.id)  -- avoid duplicate rows
           c.id,
           c.name,
           c.email,
           c.birthday,
           g.name   AS group_name,
           ph.phone,
           ph.type  AS phone_type
    FROM contacts c
    LEFT JOIN groups g  ON g.id = c.group_id   -- get group name
    LEFT JOIN phones ph ON ph.contact_id = c.id -- join multiple phones
    WHERE  c.name  ILIKE '%' || p_query || '%'  -- case-insensitive search
        OR c.email ILIKE '%' || p_query || '%'
        OR ph.phone ILIKE '%' || p_query || '%'
    ORDER BY c.id, ph.id;
END;
$$ LANGUAGE plpgsql;


-- Procedure: insert or update contact (upsert)
CREATE OR REPLACE PROCEDURE upsert_contact(
    p_name     VARCHAR,
    p_phone    VARCHAR DEFAULT NULL,
    p_email    VARCHAR DEFAULT NULL,
    p_birthday DATE DEFAULT NULL,
    p_group    VARCHAR DEFAULT 'Other'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
    v_group_id   INTEGER;
BEGIN
    -- find or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group;
    IF NOT FOUND THEN
        INSERT INTO groups (name) VALUES (p_group) RETURNING id INTO v_group_id;
    END IF;

    -- update if exists, else insert
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts
        SET email    = COALESCE(p_email, email),     -- keep old if NULL
            birthday = COALESCE(p_birthday, birthday),
            group_id = v_group_id
        WHERE name = p_name
        RETURNING id INTO v_contact_id;
    ELSE
        INSERT INTO contacts (name, email, birthday, group_id)
        VALUES (p_name, p_email, p_birthday, v_group_id)
        RETURNING id INTO v_contact_id;
    END IF;

    -- add phone if provided and not duplicate
    IF p_phone IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM phones
            WHERE contact_id = v_contact_id AND phone = p_phone
        ) THEN
            INSERT INTO phones (contact_id, phone, type)
            VALUES (v_contact_id, p_phone, 'mobile');
        END IF;
    END IF;
END;
$$;


-- Procedure: bulk insert with validation
CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    p_names  VARCHAR[],
    p_phones VARCHAR[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i       INTEGER;
    v_name  VARCHAR;
    v_phone VARCHAR;
BEGIN
    -- temp table for invalid data
    CREATE TEMP TABLE IF NOT EXISTS invalid_contacts (
        name  VARCHAR,
        phone VARCHAR,
        reason VARCHAR
    ) ON COMMIT DELETE ROWS;

    FOR i IN 1 .. array_length(p_names, 1) LOOP
        v_name  := p_names[i];
        v_phone := p_phones[i];

        -- validate phone format using regex
        IF v_phone !~ '^\+?[\d\s\-\(\)]{7,15}$' THEN
            INSERT INTO invalid_contacts VALUES (v_name, v_phone, 'invalid format');
            CONTINUE;
        END IF;

        -- insert using upsert procedure
        CALL upsert_contact(v_name, v_phone);
    END LOOP;
END;
$$;


-- Function: pagination using LIMIT/OFFSET
CREATE OR REPLACE FUNCTION get_contacts_page(
    p_limit  INTEGER DEFAULT 10,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    id         INTEGER,
    name       VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, c.email, c.birthday, g.name, c.created_at
    FROM contacts c
    LEFT JOIN groups g ON g.id = c.group_id
    ORDER BY c.name
    LIMIT p_limit   -- number of rows
    OFFSET p_offset; -- skip rows
END;
$$ LANGUAGE plpgsql;


-- Procedure: delete by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(
    p_name  VARCHAR DEFAULT NULL,
    p_phone VARCHAR DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_name IS NOT NULL THEN
        DELETE FROM contacts WHERE name = p_name;
    ELSIF p_phone IS NOT NULL THEN
        DELETE FROM contacts
        WHERE id IN (
            SELECT contact_id FROM phones WHERE phone = p_phone
        );
    ELSE
        RAISE EXCEPTION 'Provide either name or phone';
    END IF;
END;
$$;


-- Procedure: add new phone to existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER;
BEGIN
    -- find contact
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    -- validate phone type
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type';
    END IF;

    -- avoid duplicate phone
    IF EXISTS (
        SELECT 1 FROM phones
        WHERE contact_id = v_contact_id AND phone = p_phone AND type = p_type
    ) THEN
        RETURN;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);
END;
$$;


-- Procedure: move contact to another group
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id   INTEGER;
    v_contact_id INTEGER;
BEGIN
    -- find contact
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    -- find or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF NOT FOUND THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;

    -- update group
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;