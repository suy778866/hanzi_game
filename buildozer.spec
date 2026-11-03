[app]
title = 幽灵娃娃
package.name = hanzigame
package.domain = org.test
source.dir = .
version = 1.0
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

requirements = python3,kivy,jnius>=1.4.0
android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False
android.ndk_api = 21
android.ndk = 25b
android.api = 33
android.minapi = 21
