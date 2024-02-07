import sys
import psycopg2
from faker import Faker
from datetime import datetime

def create_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="user",
        password="password",
        host="localhost",
        port="5432"
    )

def create_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS orders;")
        conn.commit()

def create_orders_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders.orders (
                orderID SERIAL PRIMARY KEY,
                firstName VARCHAR(100) NOT NULL,
                lastName VARCHAR(100) NOT NULL,
                address VARCHAR(500) NOT NULL,
                orderDate TIMESTAMP WITH TIME ZONE
            );
        """)
        conn.commit()

def generate_orders_data(n):
    fake = Faker()
    return [
        (fake.first_name(), fake.last_name(), fake.address(), fake.date_time_this_decade())
        for _ in range(n)
    ]

def insert_into_orders(conn, orders_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO orders.orders (firstName, lastName, address, orderDate)
            VALUES (%s, %s, %s, %s);
        """, orders_data)
        conn.commit()

def create_products_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders.products (
                productID SERIAL PRIMARY KEY,
                productName VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                inStock BOOLEAN DEFAULT true
            );
        """)
        conn.commit()

def generate_products_data(n):
    fake = Faker()
    return [
        (fake.word(), fake.text(max_nb_chars=200), round(fake.random_number(digits=5) * 0.01, 2), fake.boolean())
        for _ in range(n)
    ]

def insert_into_products(conn, products_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO orders.products (productName, description, price, inStock)
            VALUES (%s, %s, %s, %s);
        """, products_data)
        conn.commit()

def create_order_details_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders.order_details (
                orderDetailID SERIAL PRIMARY KEY,
                orderID INT REFERENCES orders.orders(orderID),
                productID INT REFERENCES orders.products(productID),
                quantity INT NOT NULL,
                pricePerUnit DECIMAL(10, 2) NOT NULL
            );
        """)
        conn.commit()

def generate_order_details_data(n, order_id_range, product_id_range):
    fake = Faker()
    return [
        (fake.random_int(min=order_id_range[0], max=order_id_range[1]),
         fake.random_int(min=product_id_range[0], max=product_id_range[1]),
         fake.random_number(digits=2),
         round(fake.random_number(digits=5) * 0.01, 2))
        for _ in range(n)
    ]

def insert_into_order_details(conn, order_details_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO orders.order_details (orderID, productID, quantity, pricePerUnit)
            VALUES (%s, %s, %s, %s);
        """, order_details_data)
        conn.commit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python seed_database.py <number_of_rows>")
        sys.exit(1)

    num_rows = int(sys.argv[1])
    conn = create_connection()
    create_schema(conn)  # Ensure the schema exists before creating tables
    create_orders_table(conn)
    orders_data = generate_orders_data(num_rows)
    insert_into_orders(conn, orders_data)
    create_products_table(conn)
    products_data = generate_products_data(num_rows)
    insert_into_products(conn, products_data)
    create_order_details_table(conn)
    order_details_data = generate_order_details_data(num_rows, (1, num_rows + 1), (1, num_rows + 1))
    insert_into_order_details(conn, order_details_data)
    conn.close()
    print(f"Inserted {num_rows} rows into 'orders.orders, orders.products, and orders.order_details' tables.")

if __name__ == "__main__":
    main()

