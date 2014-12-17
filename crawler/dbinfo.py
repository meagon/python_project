



import sqlite3
import sys
import os


DB_PATH = sys.argv[1]

con = sqlite3.connect(DB_PATH)

cur = con.cursor()

cur.execute("SELECT count(*) FROM urls")

a = cur.fetchall()
print(a)
con.close()


