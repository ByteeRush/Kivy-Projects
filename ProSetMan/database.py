import sqlite3
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from openpyxl import Workbook

class Database:
    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.name = os.path.join(base_dir, "ProSetManAppDB.db")
        
        # Tabloları tek bağlantıda kurarak yabancı anahtar çakışmalarını önlüyoruz
        self.create_all_tables()

    def create_all_tables(self):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            
            # 1. Önce user tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL CHECK(length(trim(username)) > 0),
                    password TEXT NOT NULL CHECK(length(trim(password)) > 0),
                    email TEXT NOT NULL CHECK(length(trim(email)) > 0)
                )
            """)
            
            # 2. Hemen ardından products tablosu (producer_name CHECK hatası düzeltildi)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            producer_name TEXT NOT NULL CHECK(length(trim(producer_name)) > 0),
            product_type TEXT NOT NULL CHECK(length(trim(product_type)) > 0),
            product_name TEXT NOT NULL CHECK(length(trim(product_name)) > 0),
            product_count TEXT NOT NULL CHECK(length(trim(product_count)) > 0),
            product_price TEXT NOT NULL CHECK(length(trim(product_price)) > 0),
            product_total_price TEXT NOT NULL CHECK(length(trim(product_total_price)) > 0),
            product_barcode TEXT,
            product_image TEXT,
            datetime TEXT NOT NULL CHECK(length(trim(datetime)) > 0),
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE)""")
            connection.commit()


    def add_user(self, user_name: str, password: str, email: str) -> bool:
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO user (username, password, email) VALUES (?, ?, ?)", (user_name, password, email))
            connection.commit()
            return True

    def login(self, username: str, password: str):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM user WHERE username = ? AND password = ? ", (username, password))
            user = cursor.fetchone()
            return user[0] if user else None

    def add_product(self, user_id, producer_name, product_type, product_name, count, price, product_total_price, product_barcode, product_image, datetime_str):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""
                    INSERT INTO products (user_id, producer_name, product_type, product_name, product_count, product_price, product_total_price, product_barcode, product_image, datetime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, producer_name, product_type, product_name, count, price, product_total_price, product_barcode, product_image, datetime_str)) # <-- producer_name buraya eklendi!
                connection.commit()
                return True
        except Exception as e:
            print(f"VERİTABANI KAYIT HATASI: {e}")
            return False

    def get_user_products(self, user_id):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            # BURAYA "producer_name" EKLENDİ (Toplam 9 sütun)
            cursor.execute("""
                SELECT id, producer_name, product_name, product_price, product_count, datetime, product_type, product_total_price, product_barcode 
                FROM products 
                WHERE user_id = ?
            """, (user_id,))
            return cursor.fetchall()

    def delete_product(self, user_id, product_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                # Parametreleri tuple olarak ikinci argümana ekledik
                cursor.execute("""DELETE FROM products WHERE id = ? AND user_id = ?""", (int(product_id), user_id))
                
                connection.commit()
                
                # Gerçekten bir satır silindi mi kontrol edelim
                if cursor.rowcount > 0:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Silme Hatası: {e}")
            return False


    def get_product_for_updtae(self, product_id: int):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("SELECT * FROM products WHERE id = ?", (int(product_id),))
            data = cursor.fetchone() 
            return data # Örn: (5, "Kola", 150.0, 100, "12.10.2026", user_id)

    def update_product_item(self, user_id, product_id, producer_name, product_type, p_name, p_count, p_price, product_total_price, p_barcode, p_date):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""
                UPDATE products 
                SET producer_name = ?,
                    product_type = ?,
                    product_name = ?, 
                    product_count = ?, 
                    product_price = ?, 
                    product_total_price = ?,
                    product_barcode = ?,
                    datetime = ?
                WHERE id = ? AND user_id = ?
            """, (producer_name, product_type, p_name, p_count, p_price, product_total_price, p_barcode, p_date, product_id, user_id))
            
            connection.commit()
            return cursor.rowcount > 0












    def filter_products(
        self,
        user_id,
        name=None,
        min_price=None,
        max_price=None,
        start_date=None,
        end_date=None,
        min_count=None,
        max_count=None,
    ):
      with sqlite3.connect(self.name) as connection:
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Sütun isimlerinle (product_name, product_price vb.) birebir eşitledik
        query = (
            "SELECT id, product_name, product_price, product_count, datetime"
            " FROM products WHERE user_id = ?"
        )
        params = [user_id]

        if name:
          query += " AND product_name LIKE ?"
          params.append(f"%{name}%")
        if min_price:
          query += " AND product_price >= ?"
          params.append(float(min_price))
        if max_price:
          query += " AND product_price <= ?"
          params.append(float(max_price))
        if start_date:
          query += " AND datetime >= ?"
          params.append(start_date)
        if end_date:
          query += " AND datetime <= ?"
          params.append(end_date)
        if min_count:
          query += " AND product_count >= ?"
          params.append(int(min_count))
        if max_count:
          query += " AND product_count <= ?"
          params.append(int(max_count))

        cursor.execute(query, params)
        return cursor.fetchall()


    def simple_excel_export(self, custom_data=None):
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Ürünler"

        headers = ["ID", "Kullanıcı ID", "Ürün Adı", "Adet", "Fiyat", "Tarih"]
        ws.append(headers)

        # Eğer dışarıdan filtrelenmiş veri gönderildiyse onu kullan
        if custom_data is not None:
            rows = custom_data
        else:
            # Gönderilmediyse veritabanından tümünü çek
            connection = sqlite3.connect(self.name)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, user_id, product_name, product_count, product_price,"
                " datetime FROM products"
            )
            rows = cursor.fetchall()
            connection.close()

        for row in rows:
            ws.append(row)

        wb.save("benim_urunlerim.xlsx")
        print("Excel başarıyla oluşturuldu!")

    def simple_pdf_export(self, custom_data=None):
        
        doc = SimpleDocTemplate("benim_urunlerim.pdf", pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()

        elements.append(
            Paragraph("<b>Ürün Listesi Raporu</b>", styles["Heading1"])
        )
        elements.append(Spacer(1, 10))

        table_data = [
            ["ID", "Kullanıcı ID", "Ürün Adı", "Adet", "Fiyat", "Tarih"]
        ]

        # Eğer dışarıdan filtrelenmiş veri gönderildiyse onu kullan
        if custom_data is not None:
            rows = custom_data
        else:
            connection = sqlite3.connect(self.name)
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, user_id, product_name, product_count, product_price,"
                " datetime FROM products"
            )
            rows = cursor.fetchall()
            connection.close()

        for row in rows:
            table_data.append([str(item) for item in row])

        col_widths = [40, 60, 165, 80, 90, 100]
        product_table = Table(table_data, colWidths=col_widths)

        table_style = TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#2C3E50"),
            ),  # Başlık arka planı
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.whitesmoke,
            ),  # Başlık yazı rengi
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Ortala
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CCCCCC"),
            ),  # Kenarlık çizgileri
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ])

        product_table.setStyle(table_style)
        elements.append(product_table)

        doc.build(elements)
        print("PDF başarıyla oluşturuldu!")