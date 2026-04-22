CREATE TABLE IF NOT EXISTS phonebook (
    id SERIAL PRIMARY KEY,
    name TEXT,
    phone TEXT
);

CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.name, p.phone
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.phone ILIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_phonebook(limit_val INT, offset_val INT)
RETURNS TABLE(name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.name, p.phone
    FROM phonebook p
    ORDER BY p.id DESC
    LIMIT limit_val OFFSET offset_val;
END;
$$ LANGUAGE plpgsql;
