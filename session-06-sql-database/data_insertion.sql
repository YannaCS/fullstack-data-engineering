-- Insert customers
INSERT INTO customers (name, email) VALUES
('John Doe', 'john@example.com'),
('Jane Smith', 'jane@example.com'),
('Bob Wilson', 'bob@example.com');

-- Insert customer profiles (1-to-1)
INSERT INTO customer_profiles (customer_id, phone, address, date_of_birth) VALUES
(1, '555-0101', '123 Main St, New York, NY', '1990-05-15'),
(2, '555-0102', '456 Oak Ave, Boston, MA', '1985-08-22'),
(3, '555-0103', '789 Pine Rd, Chicago, IL', '1992-03-10');

-- Insert products
INSERT INTO products (name, price, stock) VALUES
('Laptop', 999.99, 50),
('Mouse', 29.99, 200),
('Keyboard', 79.99, 150),
('Monitor', 299.99, 75);

-- Insert orders
INSERT INTO orders (customer_id, total_amount, status) VALUES
(1, 1029.98, 'completed'),
(1, 79.99, 'pending'),
(2, 999.99, 'completed'),
(3, 329.98, 'shipped');

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 999.99),  -- Order 1: 1 Laptop
(1, 2, 1, 29.99),   -- Order 1: 1 Mouse
(2, 3, 1, 79.99),   -- Order 2: 1 Keyboard
(3, 1, 1, 999.99),  -- Order 3: 1 Laptop
(4, 2, 2, 29.99),   -- Order 4: 2 Mice
(4, 4, 1, 299.99);  -- Order 4: 1 Monitor