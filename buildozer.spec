[app]

# 你的游戏名字（手机上显示的名字）
title = 幽灵娃娃

# 包名（只能小写字母和数字）
package.name = hanzigame

# 域名反写
package.domain = org.test

# 【关键】告诉 Buildozer 当前目录就是源码目录
source.dir = .

# 资源扩展名
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

# 版本号
version = 1.0

# 依赖
requirements = python3,kivy

# 安卓配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 如果你游戏需要联网，把下面这行前面的 # 删掉
# android.permissions = INTERNET
