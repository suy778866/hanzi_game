[app]
title = 幽灵娃娃
package.name = hanzigame
package.domain = org.test
source.dir = .
version = 1.0
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

# 锁定 jnius 版本，防止 C 接口报错
requirements = python3,kivy,jnius>=1.4.0

# ！！！关键：只打包 arm64-v8a，内存占用直接减半！！！
android.archs = arm64-v8a

# 协议和 NDK 版本
android.accept_sdk_license = True
android.skip_update = False
android.ndk_api = 21

# 基础配置
android.api = 33
android.minapi = 21
android.ndk = 25b
