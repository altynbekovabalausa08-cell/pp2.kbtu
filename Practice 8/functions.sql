-- 1. Function to search contacts by pattern
CREATE OR REPLACE FUNCTION search_contacts(search_pattern TEXT)
RETURNS TABLE (
    id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.last_name, p.phone
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || search_pattern || '%'
       OR p.last_name ILIKE '%' || search_pattern || '%'
       OR p.phone ILIKE '%' || search_pattern || '%'
    ORDER BY p.id;
END;
$$ LANGUAGE plpgsql;


-- 2. Function for pagination
CREATE OR REPLACE FUNCTION get_contacts_paginated(limit_count INT, offset_count INT)
RETURNS TABLE (
    id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    phone VARCHAR
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.last_name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT limit_count OFFSET offset_count;
END;
$$ LANGUAGE plpgsql;