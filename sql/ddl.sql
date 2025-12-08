-- DDL for Newton Smart Home app
-- Run with: psql "<connection_string>" -f sql/ddl.sql

-- products
create table if not exists products (
  id bigint generated always as identity primary key,
  device text not null,
  description text,
  sku text,
  unit_price numeric(12,2) default 0.00,
  warranty text,
  image_path text,
  image_base64 text,
  created_at timestamptz default now()
);
create index if not exists idx_products_sku on products(sku);
create index if not exists idx_products_name on products(lower(device));

-- customers
create table if not exists customers (
  id bigint generated always as identity primary key,
  name text not null,
  phone text,
  email text,
  address text,
  created_at timestamptz default now()
);
create index if not exists idx_customers_phone on customers(phone);

-- quotations
create table if not exists quotations (
  id bigint generated always as identity primary key,
  quote_number text unique,
  customer_id bigint references customers(id) on delete set null,
  user_id bigint,
  subtotal numeric(14,2) default 0.00,
  installation_fee numeric(14,2) default 0.00,
  total_amount numeric(14,2) default 0.00,
  status text,
  notes text,
  created_at timestamptz default now()
);
create index if not exists idx_quotations_quote_number on quotations(quote_number);

-- quotation items
create table if not exists quotation_items (
  id bigint generated always as identity primary key,
  quotation_id bigint not null references quotations(id) on delete cascade,
  product_id bigint references products(id) on delete set null,
  description text,
  quantity numeric(12,3) default 0,
  unit_price numeric(12,2) default 0.00,
  line_total numeric(14,2) default 0.00,
  warranty text,
  created_at timestamptz default now()
);
create index if not exists idx_qitems_quotation_id on quotation_items(quotation_id);

-- users (optional)
create table if not exists users (
  id bigint generated always as identity primary key,
  name text not null,
  pin text not null,
  role text,
  allowed_pages jsonb,
  created_at timestamptz default now()
);
create index if not exists idx_users_name on users(lower(name));

-- exports/documents (track generated files)
create table if not exists exports (
  id bigint generated always as identity primary key,
  quotation_id bigint references quotations(id) on delete cascade,
  export_type text,
  file_path text,
  metadata jsonb,
  created_at timestamptz default now()
);
