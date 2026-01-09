-- SQL practice website
-- https://pgexercises.com/

-- SELECT / GET

SELECT * FROM customers

SELECT name, email FROM customers

-- SELECT WITH condition

SELECT * FROM customers where id = 7

 -- MULTIPLE VALUES
SELECT * FROM customers where id in (7, 8)

-- pattern match
SELECT * FROM customers where name LIKE '%J%'

-- multiple conditions
SELECT * FROM products 
where price < 100 
AND stock > 50

-- limit records
SELECT * FROM products limit 3

-- ORDER results
SELECT * FROM products ORDER BY price DESC
SELECT * FROM products ORDER BY price ASC

-- COUNT
SELECT COUNT(*) as total_customers from customers

INSERT INTO customers (name, email) VALUES
('Alice Brown', 'alice@example.com');

--JOIN

--INNER JOIN
SELECT * FROM customers as c
INNER JOIN customer_profiles as cp
on c.id = cp.customer_id

--LEFT JOIN
SELECT * FROM customers as c
LEFT JOIN customer_profiles as cp
on c.id = cp.customer_id

-- Find customer with no order
SELECT * FROM customers c
LEFT JOIN orders o on c.id = o.customer_id
WHERE o.id IS NULL

-- AGGREGATE GROUP BY

--  spent data by customer
SELECT
customer_id,
COUNT(*) as order_count,
SUM(total_amount) as total_spent,
AVG(total_amount) as average_spent
FROM orders
group by customer_id

