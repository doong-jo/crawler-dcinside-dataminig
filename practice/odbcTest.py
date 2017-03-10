import odbc

connect = odbc.odbc('Test')

db = connect.cursor()

db.execute('select * from test.new_table')

table = db.fetchall()
print (table)
