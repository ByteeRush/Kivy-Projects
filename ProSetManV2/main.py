import kivy
from kivy.app import App
from kivy.factory import Factory
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
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from kivy.animation import Animation
from kivy.utils import platform


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
        # Güvenli id çekme yöntemi (Python 3.14 ve Kivy çökme koruması)
        username_input = self.ids.get('login_username')
        password_input = self.ids.get('login_password')
        login_label = self.ids.get('login_label')

        user_name = username_input.text.strip() if username_input else ""
        password = password_input.text.strip() if password_input else ""

        if not user_name or not password:
            if login_label:
                login_label.text = "Tüm alanlar doldurulmalıdır!"
            else:
                print("Uyarı: Tüm alanlar doldurulmalıdır!")
            return

        try:
            app = App.get_running_app()
            user_id = app.db.login(user_name, password)
            
            if user_id:
                app.current_user_id = user_id  
                if login_label:
                    login_label.text = "Giriş Başarılı 🚀"
                self.manager.current = 'center' 
            else:
                if login_label:
                    login_label.text = "Hatalı Kullanıcı Adı veya Şifre!"
        except Exception as e:
            if login_label:
                login_label.text = f"Hata: {e}"
            print(f"Giriş hatası: {e}")

                 
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

class InsertCompanyScreen(Screen):
    
    def add_company_to_system(self):
        app: ProSetManApp = App.get_running_app()
        user_id = app.current_user_id

        company_name = self.ids.company_name.text.strip()
        company_number = self.ids.company_number.text.strip()
        company_person = self.ids.company_person.text.strip()
        company_sector = self.ids.company_sector.text.strip()


        if not company_name or not company_number or not company_person or not company_sector:
            self.ids.ins_label.color = [1, 0.6, 0, 1]  # Turuncu/Sarı (Uyarı)
            self.ids.ins_label.text = "Tüm alanlar doldurulmalıdır!"
            return

  
        if company_sector == "Ürün Seçiniz...":
            self.ids.ins_label.color = [1, 0.6, 0, 1]  # Turuncu/Sarı (Uyarı)
            self.ids.ins_label.text = "Lütfen geçerli bir sektör seçiniz!"
            return


        success = app.db.add_company( user_id, company_name, company_number, company_person, company_sector)

        if success:
            self.ids.ins_label.color = [0, 1, 0, 1]  # Canlı Yeşil (Başarı)
            self.ids.ins_label.text = "Kayıt Başarılı 🚀"

            # İsteğe bağlı: Kayıttan 1-2 saniye sonra ürünler ekranına dönebilirsin
            app.change_screen_randomly("center")
        else:
            self.ids.ins_label.color = [1, 0, 0, 1]  # Canlı Kırmızı (Hata)
            self.ids.ins_label.text = ("Kayıt Başarısız! Bu şirket adı zaten kayıtlı olabilir.")

class InsertProductScreen(Screen):
    company_dict = {}  # Firma adını anahtar (key), ID'sini değer (value) yapacağımız sözlük

    def load_companies_to_spinner(self):
        app: ProSetManApp = App.get_running_app()
        if not app.current_user_id:
            return

        # Veritabanından (id, isim) listesini alıyoruz
        companies = app.db.get_company_id_name_list(app.current_user_id)
        
        self.company_dict = {}
        firma_isimleri = []
        
        for comp_id, comp_name in companies:
            firma_isimleri.append(str(comp_name))
            self.company_dict[str(comp_name)] = str(comp_id)  # Örn: {"Firma A": "1"}
            
        # Spinner'ın açılır menüsüne sadece firma isimlerini basıyoruz
        self.ids.company_spinner.values = firma_isimleri

    def on_company_select(self, company_name):
        # Kullanıcı Spinner'dan bir firma seçtiği an bu tetiklenir ve terminalde yazı yazar seçilen firma 
        if company_name in self.company_dict:
            app: ProSetManApp = App.get_running_app()
            app.selected_company_id = self.company_dict[company_name]
            print(f"Seçilen Firma: {company_name} -> ID: {app.selected_company_id}")

    
    def product_insert(self):
        app: ProSetManApp = App.get_running_app()
        if not app.current_user_id:
            return
      
        selected_company_name = self.ids.company_spinner.text.strip()

     
        if not selected_company_name or selected_company_name == "Firma Seçiniz...":
            self.ids.ins_label.text = "Lütfen bir firma seçiniz!"
            Clock.schedule_once(lambda dt: setattr(self.ids.ins_label, 'text', 'ProSetMan - Ürün Ekleme'), 3)
            return


        if selected_company_name in self.company_dict:
            app.selected_company_id = self.company_dict[selected_company_name]
        else:
            self.ids.ins_label.text = "Geçersiz firma seçimi!"
            Clock.schedule_once(lambda dt: setattr(self.ids.ins_label, 'text', 'ProSetMan - Ürün Ekleme'), 3)
            return

        # 4. Adım: Formdaki diğer verileri topluyoruz
        product_type = self.ids.product_type.text.strip()
        product_name = self.ids.product_name.text.strip()
        product_count = self.ids.product_count.text.strip()
        product_price = self.ids.product_price.text.strip()
        product_total_price = self.ids.product_total_price.text.strip()
        product_barcode = self.ids.product_barcode.text.strip()
        product_date = self.ids.product_date.text.strip()

        # 5. Adım: Veritabanına bulduğumuz company_id ile kaydı gönderiyoruz
        success = app.db.add_product(
            app.selected_company_id,
            app.current_user_id,
            product_name,
            product_type,
            product_count,
            product_price,
            product_total_price,
            product_barcode,
            product_date
        )

        if success:
            self.ids.ins_label.text = "Ürün Ekleme Başarılı 🚀"
            Clock.schedule_once(lambda dt: setattr(self.ids.ins_label, 'text', 'ProSetMan - Ürün Ekleme'), 3)
        else:
            self.ids.ins_label.text = "Ürün Ekleme Başarısız!"
            Clock.schedule_once(lambda dt: setattr(self.ids.ins_label, 'text', 'ProSetMan - Ürün Ekleme'), 3)

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



class CompanyRow(RecycleDataViewBehavior, BoxLayout):
    company_id = StringProperty("")
    company_name = StringProperty("")
    company_number = StringProperty("")
    company_admin = StringProperty("")
    company_sector = StringProperty("")


    def delete_company(self):
        app: ProSetManApp = App.get_running_app()
        if not app.current_user_id:
            return


        app.db.delete_company(app.current_user_id,self.company_id)
        try:
            center_screen = app.root.get_screen('center')
            center_screen.load_companies_on_panel()
        except Exception as e:
            print("Liste yenilenirken hata oluştu: ", e)

    def update_company(self):
        app: ProSetManApp = App.get_running_app()
        if not app.current_user_id:
            return
            
        # company_id'yi int() yaptık!
        success = app.db.update_company(
            int(self.company_id), 
            app.current_user_id, 
            self.company_name, 
            self.company_number, 
            self.company_admin, 
            self.company_sector
        )
        
        if success:
            print("Ürün başarıyla güncellendi!")
            try:
                details_screen = app.root.get_screen('center')
                details_screen.ids.pr_title.text = "Ürün Güncellemesi Yapıldı!"
                
                # 3 saniye sonra başlığı otomatik olarak eski orijinal haline döndürür:
                Clock.schedule_once(lambda dt: setattr(details_screen.ids.pr_title, 'text', 'ProSetMan - Firma Listesi'), 3.0)
                
                details_screen.load_products() 
            except Exception as e:
                print("Ekran güncellenirken hata:", e)

    def trigger_product_id(self):
        app: ProSetManApp = App.get_running_app()
        if not self.company_id:
            return

        app.selected_company_id = self.company_id
        print(f"Seçilen Firma ID: {app.selected_company_id}")
        
      
        product_screen = app.root.get_screen('productdetails')
        product_screen.load_products()
        
        app.change_screen_randomly('productdetails')

class CenterScreen(Screen):

    def on_enter(self):
        super(CenterScreen, self).on_enter()
        # Ekran açıldığı an firmaları yükle
        Clock.schedule_once(lambda dt: self.load_companies_on_panel(), 0.1)

    def load_companies_on_panel(self):
        app = App.get_running_app()
        if not app.current_user_id:
            print("Listeleme hatası: Kullanıcı ID bulunamadı!")
            return

        try:
            # Veritabanından firmaları çekiyoruz
            companies = app.db.get_companys(app.current_user_id)
            print("Veritabanından gelen firmalar:", companies)
            
            data_list = []
            for comp in companies:
                comp_id, user_id, name, number, admin, sector = comp
                data_list.append({
                    "company_id": str(comp_id),
                    "company_name": str(name),
                    "company_number": str(number or "-"),
                    "company_admin": str(admin or "-"),
                    "company_sector": str(sector or "-"),
                })

            # RecycleView'a verileri yüklüyoruz
            if hasattr(self, 'ids') and 'rv' in self.ids:
                self.ids.rv.data = data_list
                print("Firmalar başarıyla listeye aktarıldı!")
            else:
                print("Hata: 'rv' id'si ekranda bulunamadı!")
                
        except Exception as e:
            print(f"Firma listeleme hatası: {e}")

    def open_company_filter_popup(self):
        filter_popup = CompanyFilter()
        filter_popup.open()



class CompanyFilter(Popup):
    def apply_cmp_filter(self):
        app = App.get_running_app()
        if not app.current_user_id:
            return

        # 1. Popup içindeki TextInput kutularından verileri alıyoruz
        prod_name = self.ids.filter_product_name.text.strip() or None
        sector_val = self.ids.filter_sector.text.strip() or None
        admin_val = self.ids.filter_admin.text.strip() or None

        # 2. Veritabanından esnek filtrelemeyi çalıştırıyoruz
        results = app.db.filter_products_company(
            user_id=app.current_user_id,
            name=admin_val,
            sector=sector_val,
            company=prod_name
        )

        # 3. Gelen sonuçları "center" ekranındaki RecycleView listesine yüklüyoruz
        center_screen = app.root.get_screen("center")
        data_list = []
        
        for comp in results:
            comp_id, user_id, name, number, admin, sector = comp
            data_list.append({
                "company_id": str(comp_id),
                "company_name": str(name),
                "company_number": str(number or "-"),
                "company_admin": str(admin or "-"),
                "company_sector": str(sector or "-"),
            })

        center_screen.ids.rv.data = data_list

        # 4. Popup'ı kapatıyoruz (Zaten center ekranındayız, manager'a gerek yok!)
        self.dismiss()




class ProductDetailsWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Widget oluşur oluşmaz verileri yüklüyoruz
        self.load_status()

    def load_status(self):
       
        app = App.get_running_app()
        
        if not app.current_user_id or not app.selected_company_id or not app.selected_product_id:
            return

    
        load = app.db.get_stok_data(app.current_user_id, app.selected_company_id, app.selected_product_id)

        if load:
           
            self.ids.stock_status_spinner.text = str(load[0]) if load[0] else "Seçiniz"
            self.ids.product_description.text = str(load[1]) if load[1] else ""
        else:
            self.ids.stock_status_spinner.text = "Seçiniz"
            self.ids.product_description.text = ""

    def save_or_update_stock_status(self):
        from kivy.app import App
        app = App.get_running_app()
        
        if not app.current_user_id or not app.selected_company_id or not app.selected_product_id:
            print("❌ Eksik ID: Kullanıcı, firma veya ürün seçilmemiş!")
            return

        s_status = self.ids.stock_status_spinner.text
        s_note = self.ids.product_description.text

        if s_status == "Seçiniz":
            s_status = "Belirtilmemiş"

        success = app.db.save_or_update_stock_status(
            product_id=app.selected_product_id,
            company_id=app.selected_company_id,
            user_id=app.current_user_id,
            s_status=s_status,
            s_note=s_note
        )

        if success:
            print("Ürün başarıyla güncellendi!")
            try:
                details_screen = app.root.get_screen('productdetails')
                details_screen.ids.pr_title.text = "Ürün Güncellemesi Yapıldı!"
                
                # 3 saniye sonra başlığı otomatik olarak eski orijinal haline döndürür:
                Clock.schedule_once(lambda dt: setattr(details_screen.ids.pr_title, 'text', 'ProSetMan - Ürün Detay Paneli'), 3.0)
                
                details_screen.load_products() 
            except Exception as e:
                print("Ekran güncellenirken hata:", e)
         

class ProductUpdateWidget(BoxLayout):
    # (Buradaki hatalı self.company_dict satırı silindi)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Widget oluşur oluşmaz verileri yüklüyoruz
        self.load_company_products()

        
    def load_company_products(self):
        app = App.get_running_app()
        
        if not app.current_user_id or not app.selected_company_id or not app.selected_product_id:
            print("IDLerden Biri Seçilmedi")
            return

        load = app.db.get_product_for_updtae(app.current_user_id, app.selected_company_id, app.selected_product_id)
        
        if load:
            product_company_id = load[2] # Ürünün bağlı olduğu şirket ID'si
            
            companies = app.db.get_company_id_name_list(app.current_user_id)
            
            self.company_dict = {} 
            firma_isimleri = []
            for comp_id, comp_name in companies:
                firma_isimleri.append(str(comp_name))
                self.company_dict[str(comp_name)] = str(comp_id)
            
         
            self.ids.company_spinner.values = firma_isimleri

           
            company_name = app.db.get_company_name_by_id(product_company_id)  
            if company_name:
                self.ids.company_spinner.text = str(company_name)
            else:
                self.ids.company_spinner.text = "Firma Seçiniz..."

       
            self.ids.product_name.text = str(load[3]) if load[3] else ""
            self.ids.product_type.text = str(load[4]) if load[4] else ""
            self.ids.product_count.text = str(load[5]) if load[5] else ""
            self.ids.product_price.text = str(load[6]) if load[6] else ""
            self.ids.product_total_price.text = str(load[7]) if load[7] else ""
            self.ids.product_barcode.text = str(load[8]) if load[8] else ""
            # Tarih index'i 10 olarak ayarlandı:
            self.ids.product_date.text = str(load[9]) if len(load) > 9 and load[9] else ""
           
            
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

    def update_company_product(self):
        app = App.get_running_app()
        
        selected_company_name = self.ids.company_spinner.text
        if selected_company_name not in self.company_dict:  # <--- Buradaki 'dit' -> 'dict' olacak
            print("Lütfen geçerli bir firma seçin!")
            return
            
        new_company_id = self.company_dict[selected_company_name]
        
        # 2. TextInput'lardaki güncel verileri alıyoruz
        p_type = self.ids.product_type.text
        p_name = self.ids.product_name.text
        p_count = self.ids.product_count.text
        p_price = self.ids.product_price.text
        p_total = self.ids.product_total_price.text
        p_barcode = self.ids.product_barcode.text
        p_date = self.ids.product_date.text
        
        # 3. Veritabanındaki güncelleme fonksiyonunu çağırıyoruz
        success = app.db.update_product_item(
            user_id=app.current_user_id,
            company_id=app.selected_company_id, 
            product_id=app.selected_product_id,
            product_type=p_type,
            p_name=p_name,
            p_count=p_count,
            p_price=p_price,
            product_total_price=p_total,
            p_barcode=p_barcode,
            p_date=p_date,
            new_company_id=new_company_id
        )
        
        if success:
            print("Ürün başarıyla güncellendi!")
            try:
                details_screen = app.root.get_screen('productdetails')
                details_screen.ids.pr_title.text = "Ürün Güncellemesi Yapıldı!"
                
                # 3 saniye sonra başlığı otomatik olarak eski orijinal haline döndürür:
                Clock.schedule_once(lambda dt: setattr(details_screen.ids.pr_title, 'text', 'ProSetMan - Ürün Detay Paneli'), 3.0)
                
                details_screen.load_products() 
            except Exception as e:
                print("Ekran güncellenirken hata:", e)

 
class ProductCard(BoxLayout):
    is_expanded = False
    active_panel = "none"         # "none", "details", "update"
    details_widget = None
    update_widget = None
    
    p_id = StringProperty("")
    p_name = StringProperty("")
    p_count = StringProperty("")
    p_price = StringProperty("")
    p_date = StringProperty("")

    def __init__(self, p_id, p_name, p_count, p_price, p_date, **kwargs):
        super().__init__(**kwargs)
        self.p_id = p_id
        self.p_name = p_name
        self.p_count = p_count
        self.p_price = p_price
        self.p_date = p_date  
    
    def delete_product(self):
        app = App.get_running_app()
        if not app.current_user_id or not app.selected_company_id:
            return
        
        if not self.p_id:
            print("Silme hatası: Ürün ID bulunamadı!")
            return

        success = app.db.delete_product(app.current_user_id, app.selected_company_id, self.p_id)
        if success:
            print(f"Ürün başarıyla silindi ID: {self.p_id}")
            try:
                productdetails = app.root.get_screen('productdetails')
                productdetails.load_products()
            except Exception as e:
                print("Liste yenilenirken hata oluştu: ", e)

    def toggle_expand_product_details(self):
        app = App.get_running_app()
        if self.p_id:
            if app.selected_product_id != self.p_id:
                app.selected_product_id = self.p_id
                print(f" Seçilen Ürün ID hafızaya atıldı: {app.selected_product_id}")

        if self.active_panel == "update":
            if self.update_widget and self.update_widget in self.children:
                self.remove_widget(self.update_widget)
            self.update_widget = None

        if self.active_panel != "details":
            if not self.details_widget:
                self.details_widget = Factory.ProductDetailsWidget()
            if self.details_widget not in self.children:
                self.add_widget(self.details_widget)
            
            self.active_panel = "details"
            self.is_expanded = True
        else:
            if self.details_widget and self.details_widget in self.children:
                self.remove_widget(self.details_widget)
            self.details_widget = None
            self.active_panel = "none"
            self.is_expanded = False
            
        self.do_layout()
        if self.parent:
            self.parent.do_layout()

    def toggle_expand_product_update(self):
        app = App.get_running_app()
        if self.p_id:
            if app.selected_product_id != self.p_id:
                app.selected_product_id = self.p_id
                print(f" Seçilen Ürün ID hafızaya atıldı: {app.selected_product_id}")

        if self.active_panel == "details":
            if self.details_widget and self.details_widget in self.children:
                self.remove_widget(self.details_widget)
            self.details_widget = None

        if self.active_panel != "update":
            if not self.update_widget:
                self.update_widget = Factory.ProductUpdateWidget()
            if self.update_widget not in self.children:
                self.add_widget(self.update_widget)
            
            self.active_panel = "update"
            self.is_expanded = True
        else:
            if self.update_widget and self.update_widget in self.children:
                self.remove_widget(self.update_widget)
            self.update_widget = None
            self.active_panel = "none"
            self.is_expanded = False
            
        self.do_layout()
        if self.parent:
            self.parent.do_layout()


class ProductDetailScreen(Screen):
    def on_enter(self):
        # Ekran ekrana geldiği an ürünleri otomatik yükle
        self.load_products()

    def load_products(self):
        app = App.get_running_app()
        if not app.current_user_id or not app.selected_company_id:
            return

        # 1. Eski kartlar üst üste binmesin diye konteyneri temizle
        self.ids.product_container.clear_widgets()

        # 2. Veritabanından o firmaya ait ürünleri çek
        products = app.db.get_user_products(app.current_user_id, app.selected_company_id)
        print(f"Veritabanından gelen ürünler: {products}")

      
        for prod in products:
            card = ProductCard(
                p_id=str(prod[0]),                   
                p_name=str(prod[3]),           
                p_count=str(prod[5]) + str(prod[6]), 
                p_price=str(prod[6]) + " ₺",
                p_date=str(prod[9])
            )
            self.ids.product_container.add_widget(card)

    def back_to(self):
        app = App.get_running_app()
        if app:
            app.sm.current = "center"  # Veya app.change_screen_randomly("center")

    

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

    
    def on_filter_selected(self, format_type):
        if format_type == 'Kayıt Formatı':
            return

        export_data = []
        target_screen = None

        # 1. Önce Center ekranındaki rv.data içinden o an görünen firmaları ve ID'lerini alalım
        for screen in self.root.screens:
            if screen.name == 'center' and hasattr(screen, 'ids') and 'rv' in screen.ids and screen.ids.rv.data:
                target_screen = screen
                for item in screen.ids.rv.data:
                    c_id = item.get('company_id')
                    c_name = item.get('company_name')
                    
                    if c_id:
                        # Her firmanın ID'sine ait ürünleri veritabanından çekiyoruz
                        prods = self.db.get_user_products(self.current_user_id, c_id)
                        company_products = []
                        
                        for p in prods:
                            # p yapısı: (id, user_id, company_id, name, type, count, price, total, barcode, date)
                            company_products.append({
                                'name': str(p[3] or '-'),
                                'type': str(p[4] or '-'),
                                'count': str(p[5] or '0').replace(' Adet', '').strip(),
                                'price': str(p[6] or '0').replace(' ₺', '').strip(),
                                'total': str(p[7] or '0').replace(' ₺', '').strip(),
                                'barcode': str(p[8] or '-'),
                                'date': str(p[9] or '-')
                            })
                        
                        export_data.append({
                            'company_name': c_name,
                            'products': company_products
                        })
                break

        # 2. Eğer Center ekranında değilsek (örneğin ProductDetailScreen'diysek) o anki seçili firmayı basalım
        if not export_data and hasattr(self, 'selected_company_id') and self.selected_company_id:
            c_name = self.db.get_company_name_by_id(self.selected_company_id)
            prods = self.db.get_user_products(self.current_user_id, self.selected_company_id)
            company_products = []
            
            for p in prods:
                company_products.append({
                    'name': str(p[3] or '-'),
                    'type': str(p[4] or '-'),
                    'count': str(p[5] or '0').replace(' Adet', '').strip(),
                    'price': str(p[6] or '0').replace(' ₺', '').strip(),
                    'total': str(p[7] or '0').replace(' ₺', '').strip(),
                    'barcode': str(p[8] or '-'),
                    'date': str(p[9] or '-')
                })
            
            export_data.append({
                'company_name': c_name,
                'products': company_products
            })

        if not export_data:
            print('Aktarılacak firma veya ürün verisi bulunamadı!')
            return

        if format_type == 'Pdf':
            self.db.simple_pdf_export_grouped(custom_data=export_data)
            print('Gruplandırılmış PDF raporu başarıyla oluşturuldu!')
        elif format_type == 'Excel':
            # Gruplanmış veriyi Excel'in yutabileceği düz listeye çeviriyoruz:
            flat_excel_list = []
            for item in export_data:
                c_name = item.get('company_name', 'Firma')
                for p in item.get('products', []):
                    flat_excel_list.append((
                        c_name,
                        p.get('name', '-'),
                        p.get('type', '-'),
                        p.get('count', '0'),
                        p.get('price', '0'),
                        p.get('total', '0'),
                        p.get('barcode', '-'),
                        p.get('date', '-')
                    ))
            
            self.db.simple_excel_export(custom_data=flat_excel_list)
            print('Excel raporu başarıyla oluşturuldu!')

        # Spinner seçimini sıfırla
        current_screen = self.root.current_screen
        if current_screen and hasattr(current_screen, 'walk'):
            for widget in current_screen.walk():
                if isinstance(widget, Spinner) and ('Excel' in widget.values or 'Pdf' in widget.values):
                    widget.text = 'Kayıt Formatı'
                    break


    def build(self):
        self.db = Database()
        self.current_user_id = None
        self.selected_product_id = None
        self.selected_company_id = None
        
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(CenterScreen(name='center'))
        self.sm.add_widget(InsertProductScreen(name='insertproduct'))
        self.sm.add_widget(UpdateProductScreen(name='updateproduct'))
        self.sm.add_widget(FilterScreen(name='filterproduct'))
        self.sm.add_widget(ProductDetailScreen(name="productdetails"))
        self.sm.add_widget(InsertCompanyScreen(name="insertcompany"))

        return self.sm

 
if __name__ == '__main__':
    ProSetManApp().run()