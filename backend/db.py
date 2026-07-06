import mysql.connector

try:
    # Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root123",
        database="userdb"
    )

    # Create a cursor
    cursor = db.cursor()

    print("✅ Connected to MySQL Successfully!")

except mysql.connector.Error as err:
    print("❌ Database Connection Failed!")
    print(err)