[app]

# ---------------------------------------------------------------------
# Informações da aplicação
# ---------------------------------------------------------------------

title = Gestor de Voo

package.name = gestordevoo

package.domain = org.adilson

source.dir = .

version = 1.0.0

#
# Ficheiros incluídos no APK
#

source.include_exts = py,kv,png,jpg,atlas,json,ttf

#
# Pastas que NÃO devem entrar no APK
#

source.exclude_dirs = tests,bin,venv,.venv,.git,__pycache__,build,.idea

#
# Requisitos
#

requirements = python3,kivy,kivymd

#
# Orientação
#

orientation = landscape

#
# Tela cheia
#

fullscreen = 1

#
# Ícone (adicionar futuramente)
#

#icon.filename = icon.png

#
# Splash Screen (adicionar futuramente)
#

#presplash.filename = presplash.png



# ---------------------------------------------------------------------
# Android
# ---------------------------------------------------------------------

android.api = 34

android.minapi = 24

android.ndk = 27b

android.ndk_api = 24

android.archs = arm64-v8a

android.allow_backup = True

android.enable_androidx = True

android.debug_artifact = apk

android.release_artifact = apk

#
# Sem permissões por enquanto
#

android.permissions =

#
# Armazenamento privado
#

android.private_storage = True



# ---------------------------------------------------------------------
# Buildozer
# ---------------------------------------------------------------------

[buildozer]

log_level = 2

warn_on_root = 1