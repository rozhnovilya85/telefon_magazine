import psycopg2
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import re
import bcrypt


window = tk.Tk()
window.title('Magazine')
# window.geometry("340x250")
# window.resizable(False, False)

# кортежи и словари, содержащие настройки шрифтов и отступов
font_header = ('Arial', 15)
font_btn = ('Arial', 12)
font_entry = ('Arial', 12)
label_font = ('Arial', 11)
base_padding = {'padx': 10, 'pady': 8}
header_padding = {'padx': 10, 'pady': 12}

pattern1 = "^{3,16}$"
pattern2 = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'
valid = True
connection = None
hash = None
order = []

# переменные для создание форм
name = tk.StringVar()  
surname = tk.StringVar()
patronymic = tk.StringVar()
login = tk.StringVar()  
password = tk.StringVar()  
pass_conf = tk.StringVar()
rom_memory = tk.StringVar()
ram_memory = tk.StringVar()
processor = tk.StringVar()

constring_authorization = [
("Логин", login),
("Пароль", password)
]

constring_register = [
("Имя", name),
("Отчество", patronymic),
("Фамилия", surname),
("Логин", login),
("Пароль", password),
("Подтвердите пароль", pass_conf)
]
updprod = [
("Название", name),
("Память", rom_memory),
("Оперативная память", ram_memory),
("Процессор", processor)
]


def form_register():
    global send_btn_a, send_btn_r
    #скрываем поля из формы авторизации и создаем форму регистрации
    frame_authorization.pack_forget()
    frame_register = tk.Frame(window)
    send_btn_r = tk.Button(frame_register, text='Зарегистрироваться', command=register, font=font_btn)
    send_btn_a = tk.Button(frame_register, text='Войти', state="disabled", command=authorization, font=font_btn)
    frame_register.pack()
    for i in constring_register:
        frame_register.pack()
        lbl = tk.Label(frame_register, font=label_font, text=i[0])
        if i[1] != password:
            textbox_db = tk.Entry(frame_register, textvariable=i[1], validate="focusout", validatecommand=check, font=font_entry)
        elif i[1] == pass_conf:
            textbox_db = tk.Entry(frame_register, show='*', textvariable=i[1], font=font_entry)
        else:
            textbox_db = tk.Entry(frame_register, show='*', textvariable=i[1], validate="focusout", validatecommand=check, font=font_entry)
        lbl.pack()
        textbox_db.pack()
    send_btn_r.pack(**base_padding)

    send_btn_a.pack(**base_padding)

def is_valid(newval):
    global valid
    if re.match(r"^[a-zA-Z]$", newval):
        print("Valid")
    else:
        print("Invalid")
        valid = False
check = (window.register(is_valid), "%p")

def register():
    global connection, send_btn_a, hash, password
    try:
        connection = psycopg2.connect(  # Подключение к БД PostgreSQL
            database="telefon_magazine",  # Название БД
            user="postgres",  # Имя пользователя
            password="1234demo",  # Пароль пользователя
            host="localhost",  # Путь БД (localhost) (127.0.0.1)
            port="5432"  # Порт БД
        )
    except psycopg2.OperationalError as e:
        messagebox.showerror(f"Подключится к БД не удалось\n{e}")

    try:
        if valid == True:
            if password.get() == pass_conf.get():
                password = password.get()
                bytes = password.encode('utf-8')
                salt = bcrypt.gensalt()
                hash = bcrypt.hashpw(bytes, salt)
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name,patronymic,surname,login,password) VALUES (%s,%s,%s,%s,%s)",
                               (name.get(),
                                patronymic.get(),
                                surname.get(),
                                login.get(),
                                str(hash)
                                )
                               )
                cursor.close()
                connection.commit()
                send_btn_a.config(state="normal", command=authorization)
                messagebox.showinfo(message="Пользователь успешно зарегистрирован!")

            else:
                messagebox.showerror(message="Пароль и подтвержденный пароль не совпадают!")
        else:
            messagebox.showerror(message="Ошибка в форме регистрации проверте данные!")

    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

def user_window():
    global connection, list_select, treev, cursor, frame_select
    cursor = connection.cursor()
    frame_authorization.pack_forget()
    frame_select = tk.Frame(window)
    try:  # Удаление существующей таблицы
        treev.destroy()
    except:
        pass
    try:
        cursor.execute("SELECT * FROM telephone")
        list_select = cursor.fetchall()
        columns_employee = ("name", "rom_memory", "ram_memory", "processor")
        treev = ttk.Treeview(frame_select, columns=columns_employee, show="headings")
        treev.heading("name", text="Название")
        treev.heading("rom_memory", text="Кол-во памяти")
        treev.heading("ram_memory", text="Кол-во оперативной памяти")
        treev.heading("processor", text="Процессор")

        for employee in list_select:
            treev.insert("", "end", iid=employee[0], values=employee[1:])
        treev.pack()
        connection.commit()

    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

    frame_select.pack()
    btn_order = tk.Button(frame_select, text='Заказ', command=orders, font=font_btn)
    btn_basket = tk.Button(frame_select, text='Корзина', command=basket, font=font_btn)
    btn_order.pack(**base_padding)
    btn_basket.pack(**base_padding)
    
def admin():
    global cursor, frame_authorization, treev, list_users, frame_admin_user, list_prod, treev_prod, columns_prod, frame_admin_product, frame_prod_upd
    try:  # Удаление существующей таблицы
        frame_admin_user.pack_forget()
        frame_admin_product.pack_forget()
        frame_prod_upd.pack_forget()
        treev.destroy()
    except:
        pass

    cursor = connection.cursor()

    frame_authorization.pack_forget()
    frame_admin_user = tk.LabelFrame(window, font=font_header, text="Пользователи")
    frame_admin_tv_user = tk.Frame(frame_admin_user)
    frame_admin_tv_btn = tk.Frame(frame_admin_user)
    btn_admin_user = tk.Button(frame_admin_tv_btn, font=font_btn, text='Пользователи', command=admin)
    btn_admin_adm = tk.Button(frame_admin_tv_btn, font=font_btn, text='Администратор', command=btn_admin)
    btn_admin_del = tk.Button(frame_admin_tv_btn, font=font_btn, text='Удалить', command=btn_del)
    frame_admin_product = tk.LabelFrame(window, font=font_header, text="Товары")
    frame_admin_tv_product = tk.Frame(frame_admin_product)
    frame_prod_tv_btn = tk.Frame(frame_admin_tv_product)
    btn_prod = tk.Button(frame_prod_tv_btn, font=font_btn, text='Товары', command=admin)
    btn_prod_del = tk.Button(frame_prod_tv_btn, font=font_btn, text='Удалить', command=btn_del_prod)
    btn_prod_chan = tk.Button(frame_prod_tv_btn, font=font_btn, text='Изменить', command=prod_chan)
    btn_prod_supp = tk.Button(frame_prod_tv_btn, font=font_btn, text='Добавить', command=prod_supp)
    frame_prod_upd = tk.LabelFrame(window, font=font_header, text="Добавление/Изменение")



    try:
        cursor.execute("SELECT * FROM users")
        list_users = cursor.fetchall()

        columns_users = ("surname", "name", "patronymic", "login", "password", "admin", "delete")
        treev = ttk.Treeview(frame_admin_tv_user, columns=columns_users, show="headings")
        treev.heading("surname", text="Фамилия")
        treev.heading("name", text="Имя")
        treev.heading("patronymic", text="Отчество")
        treev.heading("login", text="Логин")
        treev.heading("password", text="Пароль")
        treev.heading("admin", text="Администратор")
        treev.heading("delete", text="Удален")

        for users in list_users:
            treev.insert("", "end", iid=users[0], values=users[1:])

        connection.commit()
        cursor.close()

    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM telephone")
        list_prod = cursor.fetchall()
        columns_prod = ("name", "rom_memory", "ram_memory", "processor")
        treev_prod = ttk.Treeview(frame_admin_tv_product, columns=columns_prod, show="headings")
        treev_prod.heading("name", text="Название")
        treev_prod.heading("rom_memory", text="Память")
        treev_prod.heading("ram_memory", text="Оперативная память")
        treev_prod.heading("processor", text="Процессор")


        for prod in list_prod:
            treev_prod.insert("", "end", iid=prod[0], values=prod[1:])

        connection.commit()
        cursor.close()

    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

    for name, var in updprod:
        frame = tk.Frame(frame_prod_upd)
        frame.pack(side="left")

        tk.Label(frame, text=name,  font=label_font).pack()
        tk.Entry(frame, textvariable=var, font=font_entry).pack()


    frame_admin_user.pack()
    frame_admin_tv_user.pack()
    treev.pack()
    frame_admin_tv_btn.pack()
    btn_admin_user.pack(side="left", **base_padding)
    btn_admin_adm.pack(side="left", **base_padding)
    btn_admin_del.pack(side="left", **base_padding)
    frame_admin_product.pack()
    frame_admin_tv_product.pack()
    treev_prod.pack()
    frame_prod_tv_btn.pack()
    btn_prod.pack(side="left", **base_padding)
    btn_prod_del.pack(side="left", **base_padding)
    btn_prod_chan.pack(side="left", **base_padding)
    btn_prod_supp.pack(side="left", **base_padding)
    frame_prod_upd.pack()

def prod_supp():
    global connection
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO telephone (name,rom_memory,ram_memory,processor) VALUES (%s,%s,%s,%s)",
                       (name.get(),
                        rom_memory.get(),
                        ram_memory.get(),
                        processor.get()
                        )
                       )
        connection.commit()
        cursor.close()
        messagebox.showinfo(message="Команда была успешно выполнена")
    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

def prod_chan():
    global connection, treev_prod
    try:
        index = treev_prod.focus()


        cursor = connection.cursor()
        cursor.execute("UPDATE telephone SET name=%s,rom_memory=%s,ram_memory=%s, processor=%s WHERE id_tel=%s",
                       (name.get(),
                        rom_memory.get(),
                        ram_memory.get(),
                        processor.get(),
                        index
                        )
                       )
        cursor.close()
        connection.commit()
        messagebox.showinfo(message="Команда была успешно выполнена")
    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

def btn_del_prod():
    global connection, treev_prod
    try:
        index = treev_prod.focus()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM telephone WHERE id_tel = %s",(index))
        connection.commit()
        cursor.close()
        messagebox.showinfo(message="Команда была успешно выполнена")
    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")
    


def btn_del():
    global connection
    try:
        index = treev.focus()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET delete=True WHERE id=%s",(index))
        cursor.close()
        connection.commit()
        messagebox.showinfo(message="Команда была успешно выполнена")
    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

def btn_admin():
    global connection
    try:
        index = treev.focus()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET admin=True WHERE id=%s",(index))
        cursor.close()
        connection.commit()
        messagebox.showinfo(message="Команда была успешно выполнена")
    except Exception as e:
        connection.rollback()
        messagebox.showerror(message=f"Команда не было успешно выполнена\n{e}")

def orders():
    global order
    index = treev.focus()
    order_f = treev.item(index)["values"]
    order.append(order_f)

def basket():
    global frame_select
    frame_select.pack_forget()
    frame_basket = tk.Frame(window)
    columns_z = ("name", "rom_memory", "ram_memory", "processor")
    treev = ttk.Treeview(frame_basket, columns=columns_z, show="headings")
    treev.heading("name", text="Название")
    treev.heading("rom_memory", text="Кол-во памяти")
    treev.heading("ram_memory", text="Кол-во оперативной памяти")
    treev.heading("processor", text="Процессор")

    for employee in order:
        treev.insert("", "end", values=employee)
    frame_basket.pack()
    treev.pack()
    btn_zak = tk.Button(frame_basket, text='Купить', command=btn_z)
    btn_zak.pack()

def btn_z():
    messagebox.showinfo(message="Поздравляем с покупкой!!!")



def authorization():
    global connection, list_select, login_1, password
    try:
        connection = psycopg2.connect(  # Подключение к БД PostgreSQL
            database="telefon_magazine",  # Название БД
            user="postgres",  # Имя пользователя
            password="1234demo",  # Пароль пользователя
            host="localhost",  # Путь БД (localhost) (127.0.0.1)
            port="5432"  # Порт БД
        )
    except psycopg2.OperationalError as e:
        messagebox.showerror(f"Подключится к БД не удалось\n{e}")

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE login=%s",
                   (login.get(),))
    list_select = cursor.fetchall()
    
    
    if len(list_select) != 0:
        password_bytes = password.get()
        password_db = list_select[0][5][2:-1]
        password_db_bytes = password_db.encode('utf-8')
        userBytes = password_bytes.encode('utf-8')
        result = bcrypt.checkpw(userBytes, password_db_bytes)
        if result == True:
    
            if list_select[0][7] == False:
                if list_select[0][6] == False:
                    user_window()
                else:
                    admin()
            else:
                messagebox.showerror(message="Пользователь заблокирован администратом!")
        else:
            messagebox.showerror(message="Проверте введеный пароль пользователя!")
    else:
            messagebox.showerror(message="Проверте логин пользователя!")

    cursor.close()


# форма авторизации пользователя
frame_authorization = tk.Frame(window)
frame_authorization.pack()
lb4 = tk.Label(frame_authorization, text="Авторизуйтесь, для входа в программу!", font=font_entry)
lb4.pack()

for i in constring_authorization:
    lbl = tk.Label(frame_authorization, text=i[0], font=font_entry)
    if i[1] != password:
        textbox_db = tk.Entry(frame_authorization, textvariable=i[1], font=font_entry)
    else:
        textbox_db = tk.Entry(frame_authorization, show='*', textvariable=i[1], font=font_entry)
    lbl.pack()
    textbox_db.pack()
# кнопка отправки формы
send_btn_a = tk.Button(frame_authorization, text='Войти', command=authorization, font=font_btn)
send_btn_a.pack(**base_padding)

lb3 = tk.Label(frame_authorization, text="Первый раз у нас, тогда зарегистрируйтесь!", font=label_font)
lb3.pack()
# кнопка регистрации
send_btn_r = tk.Button(frame_authorization, text='Регистрация', font=font_btn, command=form_register)
send_btn_r.pack(**base_padding)

# форма регистрации пользователя
frame_register = tk.LabelFrame(window, text="Регистрация")
send_btn_r = tk.Button(frame_authorization, text='Зарегистрироваться', font=font_btn, command=register)



window.mainloop()
