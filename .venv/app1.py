from flask import Flask,render_template,jsonify, request
from flask_mysqldb import MySQL
app=Flask(__name__)

# mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'laptops_db'
mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")
   
@app.route('/laptop', methods=['GET', 'POST'])
def laptop():
    if request.method == 'GET':
        # koneksi ke database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM table_laptop")  # ambil seluruh data laptop
        column_names = [i[0] for i in cursor.description]
        data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(data)
    
    elif request.method == 'POST':
        nama = request.json['nama']
        kategori = request.json['kategori']
        processor = request.json['processor']
        ram = request.json['ram']
        storage = request.json['storage']
        layar = request.json['layar']
        harga = request.json['harga']
        img = request.json['img']
        # koneksi ke database
        cursor = mysql.connection.cursor()
        sql = "INSERT INTO table_laptop (nama,kategori,processor,ram,storage, layar, harga,img) VALUES (%s, %s, %s,%s, %s, %s,%s, %s)"
        val = (nama,kategori,processor,ram,storage,layar,harga,img)
        cursor.execute(sql, val)
        mysql.connection.commit()
        return jsonify({'message':'data berhasil ditambah'})
        cursor.close()

@app.route('/delete_laptop', methods=['DELETE'])
def delete_laptop():
    if 'id' in request.args:
       cursor = mysql.connection.cursor()
       sql = "DELETE FROM table_laptop WHERE id = %s"
       val = (request.args['id'],)
       cursor.execute(sql, val)  
       mysql.connection.commit()
       return jsonify({'message':'data berhasil dihapus'})
       cursor.close()

@app.route('/edit_laptop', methods=['PUT'])
def edit_laptop():
    if 'id' in request.args:
        data = request.get_json()
        cursor = mysql.connection.cursor()
        sql = "UPDATE table_laptop SET nama=%s, kategori=%s,processor=%s,ram=%s,storage=%s, layar=%s, harga=%s,img=%s WHERE id=%s"
        val = (data['nama'],data['kategori'], data['processor'], data['ram'], data['storage'], data['layar'], data['harga'], data['img'], request.args['id'],)
        cursor.execute(sql, val)  
        mysql.connection.commit()
        return jsonify({'message':'data berhasil diubah'})
        cursor.close()

@app.route('/getoffice', methods=['GET'])
def getoffice():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM table_laptop WHERE kategori='Office'"
    cursor.execute(query)
    column_names = [i[0] for i in cursor.description]
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))
    cursor.close()
    return render_template("getoffice.html", data=data)

@app.route('/getgaming', methods=['GET'])
def getgaming():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM table_laptop WHERE kategori='Gaming'"
    cursor.execute(query)
    column_names = [i[0] for i in cursor.description]
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))
    cursor.close()
    return render_template("getgaming.html", data=data)

@app.route('/getprogrammer', methods=['GET'])
def getprogrammer():
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM table_laptop WHERE kategori='Programmer'"
    cursor.execute(query)
    column_names = [i[0] for i in cursor.description]
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))
    cursor.close()
    return render_template("getprogrammer.html", data=data)

@app.route("/tambah")
def tambah():
    return render_template("tambah.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)