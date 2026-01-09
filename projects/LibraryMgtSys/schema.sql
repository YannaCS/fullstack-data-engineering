drop schema if exists LibraryMgtSys cascade;
create schema if not exists LibraryMgtSys;

set search_path to LibraryMgtSys;
/*
PostgreSQL uses CASCADE to drop schema with all its objects
PostgreSQL uses SET search_path instead of USE
*/

create table library_items (
	id serial primary key,       -- mysql: id INTEGER PRIMARY KEY AUTO_INCREMENT
	title varchar(255) not null,
	creator varchar(255) not null,
	item_type varchar(20) not null,
	total_copies integer not null default 1,
	available_copies integer not null default 1,
	created_at timestamp default current_timestamp,
	constraint check_copies check (available_copies  <= total_copies),
	constraint check_type check (item_type in ('book', 'dvd'))
);

create table books (
	id integer primary key,
	isbn varchar(20) not null unique,
	num_pages integer not null,
	constraint fk_books_id foreign key (id)
		references library_items(id)
		on update cascade
		on delete cascade
);

create table dvds (
	id integer primary key,
	duration_minutes integer not null,
	genre varchar(50) not null,
	constraint fk_dvds_id foreign key (id)
		references library_items(id)
		on update cascade
		on delete cascade
);

create table memberships (
	id serial primary key,
	member_id integer not null unique,
	membership_type varchar(20) not null check (membership_type in ('regular', 'premium')),
	borrow_limit integer not null,
	expiry_date date,
	created_at timestamp default current_timestamp,
	updated_at timestamp default current_timestamp,
	constraint check_expiry_date check (
		(membership_type = 'regular' and expiry_date is null) 
		or
		(membership_type = 'premium' and expiry_date is not null)
	)
);

create table members (
	id serial primary key,
	name varchar(255) not null,
	email varchar(255) not null unique,
	membership_id integer not null,
	created_at timestamp default current_timestamp,
	constraint fk_members_membership_id foreign key (membership_id)
		references memberships(id)
		on update cascade 
		on delete restrict
);

-- Add foreign key from memberships to members (circular reference)
alter table memberships
add constraint fk_memberships_member foreign key (member_id)
		references members(id)
		on update cascade
		on delete cascade;


create table borrowed_items (
	id serial primary key,
	member_id integer not null,
	item_id integer not null,
	borrow_date timestamp default current_timestamp,
	return_date timestamp,
	status varchar(20) not null default 'borrowed' check (status in ('borrowed', 'returned')),
	constraint fk_borrowed_member foreign key (member_id)
		references members(id)
		on update cascade 
		on delete  cascade,
	constraint fk_borrowed_item foreign key (item_id)
		references library_items(id)
		on update cascade
		on delete cascade 
);

create table waiting_list (
	id serial primary key,
	member_id integer not null,
	item_id integer not null,
	joined_at timestamp default current_timestamp,
	constraint fk_waiting_member foreign key (member_id)
		references members(id)
		on update cascade
		on delete cascade,
	constraint fk_waiting_item foreign key (item_id)
		references library_items(id)
		on update cascade
		on delete cascade,
	constraint unique_waiting_member_item unique (member_id, item_id)
);

create table notifications (
	id serial primary key,
	member_id integer not null,
	message text not null,
	is_read boolean default false,
	created_at timestamp default current_timestamp,
	constraint fk_notifications_member foreign key (member_id)
		references members(id)
		on update cascade 
		on delete cascade 
);

-- Insert library items (books first)
INSERT INTO library_items (title, creator, item_type, total_copies, available_copies) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 'book', 3, 2),
('To Kill a Mockingbird', 'Harper Lee', 'book', 2, 2),
('1984', 'George Orwell', 'book', 4, 3),
('Pride and Prejudice', 'Jane Austen', 'book', 2, 1),
('The Catcher in the Rye', 'J.D. Salinger', 'book', 3, 3);

-- Insert library items (DVDs)
INSERT INTO library_items (title, creator, item_type, total_copies, available_copies) VALUES
('Inception', 'Christopher Nolan', 'dvd', 2, 1),
('The Shawshank Redemption', 'Frank Darabont', 'dvd', 3, 2),
('Pulp Fiction', 'Quentin Tarantino', 'dvd', 2, 0),
('The Matrix', 'Wachowski Sisters', 'dvd', 3, 3),
('Interstellar', 'Christopher Nolan', 'dvd', 2, 2);

-- Insert books details
INSERT INTO books (id, isbn, num_pages) VALUES
(1, '978-0-7432-7356-5', 180),
(2, '978-0-06-112008-4', 324),
(3, '978-0-452-28423-4', 328),
(4, '978-0-14-143951-8', 432),
(5, '978-0-316-76948-0', 234);

-- Insert DVDs details
INSERT INTO dvds (id, duration_minutes, genre) VALUES
(6, 148, 'Sci-Fi'),
(7, 142, 'Drama'),
(8, 154, 'Crime'),
(9, 136, 'Sci-Fi'),
(10, 169, 'Sci-Fi');

-- Temporarily drop the foreign key constraint from memberships to members
ALTER TABLE memberships DROP CONSTRAINT fk_memberships_member;

-- Insert memberships (with member_id that doesn't exist yet)
INSERT INTO memberships (member_id, membership_type, borrow_limit, expiry_date) VALUES
(1, 'regular', 3, NULL),
(2, 'premium', 5, '2026-12-31'),
(3, 'premium', 5, '2026-06-30'),
(4, 'regular', 3, NULL),
(5, 'premium', 5, '2026-09-15'),
(6, 'regular', 3, NULL);

-- Insert members
INSERT INTO members (name, email, membership_id) VALUES
('Alice Johnson', 'alice.johnson@email.com', 1),
('Bob Smith', 'bob.smith@email.com', 2),
('Carol Davis', 'carol.davis@email.com', 3),
('David Wilson', 'david.wilson@email.com', 4),
('Emma Brown', 'emma.brown@email.com', 5),
('Frank Miller', 'frank.miller@email.com', 6);

-- Re-add the foreign key constraint from memberships to members
ALTER TABLE memberships
ADD CONSTRAINT fk_memberships_member FOREIGN KEY (member_id)
    REFERENCES members(id)
    ON UPDATE CASCADE
    ON DELETE CASCADE;

-- Insert borrowed items
INSERT INTO borrowed_items (member_id, item_id, borrow_date, return_date, status) VALUES
(1, 1, current_timestamp - interval '5 days', NULL, 'borrowed'),
(2, 6, current_timestamp - interval '3 days', NULL, 'borrowed'),
(3, 4, current_timestamp - interval '10 days', current_timestamp - interval '2 days', 'returned'),
(4, 3, current_timestamp - interval '7 days', NULL, 'borrowed'),
(5, 7, current_timestamp - interval '4 days', NULL, 'borrowed'),
(1, 2, current_timestamp - interval '15 days', current_timestamp - interval '8 days', 'returned'),
(6, 8, current_timestamp - interval '2 days', NULL, 'borrowed'),
(6, 8, current_timestamp - interval '1 day', NULL, 'borrowed');

-- Insert waiting list entries
INSERT INTO waiting_list (member_id, item_id, joined_at) VALUES
(3, 8, current_timestamp - interval '2 days'),
(4, 8, current_timestamp - interval '1 day'),
(5, 4, current_timestamp - interval '3 hours'),
(2, 1, current_timestamp - interval '1 day');

-- Insert notifications
INSERT INTO notifications (member_id, message, is_read, created_at) VALUES
(1, 'Your borrowed item "The Great Gatsby" is due in 2 days', false, current_timestamp - interval '1 day'),
(2, 'The item "Inception" you borrowed is due tomorrow', false, current_timestamp - interval '6 hours'),
(3, 'Thank you for returning "Pride and Prejudice"', true, current_timestamp - interval '2 days'),
(4, 'Reminder: "1984" is due in 3 days', false, current_timestamp - interval '12 hours'),
(5, 'Your premium membership will expire on 2026-09-15', false, current_timestamp - interval '1 day'),
(6, 'All copies of "Pulp Fiction" are currently borrowed. You are #1 on the waiting list.', false, current_timestamp - interval '2 days'),
(3, 'The item "Pulp Fiction" you are waiting for is still unavailable', true, current_timestamp - interval '1 day'),
(2, 'Your waiting list request for "The Great Gatsby" has been noted', true, current_timestamp - interval '1 day');