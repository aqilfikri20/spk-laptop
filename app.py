from flask import Flask,render_template,jsonify,session, request,redirect, url_for
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
app=Flask(__name__)
app.secret_key = 'your_password ' 

cloudinary.config(
    cloud_name='aqilfikri20',
    api_key='912145415255432',
    api_secret='C2XDAVLNiYqV82fmgyIqHS-5gUY'
)

# mysql config

app.config['MYSQL_HOST'] = os.environ.get('hopper.proxy.rlwy.net')
app.config['MYSQL_USER'] = os.environ.get('root')
app.config['MYSQL_PASSWORD'] = os.environ.get('QwOEGFDgDsACGVhqWmDsGxtvAyPqfHpF')
app.config['MYSQL_DB'] = os.environ.get('railway')

mysql = MySQL(app)

@app.route("/tambah")
def tambah():
    return render_template("tambah.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/input_filter")
def input_filter():
    return render_template("input_filter.html")

@app.route("/page_login", methods=["GET", "POST"])
def page_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = mysql.connection.cursor(DictCursor)
        query = "SELECT * FROM table_admin WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        admin = cursor.fetchone()
        cursor.close()
        
        if admin:
            session['logged_in'] = True
            session['user'] = admin['email']
            return redirect(url_for('home'))
        else:  
            return render_template('page_login.html', error="Email atau Password salah!")

    return render_template("page_login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/")
def home():
    search_query = request.args.get('search', '') 
    cursor = mysql.connection.cursor()
    if search_query:
        query = "SELECT * FROM table_laptop WHERE nama LIKE %s"
        cursor.execute(query, ('%' + search_query + '%',)) 
    else:
        query = "SELECT * FROM table_laptop"
        cursor.execute(query)

    column_names = [i[0] for i in cursor.description]
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))
    cursor.close()
    return render_template("index.html", data=data)
   
@app.route('/laptop', methods=['GET', 'POST'])
def laptop():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM table_laptop")  # ambil seluruh data laptop
        column_names = [i[0] for i in cursor.description]
        data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        cursor.close()
        return jsonify(data)
    
    elif request.method == 'POST':
        # Dapatkan data dari form
        nama = request.form['nama']
        kategori = request.form['kategori']
        processor = request.form['processor']
        ram = request.form['ram']
        storage = request.form['storage']
        layar = request.form['layar']
        baterai = request.form['baterai']
        harga = request.form['harga']
        review_design = request.form['review_design']
        keunggulan = request.form['keunggulan']
        
        # Dapatkan file gambar dari form
        if 'img' not in request.files:
            return 'No image uploaded', 400
        file = request.files['img']

        if file.filename == '':
            return 'No selected file', 400

        if file:
            # Upload gambar ke Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            img_url = upload_result['secure_url']  # Dapatkan URL gambar

            # Simpan data ke dalam database
            cursor = mysql.connection.cursor()
            sql = """INSERT INTO table_laptop 
                     (nama, kategori, processor, ram, storage, layar,baterai, harga, img, review_design, keunggulan) 
                     VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            val = (nama, kategori, processor, ram, storage, layar,baterai, harga, img_url, review_design, keunggulan)
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('home'))

@app.route('/edit_laptop/<int:id>', methods=['GET', 'POST'])
def edit_laptop(id):
    cursor = mysql.connection.cursor(DictCursor)
    if request.method == 'GET':
        # Ambil data laptop berdasarkan ID dari database
        query = "SELECT * FROM table_laptop WHERE id = %s"
        cursor.execute(query, (id,))
        laptop = cursor.fetchone()
        cursor.close()
        # Kirim data laptop ke template edit_laptop.html
        return render_template('edit_laptop.html', laptop=laptop)

    elif request.method == 'POST':
        # Ambil data dari form edit
        nama = request.form['nama']
        kategori = request.form['kategori']
        processor = request.form['processor']
        ram = request.form['ram']
        storage = request.form['storage']
        layar = request.form['layar']
        baterai = request.form['baterai']
        harga = request.form['harga']
        review_design = request.form['review_design']
        keunggulan = request.form['keunggulan']
        
        # Cek apakah ada gambar baru yang diupload
        if 'img' in request.files:
            file = request.files['img']
            if file and file.filename != '':
                # Upload gambar baru ke Cloudinary
                upload_result = cloudinary.uploader.upload(file)
                img_url = upload_result['secure_url']
            else:
                img_url = request.form['existing_img']  # Jika tidak ada gambar baru, pakai gambar yang sudah ada

        # Update data laptop di database
        query = """UPDATE table_laptop 
                   SET nama=%s, kategori=%s, processor=%s, ram=%s, storage=%s, layar=%s,baterai=%s, harga=%s, img=%s, review_design=%s, keunggulan=%s
                   WHERE id=%s"""
        cursor.execute(query, (nama, kategori, processor, ram, storage, layar, baterai, harga, img_url, review_design, keunggulan,id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))
 

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
    query = "SELECT * FROM table_laptop WHERE kategori='Programer'"
    cursor.execute(query)
    column_names = [i[0] for i in cursor.description]
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))
    cursor.close()
    return render_template("getprogrammer.html", data=data)

@app.route('/delete_laptop/<int:id>', methods=['POST'])
def delete_laptop(id):
    # Membuka koneksi database
    cursor = mysql.connection.cursor()

    # Menghapus item dari database berdasarkan ID
    sql = "DELETE FROM table_laptop WHERE id = %s"
    cursor.execute(sql, (id,))
    mysql.connection.commit()
    cursor.close()
    # Redirect ke halaman index setelah penghapusan
    return redirect(url_for('home'))

@app.route('/detail_laptop/<int:id>', methods=['GET'])
def detail_laptop(id):
    cursor = mysql.connection.cursor(DictCursor)
    # Query untuk mendapatkan detail laptop berdasarkan id
    query = "SELECT * FROM table_laptop WHERE id = %s"
    cursor.execute(query, (id,))
    laptop = cursor.fetchone()  # Ambil hanya satu hasil
    cursor.close()

    # Render template detail_laptop.html dengan data laptop
    return render_template('detail_laptop.html', laptop=laptop)

@app.route("/filter_laptop", methods=["GET"])
def filter_laptop():

    search_query = request.args.get("search", "")
    kategori = request.args.get("kategori", "")
    processor = request.args.get("processor", "")
    ram = request.args.get("ram", "")
    storage = request.args.get("storage", "")
    layar = request.args.get("layar", "")
    baterai_min = request.args.get("baterai_min", None) 
    harga_min = request.args.get("harga_min", None)  
    harga_max = request.args.get("harga_max", None)

    query = "SELECT * FROM table_laptop WHERE 1=1"
    params = []

    if search_query:
        query += " AND nama LIKE %s"
        params.append(f"%{search_query}%")
    if kategori:
        query += " AND kategori LIKE %s"
        params.append(f"%{kategori}%")
    if processor:
        query += " AND processor LIKE %s"
        params.append(f"%{processor}%")
    if ram:
        query += " AND ram LIKE %s"
        params.append(f"%{ram}%")
    if storage:
        query += " AND storage LIKE %s"
        params.append(f"%{storage}%")

    if layar:
        query += " AND layar LIKE %s"
        params.append(f"%{layar}%")

    if baterai_min:
        query += " AND baterai >= %s" 
        params.append(baterai_min)

    if harga_min:
        query += " AND harga >= %s" 
        params.append(harga_min)
    if harga_max:
        query += " AND harga <= %s"  
        params.append(harga_max)

    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute(query, params)
    data = cursor.fetchall()
    cursor.close()
    return render_template("filter_laptop.html", data=data, search_query=search_query)

@app.route("/rekomendasi")
def rekomendasi():
    return render_template("rekomendasi.html")

@app.route('/hasil_rekomendasi', methods=['GET'])
def hasil_rekomendasi():
# Ambil semua laptop dari DB
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM table_laptop")
    laptops = cursor.fetchall()
    cursor.close()

    processor_score = {
    'Intel Core i3': 3,
    'Intel Core i5': 5,
    'Intel Core i7': 7,
    'Intel Core i9': 9,
    'AMD Ryzen 3': 3,
    'AMD Ryzen 5': 5,
    'AMD Ryzen 7': 7,
    'AMD Ryzen 9': 9
}

    bobot = {
        'processor': int(request.args.get('processor', 1)),
        'ram': int(request.args.get('ram', 1)),
        'storage': int(request.args.get('storage', 1)),
        'layar': int(request.args.get('layar', 1)),
        'baterai': int(request.args.get('baterai', 1)),
        'harga': int(request.args.get('harga', 1)),
    }
    total_bobot = sum(bobot.values())
    for k in bobot:
        bobot[k] = bobot[k] / total_bobot

    max_vals = {
        'processor': max(processor_score.get(l['processor'], 0) for l in laptops),
        'ram': max(int(l['ram']) for l in laptops),
        'storage': max(int(l['storage']) for l in laptops),
        'layar': max(float(l['layar']) for l in laptops),
        'baterai': max(int(l['baterai']) for l in laptops),
    }
    min_harga = min(int(l['harga']) for l in laptops)

    hasil_saw = []
    for l in laptops:
        norm_processor = processor_score.get(l['processor'], 0) / max_vals['processor'] if max_vals['processor'] else 0
        norm_ram = int(l['ram']) / max_vals['ram'] if max_vals['ram'] else 0
        norm_storage = int(l['storage']) / max_vals['storage'] if max_vals['storage'] else 0
        norm_layar = float(l['layar']) / max_vals['layar'] if max_vals['layar'] else 0
        norm_baterai = int(l['baterai']) / max_vals['baterai'] if max_vals['baterai'] else 0
        norm_harga = min_harga / int(l['harga']) if int(l['harga']) != 0 else 0

        # Tambahkan nilai-nilai normalisasi ke dalam data laptop untuk referensi
        l['normalisasi'] = {
            'processor': round(norm_processor, 4),
            'ram': round(norm_ram, 4),
            'storage': round(norm_storage, 4),
            'layar': round(norm_layar, 4),
            'baterai': round(norm_baterai, 4),
            'harga': round(norm_harga, 4),
        }

        skor = (
            norm_processor * bobot['processor'] +
            norm_ram * bobot['ram'] +
            norm_storage * bobot['storage'] +
            norm_layar * bobot['layar'] +
            norm_baterai * bobot['baterai'] +
            norm_harga * bobot['harga']
        )
        l['skor'] = round(skor, 4)
        hasil_saw.append(l)

    hasil_saw.sort(key=lambda x: x['skor'], reverse=True)
    return render_template("hasil_rekomendasi.html", data=hasil_saw[:10])


@app.template_filter('rupiah')
def rupiah_format(value):
    return f"Rp{value:,.0f}".replace(",", ".")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
