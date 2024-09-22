import os
import sqlite3
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.label import Label
from kivymd.uix.label import MDLabel
from kivy.uix.button import Button
from kivy.core.text import LabelBase
import arabic_reshaper
from kivy.uix.textinput import TextInput
from bidi.algorithm import get_display
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
import pandas as pd
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRaisedButton
from datetime import datetime
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.resources import resource_add_path, resource_find
from kivy.uix.popup import Popup
from kivy.clock import Clock
import requests
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.spinner import SpinnerOption
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.image import Image


class ColoredCheckBox(CheckBox):
    def __init__(self, **kwargs):
        super(ColoredCheckBox, self).__init__(**kwargs)
        self.bind(active=self.on_active)
        with self.canvas.before:
            Color(1, 0, 0, 1)  # رنگ قرمز
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def on_active(self, instance, value):
        if value:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0, 1, 0, 1)  # رنگ سبز
                self.rect = Rectangle(size=self.size, pos=self.pos)
        else:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(1, 0, 0, 1)  # رنگ قرمز
                self.rect = Rectangle(size=self.size, pos=self.pos)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


resource_add_path('.')
font_path = resource_find('Nazanin.ttf')
db_path = resource_find('restaurant.db')

LabelBase.register(name='Persian', fn_regular='Nazanin.ttf')

def reshape_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text
    
class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super(CustomSpinnerOption, self).__init__(**kwargs)
        self.font_name = 'Persian'       
        self.halign = 'right'
        self.background_color = (0.8, 1, 0.8, 0.5)  
        
        
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        with self.canvas.before:
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[30])
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class StyledButton(Button):
    def __init__(self, **kwargs):
        super(StyledButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_name = 'Persian'
        self.size_hint = (0.8, None)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}    
        self.height = 50
        self.icon = kwargs.get('icon', None)
        
        with self.canvas.before:
            Color(0.18, 0.55, 0.34, 1)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[30])
            Color(0, 0, 0, 0.2)
            self.shadow = RoundedRectangle(size=(self.width + 10, self.height + 10), pos=(self.x - 5, self.y - 5), radius=[30])
            Color(0, 0, 0, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 30), width=2)
        
        if self.icon:
            self.icon_image = Image(source=self.icon, size_hint=(None, None), size=(30, 30), pos=(self.x + 10, self.y + 10))
            self.add_widget(self.icon_image)
        
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.bind(on_press=self.on_press, on_release=self.on_release)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.x - 5, self.y - 5)
        self.shadow.size = (self.width + 10, self.height + 10)
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 30)
        if self.icon:
            self.icon_image.pos = (self.x + 10, self.y + (self.height - 30) / 2)

    def on_press(self, *args):
        anim = Animation(size=(self.width - 10, self.height - 10), duration=0.1)
        anim.start(self.rect)
        self.shadow.size = (self.width + 5, self.height + 5)

    def on_release(self, *args):
        anim = Animation(size=(self.width, self.height), duration=0.1)
        anim.start(self.rect)
        self.shadow.size = (self.width + 10, self.height + 10)

class TextInputStyle(TextInput):
    def __init__(self, **kwargs):
        super(TextInputStyle, self).__init__(**kwargs)
        self.font_name = 'Nazanin.ttf'
        self.font_size = 16
        self.foreground_color = (0, 0, 0, 1)
        self.background_color = (0.8, 1, 0.8, 0.5)
        self.cursor_color = (0, 0, 1, 1)
        self.size_hint = (0.8, 0.4)
        self.height = 70
        self.width = 100
        self.pos_hint = {'center_x': 0.5}

    def insert_text(self, substring, from_undo=False):
        substring = bidi.reshape(reshape(substring))
        super(TextInputStyle, self).insert_text(substring, from_undo=from_undo)

class LoginScreen(Screen):
    current_username = None  # ویژگی کلاس برای ذخیره نام کاربری

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint=(None, None), size=(400, 400))
        self.layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        username_layout = BoxLayout(orientation='vertical', size_hint=(0.8, None), height=90)
        username_layout.add_widget(Label(text='Username', color=(0, 0, 0, 1), font_size='20sp'))
        self.username = TextInput(multiline=False, height=50)
        username_layout.add_widget(self.username)
        self.layout.add_widget(username_layout)
        
        password_layout = BoxLayout(orientation='vertical', size_hint=(0.8, None), height=90)
        password_layout.add_widget(Label(text='Password', color=(0, 0, 0, 1), font_size='20sp'))
        self.password = TextInput(password=True, multiline=False, height=50)
        password_layout.add_widget(self.password)
        self.layout.add_widget(password_layout)
        
        self.login_button = StyledButton(text=reshape_text('ورود'), font_size='20sp')
        self.login_button.bind(on_press=self.validate_user)
        self.layout.add_widget(self.login_button)
        
        self.result = Label(text='', color=(0, 0, 0, 1), font_size='18sp')  
        self.layout.add_widget(self.result)
        
        self.add_widget(self.layout)
    
    def validate_user(self, instance):
        username = self.username.text
        password = self.password.text
        
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT job_position FROM employeeinfo WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        
        if result:
            role = result[0]
            self.result.text = f'Login successful! Role: {role}'
            LoginScreen.current_username = username  # ذخیره نام کاربری در ویژگی کلاس
            self.manager.current_user = username  # ذخیره نام کاربری در ScreenManager
            if role == 'مدیر':
                self.manager.current = 'manager'
            elif role == 'کارشناس':
                self.manager.current = 'expert'
            elif role == 'کارمند':
                self.manager.current = 'employee'
            elif role == 'مهمان':
                self.manager.current = 'guest'
        else:
            self.result.text = 'Invalid username or password'
        
        conn.close()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ManagerScreen(Screen):
    def __init__(self, **kwargs):
        super(ManagerScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        
        layout = BoxLayout(orientation='vertical', size_hint=(0.8, 0.8), pos_hint={'center_x': 0.5, 'center_y': 0.5}, padding=20, spacing=20)
    
        btn1 = StyledButton(text=reshape_text('خدمات'))
        btn1.bind(on_press=self.go_to_Servicescreen)
        layout.add_widget(btn1)
        
        btn2 = StyledButton(text=reshape_text('پرسنل'))
        btn2.bind(on_press=self.go_to_Personelsscreen)
        layout.add_widget(btn2)
        
        btn3 = StyledButton(text=reshape_text('پیامک'))
        btn3.bind(on_press=self.go_to_Massengerscreen)
        layout.add_widget(btn3)
        
        btn4 = StyledButton(text=reshape_text('چک لیست‌ها'))
        btn4.bind(on_press=self.go_to_ChecklistsScreen)
        layout.add_widget(btn4)
        
        btn5 = StyledButton(text=reshape_text('شرح وظایف'))
        btn5.bind(on_press=self.go_to_Tasksscreen)
        layout.add_widget(btn5)

        btn6 = StyledButton(text=reshape_text(' رویدادها'))
        btn6.bind(on_press=self.go_to_EventScreen)
        layout.add_widget(btn6)
  
        exit_btn = StyledButton(text=reshape_text('خروج'))
        exit_btn.bind(on_press=self.exit_app)
        layout.add_widget(exit_btn)  
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_Servicescreen(self, instance):
        self.manager.current = 'service'

    def go_to_Personelsscreen(self, instance):
        self.manager.current = 'personels'
        
    def go_to_Massengerscreen(self, instance):
        self.manager.current = 'massenger'
        
    def go_to_ChecklistsScreen(self, instance):
        self.manager.current = 'checklists'
        
    def go_to_Tasksscreen(self, instance):
        self.manager.current = 'tasks'

    def go_to_EventScreen(self, instance):
        self.manager.current = 'events'

    def exit_app(self, instance):
        App.get_running_app().stop()

class Servicescreen(Screen):
    def __init__(self, **kwargs):
        super(Servicescreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        layout = BoxLayout(orientation='vertical')

        btn1 = StyledButton(text=reshape_text('پیگیری و ویرایش سفارشات'))
        btn1.bind(on_press=self.go_to_Showservicescreen)
        layout.add_widget(btn1)

        btn2 = StyledButton(text=reshape_text(' ثبت سفارش  '))
        btn2.bind(on_press=self.go_to_Addservicescreen)
        layout.add_widget(btn2)

        btn3 = StyledButton(text=reshape_text(' بازگشت'))
        btn3.bind(on_press=self.go_back)
        layout.add_widget(btn3)
        
        self.add_widget(layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def go_to_Showservicescreen(self, instance):
        self.manager.current = 'showservice'
        
    def go_to_Addservicescreen(self, instance):
        self.manager.current = 'addservice'

    def go_back(self, instance):
        self.manager.current = 'manager'

class Showservicescreen(Screen):
    def __init__(self, **kwargs):
        super(Showservicescreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.table_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        
        self.create_buttons()
        self.create_table()
        
        self.layout.add_widget(self.button_layout)
        self.layout.add_widget(self.table_layout)
        self.add_widget(self.layout)
        
    def create_table(self):
        db_path = 'restaurant.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders')
        rows = cursor.fetchall()
        conn.close()
        column_data = [
            ("ID", dp(30)),
            ("Date", dp(30)),
            ("Time", dp(30)),
            ("Name", dp(30)),
            ("Contact Number", dp(30)),
            ("Type", dp(30)),
            ("Phone Number", dp(30)),
            ("Price", dp(30)),
            ("Order Status", dp(30))
        ]

        row_data = []
        for row in rows:
            reshaped_row = [reshape_text(str(cell)) for cell in row]
            row_data.append(reshaped_row)

        self.table = MDDataTable(
            size_hint=(0.9, 0.6),  
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            column_data=column_data,
            row_data=row_data,
           
        )
        self.table_layout.add_widget(self.table)     
    
    def create_buttons(self):
        update_button = MDRaisedButton(
            text=reshape_text("بروزرسانی جدول"),font_name='Persian', halign='right',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.update_table
        )
        self.button_layout.add_widget(update_button)
        
        back_button = MDRaisedButton(
            text=reshape_text("بازگشت به منو"),font_name='Persian', halign='right',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.go_back_to_menu
        )
        self.button_layout.add_widget(back_button)  
    
    def update_table(self, instance):
        self.table_layout.clear_widgets()
        self.create_table()
        
    def go_back_to_menu(self, instance):
        self.manager.current = 'service'

class Addservicescreen(Screen):
    def __init__(self, **kwargs):
        super(Addservicescreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.name_input = TextInputStyle(hint_text=reshape_text('نام'), font_name='Persian', halign='right')
        layout.add_widget(self.name_input)
        
        self.contact_input = TextInputStyle(hint_text=reshape_text('تعداد'), font_name='Persian', halign='right')
        layout.add_widget(self.contact_input)
        
        self.typy_input = TextInputStyle(hint_text=reshape_text('نام سفارش'), font_name='Persian', halign='right')
        layout.add_widget(self.typy_input)
        
        self.phone_input = TextInputStyle(hint_text=reshape_text('شماره تلفن'),font_name='Persian',halign='right' , input_filter='int')
        layout.add_widget(self.phone_input)
        
        save_btn = StyledButton(text=reshape_text('ذخیره'), font_name='Persian' , halign='right')
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)
        
        back_btn = StyledButton(text=reshape_text('بازگشت به منو'), font_name='Persian' , halign='right')
        back_btn.bind(on_press=self.go_back_to_menu)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def save_data(self, instance):
        name = self.name_input.text
        contact = self.contact_input.text
        typy = self.typy_input.text
        phone = self.phone_input.text
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")  
        
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO orders (date, time, name, contact_number, typy, phone_number, price, order_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, time, name, contact, typy, phone,'',''))
        
        conn.commit()
        conn.close()
        
        self.name_input.text = ''
        self.contact_input.text = ''
        self.typy_input.text = ''
        self.phone_input.text = ''
   
        
    def go_back_to_menu(self, instance):
        self.manager.current = 'service'

class Personelsscreen(Screen):
    def __init__(self, **kwargs):
        super(Personelsscreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        layout = BoxLayout(orientation='vertical')

        btn1 = StyledButton(text=reshape_text('مشاهده و ویرایش پرسنل'))
        btn1.bind(on_press=self.go_to_Showpersonelscreen)
        layout.add_widget(btn1)

        btn2 = StyledButton(text=reshape_text('افزودن پرسنل '))
        btn2.bind(on_press=self.go_to_Addpersonelscreen)
        layout.add_widget(btn2)

        btn3 = StyledButton(text=reshape_text('وارد کردن گزارش پرسنل'))
        btn3.bind(on_press=self.go_to_Reportspersonelscreen)
        layout.add_widget(btn3)

        btn4 = StyledButton(text=reshape_text('بازگشت'))
        btn4.bind(on_press=self.go_back)
        layout.add_widget(btn4)

        self.add_widget(layout)
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size    

    def go_to_Showpersonelscreen(self, instance):
        self.manager.current = 'showpersonel' 
        
    def go_to_Addpersonelscreen(self, instance):
        self.manager.current = 'addpersonel'
        
    def go_to_Reportspersonelscreen(self, instance):
        self.manager.current = 'reportspersonel'

    def go_back(self, instance):
        self.manager.current = 'manager'

class Showpersonelscreen(Screen):
    def __init__(self, **kwargs):
        super(Showpersonelscreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.table_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.8))       
        self.create_buttons()
        self.create_table()        
        self.layout.add_widget(self.button_layout)
        self.layout.add_widget(self.table_layout)
        self.add_widget(self.layout)
        
    def create_table(self):
        db_path = 'restaurant.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employeeinfo')
        rows = cursor.fetchall()
        conn.close()
        column_data = [
            ("ID", dp(30)),
            ("First Name", dp(30)),
            ("Last Name", dp(30)),
            ("Employee Code", dp(30)),
            ("Hire Date", dp(30)),
            ("Document Completion Date", dp(30)),
            ("Job Position", dp(30)),
            ("Settlement Time", dp(30)),
            ("Settlement Reason", dp(30)),
            ("Username", dp(30)),
            ("Password", dp(30))
        ]
        self.table = MDDataTable(
            size_hint=(0.9, 0.6),  
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            column_data=column_data,
            row_data=rows
        )
        self.table_layout.add_widget(self.table)     
    
    def create_buttons(self):
        update_button = MDRaisedButton(
            text=reshape_text("بروزرسانی جدول"),font_name='Persian', halign='right',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.update_table
        )
        self.button_layout.add_widget(update_button)
        
        back_button = MDRaisedButton(
             text=reshape_text("بازگشت به منو"),font_name='Persian', halign='right',
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            on_release=self.go_back_to_menu
        )
        self.button_layout.add_widget(back_button)  
    
    def update_table(self, instance):
        self.table_layout.clear_widgets()
        self.create_table()
        
    def go_back_to_menu(self, instance):
        self.manager.current = 'personels'


class Addpersonelscreen(Screen):
    def __init__(self, **kwargs):
        super(Addpersonelscreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.first_name_input = TextInputStyle(hint_text=reshape_text('نام'), font_name='Persian', halign='right')
        layout.add_widget(self.first_name_input)
        
        self.last_name_input = TextInputStyle(hint_text=reshape_text('نام خانوادگی'), font_name='Persian', halign='right')
        layout.add_widget(self.last_name_input)
        
        self.employee_code_input = TextInputStyle(hint_text=reshape_text('کد پرسنلی'), font_name='Persian', halign='right')
        layout.add_widget(self.employee_code_input)
        
        self.hire_date_input = TextInputStyle(hint_text=reshape_text('تاریخ استخدام'), font_name='Persian', halign='right')
        layout.add_widget(self.hire_date_input)
        
        self.document_completion_date_input = TextInputStyle(hint_text=reshape_text('تاریخ تکمیل مدارک'), font_name='Persian', halign='right')
        layout.add_widget(self.document_completion_date_input)
        
        self.job_position_spinner = Spinner(
            text=reshape_text('سمت شغلی'),
            values=[
                reshape_text('مدیر'),
                reshape_text('کارشناس'),
                reshape_text('کارمند'),
                reshape_text('مهمان')
            ],
            font_name='Persian',
            halign='right',
            option_cls=CustomSpinnerOption
        )
        layout.add_widget(self.job_position_spinner)
        
        self.username_input = TextInputStyle(hint_text=reshape_text('نام کاربری'), font_name='Persian', halign='right')
        layout.add_widget(self.username_input)
        
        self.password_input = TextInputStyle(hint_text=reshape_text('رمز عبور'), font_name='Persian', halign='right', password=True, password_mask='*')
        layout.add_widget(self.password_input)
        
        self.settlement_time_input = TextInputStyle(hint_text=reshape_text('زمان تسویه'), font_name='Persian', halign='right')
        layout.add_widget(self.settlement_time_input)
        
        self.settlement_reason_input = TextInputStyle(hint_text=reshape_text('دلیل تسویه'), font_name='Persian', halign='right')
        layout.add_widget(self.settlement_reason_input)
        
        save_btn = StyledButton(text=reshape_text('ذخیره'), font_name='Persian', halign='right')
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)
        
        back_btn = StyledButton(text=reshape_text('بازگشت به منو'), font_name='Persian', halign='right')
        back_btn.bind(on_press=self.go_back_to_menu)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)    
    def save_data(self, instance):
        first_name = self.first_name_input.text
        last_name = self.last_name_input.text
        employee_code = self.employee_code_input.text
        hire_date = self.hire_date_input.text
        document_completion_date = self.document_completion_date_input.text
        job_position = self.job_position_spinner.text 
        username = self.username_input.text
        password = self.password_input.text
        settlement_time = self.settlement_time_input.text
        settlement_reason = self.settlement_reason_input.text
        
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO employeeinfo (first_name, last_name, employee_code, hire_date, document_completion_date, job_position, username, password, settlement_time, settlement_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, employee_code, hire_date, document_completion_date, job_position, username, password, settlement_time, settlement_reason))
        
        conn.commit()
        conn.close()
        
        self.first_name_input.text = ''
        self.last_name_input.text = ''
        self.employee_code_input.text = ''
        self.hire_date_input.text = ''
        self.document_completion_date_input.text = ''
        self.job_position_spinner.text = reshape_text('سمت شغلی')  
        self.username_input.text = ''
        self.password_input.text = ''
        self.settlement_time_input.text = ''
        self.settlement_reason_input.text = ''
   
    def go_back_to_menu(self, instance):
        self.manager.current = 'personels'

class Reportspersonelscreen(Screen):
    def __init__(self, **kwargs):
        super(Reportspersonelscreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.employee_code_input = TextInputStyle(hint_text=reshape_text('کد پرسنلی'), font_name='Persian', halign='right')
        layout.add_widget(self.employee_code_input)
        
        self.check_in_time_input = TextInputStyle(hint_text=reshape_text('زمان ورود'), font_name='Persian', halign='right')
        layout.add_widget(self.check_in_time_input)
        
        self.check_out_time_input = TextInputStyle(hint_text=reshape_text('زمان خروج'), font_name='Persian', halign='right')
        layout.add_widget(self.check_out_time_input)
        
        self.delay_input = TextInputStyle(hint_text=reshape_text('تاخیر'), font_name='Persian', halign='right')
        layout.add_widget(self.delay_input)
        
        self.overtime_input = TextInputStyle(hint_text=reshape_text('اضافه کاری'), font_name='Persian', halign='right')
        layout.add_widget(self.overtime_input)
        
        self.breakfast_input = TextInputStyle(hint_text=reshape_text('صبحانه'), font_name='Persian', halign='right')
        layout.add_widget(self.breakfast_input)
        
        self.lunch_input = TextInputStyle(hint_text=reshape_text('ناهار'), font_name='Persian', halign='right')
        layout.add_widget(self.lunch_input)
        
        self.dinner_input = TextInputStyle(hint_text=reshape_text('شام'), font_name='Persian', halign='right')
        layout.add_widget(self.dinner_input)
        
        save_btn = StyledButton(text=reshape_text('ذخیره'), font_name='Persian', halign='right')
        save_btn.bind(on_press=self.save_data)
        layout.add_widget(save_btn)
        
        back_btn = StyledButton(text=reshape_text('بازگشت به منو'), font_name='Persian', halign='right')
        back_btn.bind(on_press=self.go_back_to_menu)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def save_data(self, instance):
        employee_code = self.employee_code_input.text
        check_in_time = self.check_in_time_input.text
        check_out_time = self.check_out_time_input.text
        delay = self.delay_input.text
        overtime = self.overtime_input.text
        breakfast = self.breakfast_input.text
        lunch = self.lunch_input.text
        dinner = self.dinner_input.text
        
        conn = sqlite3.connect('restaurant.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO employeedaily (employee_code, check_in_time, check_out_time, delay, overtime, breakfast, lunch, dinner)
        VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employee_code, check_in_time, check_out_time, delay, overtime, breakfast, lunch, dinner, ))
        
        conn.commit()
        conn.close()
        
        self.employee_code_input.text = ''
        self.check_in_time_input.text = ''
        self.check_out_time_input.text = ''
        self.delay_input.text = ''
        self.overtime_input.text = ''
        self.breakfast_input.text = ''
        self.lunch_input.text = ''
        self.dinner_input.text = ''
   
    def go_back_to_menu(self, instance):
        self.manager.current = 'personels'


class Massengerscreen(Screen):
    def __init__(self, **kwargs):
        super(Massengerscreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
    
        self.text_input = TextInputStyle(hint_text=reshape_text('متن را وارد کنید'), font_name='Persian', halign='right')
        layout.add_widget(self.text_input)
        
        self.number_input = TextInputStyle(hint_text=reshape_text('شماره را وارد کنید'), font_name='Persian', input_filter='int', halign='right')
        layout.add_widget(self.number_input)
        
        send_btn = StyledButton(text=reshape_text('ارسال'), font_name='Persian', halign='right')
        send_btn.bind(on_press=self.send_message)
        layout.add_widget(send_btn)
        
        btn = StyledButton(text=reshape_text('بازگشت به صفحه اصلی'), font_name='Persian', halign='right')
        btn.bind(on_press=self.go_back)
        layout.add_widget(btn)
        
        self.add_widget(layout)

    def send_message(self, instance):
        text = self.text_input.text
        number = self.number_input.text
        
        url = "https://api.inboxino.com/send"
        payload = {
            "phone_number": number,
            "message": text,
            "api_key": "YOUR_API_KEY"
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("پیام با موفقیت ارسال شد")
        else:
            print("خطا در ارسال پیام")

    def go_back(self, instance):
        self.manager.current = 'manager'

class EventScreen(Screen):
    def __init__(self, **kwargs):
        super(EventScreen, self).__init__(**kwargs)
        self.user_name = LoginScreen.current_username
        self.create_database()      
        layout = BoxLayout(orientation='vertical')
        self.tasks_layout = GridLayout(cols=4, size_hint_y=None, spacing=70, padding=10)
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height - 100))
        scroll_view.add_widget(self.tasks_layout)        
        input_layout = BoxLayout(size_hint_y=None, height=50)
        self.task_input = TextInput(hint_text='Task')
        self.importance_input = Spinner(text='Importance', values=('Low', 'Medium', 'High'))
        self.due_date_input = TextInput(hint_text='Due Date')
        add_button = Button(text='Add Task', on_press=self.add_task)
        input_layout.add_widget(self.task_input)
        input_layout.add_widget(self.importance_input)
        input_layout.add_widget(self.due_date_input)
        input_layout.add_widget(add_button)        
        layout.add_widget(scroll_view)
        layout.add_widget(input_layout)        
        self.add_widget(layout)        
        self.load_tasks()
    def create_database(self):
        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()
        table_name = f"tasks_{self.user_name}"
        c.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, task TEXT, importance TEXT, due_date TEXT, completed INTEGER)''')
        conn.commit()
        conn.close()
    def add_task(self, instance):
        task = self.task_input.text
        importance = self.importance_input.text
        due_date = self.due_date_input.text
        if not task or not importance or not due_date:
            print("All fields must be filled")
            return
        self.task_input.text = ''
        self.importance_input.text = 'Importance'
        self.due_date_input.text = ''     
        self.add_task_to_db(task, importance, due_date)
        self.load_tasks()

    def add_task_to_db(self, task, importance, due_date):
        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()
        table_name = f"tasks_{self.user_name}"
        c.execute(f'''INSERT INTO {table_name} (task, importance, due_date, completed) VALUES (?, ?, ?, ?)''', (task, importance, due_date, 0))
        conn.commit()
        conn.close()
    def load_tasks(self):
        self.tasks_layout.clear_widgets()
        tasks = self.load_tasks_from_db()
        for task_id, task, importance, due_date, completed in tasks:
            task_label = Label(text=task, color=(0, 0, 0, 1))
            importance_label = Label(text=importance, color=(0, 0, 0, 1))
            due_date_label = Label(text=due_date, color=(0, 0, 0, 1))
            checkbox = ColoredCheckBox(active=bool(completed))
            checkbox.bind(active=self.on_checkbox_active)
            checkbox.task_id = task_id
            
            self.tasks_layout.add_widget(task_label)
            self.tasks_layout.add_widget(importance_label)
            self.tasks_layout.add_widget(due_date_label)
            self.tasks_layout.add_widget(checkbox)
    def load_tasks_from_db(self):
        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()
        table_name = f"tasks_{self.user_name}"
        c.execute(f'''SELECT id, task, importance, due_date, completed FROM {table_name}''')
        tasks = c.fetchall()
        conn.close()
        return tasks
    def on_checkbox_active(self, checkbox, value):
        task_id = checkbox.task_id
        self.update_task_status(task_id, int(value))
        self.load_tasks()
    def update_task_status(self, task_id, completed):
        conn = sqlite3.connect('restaurant.db')
        c = conn.cursor()
        table_name = f"tasks_{self.user_name}"
        c.execute(f'''UPDATE {table_name} SET completed = ? WHERE id = ?''', (completed, task_id))
        conn.commit()
        conn.close()

     
class ChecklistsScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsScreen, self).__init__(**kwargs)
        with self.canvas.before:
            Color(0.97, 0.97, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.bind(size=self._update_rect, pos=self._update_rect)
        layout = BoxLayout(orientation='vertical')

        btn1 = StyledButton(text=reshape_text('چک لیست سرویس بهداشتی'))
        btn1.bind(on_press=self.go_to_ChecklistsOneScreen)
        layout.add_widget(btn1)

        btn2 = StyledButton(text=reshape_text('چک لیست سوپروایزر '))
        btn2.bind(on_press=self.go_to_ChecklistsTwoScreen)
        layout.add_widget(btn2)

        btn3 = StyledButton(text=reshape_text('چک لیست نظافت محوطه و آلاچیق ها'))
        btn3.bind(on_press=self.go_to_ChecklistsThreeScreen)
        layout.add_widget(btn3)


        btn4= StyledButton(text=reshape_text('چک لیست مسئول دفتر'))
        btn4.bind(on_press=self.go_to_ChecklistsFourScreen)
        layout.add_widget(btn4)
        

        btn5= StyledButton(text=reshape_text('چک لیست نظافت خدمات و محوطه'))
        btn5.bind(on_press=self.go_to_ChecklistsFiveScreen)
        layout.add_widget(btn5)        
        

        btn6= StyledButton(text=reshape_text('چک لیست باز کردن هفتگی رستوران'))
        btn6.bind(on_press=self.go_to_ChecklistsSixScreen)
        layout.add_widget(btn6)
        
                

        btn7= StyledButton(text=reshape_text('چک لیست بستن رستوران'))
        btn7.bind(on_press=self.go_to_ChecklistsSevenScreen)
        layout.add_widget(btn7)                                
        
        btn8= StyledButton(text=reshape_text('بازگشت'))
        btn8.bind(on_press=self.go_back)
        layout.add_widget(btn8)

        self.add_widget(layout)
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size    

    def go_to_ChecklistsOneScreen(self, instance):
        self.manager.current = 'checklistsone'       
    def go_to_ChecklistsTwoScreen(self, instance):
        self.manager.current = 'checkliststwo'        
    def go_to_ChecklistsThreeScreen(self, instance):
        self.manager.current = 'checkliststhree'
    def go_to_ChecklistsFourScreen(self, instance):
        self.manager.current = 'checklistsfour'        
    def go_to_ChecklistsFiveScreen(self, instance):
        self.manager.current = 'checklistsfive'
    def go_to_ChecklistsSixScreen(self, instance):
       self.manager.current = 'checklistssix'       
    def go_to_ChecklistsSevenScreen(self, instance):
        self.manager.current = 'checklistsseven'       
    def go_back(self, instance):
        self.manager.current = 'manager'

class ChecklistsOneScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsOneScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['سرویس ایرانی','سرویس فرنگی','شیرآلات','سطل زباله','هواکش','مایع دست','آیینه','روشویی','درب','کف و گوشه ها','دستمال','دیوارها']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin',color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistone (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                serviceirani INTEGER,
                servicefarangi INTEGER,
                faucets INTEGER,
                trash INTEGER,
                ventilation INTEGER,
                toiletliquid INTEGER,
                mirror INTEGER,
                vanity INTEGER,
                doors INTEGER,
                floor INTEGER,
                paper INTEGER,
                walls INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        serviceirani = 1 if self.checkboxes['سرویس ایرانی'].active else 0
        servicefarangi = 1 if self.checkboxes['سرویس فرنگی'].active else 0
        faucets = 1 if self.checkboxes['شیرآلات'].active else 0
        trash = 1 if self.checkboxes['سطل زباله'].active else 0
        ventilation = 1 if self.checkboxes['هواکش'].active else 0
        toiletliquid = 1 if self.checkboxes['مایع دست'].active else 0 
        mirror = 1 if self.checkboxes['آیینه'].active else 0
        vanity = 1 if self.checkboxes['روشویی'].active else 0
        doors = 1 if self.checkboxes['درب'].active else 0
        floor = 1 if self.checkboxes['کف و گوشه ها'].active else 0
        paper = 1 if self.checkboxes['دستمال'].active else 0
        walls = 1 if self.checkboxes['دیوارها'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistone (timestamp, user, serviceirani,servicefarangi,faucets,trash,ventilation,toiletliquid,mirror,vanity,doors,floor,paper,walls)
            VALUES (?, ?, ?, ?,?, ?, ?, ?,?, ?, ?, ?,?, ?)
        ''', (timestamp, user, serviceirani,servicefarangi,faucets,trash,ventilation,toiletliquid,mirror,vanity,doors,floor,paper,walls))
        self.conn.commit()
               
 
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='notif', content=popup_content, size_hint=(0.6, 0.4))
        popup.open()
        
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
        
class ChecklistsTwoScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsTwoScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['سرویس بهداشتی', 'سکشن آبنما', 'سکو', 'سکشن جلوی کافه', 'سکشن چتری', 'سکشن دیواری', 'جلو آلاچیق', 'تراس', 'سالن۱', 'سالن ۳']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklisttwo (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                restroom INTEGER,
                fountain_section INTEGER,
                platform INTEGER,
                cafe_front_section INTEGER,
                umbrella_section INTEGER,
                wall_section INTEGER,
                gazebo_front INTEGER,
                terrace INTEGER,
                hall1 INTEGER,
                hall3 INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        restroom = 1 if self.checkboxes['سرویس بهداشتی'].active else 0
        fountain_section = 1 if self.checkboxes['سکشن آبنما'].active else 0
        platform = 1 if self.checkboxes['سکو'].active else 0
        cafe_front_section = 1 if self.checkboxes['سکشن جلوی کافه'].active else 0
        umbrella_section = 1 if self.checkboxes['سکشن چتری'].active else 0
        wall_section = 1 if self.checkboxes['سکشن دیواری'].active else 0
        gazebo_front = 1 if self.checkboxes['جلو آلاچیق'].active else 0
        terrace = 1 if self.checkboxes['تراس'].active else 0
        hall1 = 1 if self.checkboxes['سالن۱'].active else 0
        hall3 = 1 if self.checkboxes['سالن ۳'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklisttwo (timestamp, user, restroom, fountain_section, platform, cafe_front_section, umbrella_section, wall_section, gazebo_front, terrace, hall1, hall3)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, restroom, fountain_section, platform, cafe_front_section, umbrella_section, wall_section, gazebo_front, terrace, hall1, hall3))
        self.conn.commit()
        
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
        
class ChecklistsThreeScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsThreeScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['آیینه ها', 'شیشه آلاچیق', 'صندوق', 'کف محوطه', 'میزها', 'صندلی ها', 'گلدان ها', 'چراغ و لوسترها', 'چراغ محوطه', 'درب ها']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistthree (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                mirrors INTEGER,
                gazebo_glass INTEGER,
                cash_register INTEGER,
                yard_floor INTEGER,
                tables INTEGER,
                chairs INTEGER,
                vases INTEGER,
                lights_chandeliers INTEGER,
                yard_lights INTEGER,
                doors INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        mirrors = 1 if self.checkboxes['آیینه ها'].active else 0
        gazebo_glass = 1 if self.checkboxes['شیشه آلاچیق'].active else 0
        cash_register = 1 if self.checkboxes['صندوق'].active else 0
        yard_floor = 1 if self.checkboxes['کف محوطه'].active else 0
        tables = 1 if self.checkboxes['میزها'].active else 0
        chairs = 1 if self.checkboxes['صندلی ها'].active else 0
        vases = 1 if self.checkboxes['گلدان ها'].active else 0
        lights_chandeliers = 1 if self.checkboxes['چراغ و لوسترها'].active else 0
        yard_lights = 1 if self.checkboxes['چراغ محوطه'].active else 0
        doors = 1 if self.checkboxes['درب ها'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistthree (timestamp, user, mirrors, gazebo_glass, cash_register, yard_floor, tables, chairs, vases, lights_chandeliers, yard_lights, doors)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, mirrors, gazebo_glass, cash_register, yard_floor, tables, chairs, vases, lights_chandeliers, yard_lights, doors))
        self.conn.commit()
        
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
        
        
class ChecklistsFourScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsFourScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['موضوع و شرح رویداد', 'اعلام شده به', 'در ساعت', 'پیگیری ساعت', 'نتیجه پیگیری', 'بررسی نتیجه ساعت', 'ارسال برای مدیر عامل']
        self.text_inputs = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            text_input = TextInput(font_name='Nazanin', multiline=False)
            self.text_inputs[item] = text_input
            self.grid.add_widget(text_input)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistfour (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                event_subject TEXT,
                reported_to TEXT,
                reported_time TEXT,
                followup_time TEXT,
                followup_result TEXT,
                result_review_time TEXT,
                sent_to_ceo TEXT
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        event_subject = self.text_inputs['موضوع و شرح رویداد'].text
        reported_to = self.text_inputs['اعلام شده به'].text
        reported_time = self.text_inputs['در ساعت'].text
        followup_time = self.text_inputs['پیگیری ساعت'].text
        followup_result = self.text_inputs['نتیجه پیگیری'].text
        result_review_time = self.text_inputs['بررسی نتیجه ساعت'].text
        sent_to_ceo = self.text_inputs['ارسال برای مدیر عامل'].text
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistfour (timestamp, user, event_subject, reported_to, reported_time, followup_time, followup_result, result_review_time, sent_to_ceo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, event_subject, reported_to, reported_time, followup_time, followup_result, result_review_time, sent_to_ceo))
        self.conn.commit()
        
        for text_input in self.text_inputs.values():
            text_input.text = ''
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
        
class ChecklistsFiveScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsFiveScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['کف محوطه', 'شیشه های محوطه', 'آبنماها', 'کف سالن', 'باغچه ها', 'نرده ها', 'اکسسوری', 'گلدان ها', 'شیشه تراس', 'چراغ و لوستر', 'درب های شیشه ای', 'قسمت زباله ها']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistfour (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                yard_floor INTEGER,
                yard_glass INTEGER,
                fountains INTEGER,
                hall_floor INTEGER,
                gardens INTEGER,
                fences INTEGER,
                accessories INTEGER,
                vases INTEGER,
                terrace_glass INTEGER,
                lights_chandeliers INTEGER,
                glass_doors INTEGER,
                trash_area INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        yard_floor = 1 if self.checkboxes['کف محوطه'].active else 0
        yard_glass = 1 if self.checkboxes['شیشه های محوطه'].active else 0
        fountains = 1 if self.checkboxes['آبنماها'].active else 0
        hall_floor = 1 if self.checkboxes['کف سالن'].active else 0
        gardens = 1 if self.checkboxes['باغچه ها'].active else 0
        fences = 1 if self.checkboxes['نرده ها'].active else 0
        accessories = 1 if self.checkboxes['اکسسوری'].active else 0
        vases = 1 if self.checkboxes['گلدان ها'].active else 0
        terrace_glass = 1 if self.checkboxes['شیشه تراس'].active else 0
        lights_chandeliers = 1 if self.checkboxes['چراغ و لوستر'].active else 0
        glass_doors = 1 if self.checkboxes['درب های شیشه ای'].active else 0
        trash_area = 1 if self.checkboxes['قسمت زباله ها'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistfour (timestamp, user, yard_floor, yard_glass, fountains, hall_floor, gardens, fences, accessories, vases, terrace_glass, lights_chandeliers, glass_doors, trash_area)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, yard_floor, yard_glass, fountains, hall_floor, gardens, fences, accessories, vases, terrace_glass, lights_chandeliers, glass_doors, trash_area))
        self.conn.commit()
        
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
        
class ChecklistsSixScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsSixScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['نورگیر سالن۱', 'شیشه سالن۱', 'شیشه سالن۳', 'پشت فن کویل', 'کولرهای گازی', 'کف وسایل سکشن ها', 'شیشه های دیوارها', 'نرده های درب۲', 'نظافت باغچه خیابان۲', 'لای ردبی جوب خیابان ۲', 'آبنماهای محوطه', 'پلاستیک چتری ها']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistsix (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                hall1_skylight INTEGER,
                hall1_glass INTEGER,
                hall3_glass INTEGER,
                behind_fan_coil INTEGER,
                air_conditioners INTEGER,
                section_floor INTEGER,
                wall_glass INTEGER,
                door2_fences INTEGER,
                street2_garden_cleaning INTEGER,
                street2_gutter_cleaning INTEGER,
                yard_fountains INTEGER,
                umbrella_plastic INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        hall1_skylight = 1 if self.checkboxes['نورگیر سالن۱'].active else 0
        hall1_glass = 1 if self.checkboxes['شیشه سالن۱'].active else 0
        hall3_glass = 1 if self.checkboxes['شیشه سالن۳'].active else 0
        behind_fan_coil = 1 if self.checkboxes['پشت فن کویل'].active else 0
        air_conditioners = 1 if self.checkboxes['کولرهای گازی'].active else 0
        section_floor = 1 if self.checkboxes['کف وسایل سکشن ها'].active else 0
        wall_glass = 1 if self.checkboxes['شیشه های دیوارها'].active else 0
        door2_fences = 1 if self.checkboxes['نرده های درب۲'].active else 0
        street2_garden_cleaning = 1 if self.checkboxes['نظافت باغچه خیابان۲'].active else 0
        street2_gutter_cleaning = 1 if self.checkboxes['لای ردبی جوب خیابان ۲'].active else 0
        yard_fountains = 1 if self.checkboxes['آبنماهای محوطه'].active else 0
        umbrella_plastic = 1 if self.checkboxes['پلاستیک چتری ها'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistsix (timestamp, user, hall1_skylight, hall1_glass, hall3_glass, behind_fan_coil, air_conditioners, section_floor, wall_glass, door2_fences, street2_garden_cleaning, street2_gutter_cleaning, yard_fountains, umbrella_plastic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, hall1_skylight, hall1_glass, hall3_glass, behind_fan_coil, air_conditioners, section_floor, wall_glass, door2_fences, street2_garden_cleaning, street2_gutter_cleaning, yard_fountains, umbrella_plastic))
        self.conn.commit()
        
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()

        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
         
class ChecklistsSevenScreen(Screen):
    def __init__(self, **kwargs):
        super(ChecklistsSevenScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        self.conn = sqlite3.connect('restaurant.db')
        self.create_table()
        
        self.grid = GridLayout(cols=2)
        self.checklist_items = ['نظافت تمام میزها', 'انتقال ظروف به ظرفشورخانه', 'جمع‌آوری ظروف کافه', 'انتقال ظروف به کافی‌شاپ', 'جمع‌آوری نمکدان و جا دستمال‌ها', 'شمارش جا دستمال و نمکدان‌ها', 'نظافت زمین‌های قسمت', 'خالی کردن سطل زباله تمام قسمت‌ها', 'نظافت کامل سرویس‌های بهداشتی', 'خاموش بودن هواکش', 'خاموش کردن روشنایی‌های اضافی', 'خاموش کردن سیستم گرمایشی و سرمایشی', 'خاموش کردن آبنما', 'خروج پرسنل از مجموعه', 'بسته بودن تمامی درب‌های مجموعه']
        self.checkboxes = {}
        
        for item in self.checklist_items:
            reshaped_text = arabic_reshaper.reshape(item)
            bidi_text = get_display(reshaped_text)
            label = Label(text=bidi_text, font_name='Nazanin', color=(0,0,0,1))
            Rectangle(size=label.size, pos=label.pos)
            self.grid.add_widget(label)
            checkbox = ColoredCheckBox(size_hint=(None, None), size=(50, 50))
            self.checkboxes[item] = checkbox
            self.grid.add_widget(checkbox)
        layout.add_widget(self.grid)
        
        self.submit_button = StyledButton(text=reshape_text('ثبت'), font_name='Nazanin')
        self.submit_button.bind(on_press=self.submit)
        layout.add_widget(self.submit_button)
         
        self.back_button = StyledButton(text=reshape_text('بازگشت'), font_name='Nazanin')
        self.back_button.bind(on_press=self.back)
        layout.add_widget(self.back_button)
        
        self.add_widget(layout)
        
    def back(self, instance):
        self.manager.current = 'checklists'
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checklistseven (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                user TEXT,
                clean_all_tables INTEGER,
                transfer_dishes_to_kitchen INTEGER,
                collect_cafe_dishes INTEGER,
                transfer_dishes_to_cafe INTEGER,
                collect_salt_and_napkin_holders INTEGER,
                count_salt_and_napkin_holders INTEGER,
                clean_section_floors INTEGER,
                empty_all_trash_bins INTEGER,
                clean_all_restrooms INTEGER,
                exhaust_fan_off INTEGER,
                turn_off_extra_lights INTEGER,
                turn_off_heating_and_cooling INTEGER,
                turn_off_fountain INTEGER,
                staff_exit INTEGER,
                all_doors_closed INTEGER
            )
        ''')
        self.conn.commit()
    
    def submit(self, instance):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user = LoginScreen.current_username
        clean_all_tables = 1 if self.checkboxes['نظافت تمام میزها'].active else 0
        transfer_dishes_to_kitchen = 1 if self.checkboxes['انتقال ظروف به ظرفشورخانه'].active else 0
        collect_cafe_dishes = 1 if self.checkboxes['جمع‌آوری ظروف کافه'].active else 0
        transfer_dishes_to_cafe = 1 if self.checkboxes['انتقال ظروف به کافی‌شاپ'].active else 0
        collect_salt_and_napkin_holders = 1 if self.checkboxes['جمع‌آوری نمکدان و جا دستمال‌ها'].active else 0
        count_salt_and_napkin_holders = 1 if self.checkboxes['شمارش جا دستمال و نمکدان‌ها'].active else 0
        clean_section_floors = 1 if self.checkboxes['نظافت زمین‌های قسمت'].active else 0
        empty_all_trash_bins = 1 if self.checkboxes['خالی کردن سطل زباله تمام قسمت‌ها'].active else 0
        clean_all_restrooms = 1 if self.checkboxes['نظافت کامل سرویس‌های بهداشتی'].active else 0
        exhaust_fan_off = 1 if self.checkboxes['خاموش بودن هواکش'].active else 0
        turn_off_extra_lights = 1 if self.checkboxes['خاموش کردن روشنایی‌های اضافی'].active else 0
        turn_off_heating_and_cooling = 1 if self.checkboxes['خاموش کردن سیستم گرمایشی و سرمایشی'].active else 0
        turn_off_fountain = 1 if self.checkboxes['خاموش کردن آبنما'].active else 0
        staff_exit = 1 if self.checkboxes['خروج پرسنل از مجموعه'].active else 0
        all_doors_closed = 1 if self.checkboxes['بسته بودن تمامی درب‌های مجموعه'].active else 0
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO checklistseven (timestamp, user, clean_all_tables, transfer_dishes_to_kitchen, collect_cafe_dishes, transfer_dishes_to_cafe, collect_salt_and_napkin_holders, count_salt_and_napkin_holders, clean_section_floors, empty_all_trash_bins, clean_all_restrooms, exhaust_fan_off, turn_off_extra_lights, turn_off_heating_and_cooling, turn_off_fountain, staff_exit, all_doors_closed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, clean_all_tables, transfer_dishes_to_kitchen, collect_cafe_dishes, transfer_dishes_to_cafe, collect_salt_and_napkin_holders, count_salt_and_napkin_holders, clean_section_floors, empty_all_trash_bins, clean_all_restrooms, exhaust_fan_off, turn_off_extra_lights, turn_off_heating_and_cooling, turn_off_fountain, staff_exit, all_doors_closed))
        self.conn.commit()
        
        for checkbox in self.checkboxes.values():
            checkbox.active = False
        
        reshaped_message = arabic_reshaper.reshape('ثبت موفق!')
        bidi_message = get_display(reshaped_message)
        popup_content = Label(text=bidi_message, font_name='Nazanin')
        popup = Popup(title='پیام', content=popup_content, size_hint=(None, None), size=(400, 400))
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1)
    
    def on_stop(self):
        self.conn.close()
                
class TasksScreen(Screen):
    def __init__(self, **kwargs):
        super(TasksScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        label = Label(text=reshape_text('این صفحه شرح وظایف است'), font_name='Persian')
        layout.add_widget(label)
        self.add_widget(layout)

        

        
class ExpertScreen(Screen):
    pass

class EmployeeScreen(Screen):
    pass

class GuestScreen(Screen):
    pass
        
     
        


class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        
        sm.add_widget(ManagerScreen(name='manager'))
        sm.add_widget(Servicescreen(name='service'))
        sm.add_widget(Showservicescreen(name='showservice'))
        sm.add_widget(Addservicescreen(name='addservice'))
        sm.add_widget(Personelsscreen(name='personels'))
        sm.add_widget(Addpersonelscreen(name='addpersonel'))
        sm.add_widget(Showpersonelscreen(name='showpersonel'))
        sm.add_widget(Reportspersonelscreen(name='reportspersonel'))
        sm.add_widget(Massengerscreen(name='massenger'))
        sm.add_widget(ChecklistsScreen(name='checklists'))
        sm.add_widget(ChecklistsOneScreen(name='checklistsone'))
        sm.add_widget(ChecklistsTwoScreen(name='checkliststwo'))
        sm.add_widget(ChecklistsThreeScreen(name='checkliststhree'))
        sm.add_widget(ChecklistsFourScreen(name='checklistsfour'))
        sm.add_widget(ChecklistsFiveScreen(name='checklistsfive'))
        sm.add_widget(ChecklistsSixScreen(name='checklistssix'))
        sm.add_widget(ChecklistsSevenScreen(name='checklistsseven'))
        sm.add_widget(TasksScreen(name='tasks'))
        sm.add_widget(EventScreen(name='events'))
        
        sm.add_widget(ExpertScreen(name='expert'))
        
        sm.add_widget(EmployeeScreen(name='employee'))
        
        sm.add_widget(GuestScreen(name='guest'))             
        
        return sm

if __name__ == '__main__':
    MyApp().run()
