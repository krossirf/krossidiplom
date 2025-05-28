-- Создание таблицы ролей
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- Создание таблицы пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы брендов
CREATE TABLE brands (
    brand_id SERIAL PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE
);

-- Создание таблицы кроссовок
CREATE TABLE sneakers (
    sneaker_id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(brand_id),
    model VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    release_year INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы размеров кроссовок
CREATE TABLE sneaker_sizes (
    size_id SERIAL PRIMARY KEY,
    sneaker_id INTEGER REFERENCES sneakers(sneaker_id),
    size DECIMAL(3,1) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    price DECIMAL(10,2) NOT NULL
);

-- Создание таблицы заказов
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы позиций заказа
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    sneaker_id INTEGER REFERENCES sneakers(sneaker_id),
    size_id INTEGER REFERENCES sneaker_sizes(size_id),
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

-- Создание таблицы доставки
CREATE TABLE deliveries (
    delivery_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    delivery_address TEXT NOT NULL,
    delivery_cost DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка базовых ролей
INSERT INTO roles (role_name) VALUES 
('admin'),
('seller'),
('buyer'); 