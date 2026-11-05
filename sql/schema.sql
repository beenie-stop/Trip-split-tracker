-- Run this whole file in Supabase > SQL Editor
create extension if not exists pgcrypto;

-- PROFILES -------------------------------------------------
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  created_at timestamptz default now()
);

create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles(id, name)
  values (new.id, coalesce(new.raw_user_meta_data->>'name', split_part(new.email,'@',1)))
  on conflict do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute function public.handle_new_user();

-- TABLES ---------------------------------------------------
create table if not exists public.trips (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  code text unique not null,
  currency text default '₹',
  cover_url text,
  status text default 'active',
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz default now()
);

create table if not exists public.members (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  user_id uuid references auth.users(id) on delete set null,
  name text not null,
  upi_id text,
  created_at timestamptz default now()
);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  title text not null,
  amount numeric(12,2) not null check (amount > 0),
  category text default 'Other',
  paid_by uuid not null references public.members(id),
  expense_date date default current_date,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.expense_splits (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  expense_id uuid not null references public.expenses(id) on delete cascade,
  member_id uuid not null references public.members(id),
  share_amount numeric(12,2) not null
);

create table if not exists public.settlements (
  id uuid primary key default gen_random_uuid(),
  trip_id uuid not null references public.trips(id) on delete cascade,
  from_member uuid not null references public.members(id),
  to_member uuid not null references public.members(id),
  amount numeric(12,2) not null,
  method text default 'UPI',
  note text,
  status text default 'paid',
  created_at timestamptz default now()
);

-- HELPER FUNCTIONS -----------------------------------------
create or replace function public.is_trip_member(t uuid) returns boolean
language sql security definer stable set search_path = public as $$
  select exists (select 1 from public.members where trip_id = t and user_id = auth.uid())
$$;

create or replace function public.create_trip(p_name text, p_currency text, p_cover text)
returns uuid language plpgsql security definer set search_path = public as $$
declare v_id uuid; v_code text; v_name text;
begin
  if auth.uid() is null then raise exception 'Not logged in'; end if;
  loop
    v_code := upper(substr(md5(random()::text || clock_timestamp()::text), 1, 6));
    exit when not exists (select 1 from public.trips where code = v_code);
  end loop;
  insert into public.trips(name, code, currency, cover_url, created_by)
  values (p_name, v_code, p_currency, p_cover, auth.uid()) returning id into v_id;
  select name into v_name from public.profiles where id = auth.uid();
  insert into public.members(trip_id, user_id, name) values (v_id, auth.uid(), coalesce(v_name, 'Me'));
  return v_id;
end $$;

create or replace function public.join_trip(p_code text)
returns uuid language plpgsql security definer set search_path = public as $$
declare v_trip uuid; v_name text;
begin
  if auth.uid() is null then raise exception 'Not logged in'; end if;
  select id into v_trip from public.trips where code = upper(trim(p_code));
  if v_trip is null then raise exception 'Invalid trip code'; end if;
  if exists (select 1 from public.members where trip_id = v_trip and user_id = auth.uid()) then
    return v_trip;
  end if;
  select name into v_name from public.profiles where id = auth.uid();
  -- claim a member the creator already added with the same name
  update public.members set user_id = auth.uid()
   where id = (select id from public.members
               where trip_id = v_trip and user_id is null and lower(name) = lower(coalesce(v_name,''))
               limit 1);
  if not found then
    insert into public.members(trip_id, user_id, name) values (v_trip, auth.uid(), coalesce(v_name, 'Friend'));
  end if;
  return v_trip;
end $$;

-- ROW LEVEL SECURITY ---------------------------------------
alter table public.profiles enable row level security;
drop policy if exists "profiles_select" on public.profiles;
drop policy if exists "profiles_update" on public.profiles;
create policy "profiles_select" on public.profiles for select to authenticated using (true);
create policy "profiles_update" on public.profiles for update to authenticated using (id = auth.uid());

alter table public.trips enable row level security;
drop policy if exists "trips_select" on public.trips;
drop policy if exists "trips_update" on public.trips;
create policy "trips_select" on public.trips for select to authenticated using (public.is_trip_member(id));
create policy "trips_update" on public.trips for update to authenticated using (public.is_trip_member(id));

do $$
declare t text;
begin
  foreach t in array array['members','expenses','expense_splits','settlements'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists "%1$s_all" on public.%1$I', t);
    execute format('create policy "%1$s_all" on public.%1$I for all to authenticated using (public.is_trip_member(trip_id)) with check (public.is_trip_member(trip_id))', t);
  end loop;
end $$;

-- STORAGE (trip cover photos) ------------------------------
insert into storage.buckets (id, name, public) values ('trip-covers', 'trip-covers', true)
on conflict (id) do nothing;

drop policy if exists "covers_upload" on storage.objects;
drop policy if exists "covers_read" on storage.objects;
create policy "covers_upload" on storage.objects for insert to authenticated with check (bucket_id = 'trip-covers');
create policy "covers_read" on storage.objects for select using (bucket_id = 'trip-covers');
