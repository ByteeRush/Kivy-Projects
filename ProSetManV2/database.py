import sqlite3
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from openpyxl import Workbook
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # <-- ParagraphStyle buraya eklenecek!
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from kivy.utils import platform

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
            company_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            product_type TEXT,
            product_count TEXT,
            product_price TEXT,
            product_total_price TEXT,
            product_barcode TEXT,
            product_date TEXT,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES company (id) ON DELETE CASCADE)""")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            company_name TEXT NOT NULL CHECK(length(trim(company_name)) > 0),
            company_number TEXT,
            company_person TEXT,
            company_sector TEXT,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE)""")


            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    company_id INTEGER NOT NULL,
                    current_stock_status TEXT NOT NULL,
                    current_stock_notes TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
                    FOREIGN KEY (company_id) REFERENCES company (id) ON DELETE CASCADE
                )
            """)


            connection.commit()

 
    def add_company(self,user_id,name , number,person,sector):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""
            INSERT INTO company (user_id, company_name,company_number,company_person,company_sector)VALUES (?, ?, ?, ?, ?)""",(user_id, name, number, person,sector)) 
                connection.commit()
                return True
        except Exception as e:
            print(f"VERİTABANI KAYIT HATASI: {e}")
            return False

    def get_companys(self, user_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""SELECT * FROM company  WHERE user_id = ?""", (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print("Veri Tabanı Hatası : ",e)

    def delete_company(self,user_id,company_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                # Parametreleri tuple olarak ikinci argümana ekledik
                cursor.execute("""DELETE FROM company WHERE id = ? AND user_id = ?""", (int(company_id), user_id))
                connection.commit()
        except Exception as e:
            print("Veri Tabanı Hatası : ",e)

    def update_company(self, company_id, user_id, name, number, person, sector):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""UPDATE company SET company_name = ?, company_number = ?, company_person = ?, company_sector = ? WHERE id = ? AND user_id = ?
                """, (name, number, person, sector, int(company_id), user_id))
                connection.commit()
                
                print(f"Güncellenen Satır Sayısı: {cursor.rowcount}")
                return cursor.rowcount > 0
        except Exception as e:
            print("Veri Tabanı Hatası:", e)
            return False

    def get_company_id_name_list(self, user_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("SELECT id, company_name FROM company WHERE user_id = ?", (user_id,))
                rows = cursor.fetchall()
                return rows # [(1, "Firma A"), (2, "Firma B"), ...] şeklinde döner
        except Exception as e:
            print("Veritabanı Hatası:", e)
            return []


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

    
    
    def add_product(self, company_id, user_id, product_name, product_type, product_count, product_price, product_total_price, product_barcode, product_date):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                # 1. Ürünü veritabanına ekle
                cursor.execute("""
                    INSERT INTO products (
                        user_id, company_id, product_name, product_type, 
                        product_count, product_price, product_total_price, 
                        product_barcode, product_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, 
                    company_id, 
                    product_name, 
                    product_type, 
                    product_count, 
                    product_price, 
                    product_total_price, 
                    product_barcode, 
                    product_date
                ))
                connection.commit()

                # 2. Log için Kullanıcı adını ve Firma adını veritabanından çekelim
                cursor.execute("SELECT username FROM user WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                username = user_row[0] if user_row else f"ID:{user_id}"

                cursor.execute("SELECT company_name FROM company WHERE id = ?", (company_id,))
                comp_row = cursor.fetchone()
                company_name = comp_row[0] if comp_row else f"ID:{company_id}"

                # 3. Kimin kime ne eklediğini net bir şekilde konsola basalım
                print(f"🚀 [KAYIT BAŞARILI] '{username}' adlı kullanıcı, '{company_name}' adlı firmaya -> '{product_name}' ({product_count} adet) ürününü ekledi!")
                return True
                
        except Exception as e:
            print(f"❌ Ürün Ekleme Hatası: {e}")
            return False
  
    def get_user_products(self, user_id, company_id):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""
                SELECT id, user_id, company_id, product_name, product_type, product_count, product_price, product_total_price, product_barcode, product_date 
                FROM products 
                WHERE user_id = ? AND company_id = ? 
            """, (user_id, company_id))
            return cursor.fetchall()

    def delete_product(self, user_id, company_id, product_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""DELETE FROM products WHERE id = ? AND user_id = ? AND company_id = ? """, (int(product_id), user_id, company_id))
                
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Silme Hatası: {e}")
            return False


    def get_company_name_by_id(self, product_company_id):#ürüne kayıtlı olan firma idsi
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("SELECT company_name FROM company WHERE id = ?", (product_company_id,))
            data = cursor.fetchone()
            if data:
                return data[0]  # Örn: "CyberTech A.Ş."
            return "Bilinmeyen Firma"

    def get_product_for_updtae(self, user_id, company_id, product_id):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""SELECT * FROM products WHERE id = ? AND user_id = ? AND company_id = ?""", (int(product_id), int(user_id), int(company_id)))
            data = cursor.fetchone() 
            return data

    def update_product_item(self, user_id, company_id, product_id, product_type, p_name, p_count, p_price, product_total_price, p_barcode, p_date, new_company_id):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("""
                UPDATE products 
                SET company_id = ?,
                    product_type = ?,
                    product_name = ?, 
                    product_count = ?, 
                    product_price = ?, 
                    product_total_price = ?,
                    product_barcode = ?,
                    product_date = ?
                WHERE id = ? AND user_id = ?
            """, (int(new_company_id), product_type, p_name, p_count, p_price, product_total_price, p_barcode, p_date, int(product_id), int(user_id)))
            
            connection.commit()
            return cursor.rowcount > 0


    def get_stok_data(self, user_id, company_id, product_id):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                cursor.execute("""
                    SELECT current_stock_status, current_stock_notes 
                    FROM stock_status 
                    WHERE product_id = ? AND user_id = ? AND company_id = ?
                """, (int(product_id), int(user_id), int(company_id)))
                
                data = cursor.fetchone() 
                return data if data else None
                
        except Exception as e:
            print(f"Stok Veri Çekme Hatası: {e}")
            return None


    def save_or_update_stock_status(self, product_id, company_id, user_id, s_status, s_note):
        try:
            with sqlite3.connect(self.name) as connection:
                cursor = connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                # 1. Bu ürün için daha önce bir stok durumu kaydı açılmış mı kontrol edelim
                cursor.execute("""
                    SELECT id FROM stock_status 
                    WHERE product_id = ? AND company_id = ? AND user_id = ?
                """, (product_id, company_id, user_id))
                existing_record = cursor.fetchone()

                if existing_record:
                    # 2. Kayıt varsa -> UPDATE yap
                    cursor.execute("""
                        UPDATE stock_status 
                        SET current_stock_status = ?, current_stock_notes = ?
                        WHERE product_id = ? AND company_id = ? AND user_id = ?
                    """, (s_status, s_note, product_id, company_id, user_id))
                    action_type = "GÜNCELLENDİ"
                else:
                    # 3. Kayıt yoksa -> INSERT yap (İlk defa ekleniyor)
                    cursor.execute("""
                        INSERT INTO stock_status (product_id, user_id, company_id, current_stock_status, current_stock_notes) 
                        VALUES (?, ?, ?, ?, ?)
                    """, (product_id, user_id, company_id, s_status, s_note))
                    action_type = "EKLENDİ"

                connection.commit()

                # 4. Log için Kullanıcı adını ve Firma adını veritabanından çekelim
                cursor.execute("SELECT username FROM user WHERE id = ?", (user_id,))
                user_row = cursor.fetchone()
                username = user_row[0] if user_row else f"ID:{user_id}"

                cursor.execute("SELECT company_name FROM company WHERE id = ?", (company_id,))
                comp_row = cursor.fetchone()
                company_name = comp_row[0] if comp_row else f"ID:{company_id}"

                # 5. Konsola sade ve net log basımı
                print(f"🚀 [STOK {action_type}] '{username}' adlı kullanıcı, '{company_name}' firmasındaki (Ürün ID: {product_id}) stok durumunu işledi!")
                return True
                
        except Exception as e:
            print(f"❌ Stok Durum Kayıt/Güncelleme Hatası: {e}")
            return False

    def filter_products_company(self, user_id, name=None, sector=None, company=None):
        with sqlite3.connect(self.name) as connection:
            cursor = connection.cursor()
        
            query = "SELECT * FROM company WHERE user_id = ?"
            params = [user_id]

            if name:
                query += " AND company_person LIKE ?"
                params.append(f"%{name}%")
            
            if sector:
                query += " AND company_sector LIKE ?"
                params.append(f"%{sector}%")
           
            if company:
                query += " AND company_name LIKE ?"
                params.append(f"%{company}%")

            cursor.execute(query, params)
            return cursor.fetchall()

            cursor.execute(query, params)
            return cursor.fetchall()
    
    def simple_pdf_export_grouped(self, custom_data):
        try:
            # Çapraz platform dosya yolu (Android için İndirilenler, PC için proje klasörü)
            if platform == 'android':
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                downloads_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                pdf_filename = os.path.join(downloads_path, "ProSetMan_Firma_Bazli_Rapor.pdf")
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                pdf_filename = os.path.join(base_dir, "ProSetMan_Firma_Bazli_Rapor.pdf")

            doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
            elements = []

            styles = getSampleStyleSheet()
            
            # Ana Rapor Başlığı
            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor("#D97706"), # Amber tonu
                spaceAfter=15,
                alignment=1 
            )
            
            # Firma Alt Başlığı
            company_header_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor("#1F2937"),
                spaceBefore=12,
                spaceAfter=6,
                keepWithNext=True
            )

            elements.append(Paragraph("ProSetMan - Firma Bazlı Ürün Raporu", title_style))
            elements.append(Spacer(1, 10))

            for item in custom_data:
                c_name = item.get('company_name', 'Firma')
                products = item.get('products', [])

                # Firma adını başlık olarak ekle
                elements.append(Paragraph(f"<b>Firma: {c_name}</b>", company_header_style))

                if not products:
                    no_prod_style = ParagraphStyle('NoProd', parent=styles['Normal'], fontSize=9, textColor=colors.gray, leftIndent=10)
                    elements.append(Paragraph("Bu firmaya ait kayıtlı ürün bulunmamaktadır.", no_prod_style))
                    elements.append(Spacer(1, 8))
                    continue

                # Bu firmaya ait ürünlerin tablosu
                table_data = [["Ürün Adı", "Tür", "Adet", "Birim Fiyat", "Toplam", "Barkod", "Tarih"]]
                
                for p in products:
                    table_data.append([
                        str(p.get('name', '-')),
                        str(p.get('type', '-')),
                        str(p.get('count', '0')),
                        str(p.get('price', '0')),
                        str(p.get('total', '0')),
                        str(p.get('barcode', '-')),
                        str(p.get('date', '-'))
                    ])

                # A4 genişliğine tam oturan sütun oranları (Toplam: ~555 pt)
                col_widths = [115, 65, 50, 70, 75, 90, 90]
                product_table = Table(table_data, colWidths=col_widths)
                
                table_style = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")), # Koyu gri başlık
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ])
                
                product_table.setStyle(table_style)
                elements.append(product_table)
                elements.append(Spacer(1, 10))

            doc.build(elements)
            print(f"✅ Gruplandırılmış PDF başarıyla oluşturuldu: {pdf_filename}")
        except Exception as e:
            print(f"❌ PDF oluşturulurken hata çıktı: {e}")

    def simple_excel_export(self, custom_data=None):
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Firma ve Ürün Raporu"

            header_fill = PatternFill(start_color="1F2937", end_color="1F2937", fill_type="solid")
            header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
            company_font = Font(name="Arial", size=11, bold=True, color="D97706")
            data_font = Font(name="Arial", size=10)
            
            thin_border = Border(
                left=Side(style='thin', color='CCCCCC'),
                right=Side(style='thin', color='CCCCCC'),
                top=Side(style='thin', color='CCCCCC'),
                bottom=Side(style='thin', color='CCCCCC')
            )

            headers = ["Firma Adı", "Ürün Adı", "Ürün Türü", "Adet", "Birim Fiyat", "Toplam Tutar", "Barkod", "Tarih"]
            ws.append(headers)

            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col_num)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            if custom_data is not None:
                rows = custom_data
            else:
                connection = sqlite3.connect(self.name)
                cursor = connection.cursor()
                try:
                    cursor.execute("""
                        SELECT c.company_name, p.product_name, p.product_type, p.product_count, p.product_price, p.product_total_price, p.product_barcode, p.product_date 
                        FROM products p
                        LEFT JOIN company c ON p.company_id = c.id
                        ORDER BY c.company_name, p.product_name
                    """)
                except Exception:
                    cursor.execute("""
                        SELECT 'Genel Firma', product_name, product_type, product_count, product_price, product_total_price, product_barcode, product_date 
                        FROM products
                    """)
                rows = cursor.fetchall()
                connection.close()

            current_row = 2
            for row in rows:
                company_name, prod_name, prod_type, count, price, total_price, barcode, dt = row
                
                ws.cell(row=current_row, column=1, value=company_name).font = company_font
                ws.cell(row=current_row, column=2, value=prod_name).font = data_font
                ws.cell(row=current_row, column=3, value=prod_type).font = data_font
                
                c_count = ws.cell(row=current_row, column=4, value=count)
                c_count.font = data_font
                c_count.alignment = Alignment(horizontal="center")

                c_price = ws.cell(row=current_row, column=5, value=price)
                c_price.font = data_font
                
                c_total = ws.cell(row=current_row, column=6, value=total_price)
                c_total.font = data_font

                ws.cell(row=current_row, column=7, value=barcode).font = data_font
                
                c_dt = ws.cell(row=current_row, column=8, value=dt)
                c_dt.font = data_font
                c_dt.alignment = Alignment(horizontal="center")

                for col in range(1, 9):
                    ws.cell(row=current_row, column=col).border = thin_border

                current_row += 1

            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

            # Çapraz platform dosya yolu (Android için İndirilenler, PC için proje klasörü)
            if platform == 'android':
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                downloads_path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                file_name = os.path.join(downloads_path, "ProSetMan_Firma_Urun_Raporu.xlsx")
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_name = os.path.join(base_dir, "ProSetMan_Firma_Urun_Raporu.xlsx")

            wb.save(file_name)
            print(f"✅ Excel başarıyla oluşturuldu: {file_name}")
            
        except Exception as e:
            print(f"❌ Excel oluşturulurken hata çıktı: {e}")
