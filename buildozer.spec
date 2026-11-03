[app]

# 你的游戏名字（手机上显示的名字）
title = 幽灵娃娃

# 包名（只能小写字母和数字，别加空格）
package.name = hanzigame

# 域名反写（随便写个英文就行）
package.domain = org.test

# 版本号
version = 1.0

# 资源扩展名（我帮你把常见的都列进去了）
source.include_exts = py,png,jpg,kv,atlas,wav,ogg,mp3,ttf,json

# 依赖
requirements = python3,kivy

# 安卓配置
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

# 如果你游戏需要联网，把下面这行前面的 # 删掉
# android.permissions = INTERNET