import cx_Oracle

# Database connection details
DB_USER = "your_user"
DB_PASSWORD = "your_password"
DB_DSN = "your_host:1521/your_service"

# Connect to Oracle
conn = cx_Oracle.connect(DB_USER, DB_PASSWORD, DB_DSN)
cursor = conn.cursor()

# Query to get table names
cursor.execute("""
    SELECT table_name FROM user_tables
""")
tables = [row[0] for row in cursor.fetchall()]

# Query to get columns and types
columns_query = """
    SELECT table_name, column_name, data_type 
    FROM user_tab_columns 
    WHERE table_name = :table
"""

# Query to get foreign keys
foreign_keys_query = """
    SELECT 
        a.table_name, a.column_name, a.constraint_name, c_pk.table_name AS ref_table, 
        c_pk.column_name AS ref_column
    FROM user_cons_columns a
    JOIN user_constraints c ON a.constraint_name = c.constraint_name
    JOIN user_cons_columns c_pk ON c.r_constraint_name = c_pk.constraint_name
    WHERE c.constraint_type = 'R'
    AND a.table_name = :table
"""

# Generate Mermaid ER Diagram Syntax
mermaid_code = ["erDiagram"]

for table in tables:
    # Fetch columns
    cursor.execute(columns_query, {"table": table})
    columns = cursor.fetchall()

    mermaid_code.append(f"    {table} {{")
    for column in columns:
        column_name, data_type = column[1], column[2]
        mermaid_code.append(f"        {data_type} {column_name}")
    mermaid_code.append(f"    }}")

    # Fetch foreign keys
    cursor.execute(foreign_keys_query, {"table": table})
    foreign_keys = cursor.fetchall()

    for fk in foreign_keys:
        mermaid_code.append(f"    {fk[0]} }|--|| {fk[3]} : \"{fk[1]} → {fk[4]}\"")

# Close connections
cursor.close()
conn.close()

# Save to file
with open("mermaid_er_diagram.md", "w") as f:
    f.write("\n".join(mermaid_code))

print("Mermaid ER diagram saved to mermaid_er_diagram.md")