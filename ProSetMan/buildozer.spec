 #

# It largely follows the syntax of an .ini file.

# See the end of the file for more details and warnings about common mistakes.


[app]


# (str) Title of your application

title = ProSetMan


# (str) Package name

package.name = prosetman


# (str) Package domain (needed for android/ios packaging)

package.domain = org.prosetman


# (str) Source code where the main.py live

source.dir = .


# (list) Source files to include (leave empty to include all the files)

source.include_exts = py,png,jpg,kv,atlas,ttf


# (list) List of inclusions using pattern matching (Lokal kütüphaneler ve assetler dahil edildi)

source.include_patterns = assets/*,images/*,reportlab/*,openpyxl/*,defusedxml/*,et_xmlfile/*,materials/*,plyer/*



# (list) Source files to exclude (leave empty to not exclude anything)

#source.exclude_exts = spec


# (list) List of directory to exclude (leave empty to not exclude anything)

#source.exclude_dirs = tests, bin, venv


# (list) List of exclusions using pattern matching

# Do not prefix with './'

#source.exclude_patterns = license,images/*/*.jpg


# (str) Application versioning (method 1)

version = 0.1


# (str) Application versioning (method 2)

# version.regex = __version__ = ['"](.*)['"]

# version.filename = %(source.dir)s/main.py


# (list) Application requirements (PIL/pillow p4a tarafından Android için derlenecek, diğerleri lokalden gelecek)

requirements = python3,kivy,sqlite3,pillow


# (str) Custom source folders for requirements

# Sets custom source for any requirements with recipes

# requirements.source.kivy = ../../kivy


# (str) Presplash of the application

#presplash.filename = %(source.dir)s/data/presplash.png


# (str) Icon of the application

#icon.filename = %(source.dir)s/data/icon.png


# (list) Supported orientations

orientation = all


# (list) List of services to declare

#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY


#

# OSX Specific

#


# author = © Copyright Info


# Kivy version to use

osx.kivy_version = 2.2.0


#

# Android specific

#


# (bool) Indicate if the application should be fullscreen or not

fullscreen = 0


# (string) Presplash background color (for android toolchain)

#android.presplash_color = #FFFFFF


# (string) Presplash animation using Lottie format.

#android.presplash_lottie = "path/to/lottie/file.json"


# (str) Adaptive icon of the application (used if Android API level is 26+ at runtime)

#icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png

#icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png


# (list) Permissions

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, CAMERA, RECORD_AUDIO, MODIFY_AUDIO_SETTINGS, ACCESS_NETWORK_STATE, WAKE_LOCK


# (list) features (adds uses-feature -tags to manifest)

#android.features = android.hardware.usb.host


# (int) Target Android API, should be as high as possible.

android.api = 34


# (int) Minimum API your APK / AAB will support.

android.minapi = 24


# (int) Android SDK version to use

#android.sdk = 20


# (str) Android NDK version to use

#android.ndk = 23b


# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.

#android.ndk_api = 21


# (str) Android NDK directory (if empty, it will be automatically downloaded.)

#android.ndk_path =


# (str) Android SDK directory (if empty, it will be automatically downloaded.)

#android.sdk_path =


# (str) ANT directory (if empty, it will be automatically downloaded.)

#android.ant_path =


# (bool) If True, then skip trying to update the Android SDK

# android.skip_update = False


# (bool) If True, then automatically accept SDK license agreements

# android.accept_sdk_license = False


# (str) Android entry point, default is ok for Kivy-based app

#android.entrypoint = org.kivy.android.PythonActivity


# (str) Full name including package path of the Java class that implements Android Activity

#android.activity_class_name = org.kivy.android.PythonActivity


# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml

#android.extra_manifest_xml = ./src/android/extra_manifest.xml


# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml

#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml


# (str) Full name including package path of the Java class that implements Python Service

#android.service_class_name = org.kivy.android.PythonService


# (str) Android app theme, default is ok for Kivy-based app

# android.apptheme = "@android:style/Theme.NoTitleBar"


# (list) Pattern to whitelist for the whole project

#android.whitelist =


# (bool) If True, your application will be listed as a home app (launcher app)

# android.home_app = False


# (str) Path to a custom whitelist file

#android.whitelist_src =


# (str) Path to a custom blacklist file

#android.blacklist_src =


# (list) List of Java .jar files to add to the libs so that pyjnius can access their classes.

#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar


# (list) List of Java files to add to the android project

#android.add_src =


# (list) Android AAR archives to add

#android.add_aars =


# (list) Put these files or directories in the apk assets directory.

#android.add_assets =


# (list) Put these files or directories in the apk res directory.

#android.add_resources =


# (list) Gradle dependencies to add

#android.gradle_dependencies =


# (bool) Enable AndroidX support.

#android.enable_androidx = True


# (list) add java compile options

# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"


# (list) Gradle repositories to add

#android.add_gradle_repositories =


# (list) packaging options to add

#android.add_packaging_options = "exclude 'META-INF/common.kotlin_module'", "exclude 'META-INF/*.kotlin_module'"


# (list) Java classes to add as activities to the manifest.

#android.add_activities = com.example.ExampleActivity


# (str) OUYA Console category. Should be one of GAME or APP

#android.ouya.category = GAME


# (str) Filename of OUYA Console icon. It must be a 732x412 png image.

#android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png


# (str) XML file to include as an intent filters in <activity> tag

#android.manifest.intent_filters =


# (list) Copy these files to src/main/res/xml/

#android.res_xml = PATH_TO_FILE,


# (str) launchMode to set for the main activity

#android.manifest.launch_mode = standard


# (str) screenOrientation to set for the main activity.

#android.manifest.orientation = fullSensor


# (list) Android additional libraries to copy into libs/armeabi

#android.add_libs_armeabi = libs/android/*.so

#android.add_libs_armeabi_v7a = libs/android-v7/*.so

#android.add_libs_arm64_v8a = libs/android-v8/*.so

#android.add_libs_x86 = libs/android-x86/*.so

#android.add_libs_mips = libs/android-mips/*.so


# (bool) Indicate whether the screen should stay on

#android.wakelock = False


# (list) Android application meta-data to set (key=value format)

#android.meta_data =


# (list) Android library project to add

#android.library_references =


# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag

#android.uses_library =


# (str) Android logcat filters to use

#android.logcat_filters = *:S python:D


# (bool) Android logcat only display log for activity's pid

#android.logcat_pid_only = False


# (str) Android additional adb arguments

#android.adb_args = -H host.docker.internal


# (bool) Copy library instead of making a libpymodules.so

#android.copy_libs = 1


# (list) The Android archs to build for

android.archs = arm64-v8a, armeabi-v7a


# (int) overrides automatic versionCode computation

# android.numeric_version = 1


# (bool) enables Android auto backup feature (Android API >=23)

android.allow_backup = True


# (str) XML file for custom backup rules

# android.backup_rules =


# (str) manifestPlaceholders property

# android.manifest_placeholders = [:]


# (bool) Skip byte compile for .py files

# android.no-byte-compile-python = False


# (str) The format used to package the app for release mode

# android.release_artifact = aab


# (str) The format used to package the app for debug mode

# android.debug_artifact = apk


# (str) A display cutout is an area on some devices that extends into the display surface.

#android.display_cutout = never


#

# Python for android (p4a) specific

#


# (str) python-for-android URL to use for checkout

#p4a.url =


# (str) python-for-android fork to use

p4a.fork = kivy


# (str) python-for-android branch to use

p4a.branch = develop


# (str) python-for-android specific commit to use

#p4a.commit = HEAD


# (str) python-for-android git clone directory

#p4a.source_dir =


# (str) The directory in which python-for-android should look for your own build recipes

#p4a.local_recipes =


# (str) Filename to the hook for p4a

#p4a.hook =


# (str) Bootstrap to use for android builds

#p4a.bootstrap = sdl2


# (int) port number to specify an explicit --port= p4a argument

#p4a.port =


#p4a.setup_py = false


# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain

p4a.extra_args = 


#

# iOS specific

#


ios.kivy_ios_url = https://github.com/kivy/kivy-ios

ios.kivy_ios_branch = master


ios.ios_deploy_url = https://github.com/phonegap/ios-deploy

ios.ios_deploy_branch = 1.12.2


ios.codesign.allowed = false


[buildozer]


# (int) log_level (0 = error only, 1 = info, 2 = debug)

log_level = 2


# (int) warn_on_root (0 = False, 1 = True)

warn_on_root = 1


# build_dir = ./.buildozer

# bin_dir = ./bin 