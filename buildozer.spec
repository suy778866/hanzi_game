[app]
title = 幽灵娃娃
package.name = hanzigame
package.domain = org.test
source.dir = .
version = 1.0
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json
requirements = python3,kivy

# 核心修复：让系统自动同意 Android SDK 协议
android.accept_sdk_license = True
android.skip_update = False

# 安卓架构和 API 级别
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 如果需要网络权限，把下面这行的 # 去掉
# android.permissions = INTERNET
