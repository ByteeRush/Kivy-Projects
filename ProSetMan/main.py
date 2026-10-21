import kivy
from kivy.app import App
from kivy.uix.screenmanager import (
    ScreenManager, 
    Screen,
    SlideTransition, 
    FadeTransition, 
    SwapTransition, 
    FallOutTransition, 
    WipeTransition,
    RiseInTransition
)
from kivy.lang import Builder
from database import Database
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import sqlite3
from kivy.uix.spinner import Spinner
import random
from datetime import datetime
import os
import platform
from kivy.utils import platform
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


try:
    from plyer import filechooser
except ImportError:
    filechooser = None

try:
    from plyer import camera
except ImportError:
    camera = None



class LoginScreen(Screen):

    def on_enter(self):
        try:
            app = App.get_running_app()
            if app:
                app.current_user_id = None  

            if hasattr(self, 'ids') and self.ids:
                if 'login_username' in self.ids:
                    self.ids.login_username.text = ""
                if 'login_password' in self.ids:
                    self.ids.login_password.text = ""
                if 'login_label' in self.ids:
                    self.ids.login_label.text = ""
        except Exception:
            pass 

    def login_to_app(self):
        user_name = self.ids.login_username.text.strip()
        password = self.ids.login_password.text.strip()

        if not user_name or not password:
            self.ids.login_label.text = "Tüm alanlar doldurulmalıdır!"
            return

        try:
            app = App.get_running_app()
            user_id = app.db.login(user_name, password)
            
            if user_id:
                app.current_user_id = user_id  
                self.ids.login_label.text = "Giriş Başarılı 🚀"
                self.manager.current = 'products' 
            else:
                self.ids.login_label.text = "Hatalı Kullanıcı Adı veya Şifre!"
        except Exception as e:
            self.ids.login_label.text = f"Hata: {e}"

                 


class FilterScreen(Screen):
    def apply_filter(self):
        app = App.get_running_app()
        if not app.current_user_id:
            return

        name_val = self.ids.filter_name_input.text.strip() or None
        min_price = self.ids.filter_min_price.text.strip() or None
        max_price = self.ids.filter_max_price.text.strip() or None
        start_date = self.ids.filter_start_date.text.strip() or None
        end_date = self.ids.filter_end_date.text.strip() or None
        min_count = self.ids.filter_min_count.text.strip() or None
        max_count = self.ids.filter_max_count.text.strip() or None

        results = app.db.filter_products(
            user_id=app.current_user_id,
            name=name_val,
            min_price=min_price,
            max_price=max_price,
            start_date=start_date,
            end_date=end_date,
            min_count=min_count,
            max_count=max_count,
        )

        product_screen = self.manager.get_screen("products")
        data_list = []
        for prod in results:
            prod_id, name, price, count, date = prod
            data_list.append({
                "product_id": str(prod_id),
                "p_name": str(name),
                "p_price": str(price),
                "p_count": str(count),
                "p_date": str(date),
            
            })

        product_screen.ids.rv.data = data_list
        self.manager.current = "products"


class UpdateProductScreen(Screen):
    is_data_loaded = False  

    def on_enter(self):
        app = App.get_running_app()
        if not app.selected_product_id:
            return

        if self.is_data_loaded:
            return

        data = app.db.get_product_for_updtae(app.selected_product_id)
         
        if data and hasattr(self, 'ids') and self.ids:
            if 'up_producer_name' in self.ids:
                self.ids.up_producer_name.text = str(data[2]) if data[2] else ""
            if 'up_product_type' in self.ids:
                self.ids.up_product_type.text = str(data[3]) if data[3] else ""
            if 'up_product_name' in self.ids:
                self.ids.up_product_name.text = str(data[4]) if data[4] else ""
            if 'up_product_count' in self.ids:
                self.ids.up_product_count.text = str(data[5]) if data[5] else ""
            if 'up_product_price' in self.ids:
                self.ids.up_product_price.text = str(data[6]) if data[6] else ""
            if 'up_product_barcode' in self.ids:
                self.ids.up_product_barcode.text = str(data[8]) if data[8] else ""
            if 'up_product_date' in self.ids:
                self.ids.up_product_date.text = str(data[10]) if len(data) > 10 else ""
             
            self.is_data_loaded = True

    def on_leave(self):
        self.is_data_loaded = False
    
    def save_product(self):
        app = App.get_running_app()

        if app.selected_product_id is None or app.current_user_id is None:
            return

        try:
            name = self.ids.up_product_name.text.strip()
            price = self.ids.up_product_price.text.strip()
            count = self.ids.up_product_count.text.strip()
            date = self.ids.up_product_date.text.strip()

            success = app.db.update_product_item(
                app.current_user_id,
                app.selected_product_id,
                name,
                count,
                price,
                date
            )

            if success:
                product_screen = app.root.get_screen("products")
                product_screen.load_user_products()

                self.ids.up_label.text = "Güncelleme Başarılı!"
                app.change_screen_randomly("products")
            else:
                self.ids.up_label.text = "Ürün güncellenemedi!"

        except Exception as e:
            self.ids.up_label.text = f"Hata: {e}"
            print(f"Güncelleme hatası: {e}")

class RegisterScreen(Screen):
    def add_user_to_app(self):
        name = self.ids.reg_user.text.strip()
        password = self.ids.reg_pass.text.strip()
        email = self.ids.reg_email.text.strip()
         
        if not name or not password or not email:
            self.ids.reg_label.text = "Tüm alanlar doldurulmalıdır!"
            return

        try:
            app = App.get_running_app()
            if app.db.add_user(name, password, email):
                self.ids.reg_label.text = "Kayıt Başarılı!"
        except Exception as e:
            self.ids.reg_label.text = f"Kayıt Başarısız: Bu kullanıcı zaten var olabilir!"




class InsertProductScreen(Screen):
    def __init__(self, **kwargs):
        super(InsertProductScreen, self).__init__(**kwargs)
        self.selected_image_path = ""


    def open_internal_gallery(self):
        try:
            # Android'de resimlerin bulunduğu ana dizinler
            target_dirs = []
            if platform == 'android':
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                ext_storage = Environment.getExternalStorageDirectory().getAbsolutePath()
                target_dirs = [
                    os.path.join(ext_storage, "DCIM", "Camera"),
                    os.path.join(ext_storage, "Pictures"),
                    os.path.join(ext_storage, "Download")
                ]
            else:
                # Masaüstü testi için kullanıcı dizini
                target_dirs = [os.path.expanduser("~")]

            image_files = []
            for d in target_dirs:
                if os.path.exists(d):
                    for root, dirs, files in os.walk(d):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                image_files.append(os.path.join(root, file))
            
            # En son çekilenler en başta gelsin
            image_files.sort(key=os.path.getmtime, reverse=True)
            image_files = image_files[:30] # Son 30 resmi listele

            # Popup arayüzünü oluşturuyoruz
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            content.add_widget(Label(text="Galeriden Resim Seç", size_hint_y=None, height=40, bold=True))
            
            scroll = ScrollView()
            grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
            grid.bind(minimum_height=grid.setter('height'))

            modal = ModalView(size_hint=(0.9, 0.9))

            if not image_files:
                content.add_widget(Label(text="Hiç resim bulunamadı!"))
            else:
                for img_path in image_files:
                    btn_box = BoxLayout(orientation='vertical', size_hint_y=None, height=180, spacing=5)
                    try:
                        img = Image(source=img_path, size_hint_y=None, height=130, allow_stretch=True)
                        btn_box.add_widget(img)
                        
                        select_btn = Button(text="Seç", size_hint_y=None, height=40)
                        select_btn.bind(on_release=lambda x, p=img_path: [self.set_image_source(p), modal.dismiss()])
                        btn_box.add_widget(select_btn)
                        
                        grid.add_widget(btn_box)
                    except Exception:
                        pass

            scroll.add_widget(grid)
            content.add_widget(scroll)
            
            close_btn = Button(text="Kapat", size_hint_y=None, height=50)
            close_btn.bind(on_release=modal.dismiss)
            content.add_widget(close_btn)

            modal.add_widget(content)
            modal.open()

        except Exception as e:
            print(f"Galeri açma hatası: {e}")
            if 'ins_label' in self.ids:
                self.ids.ins_label.text = "Galeri açılamadı!"


    def select_product_image(self):
        if platform == 'android':
            try:
                from plyer import filechooser
                filechooser.open_file(
                    title="Ürün Fotoğrafı Seç",
                    filters=[("Resim Dosyaları", "*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.gif", "*.heic", "*.heif")],
                    on_selection=self.handle_image_selected
                )
            except Exception as e:
                print(f"Android dosya seçici hatası: {e}")
                if 'ins_label' in self.ids:
                    self.ids.ins_label.text = "Dosya seçici açılamadı!"
        else:
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    title="Ürün Fotoğrafı Seç",
                    filetypes=[("Resim Dosyaları", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.heic *.heif")]
                )
                root.destroy()
                
                if file_path:
                    self.handle_image_selected([file_path])
            except Exception as e:
                print(f"Masaüstü dosya seçici hatası: {e}")



    def handle_image_selected(self, selection):
        if selection and len(selection) > 0:
            uri = selection[0]
            if uri:
                valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.heic', '.heif')
                lower_uri = uri.lower()
                
                if not lower_uri.endswith(valid_extensions):
                    print(f"Hatalı dosya türü seçildi: {uri}")
                    if 'ins_label' in self.ids:
                        self.ids.ins_label.text = "Lütfen geçerli bir resim dosyası seçin!"
                    return

                Clock.schedule_once(lambda dt: self.copy_and_set_image(uri))

    def copy_and_set_image(self, uri):
        try:
            app = App.get_running_app()
            local_path = os.path.join(app.user_data_dir, "product_img.jpg")
            
            if platform == 'android' and uri.startswith('content://'):
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                resolver = context.getContentResolver()
                Uri = autoclass('android.net.Uri')
                j_uri = Uri.parse(uri)
                inputStream = resolver.openInputStream(j_uri)
                
                FileOutputStream = autoclass('java.io.FileOutputStream')
                fos = FileOutputStream(local_path)
                
                java_array = autoclass('java.lang.reflect.Array')
                Byte = autoclass('java.lang.Byte')
                buffer = java_array.newInstance(Byte.TYPE, 1024)
                
                while True:
                    length = inputStream.read(buffer)
                    if length < 0:
                        break
                    fos.write(buffer, 0, length)
                fos.close()
                inputStream.close()
                target_path = local_path
            else:
                target_path = uri
                
            if target_path:
                self.set_image_source(target_path)
        except Exception as e:
            print(f"Resim kopyalama hatası: {e}")
            self.set_image_source(uri)

    def set_image_source(self, path):
        if path:
            self.selected_image_path = path
            if 'product_image_preview' in self.ids and self.ids.product_image_preview:
                self.ids.product_image_preview.source = path
                self.ids.product_image_preview.reload()

    def on_enter(self):
        if not self.ids.product_date.text:
            self.ids.product_date.text = datetime.now().strftime("%Y-%m-%d")
        self.ids.ins_label.text = ""
        self.calculate_total()


    def take_photo_with_camera(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                from android.runnable import run_on_ui_thread
                
                app = App.get_running_app()
                # Kameranın kaydedeceği hedef dosya yolu
                self.camera_image_path = os.path.join(
                    app.user_data_dir, 
                    f"camera_product_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )
                
                @run_on_ui_thread
                def open_native_camera(*args):
                    try:
                        PythonActivity = autoclass('org.kivy.android.PythonActivity')
                        activity = PythonActivity.mActivity
                        
                        Intent = autoclass('android.content.Intent')
                        MediaStore = autoclass('android.provider.MediaStore')
                        File = autoclass('java.io.File')
                        FileProvider = autoclass('androidx.core.content.FileProvider')
                        
                        file_obj = File(self.camera_image_path)
                        
                        # Android 24+ için FileProvider üzerinden güvenli URI oluşturuyoruz
                        ctx = activity.getApplicationContext()
                        authority = f"{activity.getPackageName()}.fileprovider"
                        image_uri = FileProvider.getUriForFile(ctx, authority, file_obj)
                        
                        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
                        intent.putExtra(MediaStore.EXTRA_OUTPUT, image_uri)
                        
                        # Kamera uygulamasının dosyaya yazma izni vermesini sağlıyoruz
                        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
                        
                        # Kamerayı başlat (Kod: 101)
                        activity.startActivityForResult(intent, 101)
                    except Exception as e:
                        print(f"Java Kamera Başlatma Hatası: {e}")
                        if 'ins_label' in self.ids:
                            self.ids.ins_label.text = "Kamera başlatılamadı!"

                open_native_camera()
            except Exception as e:
                print(f"Kamera hatası: {e}")
                if 'ins_label' in self.ids:
                    self.ids.ins_label.text = "Kamera başlatılamadı!"
        else:
            print("Masaüstünde gerçek kamera tetiklenemez.")
            if 'ins_label' in self.ids:
                self.ids.ins_label.text = "Kamera sadece telefonda aktif olur!"

    def handle_camera_complete(self, image_path):
        if image_path and os.path.exists(image_path):
            Clock.schedule_once(lambda dt: self.set_image_source(image_path))
        else:
            print("Kamera çekimi iptal edildi veya dosya oluşturulamadı.")
            Clock.schedule_once(lambda dt: setattr(self.ids.ins_label, 'text', "Fotoğraf çekilemedi!"))

    def calculate_total(self):
        try:
            price_text = self.ids.product_price.text.strip()
            count_text = self.ids.product_count.text.strip()
            
            if not price_text or not count_text:
                self.ids.product_total_price.text = "0.00"
                return

            price = float(price_text)
            count = float(count_text)
            total = price * count
            self.ids.product_total_price.text = f"{total:.2f}"
        except ValueError:
            self.ids.product_total_price.text = "0.00"

    def add_product_to_system(self):
        producer_name = self.ids.producer_name.text.strip()
        product_type = self.ids.product_type.text.strip()
        product_name = self.ids.product_name.text.strip()
        product_count = self.ids.product_count.text.strip()
        product_price = self.ids.product_price.text.strip()
        product_total_price = self.ids.product_total_price.text.strip()
        product_barcode = self.ids.product_barcode.text.strip()
        product_date = self.ids.product_date.text.strip()
        product_image = self.selected_image_path or "" # Fotoğraf seçilmediyse boş string gider

        # product_image kontrolünü buradan çıkardık!
        if not product_name or not product_count or not product_price or not product_date or not product_type or not producer_name:
            self.ids.ins_label.text = "Tüm alanlar doldurulmalıdır!"
            return

        try:
            app = App.get_running_app()
            success = app.db.add_product(
                app.current_user_id,
                producer_name, 
                product_type, 
                product_name, 
                product_count, 
                product_price, 
                product_total_price, 
                product_barcode, 
                product_image, 
                str(product_date)
            )
            
            if success:
                self.ids.ins_label.text = "Kayıt Başarılı 🚀"
                
                product_screen = app.root.get_screen("products")
                product_screen.load_user_products()
                
                # Formu temizle
                self.ids.producer_name.text = ""
                self.ids.product_name.text = ""
                self.ids.product_count.text = ""
                self.ids.product_price.text = ""
                self.ids.product_total_price.text = "0.00"
                self.ids.product_barcode.text = ""
                self.ids.product_type.text = ""
                self.ids.product_date.text = datetime.now().strftime("%Y-%m-%d")
                
                self.selected_image_path = ""
                if 'product_image_preview' in self.ids:
                    self.ids.product_image_preview.source = ""
            else:
                self.ids.ins_label.text = "Kayıt Başarısız"
        except Exception as e:
            self.ids.ins_label.text = f"Hata: {e}"

class ProductRow(RecycleDataViewBehavior, BoxLayout):
    product_id = StringProperty("")
    producer_name = StringProperty("")
    p_name = StringProperty("")
    p_price = StringProperty("")
    p_count = StringProperty("")
    p_date = StringProperty("")
    p_type = StringProperty("")
    p_barcode  = StringProperty("")
    p_total_price = StringProperty("")

    def delete_item(self):
        app = App.get_running_app()
        if not app.current_user_id or not self.product_id:
            return

        success = app.db.delete_product(app.current_user_id, self.product_id)
         
        if success:
            product_screen = app.root.get_screen('products')
            product_screen.load_user_products()


    def trigger_update(self):
        app = App.get_running_app()
        if not self.product_id:
            return
         
        app.selected_product_id = self.product_id
        app.root.current = "updateproduct"

    def trigger_update_for_details(self):
        app = App.get_running_app()
        if not self.product_id:
            return

        app.selected_product_id = self.product_id
        app.root.current = "productdetails"
        


         
class ProductScreen(Screen):

    def on_enter(self):
        if not self.ids.rv.data:
            self.load_user_products()

    def load_user_products(self):
        app = App.get_running_app()
        if not app.current_user_id:
            return

        products = app.db.get_user_products(app.current_user_id)

        data_list = []
        for prod in products:
            prod_id,producer_name, name, price, count, date , product_type , product_total_price, product_barcode= prod
            data_list.append({
                "product_id": str(prod_id),
                "pr_name": str(producer_name),
                "p_name": str(name),
                "p_price": str(price),
                "p_count": str(count),
                "p_date": str(date),
                "p_type": str(product_type),
                "p_total_price": str(product_total_price),
                "p_barcode": str(product_barcode),
                
            })

        self.ids.rv.data = data_list



class ProductDetailScreen(Screen):
    def on_enter(self):
        try:
            app = App.get_running_app()
            if not app.selected_product_id:
                return

            data = app.db.get_product_for_updtae(app.selected_product_id)
            
            if data and hasattr(self, 'ids') and self.ids:
                if 'lbl_producer' in self.ids:
                    self.ids.lbl_producer.text = f"Firma / Üretici: {data[2]}"
                if 'lbl_type' in self.ids:
                    self.ids.lbl_type.text = f"Ürün Tipi: {data[3]}"
                if 'lbl_name' in self.ids:
                    self.ids.lbl_name.text = f"Ürün Adı: {data[4]}"
                if 'lbl_count' in self.ids:
                    self.ids.lbl_count.text = f"Adet / Koli: {data[5]}"
                if 'lbl_price' in self.ids:
                    self.ids.lbl_price.text = f"Birim Fiyat: {data[6]} ₺"
                if 'lbl_total' in self.ids:
                    self.ids.lbl_total.text = f"Toplam Tutar: {data[7]} ₺"
                
                barcode_val = data[8] if len(data) > 8 and data[8] else 'Yok'
                if 'lbl_barcode' in self.ids:
                    self.ids.lbl_barcode.text = f"Barkod: {barcode_val}"
                
                date_val = data[10] if len(data) > 10 else (data[5] if len(data) > 5 else '')
                if 'lbl_date' in self.ids:
                    self.ids.lbl_date.text = f"Kayıt Tarihi: {date_val}"
                
                image_val = data[9] if len(data) > 9 else None
                if 'detail_image' in self.ids:
                    if image_val and os.path.exists(image_val):
                        self.ids.detail_image.source = image_val
                    else:
                        self.ids.detail_image.source = ""
        except Exception as e:
            print(f"Detay ekranı yükleme hatası: {e}")




print("1. KV dosyası yükleniyor...")
Builder.load_file("Designs/main.kv")
print("2. KV dosyası yüklendi, App sınıfı başlıyor...")

class ProSetManApp(App):

    def change_screen_randomly(self, target_screen):
        transitions = [
            FadeTransition(duration=0.3),
            SwapTransition(duration=0.4),
            FallOutTransition(duration=0.3),
            WipeTransition(duration=0.3),
            SlideTransition(duration=0.3, direction='left'),
            RiseInTransition(duration=0.3)
        ]
        
        self.sm.transition = random.choice(transitions)
        self.sm.current = target_screen


    def build(self):
        self.db = Database()
        self.current_user_id = None
        self.selected_product_id = None
        
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(ProductScreen(name='products'))
        self.sm.add_widget(InsertProductScreen(name='insertproduct'))
        self.sm.add_widget(UpdateProductScreen(name='updateproduct'))
        self.sm.add_widget(FilterScreen(name='filterproduct'))
        self.sm.add_widget(ProductDetailScreen(name="productdetails"))

        return self.sm

    def on_filter_selected(self, format_type):
        if format_type == 'Kayıt Formatı':
            return

        product_screen = self.root.get_screen('products')
        current_data = product_screen.ids.rv.data

        if not current_data:
            print('Aktarılacak ürün bulunamadı!')
            return

        export_list = []
        for item in current_data:
            row = (
                int(item['product_id']),
                self.current_user_id or 1,
                item['p_name'],
                item['p_count'].replace(' Adet', '').strip(),
                item['p_price'].replace(' ₺', '').strip(),
                item['p_date'],
            )
            export_list.append(row)

        if format_type == 'Excel':
            self.db.simple_excel_export(custom_data=export_list)
            print('Görünen liste Excel olarak kaydedildi!')
        elif format_type == 'Pdf':
            self.db.simple_pdf_export(custom_data=export_list)
            print('Görünen liste PDF olarak kaydedildi!')

        for widget in product_screen.walk():
            if isinstance(widget, Spinner) and widget.values == ['Excel', 'Pdf']:
                widget.text = 'Kayıt Formatı'
                break


if __name__ == '__main__':
    ProSetManApp().run()