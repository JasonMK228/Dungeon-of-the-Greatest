from tkinter import * #Импорт библиотек
from tkinter.scrolledtext import ScrolledText
from ClassHero import get_hero,CLASS_TEMPLATES, get_hero_damage
from ASC_Sprites import *
from random import *
from math import ceil
from Enemy_DB import ENEMY_DB
from ChestLoot import CHESTLOOT

room = 0
hero = None
money = 0
enemy = None
current_enemy = None
combat_active = False
is_defending = False
current_loot = None

root = Tk()#Создание окна
root.title("Darkest Dungeon")
root.geometry("640x480+600+200")
root.resizable(False, False)
root.configure(bg="#0b0b0b")

BG_DARK = "#0b0b0b"       # Основной фон окна
BG_PANEL = "#141414"      # Фон боковых панелей
TEXT_MAIN = "#c9c9c9"     # Основной текст
TEXT_HP = "#e74c3c"       # Красный для HP
TEXT_STAMINA = "#2ecc71"  # Зелёный для стамины
TEXT_MANA = "#0091ff"     # Голубой для маны
TEXT_MONEY = "#fff01c"    # Жёлтый для монет
BORDER_COL = "#333333"
"""========================================================================="""

info_frame = Frame(root, bg=BG_PANEL, width=150)
info_frame.pack(side="left", fill="y", padx=5)
info_frame.pack_propagate(False)

log_frame = Frame(root, bg="#0b0b0b", bd=2, relief="solid")
log_frame.pack(side="right", fill="y", padx=5)

Label(info_frame, text="⚔️ ГЕРОЙ", font=("Times", 14, "bold"), bg=BG_PANEL, fg=TEXT_MAIN).pack(pady=(10, 5))
Frame(info_frame, height=1, bg=BORDER_COL).pack(fill="x", pady=5)

listbox = ScrolledText(log_frame,bg = "#0b0b0b",fg = "white",font = ("Times",11),state = "disabled",width = 24)
listbox.pack(side="right",fill = "y")

mainbox = Text(root,bg="#0b0b0b",fg="white",font=("Consolas", 10),state="disabled",width=40,bd=0,)

classL = Label(info_frame, text="Класс: -", font=("Times", 12, "bold"), bg=BG_PANEL, fg=TEXT_MAIN)
classL.pack(anchor="w", padx=10, pady=(0, 5))

HPL = Label(info_frame, text="HP: -", font=("Consolas", 13, "bold"), bg=BG_PANEL, fg=TEXT_HP)
HPL.pack(anchor="w", padx=10, pady=2)

staminaL = Label(info_frame, text="Стамина: -", font=("Consolas", 12), bg=BG_PANEL, fg=TEXT_STAMINA)
staminaL.pack(anchor="w", padx=10, pady=2)

manaL = Label(info_frame,text="Мана: -",font=("Consolas",12),bg=BG_PANEL,fg = TEXT_MANA)
manaL.pack(anchor = "w",padx=10,pady=2)

moneyL = Label(info_frame,text="💰: -", font = ("Colsolas", 12), bg=BG_PANEL,fg = TEXT_MONEY)
moneyL.pack(anchor = "w", padx=10, pady=2)

Frame(info_frame, height=1, bg=BORDER_COL).pack(fill="x", pady=8)

Label(info_frame, text="ХАРАКТЕРИСТИКИ", font=("Times", 10, "bold"), bg=BG_PANEL, fg=TEXT_MAIN).pack(anchor="w", padx=10)
statL = Label(info_frame, text="Сила: -\nЛовкость: -\nИнтеллект: -", font=("Consolas", 11), bg=BG_PANEL, fg=TEXT_MAIN)
statL.pack(anchor="w", padx=10, pady=5)

Frame(info_frame, height=1, bg=BORDER_COL).pack(fill="x", pady=8)

roomL = Label(info_frame, text="Комната: 0", font=("Consolas", 12, "bold"), bg=BG_PANEL, fg=TEXT_MAIN)
roomL.pack(anchor="w", padx=10, pady=2)

Label(info_frame, text="🎒 ИНВЕНТАРЬ", font=("Times", 11, "bold"), bg=BG_PANEL, fg=TEXT_MAIN).pack(anchor="w", padx=10, pady=(8, 2))

inventoryL = Label(info_frame, text="Пусто", font=("Consolas", 9), bg=BG_PANEL, fg=TEXT_MAIN,justify="left", anchor="w", wraplength=140)
inventoryL.pack(anchor="w", padx=10, pady=2, fill="x")

"""========================================================================="""
def update_info():
    if hero is None:
        return
    classL.config(text=f"Класс: {hero.Class}")
    max_hp = getattr(hero, "MAX_HP",hero.HP)
    HPL.config(text=f"HP: {hero.HP}/{max_hp}")
    staminaL.config(text=f"Стамина: {hero.Stamina}")
    manaL.config(text=f"Мана: {hero.Mana}")
    moneyL.config(text=f"💰: {money}")
    statL.config(text=f'Сила: {hero.Strength}\n'
                      f'Ловкость: {hero.Agility}\n'
                      f'Интеллект: {hero.Intellect}')
    roomL.config(text=f"Комната: {room}")
    inv_text = ", ".join(hero.Inventory) if hero.Inventory else "Пусто"
    inventoryL.config(text=f"Инвентарь: \n{inv_text}")

def add_log(message):
    listbox.config(state = "normal")
    listbox.insert("end",message +"\n")
    listbox.see("end")
    listbox.config(state="disabled")

def draw_ascii(text):
    mainbox.config(state = "normal")
    mainbox.delete("1.0","end")
    mainbox.insert("1.0",text)
    mainbox.config(state = "disabled")

#Фрейм для кнопок
action_frame = Frame(root,bg = BG_DARK)
action_frame.pack(side = "bottom",fill = "x", pady=10)

#Генерация кнопок
def clear_buttons():
    for widget in action_frame.winfo_children():
        widget.destroy()

def select_class(name):
    global hero, room
    hero = get_hero(name)
    room = 0

    if not hasattr(hero,"Mana"):
        if hero.Class in ["Маг","Палладин"]:
            hero.Mana,hero.MaxMana = 50,50
        else:
            hero.Mana, hero.MaxMana = 0,0

    update_info()
    town()

def style_btn(btn):
    btn.config(bg="#2a2a2a", fg="white", font=("Times", 12),
               relief="flat",
               bd=0,
               highlightthickness=0,
               activebackground="#3a3a3a",
               activeforeground="white")
    btn.bind("<Enter>",lambda e: btn.config(bg="#3a3a3a"))
    btn.bind("<Leave>",lambda e:btn.config(bg="#2a2a2a"))
"""========================================================================="""

def dungeon():
    clear_buttons()
    add_log("------------------")
    add_log("Вы спустились во тьму...")
    draw_ascii(dungeon_art)

    row = Frame(action_frame, bg = BG_DARK)
    row.pack(side="top", pady=5)

    below_but = Frame(action_frame)
    below_but.pack(side="top", pady=5)

    bt1 = Button(row, text="Идти вперёд", command=step)
    style_btn(bt1)
    bt1.pack(side="left", padx=5)

    bt2 = Button(row, text="Использовать зелье", command=hero_potion)
    style_btn(bt2)
    bt2.pack(side="left", padx=5)

    bt3 = Button(action_frame, text="Вернуться в город", command=town)
    style_btn(bt3)
    bt3.pack(side="top", pady=5)

    if hero is not None and hero.Class == "Вор":
        btn4 = Button(action_frame, text="Пробежать комнаты")
        style_btn(btn4)
        btn4.pack(side="top", pady=5)

def town():
    hover_info.pack_forget()

    mainbox.pack(side="top", fill="both", expand=True)
    draw_ascii(town_art)
    global room
    clear_buttons()
    add_log("------------------")
    add_log("Добро пожаловать в город!\n"
            "Чувствуйте себя как дома")
    room = 0
    # if hasattr(hero,"MAX_HP") or hero.HP<hero.MAX_HP:
    #     hero.HP = hero.MAX_HP
    update_info()

    row1 = Frame(action_frame,bg=BG_DARK)
    row1.pack(side="top",pady=5)

    btn1 = Button(row1, text="Таверна",command=tavern)
    style_btn(btn1)
    btn1.pack(side="left", padx=5)

    btn2 = Button(row1, text = "Монастырь",command=monastery)
    style_btn(btn2)
    btn2.pack(side="left",padx=5)

    btn3 = Button(row1,text="Лавка")
    style_btn(btn3)
    btn3.pack(side='left',padx=5)

    row2 = Frame(action_frame,bg=BG_DARK)
    row2.pack(side = "top",pady=5)

    btn4 = Button(row2,text = "Гильдия")
    style_btn(btn4)
    btn4.pack(side = "left",padx=5)

    btn5 = Button(row2,text="Шатёр Барда")
    style_btn(btn5)
    btn5.pack(side="left",padx=5)

    btn6 = Button(action_frame, text="Спуск в пещеру", command=show_dungeon_ui)
    style_btn(btn6)
    btn6.pack(side="top", padx=5)

# def combat():
#     top_buttons_frame = Frame(action_frame)
#     top_buttons_frame.pack(side="top", pady=5)
#
#     Button(top_buttons_frame, text="Атаковать").pack(side="left", padx=5)
#     Button(top_buttons_frame, text="Защита").pack(side="left", padx=5)
#     Button(top_buttons_frame, text="Использовать зелье").pack(side="left", padx=5)
#     if hero is not None and hero.Class == "Маг":
#         Button(action_frame, text="Использовать заклинание").pack(side="top",pady = 5)
#     if hero is not None and hero.Class == "Паладин":
#         Button(action_frame, text="Лечебное заклинание").pack(side="top", pady=5)

"""========================================================================="""
def tavern():
    clear_buttons()
    add_log("\n🍺Таверна: Тепло, запах эля и шумиха")

    row = Frame(action_frame,bg = BG_DARK)
    row.pack(side="top",pady=5)

    btn1 = Button(row,text="Отдохнуть (+HP,50💰)",command=lambda:rest_tavern(50))
    style_btn(btn1)
    btn1.pack(side = "left",padx=5)

    btn2 = Button(row,text="Сплетни (20💰)")
    style_btn(btn2)
    btn2.pack(side="left",padx=5)

    btn3 = Button(action_frame,text="Назад",command=town)
    style_btn(btn3)
    btn3.pack(side="top",pady=5)

def monastery():
    clear_buttons()
    add_log("\nМонастырь: Тишина, свечи и запах ладана.")
    if hero.Class not in ["Маг","Палладин"]:
        add_log("\nМонахи кивают вам, но молитвы не для вашего пути")
    row = Frame(action_frame,bg=BG_PANEL)
    row.pack(side="top",pady=5)

    btn1 = Button(row,text = "Помолиться (+Мана, 40💰")
    style_btn(btn1)
    btn1.pack(side="left",padx=5)

    btn2 = Button(action_frame,text = "Назад",command=town)
    style_btn(btn2)
    btn2.pack(side="top",pady=5)
def rest_tavern(cost):
    global money
    if money>=cost and hero.HP<hero.MAX_HP:
        money-=cost
        hero.HP = getattr(hero,"MAX_HP",hero.HP)
        add_log(f"\nВы отдохнули. HP восстановлено. (-{cost} 💰)")
    elif hero.HP>=hero.MAX_HP:
        add_log("\nВаше здоровье на максимуме!")
    else:
        add_log("\nНедостаточно золота!")
    update_info()

"""========================================================================="""

hover_info = Label(root,text = "",font = ("Consolas",10),bg="#0b0b0b",fg="#e0c97f",wraplength=140)
hover_info.pack(side="top",fill="x",pady = 5)

def show_class_stats(class_name):
    data = CLASS_TEMPLATES[class_name]
    info = (f"HP: {data['hp']} Выносливость: {data['stamina']}\n"
            f"Сила: {data['strength']} ЛВК: {data['agility']} ИНТ: {data['intellect']}\n"
            f"Инвентарь: {', '.join(data['inventory'])}")
    hover_info.config(text=info)
def hide_class_stats():
    hover_info.config(text='')

def class_selection():
    clear_buttons()
    add_log("Выберите себе класс")

    classes = ["Рыцарь","Воин","Маг","Бард","Паладин","Вор"]
    for cls in classes:
        btn = Button(action_frame,text = cls,command=lambda  c=cls:select_class(c),font=("Times",16),width=10)
        style_btn(btn)
        btn.pack(side="top", pady=10)

        btn.bind("<Enter>", lambda e,c=cls:show_class_stats(c))
        btn.bind("<Leave>", lambda e:hide_class_stats())
    """
    Button(action_frame, text="Рыцарь",command=lambda: select_class("Рыцарь"),font = ("Times",17),width=10).pack(side="top",pady=15)
    Button(action_frame, text="Воин",command=lambda: select_class("Воин"), font = ("Times",17),width=10).pack(side="top",pady=15)
    Button(action_frame, text="Маг",command=lambda: select_class("Маг"),font = ("Times",17),width=10).pack(side="top",pady=15)
    Button(action_frame, text="Бард",command=lambda: select_class("Бард"), font = ("Times",17),width=10).pack(side="top",pady=15)
    Button(action_frame, text="Паладин",command=lambda: select_class("Паладин"), font = ("Times",17),width=10).pack(side="top",pady=15)
    Button(action_frame, text="Вор", command=lambda: select_class("Вор"), font=("Times", 17),width=10).pack(side="top",pady=15)
    """
def show_dungeon_ui():
    clear_buttons()
    row = Frame(action_frame,bg = BG_DARK)
    row.pack(side = "top",pady=5)

    draw_ascii(dungeon_art)

    bt1 = Button(row, text="Идти вперёд", command=step)
    style_btn(bt1)
    bt1.pack(side="left", padx=5)

    bt2 = Button(row, text="Использовать зелье", command=hero_potion,bg = BG_PANEL)
    style_btn(bt2)
    bt2.pack(side="left", padx=5)

    bt3 = Button(action_frame, text="Вернуться в город", command=town)
    style_btn(bt3)
    bt3.pack(side="top", pady=5)

    if hero is not None and hero.Class == "Вор":
        btn4 = Button(action_frame, text="Пробежать комнаты")
        style_btn(btn4)
        btn4.pack(side="top", pady=5)

def step():
    global room
    if hero is None:
        return;

    if hero.Stamina <= 70: hero.Stamina +=5
    room+=1
    event = randrange(1,15)
    update_info()
    add_log(f"\nВы прошли комнату {room}")

    if event == 1:
        add_log("\nВы нашли деревянный сундук! Хотите его открыть?")
        draw_ascii(chest_art)
        clear_buttons()

        below_but = Frame(action_frame,bg = BG_DARK)
        below_but.pack(side="top", pady=5)

        btn1 = Button(below_but, text="Открыть", command=get_loot)
        style_btn(btn1)
        btn1.pack(side="left", padx=5)

        btn2 = Button(below_but, text="Пропустить", command=step)
        style_btn(btn2)
        btn2.pack(side="left", padx=5)

    elif event in [2,3]:
        enemy_name = choice(list(ENEMY_DB.keys()))
        start_combat(enemy_name)

    else:
        show_dungeon_ui()
        draw_ascii(dungeon_art)

"""====================================================================="""

def start_combat(enemy_name):
    global current_enemy,combat_active,is_defending
    if hero is None or enemy_name not in ENEMY_DB:
        return
    clear_buttons()
    data = ENEMY_DB[enemy_name]
    current_enemy = {
        "name": enemy_name,
        "hp": data["hp"],
        "max_hp": data["hp"],
        "dmg_min": data["dmg"][0],
        "dmg_max": data["dmg"][1],
        "def": data.get("def", 0)
    }
    combat_active = True
    is_defending = False
    if "Скелет" in enemy_name:
        draw_ascii(skeleton_art)
    elif "Волк" in enemy_name or "волк" in enemy_name.lower():
        draw_ascii(wolf_art)
    else:
        draw_ascii(dungeon_art)
    add_log(f"\nПоявляется {enemy_name}. HP: {current_enemy['hp']}")
    show_combat_ui()

def show_combat_ui():
    clear_buttons()

    top_buttons_frame = Frame(action_frame,bg = BG_DARK)
    top_buttons_frame.pack(side="top", pady=5)

    btn1 = Button(top_buttons_frame, text="Атаковать", command=hero_attack)
    style_btn(btn1)
    btn1.pack(side="left", padx=5)

    btn2 = Button(top_buttons_frame, text="Защита",command=hero_defend)
    style_btn(btn2)
    btn2.pack(side="left", padx=5)

    btn3 = Button(top_buttons_frame, text="Использовать зелье",command=hero_potion)
    style_btn(btn3)
    btn3.pack(side="left", padx=5)

    if hero is not None and hero.Class == "Маг":
        btn4 = Button(action_frame, text="Использовать заклинание")
        style_btn(btn4)
        btn4.pack(side="top", pady=5)
    if hero is not None and hero.Class == "Паладин":
        btn5 = Button(action_frame, text="Лечебное заклинание").pack(side="top", pady=5)
        style_btn(btn5)
        btn5.pack(side="top", pady=5)
    add_log(f"\nТвой ход")
def hero_attack():
    global current_enemy,combat_active,is_defending
    if not combat_active or hero is None or current_enemy is None: return

    if hero.Stamina<5:
        add_log("\nНе хватает стамины!")
        root.after(500,enemy_turn)
        return
    hero.Stamina -=5
    w_min,w_max = get_hero_damage(hero)
    base_dmg = randint(w_min,w_max) + ceil(hero.Strength/2)
    final_dmg = max(1,base_dmg-current_enemy["def"])

    if randint(1,100)<=10:
        add_log("\nВы промазали!")
    else:
        current_enemy["hp"]-=final_dmg
        add_log(f"\nВы попали! {current_enemy['name']} получил {final_dmg} урона")
    is_defending = False
    update_info()

    if current_enemy["hp"]<=0:
        combat_end(victory = True)
    else:
        root.after(400,enemy_turn)

def hero_defend():
    global is_defending
    if not combat_active: return
    is_defending = True
    hero.Stamina+=10
    add_log("\nТы принимаешь защитную стойку")
    update_info()
    root.after(400,enemy_turn)

def hero_potion():
    if hero is None: return
    if "Зелье Исцеления" in hero.Inventory:
        hero.Inventory.remove("Зелье Исцеления")
        heal = randint(30,50)
        hero.HP+=heal
        add_log(f"\nВы выпили зелье и восстановили {heal} хп")
    else:
        add_log("\nЗелий нет в инвентаре")
    update_info()
    root.after(400,enemy_turn)

def enemy_turn():
    global current_enemy,combat_active,is_defending
    if not combat_active or hero is None or current_enemy is None: return

    dmg = randint(current_enemy["dmg_min"],current_enemy["dmg_max"])
    if is_defending:
        dmg = ceil(dmg/2)
        add_log(f"\nБлок! {current_enemy['name']} наносит вам {dmg} урона")
    else:
        add_log(f"\n{current_enemy['name']} наносит вам {dmg} урона")

    hero.HP-=dmg
    is_defending = False
    update_info()

    if hero.HP <=0:
        add_log("\nТьма поглотила тебя...")
        combat_active = False
        root.after(1000,lambda: [clear_buttons(),town()])
    else:
        show_combat_ui()
def combat_end(victory = False):
    global current_enemy, combat_active, is_defending, money
    combat_active = False
    if victory:
        gold = randint(10,40)
        money+=gold
        add_log(f"\nВы победили и получаете {gold} монет!")
        current_enemy = None
        update_info()
        root.after(800,show_dungeon_ui)
    else:
        current_enemy = None
        update_info()
        root.after(1000, lambda: [clear_buttons(), town()])
"""========================================================="""
def get_loot():
    global current_loot
    clear_buttons()

    current_loot = choice(CHESTLOOT)

    add_log(f"\nСундук открыт. Внутри {current_loot}")

    row = Frame(action_frame,bg = BG_PANEL)
    row.pack(side = "top",pady=5)

    btn1 = Button(row,text = "Взять",command=confirm_loot)
    style_btn(btn1)
    btn1.pack(side = "left",padx=5)

    btn2 = Button(row,text = "Оставить", command=decline_loot)
    style_btn(btn2)
    btn2.pack(side = "left", padx=5)

def confirm_loot():
    global current_loot
    if current_loot is not None:
        hero.Inventory.append(current_loot)
        add_log(f"\nВы получили {current_loot}")
        update_info()
    show_dungeon_ui()
def decline_loot():
    add_log("\nВы оставили вещи в сундуке")
    show_dungeon_ui()

Location = "0"

#Начинаем с выбора класса
class_selection()
#combat()
update_info()

root.mainloop()

