[app]
title = 幽灵娃娃
package.name = hanzigame
package.domain = org.test
source.dir = .
version = 1.0
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

# 锁定jnius版本，并只打包arm64-v8a架构，大幅降低编译内存峰值
requirements = python3,kivy,jnius>=1.4.0
android.archs = arm64-v8a

# 核心修复：自动同意协议 & 设置NDK API为21
android.accept_sdk_license = True
android.skip_update = False
android.ndk_api = 21

# 安卓基础配置
android.api = 33
android.minapi = 21
android.ndk = 25b
