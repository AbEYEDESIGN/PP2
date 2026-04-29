-- новые процедуры для tsis 1 (процедуры из practice 8 не дублируем)

-- добавляет телефон к существующему контакту
create or replace procedure add_phone(
    p_contact_name varchar,
    p_phone        varchar,
    p_type         varchar  -- 'home', 'work' или 'mobile'
)
language plpgsql as $$
declare
    v_id integer;
begin
    select id into v_id from phonebook where name = p_contact_name;

    if not found then
        raise exception 'контакт "%" не найден', p_contact_name;
    end if;

    insert into phones (contact_id, phone, type)
    values (v_id, p_phone, p_type);
end;
$$;


-- перемещает контакт в группу, если группы нет — создаёт её
create or replace procedure move_to_group(
    p_contact_name varchar,
    p_group_name   varchar
)
language plpgsql as $$
declare
    v_group_id integer;
begin
    select id into v_group_id from groups where name = p_group_name;

    if not found then
        insert into groups (name) values (p_group_name)
        returning id into v_group_id;
    end if;

    update phonebook set group_id = v_group_id where name = p_contact_name;

    if not found then
        raise exception 'контакт "%" не найден', p_contact_name;
    end if;
end;
$$;


-- поиск по имени, email и всем телефонам из таблицы phones
-- distinct убирает дубликаты (если у контакта 3 номера — без него он появится 3 раза)
create or replace function search_contacts(p_query text)
returns table(id integer, name text, email varchar, birthday date, grp varchar)
language plpgsql as $$
begin
    return query
    select distinct pb.id, pb.name, pb.email, pb.birthday, g.name
    from phonebook pb
    left join groups g  on pb.group_id = g.id
    left join phones ph on ph.contact_id = pb.id
    where pb.name  ilike '%' || p_query || '%'
       or pb.email ilike '%' || p_query || '%'
       or ph.phone ilike '%' || p_query || '%';
end;
$$;
