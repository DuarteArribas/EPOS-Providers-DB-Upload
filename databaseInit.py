import sqlite3

# Global variables
DATABASE = "db/detectFiles.db"

# Open database connection
con = sqlite3.connect(DATABASE)
cur = con.cursor()

# Create table
cur.execute("CREATE TABLE previousFiles(filename VARCHAR PRIMARY KEY)")