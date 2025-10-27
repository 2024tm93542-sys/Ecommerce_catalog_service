from .db import get_connection

def fetch_products(
    page=1,
    per_page=10,
    category=None,
    price_gt=None,
    price_lt=None,
    sort_by_price=None,
    substring=None
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM catalogue WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM catalogue WHERE 1=1"
    params = []
    count_params = []

    # ---- Filters ----
    if category:
        query += " AND category = %s"
        count_query += " AND category = %s"
        params.append(category)
        count_params.append(category)

    if price_gt is not None:
        query += " AND price >= %s"
        count_query += " AND price >= %s"
        params.append(price_gt)
        count_params.append(price_gt)

    if price_lt is not None:
        query += " AND price <= %s"
        count_query += " AND price <= %s"
        params.append(price_lt)
        count_params.append(price_lt)

    if substring:
        query += " AND name LIKE %s"
        count_query += " AND name LIKE %s"
        pattern = f"%{substring}%"
        params.append(pattern)
        count_params.append(pattern)

    # Always only show active products
    query += " AND is_active = TRUE"
    count_query += " AND is_active = TRUE"

    # ---- Sorting ----
    if sort_by_price in ('asc', 'desc'):
        query += f" ORDER BY price {sort_by_price.upper()}"
    else:
        query += " ORDER BY product_id ASC"

    # ---- Pagination ----
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    # ---- Execute ----
    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()["total"]

    conn.close()
    return rows, total

def create_product(product):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO catalogue (sku, name, category, price, is_active) VALUES (%s,%s,%s,%s,%s)",
        (product.sku, product.name, product.category, product.price, product.is_active)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def update_product(sku, product_data):
    conn = get_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for k, v in product_data.items():
        fields.append(f"{k}=%s")
        values.append(v)
    values.append(sku)
    query = f"UPDATE catalogue SET {', '.join(fields)} WHERE sku=%s"
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()
    return cursor.rowcount

def soft_delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE catalogue SET is_active=FALSE WHERE product_id=%s", (product_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount
