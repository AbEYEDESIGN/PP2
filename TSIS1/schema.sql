-- расширяем схему из practice 8 (таблица phonebook уже есть)

-- группы контактов
create table if not exists groups (
    id   serial primary key,
    name varchar(50) unique not null
);

insert into groups (name) values
    ('Family'), ('Work'), ('Friend'), ('Other')
on conflict (name) do nothing;

-- добавляем новые поля в phonebook
alter table phonebook
    add column if not exists email    varchar(100),
    add column if not exists birthday date,
    add column if not exists group_id integer references groups(id);

-- отдельная таблица для телефонов (один контакт — много номеров)
-- on delete cascade — при удалении контакта его телефоны тоже удалятся
create table if not exists phones (
    id         serial primary key,
    contact_id integer references phonebook(id) on delete cascade,
    phone      varchar(20) not null,
    type       varchar(10) check (type in ('home', 'work', 'mobile'))
);
