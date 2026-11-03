[app]
title = 幽灵娃娃
package.name = hanzigame
package.domain = org.test
source.dir = .
version = 1.0
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

# 锁定 jnius 版本，防止 C 接口报错
requirements = python3,kivy,jnius>=1.4.0

# 关键：只打包 arm64-v8a，内存占用直接减半，且兼容绝大多数现代手机
android.archs = arm64-v8a

# 同意协议 & 关键版本设定
android.accept_sdk_license = True
android.skip_update = False
android.ndk_api = 21
android.ndk = 25b
android.api = 33
android.minapi = 21
