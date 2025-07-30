create table login(
user_name text references customers(user_name),
login_time text not null,
logout_time text not null)

create table password_reset(
user_name text not null,
old_password text not null,
new_password text not null)

create table vendors(
vendor_id serial primary key,
vendor_name text not null,
address text not null,
number text not null,
mail_id text not null,
)

create table category(
category_id serial primary key,
category_name text not null)

create table products(
product_id serial primary key,
category_id integer not null,
product_brand text not null,
product_name json not null,
quantity numeric(10,0) not null,
price numeric(100,0) not null,
features jsonb not null,
vendor_id integer references vendors(vendor_id)
)

create table cart(
cart_id serial primary key,
user_name text references customers (user_name),
product_id integer references products (product_id),
quantity numeric(10,0) not null,
price numeric(100,0) not null)

create table bought_item(
bought_item_id serial primary key,
cart_id integer references cart (cart_id))

create table check_out(
order_id serial primary key,
product_id integer references products(product_id),
quantity numeric(10,0) not null,
price numeric(100,0) not null,
address text not null,
bought_item_id integer references bought_item(bought_item_id)
)

create table delivery(
delivery_id serial primary key,
order_id integer references check_out(order_id),
delivery_date text not null,
delivery_name text not null,
tracking text not null)
