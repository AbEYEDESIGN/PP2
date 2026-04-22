CREATE OR REPLACE PROCEDURE upsert_user(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE phonebook
    SET phone = p_phone
    WHERE name = p_name;

    IF NOT FOUND THEN
        INSERT INTO phonebook(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE insert_many(names TEXT[], phones TEXT[])
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO phonebook(name, phone)
    SELECT n, p
    FROM unnest(names, phones) AS t(n, p);
END;
$$;


CREATE OR REPLACE PROCEDURE delete_user(val TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = val OR phone = val;
END;
$$;
