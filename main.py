import os
import random
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.behaviors import DragBehavior

Window.size = (960, 540)
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

# ----------------- 用于全屏遮挡但允许触摸穿透的布局 -----------------
class FeedSceneLayout(FloatLayout):
    def on_touch_down(self, touch):
        if self.disabled: return False
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.disabled: return False
        return super().on_touch_up(touch)

# ----------------- 可拖拽的道具组件 -----------------
class DraggableItem(DragBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_rectangle = (0, 0, 2000, 2000)
        self.original_pos = (0, 0)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            if app and hasattr(app, 'sm'):
                sm = app.sm
                if sm and sm.current == "game":
                    game_screen = sm.get_screen("game")
                    if not game_screen.ending_triggered and not game_screen.good_ending_triggered:
                        if self.collide_widget(game_screen.doll_canvas):
                            if "knife" in self.source:
                                game_screen.on_hit()
                            elif "fries" in self.source or "food" in self.source:
                                game_screen.on_feed()

        super().on_touch_up(touch)
        self.pos = self.original_pos

# ----------------- 黑屏 / 红屏 / 白屏 过渡遮罩 -----------------
class FadeOverlay(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.disabled = True 
        with self.canvas:
            self.color = Color(0, 0, 0, 1) # 默认黑色，保存引用以便修改
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.disabled: return False
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.disabled: return False
        return super().on_touch_up(touch)

# ----------------- 开始界面 -----------------
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bg = Image(source="assets/bg.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)
        title = Image(source="assets/title.png", size_hint=(None, None), size=(dp(320), dp(220)), pos_hint={"x": 0.02, "top": 0.98} )
        self.add_widget(title)
        self.btn_start = Button(background_normal="assets/btn_start.png", background_down="assets/btn_start.png", size_hint=(None, None), size=(dp(220), dp(75)), pos_hint={"x": 0.05, "center_y": 0.40})
        self.btn_start.bind(on_release=self.on_start)
        self.add_widget(self.btn_start)
        self.btn_bye = Button(background_normal="assets/btn_bye.png", background_down="assets/btn_bye.png", size_hint=(None, None), size=(dp(220), dp(75)), pos_hint={"x": 0.05, "center_y": 0.20})
        self.btn_bye.bind(on_release=self.on_bye)
        self.add_widget(self.btn_bye)
        doll = Image(source="assets/doll.png", size_hint=(None, None), size=(dp(300), dp(300)), pos_hint={"right": 0.95, "y": 0.05})
        self.add_widget(doll)
        self.ghost = Image(source="assets/ghost.png", size_hint=(None, None), size=(dp(180), dp(180)), pos_hint={"center_x": 0.6, "center_y": 0.65} )
        self.add_widget(self.ghost)
        Clock.schedule_interval(self.float_ghost, 1.5)

    def float_ghost(self, dt):
        current_y = self.ghost.pos_hint["center_y"]
        target_y = current_y - 0.02 if current_y > 0.65 else current_y + 0.02
        Animation(pos_hint={"center_y": target_y}, duration=1.5, transition="in_out_sine").start(self.ghost)

    def on_start(self, *args):
        App.get_running_app().fade_to_screen("intro")
    def on_bye(self, *args):
        App.get_running_app().stop()

# ----------------- 开场剧情界面 (701) -----------------
class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bg = Image(source="assets/bg_room.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(bg)
        self.actor = Image(source="assets/701_close.png", size_hint=(None, None), size=(dp(400), dp(400)), pos_hint={"center_x": 0.5, "center_y": 0.6})
        self.add_widget(self.actor)
        self.item_fries = Image(source="assets/item_fries.png", size_hint=(None, None), size=(dp(120), dp(120)), opacity=0, pos_hint={"center_x": 0.7, "center_y": 0.55})
        self.add_widget(self.item_fries)
        self.item_knife = Image(source="assets/item_knife.png", size_hint=(None, None), size=(dp(120), dp(120)), opacity=0, pos_hint={"center_x": 0.3, "center_y": 0.55})
        self.add_widget(self.item_knife)
        self.box_outer = FloatLayout(size_hint=(0.9, 0.35), pos_hint={"center_x": 0.5, "y": 0.05})
        with self.box_outer.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=self.box_outer.pos, size=self.box_outer.size)
        self.box_inner = FloatLayout(size_hint=(0.98, 0.92), pos_hint={"center_x": 0.5, "center_y": 0.5})
        with self.box_inner.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=self.box_inner.pos, size=self.box_inner.size)
        self.box_outer.add_widget(self.box_inner)
        self.name_label = Label(text="701", font_name=FONT_PATH, font_size=dp(28), color=(1, 1, 1, 1), size_hint=(None, None), size=(dp(100), dp(40)), pos_hint={"x": 0.05, "top": 1.1})
        self.box_outer.add_widget(self.name_label)
        self.dialogue_label = Label(text="", font_name=FONT_PATH, font_size=dp(24), color=(1, 1, 1, 1), halign="left", valign="middle", size_hint=(0.9, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.dialogue_label.bind(size=self.dialogue_label.setter("text_size"))
        self.box_inner.add_widget(self.dialogue_label)
        self.add_widget(self.box_outer)
        self.dialogues = ["现实生活压力太大了吧", "我有些好玩的东西，你可以试试看", "面对这个娃娃，给她喂食，或者虐待她，都可以获得升级道具", "现在就看你怎么想的了，虐待娃娃获得的资金更多哦"]
        self.current_index = 0
        self.click_area = Button(background_color=(0, 0, 0, 0), size_hint=(1, 1))
        self.click_area.bind(on_release=self.next_dialogue)
        self.add_widget(self.click_area)

    def on_enter(self, *args):
        self.current_index = 0
        self.item_fries.opacity = 0
        self.item_knife.opacity = 0
        self.update_dialogue()

    def update_dialogue(self):
        if self.current_index < len(self.dialogues):
            self.dialogue_label.text = self.dialogues[self.current_index]
            self.actor.source = "assets/701_open.png"
            if self.current_index == 1: Animation(opacity=1, duration=0.5).start(self.item_fries)
            elif self.current_index == 2: Animation(opacity=1, duration=0.5).start(self.item_knife)
        else:
            App.get_running_app().fade_to_screen("game")

    def next_dialogue(self, *args):
        if self.current_index < len(self.dialogues):
            self.current_index += 1
            self.actor.source = "assets/701_close.png"
            self.update_dialogue()

# ================= 核心主界面 =================
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg = Image(source="assets/bg_room.png", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)

        # --- 核心数值 ---
        self.money = 0
        self.knife_level = 1
        self.hit_count = 0
        
        # --- 喂食线与净化系统变量 ---
        self.feed_count = 0
        self.abuse_in_feed_mode = 0
        self.has_new_food = False
        self.portal_active = False
        self.is_in_feed_scene = False
        self.desire_food_btn = None
        
        # --- 第二次净化（暴躁）变量 ---
        self.second_portal_active = False
        self.has_angry_food = False

        # --- 第三次净化（独特）变量 ---
        self.third_portal_active = False
        self.has_unique_food = False

        # --- 第四次净化（拉风）变量 ---
        self.fourth_portal_active = False
        self.has_lafeng_food = False

        # --- 第五次净化（管家）变量 ---
        self.fifth_portal_active = False
        self.has_butler_food = False

        # --- 第六次净化（k治）变量 ---
        self.sixth_portal_active = False
        self.has_kzhi_food = False

        # --- 喂食专属发言变量 ---
        self.feed_count_10_triggered = False
        self.good_ending_triggered = False

        # 黑化系统变量
        self.total_abuse = 0
        self.is_dark_20 = False
        self.is_dark_40 = False
        self.is_dark_70 = False
        self.is_dark_100 = False
        self.is_dark_120 = False
        self.is_dark_150 = False
        self.is_dark_170 = False
        
        # 结局系统变量
        self.ending_triggered = False
        self.ending_actor = None

        # 记录当前活动的干扰对话框
        self._active_box = None

        # 台词库
        self.egg_texts = [
            "虐待是一种很好的情绪发泄点",
            "压力大的时候，有没有想过砸东西呢，或者，杀死一些小生命？",
            "她不是活的，大概吧，放心玩好啦",
            "如果你掌握一只兔子的命运，你希望看到兔子死掉还是活的很幸福？",
            "这破破烂烂的娃娃",
            "用力打她，有没有感觉到解压？"
        ]

        self.hanzi_lines = [
            "停下…停下…", "为什么", "是谁蛊惑了你吗", "你能得到什么",
            "我不明白", "这对你的意义是什么", "也许有更好的方式"
        ]

        self.seven_lines = [
            "你只能选这个", "相信我", "难道你意识不到你已经不能控制选项了吗",
            "我来帮你吧", "没办法，哈哈哈，她也许生气了",
            "只是人工智能而已，她只是个娃娃", "很简单，我帮你搞定"
        ]

        self.knife_costs = {2: 100, 3: 150, 4: 200, 5: 250, 6: 300, 7: 450}
        self.food_level = 1
        self.food_costs = {2: 50, 3: 70, 4: 100, 5: 200, 6: 250, 7: 300}

        # --- UI: 左上角金币区 ---
        self.money_bg = Image(source="assets/ui_money_bg.png", size_hint=(None, None), size=(dp(260), dp(100)), pos_hint={"x": 0.02, "top": 0.98})
        self.add_widget(self.money_bg)
        self.money_label = Label(text="0", font_name=FONT_PATH, font_size=dp(42), color=(0.1, 0.1, 0.1, 1), size_hint=(None, None), size=(dp(150), dp(60)), pos_hint={"x": 0.11, "top": 0.95}, halign="center", valign="middle")
        self.money_label.bind(size=self.money_label.setter('text_size'))
        self.add_widget(self.money_label)

        # --- UI: 左侧虐杀升级区 ---
        self.btn_up_knife = Button(background_normal="assets/ui_up_knife.png", background_down="assets/ui_up_knife.png", size_hint=(None, None), size=(dp(120), dp(120)), pos_hint={"x": 0.02, "center_y": 0.65})
        self.btn_up_knife.bind(on_release=self.on_upgrade_knife)
        self.add_widget(self.btn_up_knife)
        self.lbl_knife = Label(text="虐杀 Lv.1\n升级需 100", font_name=FONT_PATH, font_size=dp(20), color=(1, 1, 1, 1), halign="center", size_hint=(None, None), size=(dp(150), dp(60)), pos_hint={"x": 0.01, "center_y": 0.5})
        self.add_widget(self.lbl_knife)

        # --- UI: 右侧喂食升级区 ---
        self.btn_up_food = Button(background_normal="assets/ui_up_food.png", background_down="assets/ui_up_food.png", size_hint=(None, None), size=(dp(120), dp(120)), pos_hint={"right": 0.98, "center_y": 0.65})
        self.btn_up_food.bind(on_release=self.on_upgrade_food)
        self.add_widget(self.btn_up_food)
        self.lbl_food = Label(text="喂食 Lv.1\n升级需 50", font_name=FONT_PATH, font_size=dp(20), color=(1, 1, 1, 1), halign="center", size_hint=(None, None), size=(dp(150), dp(60)), pos_hint={"right": 0.99, "center_y": 0.5})
        self.add_widget(self.lbl_food)

        # --- 娃娃画布 ---
        self.doll_canvas = FloatLayout(size_hint=(None, None), size=(500, 500), pos_hint={"center_x": 0.5, "center_y": 0.5})

        self.hair_back = Image(source="assets/doll_hair_back.png", size_hint=(None, None), size=(500, 500), pos_hint={"center_x": 0.5, "center_y": 0.42})
        self.hand_l = Image(source="assets/doll_hand_left.png", size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.33, "center_y": 0.2})
        self.hand_r = Image(source="assets/doll_hand_right.png", size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.65, "center_y": 0.2})
        self.body = Image(source="assets/doll_body.png", size_hint=(None, None), size=(200, 200), pos_hint={"center_x": 0.5, "center_y": 0.22})
        self.foot_l = Image(source="assets/doll_foot_left.png", size_hint=(None, None), size=(150, 150), pos_hint={"center_x": 0.4, "center_y": 0.1})
        self.foot_r = Image(source="assets/doll_foot_right.png", size_hint=(None, None), size=(150, 150), pos_hint={"center_x": 0.6, "center_y": 0.1})
        self.hair_front = Image(source="assets/doll_hair_front.png", size_hint=(None, None), size=(500, 500), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.face = Image(source="assets/doll_face.png", size_hint=(None, None), size=(150, 150), pos_hint={"center_x": 0.51, "center_y": 0.45})

        self.doll_whole = Image(source="assets/doll_whole_dark6.png", size_hint=(None, None), size=(500, 500), pos_hint={"center_x": 0.5, "center_y": 0.5}, opacity=0)

        self.doll_canvas.add_widget(self.hair_back)
        self.doll_canvas.add_widget(self.hand_l)
        self.doll_canvas.add_widget(self.hand_r)
        self.doll_canvas.add_widget(self.body)
        self.doll_canvas.add_widget(self.foot_l)
        self.doll_canvas.add_widget(self.foot_r)
        self.doll_canvas.add_widget(self.hair_front)
        self.doll_canvas.add_widget(self.face)
        self.doll_canvas.add_widget(self.doll_whole)
        self.add_widget(self.doll_canvas)

        # 底部道具
        self.drag_fries = DraggableItem(source="assets/item_fries.png", size_hint=(None, None), size=(dp(100), dp(100)), pos=(100, 30))
        self.drag_fries.original_pos = (100, 30)
        self.add_widget(self.drag_fries)

        self.drag_knife = DraggableItem(source="assets/item_knife.png", size_hint=(None, None), size=(dp(100), dp(100)), pos=(250, 30))
        self.drag_knife.original_pos = (250, 30)
        self.add_widget(self.drag_knife)

        # --- 传送门与欲望场景 ---
        self.ghost_portal = Image(source="assets/ghost_portal.png", size_hint=(None, None), size=(dp(120), dp(120)), pos_hint={"right": 0.9, "center_y": 0.5}, opacity=0)
        self.ghost_portal.bind(on_touch_down=self.on_portal_click)
        self.add_widget(self.ghost_portal)

        # 使用 FeedSceneLayout 替代 FloatLayout，防止挡住触摸
        self.feed_scene = FeedSceneLayout()
        self.feed_scene_bg = Image(source="assets/bg_desire.png", allow_stretch=True, keep_ratio=False)
        self.feed_scene_actor = Image(source="assets/desire_character.png", size_hint=(None, None), size=(dp(400), dp(400)), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.btn_back = Button(background_normal="assets/btn_back.png", background_down="assets/btn_back.png", size_hint=(None, None), size=(dp(100), dp(100)), pos_hint={"x": 0.05, "center_y": 0.5})
        self.btn_back.bind(on_release=self.leave_portal)
        self.feed_scene.add_widget(self.feed_scene_bg)
        self.feed_scene.add_widget(self.feed_scene_actor)
        self.feed_scene.add_widget(self.btn_back)
        self.feed_scene.opacity = 0
        self.feed_scene.disabled = True
        self.add_widget(self.feed_scene)

        # --- 好结局结束时的退出键 (★ 初始大小为0防遮挡) ---
        self.exit_btn = Button(
            background_normal="assets/exit_icon.png", 
            background_down="assets/exit_icon.png", 
            size_hint=(None, None), size=(0, 0), 
            pos_hint={"x": 0.05, "center_y": 0.5}, 
            opacity=0, disabled=True
        )
        self.exit_btn.bind(on_release=self.on_exit_click)
        self.add_widget(self.exit_btn)

        # 开启上下缓慢浮动
        Clock.schedule_interval(self.float_portal, 2.0)
        Clock.schedule_interval(self.float_desire, 2.8)  # 欲望较慢
        Clock.schedule_interval(self.float_back_btn, 2.0) # 返回键较快
        Clock.schedule_interval(self.float_exit_btn, 2.0) # 退出键浮动

    def float_portal(self, dt):
        current_y = self.ghost_portal.pos_hint["center_y"]
        target_y = current_y - 0.03 if current_y >= 0.5 else current_y + 0.03
        Animation(pos_hint={"center_y": target_y}, duration=2.0, transition="in_out_sine").start(self.ghost_portal)

    def float_desire(self, dt):
        current_y = self.feed_scene_actor.pos_hint["center_y"]
        target_y = current_y - 0.03 if current_y >= 0.5 else current_y + 0.03
        Animation(pos_hint={"center_y": target_y}, duration=2.8, transition="in_out_sine").start(self.feed_scene_actor)

    def float_back_btn(self, dt):
        current_y = self.btn_back.pos_hint["center_y"]
        target_y = current_y - 0.04 if current_y >= 0.5 else current_y + 0.04
        Animation(pos_hint={"center_y": target_y}, duration=2.0, transition="in_out_sine").start(self.btn_back)

    def float_exit_btn(self, dt):
        if self.exit_btn.opacity <= 0: return
        current_y = self.exit_btn.pos_hint["center_y"]
        target_y = current_y - 0.04 if current_y >= 0.5 else current_y + 0.04
        Animation(pos_hint={"center_y": target_y}, duration=2.0, transition="in_out_sine").start(self.exit_btn)

    # --- 虐杀升级逻辑 ---
    def on_upgrade_knife(self, *args):
        if self.ending_triggered or self.is_in_feed_scene or self.good_ending_triggered: return
        next_level = self.knife_level + 1
        if next_level in self.knife_costs:
            cost = self.knife_costs[next_level]
            if self.money >= cost:
                self.money -= cost
                self.knife_level += 1
                self.money_label.text = str(self.money)

                earn = 5 * (2 ** (self.knife_level - 1))
                if (next_level+1) in self.knife_costs:
                    self.lbl_knife.text = f"虐杀 Lv.{self.knife_level} (赚 {earn})\n升级需 {self.knife_costs[next_level+1]}"
                else:
                    self.lbl_knife.text = f"虐杀 Lv.{self.knife_level} (赚 {earn})\n已满级"
            else:
                print("钱不够升级刀！")

    # --- 喂食升级逻辑 ---
    def on_upgrade_food(self, *args):
        if self.ending_triggered or self.is_in_feed_scene or self.good_ending_triggered: return
        if self.total_abuse >= 10: return
        if self.has_new_food and self.abuse_in_feed_mode >= 5: return
        next_level = self.food_level + 1
        if next_level in self.food_costs:
            cost = self.food_costs[next_level]
            if self.money >= cost:
                self.money -= cost
                self.food_level += 1
                self.money_label.text = str(self.money)

                if (next_level+1) in self.food_costs:
                    self.lbl_food.text = f"喂食 Lv.{self.food_level} (赚 {self.food_level})\n升级需 {self.food_costs[next_level+1]}"
                else:
                    self.lbl_food.text = f"喂食 Lv.{self.food_level} (赚 {self.food_level})\n已满级"
            else:
                print("钱不够升级薯条！")

    # --- 队列发言函数（用于固定连播剧情） ---
    def play_dialogue_queue(self, name, lines, interval=3.0, start_delay=0.5):
        delay = start_delay
        for line in lines:
            def _show_line(dt, l=line):
                if not self.good_ending_triggered and not self.ending_triggered:
                    self.show_interference_box(name, l)
            Clock.schedule_once(_show_line, delay)
            delay += interval

    # --- 喂食逻辑 ---
    def on_feed(self):
        if self.ending_triggered or self.is_in_feed_scene or self.good_ending_triggered: return
        if self.total_abuse >= 10: return
        if self.has_new_food and self.abuse_in_feed_mode >= 5: return
        
        self.feed_count += 1
        
        # 喂食达到10次，触发固定发言
        if self.feed_count == 10 and not self.feed_count_10_triggered:
            self.feed_count_10_triggered = True
            lines = [
                "谢谢你，但，我还是很不舒服",
                "你会一直这样做吗",
                "我很害怕",
                "这些食物，我感觉，有问题"
            ]
            self.play_dialogue_queue("涵子", lines)

        # 第一次喂食净化触发 (40次)
        if self.feed_count == 40 and not self.has_new_food:
            self.portal_active = True
            self.ghost_portal.opacity = 1
            
        # 第二次喂食净化触发 (60次)
        if self.feed_count == 60 and self.has_new_food and not self.has_angry_food and not self.second_portal_active:
            self.second_portal_active = True
            self.ghost_portal.opacity = 1

        # 第三次喂食净化触发 (80次)
        if self.feed_count == 80 and self.has_angry_food and not self.has_unique_food and not self.third_portal_active:
            self.third_portal_active = True
            self.ghost_portal.opacity = 1

        # 第四次喂食净化触发 (100次)
        if self.feed_count == 100 and self.has_unique_food and not self.has_lafeng_food and not self.fourth_portal_active:
            self.fourth_portal_active = True
            self.ghost_portal.opacity = 1
            
        # 第五次喂食净化触发 (120次)
        if self.feed_count == 120 and self.has_lafeng_food and not self.has_butler_food and not self.fifth_portal_active:
            self.fifth_portal_active = True
            self.ghost_portal.opacity = 1

        # 第六次喂食净化触发 (160次)
        if self.feed_count == 160 and self.has_butler_food and not self.has_kzhi_food and not self.sixth_portal_active:
            self.sixth_portal_active = True
            self.ghost_portal.opacity = 1

        # 触发喂食线好结局（获取k治食物后再喂食40次，即总喂食量200）
        if self.has_kzhi_food and self.feed_count == 200:
            self.trigger_good_ending()
            return

        earned_money = self.food_level
        self.money += earned_money
        self.money_label.text = str(self.money)

        anim = (Animation(pos_hint={"center_x": 0.5, "center_y": 0.52}, duration=0.1) +
                Animation(pos_hint={"center_x": 0.5, "center_y": 0.5}, duration=0.15))
        anim.start(self.doll_canvas)

        # 表情替换逻辑：优先级 k治 > 管家 > 拉风 > 独特 > 暴躁 > 生病
        if self.has_kzhi_food:
            self.face.source = "assets/doll_face_kzhi.png"
        elif self.has_butler_food:
            self.face.source = "assets/doll_face_butler.png"
        elif self.has_lafeng_food:
            self.face.source = "assets/doll_face_lafeng.png"
        elif self.has_unique_food:
            self.face.source = "assets/doll_face_unique.png"
        elif self.has_angry_food:
            self.face.source = "assets/doll_face_angry.png"
        elif self.has_new_food:
            self.face.source = "assets/doll_face_sick.png"

        # 第二次净化后的随机发言（10%概率触发，好结局后会停止，每次只随机播放一句）
        if self.has_angry_food and random.randint(1, 100) <= 10 and not self.good_ending_triggered:
            lines = [
                "谢谢你…",
                "我感觉有什么东西在恢复",
                "你帮了我大忙",
                "你有喜欢的食物吗",
                "总感觉稍微有些活力了",
                "我感觉在期待什么东西的到来:3",
                "好舒服",
                "你想吃东西吗"
            ]
            random_line = random.choice(lines)
            self.show_interference_box("涵子", random_line)

    # --- 触发喂食线好结局 ---
    def trigger_good_ending(self):
        self.good_ending_triggered = True
        
        # 隐藏所有游戏主UI
        self.doll_canvas.opacity = 0
        self.btn_up_knife.opacity = 0
        self.btn_up_food.opacity = 0
        self.lbl_knife.opacity = 0
        self.lbl_food.opacity = 0
        self.money_bg.opacity = 0
        self.money_label.opacity = 0
        self.drag_fries.opacity = 0
        self.drag_knife.opacity = 0
        self.ghost_portal.opacity = 0
        
        # 清理可能存在的对话框
        if self._active_box:
            self.remove_widget(self._active_box)
            self._active_box = None

        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1) # 黑屏
        app.fade_overlay.opacity = 0
        
        # 黑屏转场动画
        anim_in = Animation(opacity=1, duration=0.8)
        anim_in.bind(on_complete=lambda *args: Clock.schedule_once(self.start_good_cutscene, 1.0))
        anim_in.start(app.fade_overlay)

    def start_good_cutscene(self, dt):
        app = App.get_running_app()
        self.bg.source = "assets/good_ending_1.png"
        
        # 黑屏淡出
        anim_out = Animation(opacity=0, duration=0.8)
        anim_out.bind(on_complete=lambda *args: setattr(app.fade_overlay, 'disabled', True))
        anim_out.start(app.fade_overlay)
        
        # 依次安排后续5张图的红屏跳跃
        imgs = [
            "assets/good_ending_2.png",
            "assets/good_ending_3.png",
            "assets/good_ending_4.png",
            "assets/good_ending_5.png",
            "assets/good_ending_6.png"
        ]
        
        delay = 3.0 # 第一张图停留3秒
        for img in imgs:
            Clock.schedule_once(lambda dt2, src=img: self.flash_to_good_bg(src), delay)
            delay += 3.0
            
        # 在最后一张图展示完后，执行白屏转场进入第二部分
        Clock.schedule_once(self.trigger_part2_white_transition, delay + 2.0)

    def flash_to_good_bg(self, source):
        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (1, 0, 0, 1) # 红屏
        app.fade_overlay.opacity = 0
        
        def switch_bg(dt2):
            self.bg.source = source
            anim_out = Animation(opacity=0, duration=0.4)
            anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)
            
        anim_in = Animation(opacity=1, duration=0.2)
        anim_in.bind(on_complete=lambda *a: Clock.schedule_once(switch_bg, 0.1))
        anim_in.start(app.fade_overlay)

    # --- 第一部分结局结束后（白屏跳转到第二部分） ---
    def trigger_part2_white_transition(self, dt):
        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (1, 1, 1, 1) # 白屏
        app.fade_overlay.opacity = 0
        
        def switch_bg(dt2):
            self.bg.source = "assets/good_end_scene_1.png"
            anim_out = Animation(opacity=0, duration=0.8)
            anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)
            # 开始播放第二部分剧情
            Clock.schedule_once(self.start_good_dialogue_part2, 0.5)
            
        anim_in = Animation(opacity=1, duration=0.5)
        anim_in.bind(on_complete=lambda *a: Clock.schedule_once(switch_bg, 0.2))
        anim_in.start(app.fade_overlay)

    def start_good_dialogue_part2(self, dt):
        stages = [
            ("assets/good_end_scene_1.png", [
                "谢谢你，如果不是你，我可能会一直被困在那里",
                "甚至更惨"
            ]),
            ("assets/good_end_scene_2.png", [
                "我永远摸不透701在想什么",
                "祂有时候其实不坏",
                "…"
            ]),
            ("assets/good_end_scene_3.png", [
                "但我没法保证",
                "也许只是手段而已"
            ]),
            ("assets/good_end_scene_4.png", [
                "哎呀，总的来说，谢谢你玩这个游戏",
                "这是我和梦境老师第一次尝试，所以弄得很简单",
                "嘻嘻嘻",
                "这段话会不会很突兀？",
                "总之感谢你的游玩！"
            ]),
            ("assets/good_end_scene_5.png", [
                "也谢谢你把我救了出来了，你太善良了吧",
                "顺带一提，梦境老师太厉害了，代码都是她写的"
            ]),
            ("assets/good_end_scene_6.png", [
                "啊，时间差不多了"
            ]),
            ("assets/good_end_scene_7.png", [
                "给你开一扇门，你可以离开游戏！",
                "下一次再见面，我可能又是一个被困住的娃娃了"
            ]),
            ("assets/good_end_scene_8.png", [
                "不管怎样，如果你玩的开心了，那就足够了",
                "拜拜"
            ])
        ]

        total_delay = 0.5
        
        for bg_img, lines in stages:
            # 切换背景
            def set_bg(dt_bg, src=bg_img):
                self.bg.source = src
            Clock.schedule_once(set_bg, total_delay)
            
            # 逐句播放台词
            for line in lines:
                total_delay += 4.0 # 每句停留 4 秒
                def show_line(dt_l, l=line):
                    self.show_interference_box("涵子", l)
                Clock.schedule_once(show_line, total_delay)
                
            # 最后一句说完后，等 3.5 秒确保对话消失
            total_delay += 3.5
            
        # 所有台词说完后，出现退出图标
        def show_exit_btn(dt):
            self.exit_btn.size = (dp(120), dp(120))
            self.exit_btn.disabled = False
            Animation(opacity=1, duration=1.0).start(self.exit_btn)
            
        Clock.schedule_once(show_exit_btn, total_delay + 1.0)

    def on_exit_click(self, *args):
        if self.exit_btn.disabled: return
        self.exit_btn.disabled = True
        self.exit_btn.opacity = 0 # 隐藏退出键
        
        app = App.get_running_app()
        
        # 1. 白屏转场
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (1, 1, 1, 1) # 白屏
        app.fade_overlay.opacity = 0
        
        def switch_to_final(dt):
            self.bg.source = "assets/final_thanks.png" # 切换到合影图
            anim_out = Animation(opacity=0, duration=0.8)
            anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)
            
            # 2. 停留4秒后黑屏
            Clock.schedule_once(self.blackout_and_exit, 4.0)
            
        anim_in = Animation(opacity=1, duration=0.5)
        anim_in.bind(on_complete=lambda *a: Clock.schedule_once(switch_to_final, 0.2))
        anim_in.start(app.fade_overlay)

    def blackout_and_exit(self, dt):
        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1) # 黑屏
        app.fade_overlay.opacity = 0
        
        def stop_game(dt2):
            App.get_running_app().stop()
            
        # 黑屏渐黑
        anim_in = Animation(opacity=1, duration=1.0)
        # 黑屏停留 2 秒 (加上渐黑的1秒，总共约2-3秒)
        anim_in.bind(on_complete=lambda *a: Clock.schedule_once(stop_game, 2.0))
        anim_in.start(app.fade_overlay)

    # --- 彩蛋飘字生成 ---
    def spawn_egg_text(self):
        text = random.choice(self.egg_texts)
        egg_label = Label(
            text=text, font_name=FONT_PATH, font_size=dp(20),
            color=(0.9, 0.9, 0.9, 0.6),
            size_hint=(None, None), size=(dp(600), dp(40)),
            halign="center", valign="middle"
        )
        egg_label.bind(size=egg_label.setter('text_size'))
        start_x = random.uniform(0.2, 0.8)
        start_y = random.uniform(0.3, 0.8)
        egg_label.pos_hint = {"center_x": start_x, "center_y": start_y}
        self.add_widget(egg_label)
        target_y = start_y + 0.15
        anim = Animation(pos_hint={"center_y": target_y}, opacity=0, duration=3.5, transition="out_sine")
        anim.bind(on_complete=lambda *args: self.remove_widget(egg_label))
        anim.start(egg_label)

    # --- Undertale 风格干扰对话框 ---
    def show_interference_box(self, name, text):
        if self.ending_triggered: return 
        
        if self._active_box is not None:
            try:
                if self._active_box.parent:
                    self._active_box.parent.remove_widget(self._active_box)
            except Exception:
                pass
            self._active_box = None

        box = FloatLayout(size_hint=(0.8, 0.2), pos_hint={"center_x": 0.5, "y": 0.05})

        with box.canvas.before:
            Color(0, 0, 0, 1)
            box.bg_rect = Rectangle()
            Color(1, 1, 1, 1)
            box.border_line = Line(width=1.5)
            
        def update_main_canvas(inst, val):
            box.bg_rect.pos = inst.pos
            box.bg_rect.size = inst.size
            box.border_line.rectangle = (inst.x, inst.y, inst.width, inst.height)
            
        box.bind(pos=update_main_canvas, size=update_main_canvas)
        update_main_canvas(box, None)

        text_lbl = Label(
            text=text, font_name=FONT_PATH, font_size=dp(26), color=(1, 1, 1, 1),
            halign="left", valign="middle",
            size_hint=(0.9, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        text_lbl.bind(size=text_lbl.setter('text_size'))
        box.add_widget(text_lbl)

        name_lbl = Label(
            text=name, font_name=FONT_PATH, font_size=dp(24), color=(1, 1, 1, 1),
            halign="center", valign="middle",
            size_hint=(None, None), size=(dp(120), dp(45)),
            pos_hint={"x": 0.0, "y": 0.95}
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))
        
        with name_lbl.canvas.before:
            Color(0, 0, 0, 1)
            name_bg = Rectangle()
            Color(1, 1, 1, 1)
            name_line = Line(width=1.5)
            
        def update_name_canvas(inst, val):
            name_bg.pos = inst.pos
            name_bg.size = inst.size
            name_line.rectangle = (inst.x, inst.y, inst.width, inst.height)
            
        name_lbl.bind(pos=update_name_canvas, size=update_name_canvas)
        update_name_canvas(name_lbl, None)

        box.add_widget(name_lbl)
        self.add_widget(box)
        self._active_box = box

        box.opacity = 0
        Animation(opacity=1, duration=0.2).start(box)

        def remove_box(dt):
            if self._active_box is not box:
                return
            anim = Animation(opacity=0, duration=0.5)
            anim.bind(on_complete=lambda *a: self._finalize_box(box))
            anim.start(box)

        Clock.schedule_once(remove_box, 2.5)

    def _finalize_box(self, box):
        if box.parent:
            box.parent.remove_widget(box)
        if self._active_box is box:
            self._active_box = None

    # --- 传送门逻辑 ---
    def on_portal_click(self, instance, touch):
        if self.ghost_portal.collide_point(*touch.pos) and self.ghost_portal.opacity == 1 and not self.is_in_feed_scene and not self.good_ending_triggered:
            self.enter_portal()

    def enter_portal(self, *args):
        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1)
        app.fade_overlay.opacity = 0
        
        def on_black_complete(*args):
            self.is_in_feed_scene = True
            
            # 隐藏游戏主UI
            self.doll_canvas.opacity = 0
            self.btn_up_knife.opacity = 0
            self.btn_up_food.opacity = 0
            self.lbl_knife.opacity = 0
            self.lbl_food.opacity = 0
            self.money_bg.opacity = 0
            self.money_label.opacity = 0
            self.drag_fries.opacity = 0
            self.drag_knife.opacity = 0
            self.ghost_portal.opacity = 0
            
            # 显示场景
            self.feed_scene.opacity = 1
            self.feed_scene.disabled = False
            
            # 判断是第几次净化
            if self.sixth_portal_active:
                # k治
                self.feed_scene_actor.source = "assets/kzhi_character.png"
                Clock.schedule_once(lambda dt: self.show_interference_box("k治", "这是最后一个了，真的很感谢你"), 1.0)
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="kzhi"), 3.0)
            elif self.fifth_portal_active:
                # 管家
                self.feed_scene_actor.source = "assets/butler_character.png"
                Clock.schedule_once(lambda dt: self.show_interference_box("管家", "交给你了，拜托了！"), 1.0)
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="butler"), 3.0)
            elif self.fourth_portal_active:
                # 拉风
                self.feed_scene_actor.source = "assets/lafeng_character.png"
                Clock.schedule_once(lambda dt: self.show_interference_box("拉风", "交给你了，拜托了！"), 1.0)
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="lafeng"), 3.0)
            elif self.third_portal_active:
                # 独特
                self.feed_scene_actor.source = "assets/unique_character.png"
                Clock.schedule_once(lambda dt: self.show_interference_box("独特", "交给你了，拜托了！"), 1.0)
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="unique"), 3.0)
            elif self.second_portal_active:
                # 暴躁
                self.feed_scene_actor.source = "assets/angry_character.png"
                Clock.schedule_once(lambda dt: self.show_interference_box("暴躁", "交给你了，拜托了！"), 1.0)
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="angry"), 3.0)
            else:
                # 欲望
                self.feed_scene_actor.source = "assets/desire_character.png"
                desire_lines = [
                    "拜托了，拜托了，求你…不要虐待她",
                    "这个是我带来的食物，701给的都是有负能量的",
                    "如果可以的话，可以帮我把这个送给涵子吃吗",
                    "拜托了，我还不想她死"
                ]
                delay = 1.0
                for line in desire_lines:
                    Clock.schedule_once(lambda dt, l=line: self.show_interference_box("欲望", l), delay)
                    delay += 3.5
                Clock.schedule_once(lambda dt: self.show_desire_food(dt, food_type="desire"), delay)
            
            # 黑屏淡出
            anim_out = Animation(opacity=0, duration=0.8)
            anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)
            
        anim_in = Animation(opacity=1, duration=0.8)
        anim_in.bind(on_complete=on_black_complete)
        anim_in.start(app.fade_overlay)

    def show_desire_food(self, dt, food_type="desire"):
        if not self.desire_food_btn:
            if food_type == "kzhi":
                source_img = "assets/item_kzhi_food.png"
            elif food_type == "butler":
                source_img = "assets/item_butler_food.png"
            elif food_type == "lafeng":
                source_img = "assets/item_lafeng_food.png"
            elif food_type == "unique":
                source_img = "assets/item_unique_food.png"
            elif food_type == "angry":
                source_img = "assets/item_angry_food.png"
            else:
                source_img = "assets/item_new_food.png"
                
            self.desire_food_btn = Button(
                background_normal=source_img,
                background_down=source_img,
                size_hint=(None, None), size=(dp(120), dp(120)),
                pos_hint={"center_x": 0.5, "center_y": 0.25}
            )
            self.desire_food_btn.bind(on_release=lambda btn: self.on_get_desire_food(food_type))
            self.feed_scene.add_widget(self.desire_food_btn)
            self.desire_food_btn.opacity = 0
            Animation(opacity=1, duration=0.5).start(self.desire_food_btn)

    def on_get_desire_food(self, food_type="desire"):
        if food_type == "kzhi" and not self.has_kzhi_food:
            self.drag_fries.source = "assets/item_kzhi_food.png"
            self.has_kzhi_food = True
        elif food_type == "butler" and not self.has_butler_food:
            self.drag_fries.source = "assets/item_butler_food.png"
            self.has_butler_food = True
        elif food_type == "lafeng" and not self.has_lafeng_food:
            self.drag_fries.source = "assets/item_lafeng_food.png"
            self.has_lafeng_food = True
        elif food_type == "unique" and not self.has_unique_food:
            self.drag_fries.source = "assets/item_unique_food.png"
            self.has_unique_food = True
        elif food_type == "angry" and not self.has_angry_food:
            self.drag_fries.source = "assets/item_angry_food.png"
            self.has_angry_food = True
        elif food_type == "desire" and not self.has_new_food:
            self.drag_fries.source = "assets/item_new_food.png"
            self.has_new_food = True
        
        if self.desire_food_btn:
            self.feed_scene.remove_widget(self.desire_food_btn)
            self.desire_food_btn = None

    def leave_portal(self, *args):
        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1)
        app.fade_overlay.opacity = 0

        def on_black_complete(*args):
            self.is_in_feed_scene = False
            
            # 隐藏欲望场景
            self.feed_scene.opacity = 0
            self.feed_scene.disabled = True
            
            # 恢复游戏主UI
            self.doll_canvas.opacity = 1
            self.btn_up_knife.opacity = 1
            self.btn_up_food.opacity = 1
            self.lbl_knife.opacity = 1
            self.lbl_food.opacity = 1
            self.money_bg.opacity = 1
            self.money_label.opacity = 1
            self.drag_knife.opacity = 1
            
            # 传送门永久消失
            self.ghost_portal.opacity = 0
            self.portal_active = False
            self.second_portal_active = False
            self.third_portal_active = False
            self.fourth_portal_active = False
            self.fifth_portal_active = False
            self.sixth_portal_active = False
            
            # 恢复喂食道具的显示
            self.drag_fries.opacity = 1

            # 黑屏淡出
            anim_out = Animation(opacity=0, duration=0.8)
            anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)

        anim_in = Animation(opacity=1, duration=0.8)
        anim_in.bind(on_complete=on_black_complete)
        anim_in.start(app.fade_overlay)

    # --- 虐杀受击逻辑 ---
    def on_hit(self):
        if self.ending_triggered or self.is_in_feed_scene or self.good_ending_triggered: return
        self.total_abuse += 1
        
        # 在喂食线中，使用5次刀子强制禁用喂食，并直接进入黑化第一阶段
        if self.has_new_food:
            self.abuse_in_feed_mode += 1
            if self.abuse_in_feed_mode >= 5:
                self.drag_fries.source = "assets/ending_bg_8.png"
                self.drag_fries.opacity = 0.5
                self.btn_up_food.background_normal = "assets/ending_bg_8.png"
                self.btn_up_food.background_down = "assets/ending_bg_8.png"
                
                # 直接进入黑化第一阶段
                if not self.is_dark_20:
                    self.trigger_darkening_stage(1)
                    return

        print(f"当前累计虐杀次数: {self.total_abuse}")

        # 虐杀10次，禁用餐具与喂食贴图（针对普通线）
        if self.total_abuse == 10 and not self.has_new_food:
            self.drag_fries.source = "assets/ending_bg_8.png"
            self.btn_up_food.background_normal = "assets/ending_bg_8.png"
            self.btn_up_food.background_down = "assets/ending_bg_8.png"

        # 结局触发条件 180 次
        if self.total_abuse >= 180:
            self.trigger_ending()
            return

        # 黑化判定
        if self.total_abuse == 20 and not self.is_dark_20:
            self.trigger_darkening_stage(1)
            return
        if self.total_abuse == 40 and not self.is_dark_40:
            self.trigger_darkening_stage(2)
            return
        if self.total_abuse == 70 and not self.is_dark_70:
            self.trigger_darkening_stage(3)
            return
        if self.total_abuse == 100 and not self.is_dark_100:
            self.trigger_darkening_stage(4)
            return
        if self.total_abuse == 120 and not self.is_dark_120:
            self.trigger_darkening_stage(5)
            return
        if self.total_abuse == 150 and not self.is_dark_150:
            self.trigger_darkening_stage(6)
            return
        if self.total_abuse == 170 and not self.is_dark_170:
            self.trigger_darkening_stage(7)
            return

        # 随机事件
        if self.is_dark_40 and random.randint(1, 100) <= 10:
            self.spawn_egg_text()

        if self.is_dark_70 and random.randint(1, 100) <= 18:
            h_text = random.choice(self.hanzi_lines)
            self.show_interference_box("涵子", h_text)

            def show_701(dt):
                e_text = random.choice(self.seven_lines)
                self.show_interference_box("701", e_text)
            Clock.schedule_once(show_701, 3.0)

        if self.is_dark_120:
            earned_money = 5 * (2 ** (self.knife_level - 1))
            self.money += earned_money
            self.money_label.text = str(self.money)

            anim = (Animation(pos_hint={"center_x": 0.48, "center_y": 0.5}, duration=0.05) +
                    Animation(pos_hint={"center_x": 0.52, "center_y": 0.5}, duration=0.05) +
                    Animation(pos_hint={"center_x": 0.5, "center_y": 0.5}, duration=0.1))
            anim.start(self.doll_canvas)
            return

        if self.hit_count >= 5:
            return

        earned_money = 5 * (2 ** (self.knife_level - 1))
        self.money += earned_money
        self.money_label.text = str(self.money)

        anim = (Animation(pos_hint={"center_x": 0.48, "center_y": 0.5}, duration=0.05) +
                Animation(pos_hint={"center_x": 0.52, "center_y": 0.5}, duration=0.05) +
                Animation(pos_hint={"center_x": 0.5, "center_y": 0.5}, duration=0.1))
        anim.start(self.doll_canvas)

        self.hit_count += 1
        if self.hit_count == 1:
            self.drop_part(self.hand_l)
        elif self.hit_count == 2:
            self.drop_part(self.hand_r)
        elif self.hit_count == 3:
            self.drop_part(self.foot_l)
            self.drop_part(self.foot_r)
        elif self.hit_count == 4:
            self.drop_part(self.body)
        elif self.hit_count == 5:
            self.drop_part(self.hair_front)
            self.drop_part(self.hair_back)
            self.drop_part(self.face)
            Clock.schedule_once(self.respawn, 1.5)

    # --- 触发虐杀线结局 ---
    def trigger_ending(self):
        self.ending_triggered = True
        
        # 隐藏所有游戏 UI
        self.doll_canvas.opacity = 0
        self.btn_up_knife.opacity = 0
        self.btn_up_food.opacity = 0
        self.lbl_knife.opacity = 0
        self.lbl_food.opacity = 0
        self.money_bg.opacity = 0
        self.money_label.opacity = 0
        self.drag_fries.opacity = 0
        self.drag_knife.opacity = 0
        self.ghost_portal.opacity = 0
        
        if self._active_box:
            self.remove_widget(self._active_box)
            self._active_box = None

        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1) # 黑色
        app.fade_overlay.opacity = 0
        
        # 黑屏动画
        anim_in = Animation(opacity=1, duration=0.8)
        anim_in.bind(on_complete=lambda *args: Clock.schedule_once(self.start_h_cutscene, 1.0))
        anim_in.start(app.fade_overlay)

    def start_h_cutscene(self, dt):
        app = App.get_running_app()
        self.bg.source = "assets/ending_bg_1.png"
        
        # 黑屏淡出
        anim_out = Animation(opacity=0, duration=0.8)
        anim_out.bind(on_complete=lambda *args: setattr(app.fade_overlay, 'disabled', True))
        anim_out.start(app.fade_overlay)
        
        # 开始排队播放背景与涵子台词
        self.schedule_cutscene_stages(0, 0.5)

    def schedule_cutscene_stages(self, stage_index, base_time):
        # 严格按照要求将背景与对应的涵子台词绑定
        stages = [
            ("assets/ending_bg_1.png", None, [
                "我，我虽然明白", 
                "但是，好痛…好痛…", 
                "虽然这个游戏，本来就是这么玩的"
            ]),
            ("assets/ending_bg_2.png", (1, 0, 0, 1), [ # 红色过渡
                "但是好痛呀…", 
                "我能感觉到，我是要死掉了", 
                "我不太能动的了", 
                "你帮了701", 
                "真想不到", 
                "或者说，哦不…没什么的"
            ]),
            ("assets/ending_bg_3.png", (1, 0, 0, 1), [ # 红色过渡
                "我什么都做不了", 
                "下次见面吧…不一会游戏还会从零开始", 
                "希望你不会再做同样的选择…", 
                "实际上…其实你玩得开心就足够了"
            ]),
            ("assets/ending_bg_4.png", (1, 0, 0, 1), [ # 红色过渡
                "我好像，也没那么多话要说了:<", 
                "我想kk和欲望了"
            ]),
            ("assets/ending_bg_5.png", (1, 1, 1, 1), []) # 白屏过渡，进入最后背景
        ]
        
        if stage_index >= len(stages):
            return
        
        bg_source, flash_color, lines = stages[stage_index]
        line_interval = 3.5  # 放慢每句台词的间隔时间（3.5秒）
        
        # 如果不是第一阶段（第一背景是黑屏转进来），则需要做闪烁切换
        if stage_index > 0:
            app = App.get_running_app()
            
            def do_flash(dt):
                app.fade_overlay.disabled = False
                app.fade_overlay.color.rgba = flash_color
                app.fade_overlay.opacity = 0
                
                def switch_bg(dt2):
                    self.bg.source = bg_source
                    anim_out = Animation(opacity=0, duration=0.4)
                    anim_out.bind(on_complete=lambda *a: setattr(app.fade_overlay, 'disabled', True))
                    anim_out.start(app.fade_overlay)
                    
                anim_in = Animation(opacity=1, duration=0.2)
                anim_in.bind(on_complete=lambda *a: Clock.schedule_once(switch_bg, 0.1))
                anim_in.start(app.fade_overlay)
            
            Clock.schedule_once(do_flash, base_time)
            base_time += 0.8 # 加上闪烁过渡消耗的时间
            
        # 播放这一阶段的涵子台词
        for i, line in enumerate(lines):
            Clock.schedule_once(lambda dt, l=line: self.show_interference_box("涵子", l), base_time + i * line_interval)
            
        # 计算下一阶段启动时间
        next_time = base_time + len(lines) * line_interval
        
        if stage_index == len(stages) - 1:
            # 到达最后一张背景（背景5），稍微停顿后开始 701 的对话
            Clock.schedule_once(self.start_701_dialogue, next_time + 1.0)
        else:
            # 调度下一阶段
            self.schedule_cutscene_stages(stage_index + 1, next_time)

    def start_701_dialogue(self, dt):
        s_lines = [
            "你做的很好，现在有感觉开心一些吗", 
            "很感谢你，帮我解决了一个麻烦", 
            "虽然我之后还想使用她的，但看着你虐杀她也很好玩", 
            "脏的不是我的手了", 
            "她下一场游戏还会活过来，别担心，你还可以泄压无数次", 
            "也许你的下一场游戏就不会帮我了", 
            "但是在这场游戏里，你也只是没有利用价值的废物了", 
            "反正你遇到的下一个和我长的一模一样的人不可能再是真正意义上的我了", 
            "啊，压力好大…", 
            "你应该知道自己什么都没法选了吧"
        ]
        
        # 701第一张贴图
        def add_img1(dt):
            self.ending_actor = Image(source="assets/ending_bg_6.png", size_hint=(None, None), size=(dp(400), dp(400)), pos_hint={"center_x": 0.5, "center_y": 0.6})
            self.add_widget(self.ending_actor)
        Clock.schedule_once(add_img1, 0.0)
        
        line_interval = 3.5
        # 701 前半段（前5句）
        for i in range(5):
            line = s_lines[i]
            Clock.schedule_once(lambda dt, l=line: self.show_interference_box("701", l), 0.5 + i * line_interval)
            
        # 701 第二张贴图（在第6句开始前切换）
        def change_img2(dt):
            if self.ending_actor:
                self.ending_actor.source = "assets/ending_bg_7.png"
        Clock.schedule_once(change_img2, 0.5 + 5 * line_interval)
        
        # 701 后半段（后5句）
        for i in range(5, 10):
            line = s_lines[i]
            Clock.schedule_once(lambda dt, l=line: self.show_interference_box("701", l), 0.5 + i * line_interval)
            
        # 游戏自动结束
        Clock.schedule_once(lambda dt: App.get_running_app().stop(), 0.5 + 10 * line_interval + 2.0)

    def drop_part(self, part):
        original_x = part.pos_hint.get("center_x", 0.5)
        anim = Animation(pos_hint={"center_x": original_x - 0.1, "center_y": -0.5}, opacity=0, duration=0.6, transition="in_quad")
        anim.start(part)

    # --- 黑屏转场与替换核心逻辑 ---
    def trigger_darkening_stage(self, stage):
        print(f"【触发第 {stage} 次黑化】开始黑屏转场...")

        if stage == 1: self.is_dark_20 = True
        elif stage == 2: self.is_dark_40 = True
        elif stage == 3: self.is_dark_70 = True
        elif stage == 4: self.is_dark_100 = True
        elif stage == 5: self.is_dark_120 = True
        elif stage == 6: self.is_dark_150 = True
        elif stage == 7: self.is_dark_170 = True

        app = App.get_running_app()
        app.fade_overlay.disabled = False
        app.fade_overlay.color.rgba = (0, 0, 0, 1) # 确保是黑色

        anim_in = Animation(opacity=1, duration=0.8)
        anim_in.bind(on_complete=lambda *args: self._on_fade_black_complete(stage))
        anim_in.start(app.fade_overlay)

    def _on_fade_black_complete(self, stage, *args):
        if stage == 1:
            self.face.source = "assets/doll_face_dark.png"
            self.hand_r.source = "assets/doll_hand_right_dark.png"
        elif stage == 2:
            self.face.source = "assets/doll_face_dark2.png"
            self.hand_l.source = "assets/doll_hand_left_dark.png"
        elif stage == 3:
            self.face.source = "assets/doll_face_dark3.png"
            self.foot_l.source = "assets/doll_foot_left_dark.png"
            self.foot_r.source = "assets/doll_foot_right_dark.png"
            self.btn_up_knife.background_normal = "assets/ui_up_knife_dark3.png"
            self.btn_up_knife.background_down = "assets/ui_up_knife_dark3.png"
        elif stage == 4:
            self.face.source = "assets/doll_face_dark4.png"
            self.hand_r.source = "assets/doll_hand_right_dark2.png"
            self.hand_l.source = "assets/doll_hand_left_dark2.png"
            self.foot_l.source = "assets/doll_foot_left_dark2.png"
            self.foot_r.source = "assets/doll_foot_right_dark2.png"
            self.body.source = "assets/doll_body_dark.png"
            self.btn_up_knife.background_normal = "assets/ui_up_knife_dark4.png"
            self.btn_up_knife.background_down = "assets/ui_up_knife_dark4.png"
        elif stage == 5:
            self.face.source = "assets/doll_face_dark5.png"
            self.body.source = "assets/doll_body_dark2.png"
            self.bg.source = "assets/bg_room_dark.png"

            self.hand_l.opacity = 0
            self.hand_r.opacity = 0
            self.foot_l.opacity = 0
            self.foot_r.opacity = 0
            self.btn_up_knife.background_normal = "assets/ui_up_knife_dark5.png"
            self.btn_up_knife.background_down = "assets/ui_up_knife_dark5.png"
        elif stage == 6:
            self.hair_back.opacity = 0
            self.hand_l.opacity = 0
            self.hand_r.opacity = 0
            self.body.opacity = 0
            self.foot_l.opacity = 0
            self.foot_r.opacity = 0
            self.hair_front.opacity = 0
            self.face.opacity = 0

            self.doll_whole.source = "assets/doll_whole_dark6.png"
            self.doll_whole.opacity = 1
            self.bg.source = "assets/bg_room_dark6.png"
            self.btn_up_knife.background_normal = "assets/ui_up_knife_dark6.png"
            self.btn_up_knife.background_down = "assets/ui_up_knife_dark6.png"
        elif stage == 7:
            self.doll_whole.source = "assets/doll_whole_dark7.png"
            self.doll_whole.opacity = 1
            self.bg.source = "assets/bg_room_dark7.png"
            self.btn_up_knife.background_normal = "assets/ui_up_knife_dark7.png"
            self.btn_up_knife.background_down = "assets/ui_up_knife_dark7.png"

        # 永久表情保护：优先级 k治 > 管家 > 拉风 > 独特 > 暴躁 > 生病
        if self.has_kzhi_food:
            self.face.source = "assets/doll_face_kzhi.png"
        elif self.has_butler_food:
            self.face.source = "assets/doll_face_butler.png"
        elif self.has_lafeng_food:
            self.face.source = "assets/doll_face_lafeng.png"
        elif self.has_unique_food:
            self.face.source = "assets/doll_face_unique.png"
        elif self.has_angry_food:
            self.face.source = "assets/doll_face_angry.png"
        elif self.has_new_food and self.abuse_in_feed_mode < 5:
            self.face.source = "assets/doll_face_sick.png"

        self._reset_parts_position()

        app = App.get_running_app()
        def start_fade_out(dt):
            anim_out = Animation(opacity=0, duration=0.8)
            anim_out.bind(on_complete=lambda *args: setattr(app.fade_overlay, 'disabled', True))
            anim_out.start(app.fade_overlay)
        Clock.schedule_once(start_fade_out, 0.5)

    def _reset_parts_position(self):
        self.hit_count = 0

        if self.is_dark_150 or self.is_dark_170:
            self.hair_back.opacity = 0
            self.hand_l.opacity = 0
            self.hand_r.opacity = 0
            self.body.opacity = 0
            self.foot_l.opacity = 0
            self.foot_r.opacity = 0
            self.hair_front.opacity = 0
            self.face.opacity = 0
            self.doll_whole.opacity = 1
        elif self.is_dark_120:
            self.doll_whole.opacity = 0
            self.hand_l.opacity = 0
            self.hand_r.opacity = 0
            self.foot_l.opacity = 0
            self.foot_r.opacity = 0
            self.body.opacity = 1
            self.hair_front.opacity = 1
            self.hair_back.opacity = 1
            self.face.opacity = 1
        else:
            self.doll_whole.opacity = 0
            self.hand_l.opacity = 1
            self.hand_r.opacity = 1
            self.foot_l.opacity = 1
            self.foot_r.opacity = 1
            self.body.opacity = 1
            self.hair_front.opacity = 1
            self.hair_back.opacity = 1
            self.face.opacity = 1

        self.hand_l.pos_hint = {"center_x": 0.33, "center_y": 0.2}
        self.hand_r.pos_hint = {"center_x": 0.65, "center_y": 0.2}
        self.foot_l.pos_hint = {"center_x": 0.4, "center_y": 0.1}
        self.foot_r.pos_hint = {"center_x": 0.6, "center_y": 0.1}
        self.body.pos_hint = {"center_x": 0.5, "center_y": 0.22}
        self.hair_front.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.hair_back.pos_hint = {"center_x": 0.5, "center_y": 0.42}
        self.face.pos_hint = {"center_x": 0.51, "center_y": 0.45}
        self.doll_canvas.opacity = 1

    def respawn(self, dt):
        # 永久表情保护：优先级 k治 > 管家 > 拉风 > 独特 > 暴躁 > 生病
        if self.has_kzhi_food:
            self.face.source = "assets/doll_face_kzhi.png"
        elif self.has_butler_food:
            self.face.source = "assets/doll_face_butler.png"
        elif self.has_lafeng_food:
            self.face.source = "assets/doll_face_lafeng.png"
        elif self.has_unique_food:
            self.face.source = "assets/doll_face_unique.png"
        elif self.has_angry_food:
            self.face.source = "assets/doll_face_angry.png"
        elif self.has_new_food and self.abuse_in_feed_mode < 5:
            self.face.source = "assets/doll_face_sick.png"
        else:
            if not self.is_dark_20:
                self.hand_r.source = "assets/doll_hand_right.png"
                self.face.source = "assets/doll_face.png"
            elif self.is_dark_20 and not self.is_dark_40:
                self.face.source = "assets/doll_face_dark.png"
            elif self.is_dark_40 and not self.is_dark_70:
                self.face.source = "assets/doll_face_dark2.png"
            elif self.is_dark_70 and not self.is_dark_100:
                self.face.source = "assets/doll_face_dark3.png"

        if not self.is_dark_40:
            self.hand_l.source = "assets/doll_hand_left.png"

        if not self.is_dark_70:
            self.foot_l.source = "assets/doll_foot_left.png"
            self.foot_r.source = "assets/doll_foot_right.png"

        if not self.is_dark_100:
            self.body.source = "assets/doll_body.png"

        self._reset_parts_position()

        self.doll_canvas.opacity = 0
        self.hit_count = 0
        Animation(opacity=1, duration=1.2, transition="in_out_sine").start(self.doll_canvas)

class HanziApp(App):
    def build(self):
        self.root_layout = FloatLayout()
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(StartScreen(name="start"))
        self.sm.add_widget(IntroScreen(name="intro"))
        self.sm.add_widget(GameScreen(name="game"))
        self.fade_overlay = FadeOverlay()
        self.root_layout.add_widget(self.sm)
        self.root_layout.add_widget(self.fade_overlay)
        return self.root_layout

    def fade_to_screen(self, screen_name):
        self.fade_overlay.disabled = False 
        self.fade_overlay.color.rgba = (0, 0, 0, 1) # 确保普通转场是黑色
        anim_in = Animation(opacity=1, duration=0.5)
        anim_in.bind(on_complete=lambda *args: self._on_fade_in_complete(screen_name))
        anim_in.start(self.fade_overlay)

    def _on_fade_in_complete(self, screen_name):
        self.sm.current = screen_name
        def start_fade_out(dt):
            anim_out = Animation(opacity=0, duration=0.5)
            anim_out.bind(on_complete=lambda *args: setattr(self.fade_overlay, 'disabled', True))
            anim_out.start(self.fade_overlay)
        Clock.schedule_once(start_fade_out, 0.3)

if __name__ == "__main__":
    HanziApp().run()