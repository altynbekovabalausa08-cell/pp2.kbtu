-- 1. Procedure: insert new user or update phone if user already exists
CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_first_name VARCHAR,
    p_last_name VARCHAR,
    p_phone VARCHAR
)
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM phonebook
        WHERE first_name = p_first_name
          AND last_name = p_last_name
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE first_name = p_first_name
          AND last_name = p_last_name;
    ELSE
        INSERT INTO phonebook(first_name, last_name, phone)
        VALUES (p_first_name, p_last_name, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 2. Procedure: insert many users with validation
CREATE OR REPLACE PROCEDURE insert_many_users(
    IN p_first_names TEXT[],
    IN p_last_names TEXT[],
    IN p_phones TEXT[]
)
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1 .. array_length(p_first_names, 1)
    LOOP
        IF p_phones[i] ~ '^[0-9+\-() ]{6,20}$' THEN
            CALL insert_or_update_user(
                p_first_names[i],
                p_last_names[i],
                p_phones[i]
            );
        ELSE
            RAISE NOTICE 'Incorrect data: %, %, %',
                p_first_names[i], p_last_names[i], p_phones[i];
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;


-- 3. Procedure: delete by username or phone
CREATE OR REPLACE PROCEDURE delete_user(p_value VARCHAR)
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = p_value
       OR last_name = p_value
       OR phone = p_value;
END;
$$ LANGUAGE plpgsql;