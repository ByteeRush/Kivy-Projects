[app]

title = Hesap Makinesi
package.name = hesapmakinesi
package.domain = com.hesapmakinesi
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# --- EKLEMEN GEREKEN KRİTİK AYARLAR ---
android.api = 33
android.minapi = 24
android.ndk = 25b
# -------------------------------------

[buildozer]
log_level = 2
warn_on_root = 1
