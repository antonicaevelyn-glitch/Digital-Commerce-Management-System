from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/products")
def products():
    connection = get_db_connection()
    products = connection.execute(
        "SELECT * FROM products"
    ).fetchall()
    connection.close()

    return render_template("products.html", products=products)


@app.route("/add_product", methods=("GET", "POST"))
def add_product():

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO products
            (name, category, price, stock, description)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, stock, description))

        connection.commit()
        connection.close()

        return redirect("/products")

    return render_template("add_product.html")
@app.route("/edit_product/<int:id>", methods=("GET", "POST"))
def edit_product(id):

    connection = get_db_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        price = request.form["price"]
        stock = request.form["stock"]
        description = request.form["description"]

        connection.execute("""
            UPDATE products
            SET name = ?, category = ?, price = ?, stock = ?, description = ?
            WHERE id = ?
        """, (name, category, price, stock, description, id))

        connection.commit()
        connection.close()

        return redirect("/products")

    connection.close()

    return render_template("edit_product.html", product=product)
@app.route("/delete_product/<int:id>")
def delete_product(id):


    connection = get_db_connection()

    connection.execute(
        "DELETE FROM products WHERE id = ?",
        (id,)
    )
       

    connection.commit()
    connection.close()

    return redirect("/products")
@app.route("/orders")
def orders():

    connection = get_db_connection()

    orders = connection.execute(
        "SELECT * FROM orders"
    ).fetchall()

    connection.close()

    return render_template("orders.html", orders=orders)
@app.route("/add_order", methods=("GET", "POST"))
def add_order():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        product_name = request.form["product_name"]
        quantity = int(request.form["quantity"])
        total_price = request.form["total_price"]
        status = request.form["status"]

        connection = get_db_connection()

        # Add the order
        connection.execute("""
            INSERT INTO orders
            (customer_name, product_name, quantity, total_price, status)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_name, product_name, quantity, total_price, status))

        # Reduce product stock
        connection.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE name = ?
        """, (quantity, product_name))

        connection.commit()
        connection.close()

        return redirect("/orders")

    return render_template("add_order.html")
@app.route("/edit_order/<int:id>", methods=("GET", "POST"))
def edit_order(id):
    connection = get_db_connection()

    order = connection.execute(
        "SELECT * FROM orders WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        product_name = request.form["product_name"]
        quantity = request.form["quantity"]
        total_price = request.form["total_price"]
        status = request.form["status"]

        connection.execute("""
            UPDATE orders
            SET customer_name = ?, product_name = ?, quantity = ?,
                total_price = ?, status = ?
            WHERE id = ?
        """, (customer_name, product_name, quantity,
              total_price, status, id))

        connection.commit()
        connection.close()

        return redirect("/orders")

    connection.close()

    return render_template("edit_order.html", order=order)


@app.route("/delete_order/<int:id>")
def delete_order(id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM orders WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/orders")
@app.route("/ai", methods=("GET", "POST"))
def ai():
    description = ""

    if request.method == "POST":
        product_name = request.form["product_name"]
        category = request.form["category"]
        features = request.form["features"]

        description = (
            f"{product_name} is a reliable {category} product "
            f"designed to provide excellent value and convenience. "
            f"Key features include {features}. "
            f"It is suitable for customers looking for quality, "
            f"performance, and ease of use."
        )

    return render_template("ai.html", description=description)
@app.route("/reports")
def reports():
    connection = get_db_connection()

    total_products = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    total_orders = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    total_stock = connection.execute(
        "SELECT COALESCE(SUM(stock), 0) FROM products"
    ).fetchone()[0]

    total_sales = connection.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_orders=total_orders,
        total_stock=total_stock,
        total_sales=total_sales
    )

if __name__ == "__main__":
    create_database()
    app.run(debug=True)