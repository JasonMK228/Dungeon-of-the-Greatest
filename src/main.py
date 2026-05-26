from tkinter import * #Импорт библиотек
from tkinter.scrolledtext import ScrolledText
from ClassHero import get_hero,CLASS_TEMPLATES, get_hero_damage
from ASC_Sprites import *
from random import *
from math import ceil
from Enemy_DB import ENEMY_DB
from ChestLoot import CHESTLOOT
from Story_from_tavern import GOSSIP_LIST

room = 0
hero = None
money = 0
enemy = None
current_enemy = None
combat_active = False
is_defending = False
current_loot = None
MAX_INV_SLOT = 10
day_count = 1
hero_stunned = False
demon_attack_mode = None

root = Tk()#Создание окна
root.title("Dungeon of the Greatest")
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
        if hero.Class in ["Маг","Паладин"]:
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

def open_inventory(return_to):
    clear_buttons()

    if not hero.Inventory:
        add_log("Пусто")
    else:
        for item in hero.Inventory:
            btn = Button(action_frame,text=f"{item}",command=lambda it=item: drop_item(it,return_to))
            style_btn(btn)
            btn.pack(side="top",pady=3,fill="x",padx=30)
    btn_back = Button(action_frame,text="Назад",command=return_to)
    style_btn(btn_back)
    btn_back.pack(side="top",pady=10)

def drop_item(item,return_to):
    if item in hero.Inventory:
        hero.Inventory.remove(item)
        add_log(f"Выбросили:{item}")
        update_info()
        open_inventory(return_to)
def confirm_loot():
    global current_loot
    if len(hero.Inventory)>=MAX_INV_SLOT:
        add_log("\nИнвентарь полон!")
        show_dungeon_ui()
        return
    if current_loot is not None:
        hero.Inventory.append(current_loot)
        add_log(f"Вы получили {current_loot}")
        update_info()
    show_dungeon_ui()
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
    global day_count
    global room

    if room>0:
        day_count+=1;

    hover_info.pack_forget()

    mainbox.pack(side="top", fill="both", expand=True)
    draw_ascii(town_art)

    clear_buttons()
    add_log("------------------")
    add_log("Добро пожаловать в город!\n"
            "Чувствуйте себя как дома")
    add_log(f"День {day_count}")
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

    btn3 = Button(row1,text="Лавка",command=shop)
    style_btn(btn3)
    btn3.pack(side='left',padx=5)

    row2 = Frame(action_frame,bg=BG_DARK)
    row2.pack(side = "top",pady=5)

    btn4 = Button(row2,text = "Гильдия",command=guild)
    style_btn(btn4)
    btn4.pack(side = "left",padx=5)

    # btn5 = Button(row2,text="Шатёр Барда")
    # style_btn(btn5)
    # btn5.pack(side="left",padx=5)

    btn6 = Button(action_frame, text="Спуск в пещеру", command=show_dungeon_ui)
    style_btn(btn6)
    btn6.pack(side="top", padx=5)

    btn_inv = Button(action_frame, text="Инвентарь", command=lambda: open_inventory(town))
    style_btn(btn_inv)
    btn_inv.pack(side="top", pady=5)

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

    btn1 = Button(row,text="Отдохнуть (+HP,150💰)",command=lambda:rest_tavern(150))
    style_btn(btn1)
    btn1.pack(side = "top",pady=5)

    btn2 = Button(row,text="Сплетни (50💰)",command=lambda:gossip_taver(50))
    style_btn(btn2)
    btn2.pack(side="top",pady=5)

    btn4 = Button(row,text="Ставка 50💰", command=lambda:gample(50,150,40))
    style_btn(btn4); btn4.pack(side="top",pady=5)

    btn5 = Button(row,text="Ставка 100💰",command=lambda:gample(100,400,10))
    style_btn(btn5); btn5.pack(side="top",pady=5)

    btn3 = Button(action_frame,text="Назад",command=town)
    style_btn(btn3)
    btn3.pack(side="top",pady=5)

def monastery():
    clear_buttons()
    add_log("\nМонастырь: Тишина, свечи и запах ладана.")
    if hero.Class not in ["Маг","Паладин"]:
        add_log("\nМонахи кивают вам, но молитвы не для вашего пути")
    row = Frame(action_frame,bg=BG_PANEL)
    row.pack(side="top",pady=5, fill = "x")

    if hero.Class in ["Маг","Паладин"]:
        btn1 = Button(row, text="Помолиться (+Мана, 100💰)", command=lambda: pray_monastery(100))
        style_btn(btn1);
        btn1.pack(side="left", pady=3, fill="x", padx=10)
    if hero.Class=="Бард":
        btn3 = Button(row,text="Очищение Разума(+Макс. Стамина, 250💰", command=lambda:clear_mind(150))
        style_btn(btn3); btn3.pack(side="top",pady=3,fill='x',padx=10)

    btn2 = Button(action_frame,text = "Назад",command=town)
    style_btn(btn2)
    btn2.pack(side="top",pady=5)

def shop():
    clear_buttons()
    add_log("\nЛавка: \"Лучшие товары по лучшим ценам... почти.\"")

    catalog = {
        "Зелье Исцеления": 60, "Зелье Маны": 80, "Отмычка": 50, "Лопата": 40,
        "Верёвка": 40, "Противоядие": 50,
        "Кинжал": 150, "Булава": 180, "Посох": 200, "Гитерн": 200, "Рапира": 220,
        "Длинный меч": 260, "Боевой топор": 280, "Копьё": 290, "Баклер": 140, "Щит": 240,
        "Святой меч": 330, "Двуручный меч": 380, "Огромный меч": 400, "Алебарда": 420
    }

    shop_container = Frame(action_frame, bg=BG_DARK)
    shop_container.pack(side="top", pady=5, fill="x")

    items = list(catalog.items())
    mid = len(items) // 2
    left_items = items[:mid]
    right_items = items[mid:]

    col_left = Frame(shop_container, bg=BG_DARK)
    col_left.pack(side="left", fill="both", expand=True, padx=5)

    for item, price in left_items:
        btn = Button(col_left, text=f"{item} ({price}💰)",
                     command=lambda i=item, p=price: buy_item(i, p),
                     justify="left")
        style_btn(btn)
        btn.config(font=("Times", 9))
        btn.pack(side="top", pady=2, fill="x", padx=5, anchor="w")

    col_right = Frame(shop_container, bg=BG_DARK)
    col_right.pack(side="left", fill="both", expand=True, padx=5)

    for item, price in right_items:
        btn = Button(col_right, text=f"{item} ({price}💰)",
                     command=lambda i=item, p=price: buy_item(i, p),
                     justify="left")
        style_btn(btn)
        btn.config(font=("Times", 9))
        btn.pack(side="top", pady=2, fill="x", padx=5, anchor="w")

    btn_back = Button(action_frame, text="Назад", command=town)
    style_btn(btn_back)
    btn_back.pack(side="top", pady=5)

def guild():
    clear_buttons()
    add_log("\n Гильдия Искателей: Здесь куют героев.")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top",pady=5,fill="x")

    btn1 = Button(row,text="Совет ветерана",command=guild_advice)
    style_btn(btn1); btn1.pack(side="top",pady=3,fill="x",padx=10)

    str_cost = 300 + (hero.Strength * 50) if hero else 300
    agi_cost = 300 + (hero.Agility * 50) if hero else 300
    int_cost = 300 + (hero.Intellect * 50) if hero else 300

    btn2 = Button(row,text=f"+1 Сила ({str_cost}💰)",command=lambda: train_stat("Сила",str_cost))
    style_btn(btn2); btn2.pack(side="top",pady=3,fill="x",padx=10)

    btn3 = Button(row,text=f"+1 Ловкость ({agi_cost}💰)",command=lambda:train_stat("Ловкость",agi_cost))
    style_btn(btn3);
    btn3.pack(side="top", pady=3, fill="x", padx=10)

    btn4 = Button(row, text=f"+1 Интеллект ({int_cost}💰)", command=lambda: train_stat("Интеллект", int_cost))
    style_btn(btn4);
    btn4.pack(side="top", pady=3, fill="x", padx=10)

    btn_back = Button(action_frame, text="Назад", command=town)
    style_btn(btn_back);
    btn_back.pack(side="top", pady=5)

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

def gossip_taver(cost):
    global money
    if money >= cost:
        money-=cost
        add_log(choice(GOSSIP_LIST))
        update_info()
    else:
        add_log("\nНедостаточно золота!")
        update_info()

def gample(bet,prize,chance):
    global money
    if money>=bet:
        money-=bet
        if randint(1,100)<=chance:
            money+=prize
            add_log(f"\n Удача! Вы выиграли {prize} монет!")
        else:
            add_log("\n Не повезло...")
    else:
        add_log("\n Недостаточно золота для ставки!")
    update_info()

def pray_monastery(cost):
    global money
    if money>=cost:
        money-=cost
        hero.Mana = getattr(hero,"MaxMana",50)
        add_log(f"\n Молитва услышана. Мана восстановлена. (-{cost}💰)")
    else:
        add_log("\n Недостаточно золота!")
    update_info()

def clear_mind(cost):
    global money
    if money >=cost:
        money-=cost
        hero.Stamina = getattr(hero,"MAX_STAMINA",70)
        add_log(f"Разум чист! Стамина восстановлена. (-{cost}💰)")
    else:
        add_log("Недостаточно золота!")
    update_info()

def buy_item(item,price):
    global money
    if money>=price:
        if len(hero.Inventory) >= MAX_INV_SLOT and item not in ["Зелье Исцеления", "Зелье Маны", "Противоядие"]:
            add_log("\nИнвентарь полон! Выбросьте что-нибудь")
            return
        money -=price
        hero.Inventory.append(item)
        add_log(f"\nВы купили: {item}")
    else:
        add_log("\nНедостаточно золота")
    update_info()


def guild_advice():
    advice = choice([
        "Умей проигрывать",
        "Случайности не случайны",
        "Имей щит, а лучше два",
        "Защита снижает урон врага вдвое на один ход.",
        "Не тратьте все зелья сразу. Босс может быть близко."
    ])
    add_log(f"\nВетеран шепчет: \"{advice}\"")


def train_stat(stat_name, cost):
    global money
    if money >= cost:
        money -= cost
        if stat_name == "Сила":
            hero.Strength += 1
        elif stat_name == "Ловкость":
            hero.Agility += 1
        elif stat_name == "Интеллект":
            hero.Intellect += 1

        add_log(
            f"Тренировка завершена. {stat_name} +1 (Теперь: {getattr(hero, stat_name.replace('Ловкость', 'Agility').replace('Сила', 'Strength').replace('Интеллект', 'Intellect'))})")
    else:
        add_log(f"Недостаточно золота! Нужно {cost} монет.")
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

    classes = ["Рыцарь","Воин","Маг","Бард","Паладин","Вор","Нищий"]
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
    top_buttons_frame = Frame(action_frame, bg=BG_DARK)
    top_buttons_frame.pack(side="top", pady=5)

    draw_ascii(dungeon_art)

    bt1 = Button(row, text="Идти вперёд", command=step)
    style_btn(bt1)
    bt1.pack(side="left", padx=5)

    bt2 = Button(row, text="Использовать зелье", command=hero_potion,bg = BG_PANEL)
    style_btn(bt2)
    bt2.pack(side="left", padx=5)

    if hero is not None and "Зелье Маны" in hero.Inventory:
        btn_mana = Button(top_buttons_frame, text="Зелье Маны", command=use_mana_potion)
        style_btn(btn_mana)
        btn_mana.pack(side="left", padx=5)

    bt3 = Button(action_frame, text="Вернуться в город", command=town)
    style_btn(bt3)
    bt3.pack(side="top", pady=5)

    btn_inv = Button(action_frame, text="Инвентарь", command=lambda: open_inventory(show_dungeon_ui))
    style_btn(btn_inv)
    btn_inv.pack(side="top", pady=5)

    if hero is not None and hero.Class == "Вор":
        btn4 = Button(action_frame, text="Пробежать комнаты",command=rogue_skip_rooms)
        style_btn(btn4)
        btn4.pack(side="top", pady=5)

def step():
    global room
    if hero is None:
        return;

    max_stam = getattr(hero, "MAX_STAMINA", 70)
    if hero.Stamina < max_stam:
        hero.Stamina = min(hero.Stamina + 5, max_stam)

    room+=1
    event = randrange(1,150)
    update_info()
    add_log(f"\nВы прошли комнату {room}")
    if room == 100:
        add_log("------------------\n СТЕНЫ ДРОЖАТ! КРЫЛАТЫЙ ДЕМОН ПРЕГРАЖДАЕТ ПУТЬ!")
        draw_ascii(demon_art)
        start_combat("Крылатый Демон")
        return
    if event <=40:
        enemies = [e for e in ENEMY_DB.keys() if ENEMY_DB[e]["weight"] > 0]
        weights = [ENEMY_DB[e]["weight"] for e in enemies]
        enemy_name = choices(enemies, weights=weights, k=1)[0]
        start_combat(enemy_name)
    elif event <= 73:
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
    elif event<=76:
        event_boulder()
    elif event<=78:
        event_poison_gas()
    elif event<=80:
        event_altar()
    elif event<=84:
        event_locked_door()
    elif event<=88:
        event_spike_trap()
    elif event<=92:
        event_wounded_traveler()
    elif event<=96:
        event_mysterious_door()
    elif event<=100:
        event_cursed_weapon()
    elif event<=102:
        event_ghost_encounter()
    elif event<=104:
        event_collapsing_bridge()
    elif event <=106:
        event_merchant_ghost()
    else:
        show_dungeon_ui()
        draw_ascii(dungeon_art)
def rogue_skip_rooms():
    global room
    if hero is None or hero.Class != "Вор": return
    if hero.Stamina >= 20:
        add_log("\nВор пробежал несколько комнат")
        room += 2
        hero.Stamina = max(0, hero.Stamina - 20)
        update_info()
        show_dungeon_ui()
    else:
        add_log("Не хватает стамины!")
def check_event_death():
    if hero.HP <= 0:
        add_log("☠️ Ты не выдержал испытаний...")
        if hasattr(hero, "MAX_HP"):
            hero.HP = hero.MAX_HP
        update_info()
        root.after(1000, lambda: [clear_buttons(), town()])
        return True
    return False
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
    if enemy_name == "Крылатый Демон":
        current_enemy["charge_turn"] = False
        current_enemy["attack_mode"] = None
    elif "Скелет" in enemy_name:
        draw_ascii(skeleton_art)
    elif "Волк" in enemy_name or "волк" in enemy_name.lower():
        draw_ascii(wolf_art)
    elif "Слизень" in enemy_name:
        draw_ascii(slime_art)
    elif "Свинья" in enemy_name:
        draw_ascii(pig_art)
    elif "Паук" in enemy_name:
        draw_ascii(spider_art)
    elif "Сумасшедший воин" in enemy_name:
        draw_ascii(warrior_art)
    elif "Разбойник" in enemy_name:
        draw_ascii(robber_art)
    elif "Заросший голем" in enemy_name:
        draw_ascii(golem_art)
    else:
        draw_ascii(dungeon_art)
    add_log(f"\nПоявляется {enemy_name}. HP: {current_enemy['hp']}")
    show_combat_ui()


def show_combat_ui():
    clear_buttons()

    top_buttons_frame = Frame(action_frame, bg=BG_DARK)
    top_buttons_frame.pack(side="top", pady=5)

    btn1 = Button(top_buttons_frame, text="Атаковать", command=hero_attack)
    style_btn(btn1);
    btn1.pack(side="left", padx=5)

    btn2 = Button(top_buttons_frame, text="Защита", command=hero_defend)
    style_btn(btn2);
    btn2.pack(side="left", padx=5)

    btn3 = Button(top_buttons_frame, text="Использовать зелье", command=hero_potion)
    style_btn(btn3);
    btn3.pack(side="left", padx=5)

    if hero is not None and "Зелье Маны" in hero.Inventory:
        btn_mana = Button(action_frame, text="Зелье Маны", command=use_mana_potion)
        style_btn(btn_mana)
        btn_mana.pack(side="top", pady=5)  # Пакуем в action_frame, а не в row

    if hero is not None and hero.Class == "Маг":
        btn4 = Button(action_frame, text="Огненный шар", command=cast_mage_fireball)
        style_btn(btn4);
        btn4.pack(side="top", pady=5)

    if hero is not None and hero.Class == "Паладин":
        btn5 = Button(action_frame, text="Святой удар", command=cast_palladin_smite)
        style_btn(btn5);
        btn5.pack(side="top", pady=5)

    if hero is not None and hero.Class == "Вор":
        btn6 = Button(action_frame, text="🗡Удар в спину", command=rogue_backstab)
        style_btn(btn6);
        btn6.pack(side="top", pady=5)

    add_log(f"\nТвой ход")

def hero_attack():
    global current_enemy,combat_active,is_defending
    if not combat_active or hero is None or current_enemy is None: return

    global hero_stunned
    if hero_stunned:
        hero_stunned = False
        add_log("💫 Ты приходишь в себя после оглушения...")
        root.after(500, enemy_turn)
        return
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
    global is_defending, hero_stunned
    if hero_stunned:
        hero_stunned = False
        add_log("Ты приходишь в себя после оглушения...")
        root.after(500, enemy_turn)
        return
    if not combat_active: return
    is_defending = True
    max_stam = getattr(hero, "MAX_STAMINA", 70)
    hero.Stamina = min(hero.Stamina + 10, max_stam)

    add_log("\nТы принимаешь защитную стойку (+10 Стамина)")
    update_info()
    root.after(400, enemy_turn)


def hero_potion():
    global hero_stunned
    if hero_stunned:
        hero_stunned = False
        add_log("💫 Ты приходишь в себя после оглушения...")
        root.after(500, enemy_turn)
        return
    if hero is None: return

    if "Зелье Исцеления" in hero.Inventory:
        hero.Inventory.remove("Зелье Исцеления")
        heal = randint(30, 50)
        hero.HP = min(getattr(hero, "MAX_HP", 150), hero.HP + heal)
        add_log(f"\nВы выпили зелье и восстановили {heal} HP")
    else:
        add_log("\nЗелий нет в инвентаре")
    update_info()
    root.after(400, enemy_turn)
def use_mana_potion():
    global hero_stunned
    if hero_stunned:
        hero_stunned = False
        add_log("💫 Ты приходишь в себя после оглушения...")
        root.after(500, enemy_turn)
        return
    if hero is None: return

    if "Зелье Маны" in hero.Inventory:
        hero.Inventory.remove("Зелье Маны")
        recovery = randint(20, 40)
        hero.Mana = min(getattr(hero, "MaxMana", 50), hero.Mana + recovery)
        add_log(f"🔮 Вы выпили Зелье Маны. +{recovery} маны.")
    else:
        add_log("Нет зелий маны!")

    update_info()
    root.after(400, enemy_turn)
def cast_mage_fireball():
    global current_enemy,combat_active,is_defending
    if not combat_active or hero.Class != "Маг": return
    if hero.Mana<5:
        add_log("Недостаточно маны")
        return
    hero.Mana-=5
    dmg = randint(15,25)+hero.Intellect
    current_enemy["hp"]-=dmg
    add_log(f"Огненный шар! {dmg} урона")
    is_defending = False
    update_info()
    if current_enemy["hp"]<=0: combat_end(victory=True)
    else:root.after(400,enemy_turn)

def cast_palladin_smite():
    global current_enemy,combat_active,is_defending
    if not combat_active or hero.Class !="Паладин": return
    if hero.Mana<12:
        add_log("Недостаточно маны")
        return
    hero.Mana -=12
    dmg = randint(8,14) + ceil(hero.Strength/2)+hero.Intellect
    current_enemy["hp"]-=dmg
    heal = dmg//2
    hero.HP = min(getattr(hero,"MAX_HP",150),hero.HP + heal)
    add_log(f"Святой удар! {dmg} урона. Исцеление: + {heal} HP.")
    is_defending = False
    update_info()
    if current_enemy['hp']<=0:combat_end(victory=True)
    else:root.after(400,enemy_turn)

def rogue_backstab():
    global current_enemy,combat_active, is_defending
    if not combat_active or hero.Class != "Вор":return
    if hero.Stamina<10:
        add_log("Не хватает стамины!")
        return
    hero.Stamina -=10
    base_dmg = randint(10,18) + ceil(hero.Agility/2)
    is_crit = randint(1,100)<=40
    final_dmg = int (base_dmg*1.5) if is_crit else base_dmg
    current_enemy["hp"] -= final_dmg
    crit_txt = "КРИТ!" if is_crit else ""
    add_log(f"{crit_txt} Удар в спину! {final_dmg} урона")
    is_defending=False
    update_info()
    if current_enemy["hp"]<=0:combat_end(victory=True)
    else: root.after(400,enemy_turn)

def enemy_turn():
    global current_enemy, combat_active, is_defending, hero_stunned
    if not combat_active or hero is None or current_enemy is None: return

    if current_enemy["name"] == "Крылатый Демон":
        global demon_attack_mode
        if current_enemy.get("charge_turn", False):
            current_enemy["charge_turn"] = False
            add_log("Крылатый Демон обрушивает заряженный удар!")

            if is_defending:
                dmg = 10
                add_log(f"Защита сработала! Урон снижен до {dmg}.")
            else:
                dmg = 50
                add_log(f"☠Критический удар! -{dmg} HP!")

            hero.HP -= dmg
            is_defending = False
            update_info()

            if hero.HP <= 0:
                add_log("\n☠️ Тьма поглотила тебя...")
                combat_active = False
                if hero and hasattr(hero, "MAX_HP"):
                    hero.HP = max(1, hero.MAX_HP // 2)
                update_info()
                root.after(1000, lambda: [clear_buttons(), town()])
            else:
                show_combat_ui()
            return
        attack_roll = randint(1, 100)

        if attack_roll <= 50:
            dmg = randint(15, 20)
            if is_defending:
                dmg = ceil(dmg / 2)
                add_log(f"Блок! Демон наносит {dmg} урона.")
            else:
                add_log(f"Демон атакует! -{dmg} HP.")
            hero.HP -= dmg

        elif attack_roll <= 80:
            current_enemy["charge_turn"] = True
            add_log("Крылатый Демон набирает силу...")

        else:
            add_log("🗣️ Демон издаёт оглушающий рёв!")
            if randint(1, 100) <= 60:
                add_log("Ты оглушён! Пропускаешь следующий ход.")
                hero_stunned = True
            else:
                add_log("Ты устоял на ногах!")

        is_defending = False
        update_info()

        if hero.HP <= 0:
            add_log("\n☠️ Тьма поглотила тебя...")
            combat_active = False
            if hero and hasattr(hero, "MAX_HP"):
                hero.HP = max(1, hero.MAX_HP // 2)
            update_info()
            root.after(1000, lambda: [clear_buttons(), town()])
        else:
            show_combat_ui()
        return

    dmg = randint(current_enemy["dmg_min"], current_enemy["dmg_max"])
    if is_defending:
        dmg = ceil(dmg/2)
        add_log(f"\nБлок! {current_enemy['name']} наносит вам {dmg} урона")
    else:
        add_log(f"\n{current_enemy['name']} наносит вам {dmg} урона")

    hero.HP -= dmg
    is_defending = False
    update_info()

    if hero.HP <= 0:
        add_log("\n☠️ Тьма поглотила тебя...")
        combat_active = False
        if hero is not None and hasattr(hero, "MAX_HP"):
            hero.HP = max(1, hero.MAX_HP)

        update_info()
        root.after(1000, lambda: [clear_buttons(), town()])
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


def event_boulder():
    clear_buttons()
    add_log("\n Путь преграждает огромный обвал!")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if "Лопата" in hero.Inventory:
        btn1 = Button(row, text="Использовать Лопату", command=lambda: resolve_boulder("shovel"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Разобрать руками", command=lambda: resolve_boulder("hp"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Обойти в темноте", command=lambda: resolve_boulder("stamina"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_boulder(method):
    if method == "shovel":
        hero.Inventory.remove("Лопата")
        add_log("\n Лопата сломалась, но путь расчищен.")
    elif method == "hp":
        hero.HP -= 15
        add_log("\n Ты ободрал руки и сбил ногти. -15 HP.")
        if check_event_death(): return
    elif method == "stamina":
        hero.Stamina = max(0, hero.Stamina - 12)
        add_log("\n Ты пробрался по узкому карнизу. -12 Стамина.")
    update_info()
    show_dungeon_ui()


def event_poison_gas():
    clear_buttons()
    add_log("\n Комната наполнена едким туманом!")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if "Противоядие" in hero.Inventory:
        btn1 = Button(row, text="Выпить Противоядие", command=lambda: resolve_gas("antidote"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Задержать дыхание", command=lambda: resolve_gas("stamina"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Пробежать насквозь", command=lambda: resolve_gas("hp"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_gas(method):
    if method == "antidote":
        hero.Inventory.remove("Противоядие")
        add_log("\n Противоядие нейтрализовало яд.")
    elif method == "stamina":
        hero.Stamina = max(0, hero.Stamina - 20)
        add_log("\n Ты задержал дыхание и проскочил. -20 Стамина.")
    elif method == "hp":
        hero.HP -= 25
        add_log("\n Ты надышался ядом. -25 HP.")
        if check_event_death(): return
    update_info()
    show_dungeon_ui()


def event_altar():
    clear_buttons()
    add_log("\n В углу стоит древний алтарь. От него исходит сила...")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    btn1 = Button(row, text="Пожертвовать", command=lambda: resolve_altar(),
                  anchor="w", justify="left")
    style_btn(btn1)
    btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Не трогать", command=show_dungeon_ui,
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

def resolve_altar():
    global money
    if hero.HP <= 20:
        add_log("\n Слишком мало сил для жертвы!")
        return
    hero.HP -= 20
    reward = choice(["mana", "gold"])
    if reward == "mana":
        hero.Mana = min(getattr(hero, "MaxMana", 50), hero.Mana + 30)
        add_log("\n Алтарь принял жертву. +30 Маны.")
    else:
        money += 40
        add_log("\n Алтарь принял жертву. +40 монет.")
    update_info()
    show_dungeon_ui()


def event_locked_door():
    clear_buttons()
    add_log("\n Массивная дверь преграждает путь. Замок ржавый, но крепкий.")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if "Отмычка" in hero.Inventory:
        btn1 = Button(row, text="Вскрыть Отмычкой", command=lambda: resolve_door("lockpick"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)
    elif hero.Class == "Вор":
        btn3 = Button(row, text="Взломать (классовый навык)", command=lambda: resolve_door("skill"),
                      anchor="w", justify="left")
        style_btn(btn3)
        btn3.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Выбить плечом", command=lambda: resolve_door("hp"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

def resolve_door(method):
    global money
    if method == "lockpick":
        hero.Inventory.remove("Отмычка")
        reward = choice([25, "Зелье Исцеления", "Кинжал"])
        add_log(f"\n Замок щёлкнул. За дверью найдено: {reward}")
        if isinstance(reward, int):
            money += reward
        else:
            hero.Inventory.append(reward)
    elif method == "skill":
        money += 30
        add_log("\n Вор легко справился с замком. +30 монет.")
    elif method == "hp":
        hero.HP -= 20
        add_log("\n Дверь поддалась, но плечо вывернуто. -20 HP.")
        if check_event_death(): return
    update_info()
    show_dungeon_ui()


def event_spike_trap():
    clear_buttons()
    add_log("\n Ловушка! Из пола вылетают шипы!")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if hero.Agility >= 10:
        btn1 = Button(row, text="Уклониться (Ловкость)", command=lambda: resolve_spike("dodge"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Защититься щитом", command=lambda: resolve_spike("shield"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Принять удар", command=lambda: resolve_spike("hp"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_spike(method):
    if method == "dodge":
        add_log("Ты перекатился мимо шипов!")
    elif method == "shield":
        broken = randint(1,10)
        if "Баклер" in hero.Inventory:
            hero.Inventory.remove("Баклер")
            add_log("\n Баклер принял удар и раскололся")
        elif "Щит" in hero.Inventory:
            if broken == 9:
                hero.Inventory.remove("Щит")
                add_log("\nЩит принял удар, но сломался")
            else:
                add_log("\nЩит принял удар")
        else:
            hero.HP -= 30
            add_log("\nЩита нет! -30 HP")
            if check_event_death(): return
    elif method == "hp":
        hero.HP -= 30
        add_log("\nШипы пронзили плоть. -30 HP")
        if check_event_death(): return
    update_info()
    show_dungeon_ui()


def event_wounded_traveler():
    clear_buttons()
    add_log("В углу сидит раненый путник. Он стонет от боли")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if "Зелье Исцеления" in hero.Inventory:
        btn1 = Button(row, text="Дать Зелье", command=lambda: resolve_traveler("potion"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Пройти мимо", command=show_dungeon_ui,
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Ограбить", command=lambda: resolve_traveler("rob"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_traveler(method):
    global money
    if method == "potion":
        hero.Inventory.remove("Зелье Исцеления")
        money += 50
        add_log("\n Путник благодарит тебя! Он дарит 50 золота и карту сокровищ.")
    elif method == "rob":
        money += 30
        add_log("\n Ты его ограбил. Путник проклинает тебя")
    update_info()
    show_dungeon_ui()


def event_mysterious_door():
    clear_buttons()
    add_log("Таинственная дверь с рунами. Она слегка приоткрыта")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if hero.Class == "Маг" or hero.Class == "Паладин":
        btn1 = Button(row, text="Прочитать руны (Интеллект)", command=lambda: resolve_mystery("read"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Открыть и войти", command=lambda: resolve_mystery("enter"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Пройти мимо", command=show_dungeon_ui,
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_mystery(method):
    global money
    if method == "read":
        reward = choice(["mana", "gold", "item"])
        if reward == "mana":
            hero.Mana = min(getattr(hero, "MaxMana", 50), hero.Mana + 40)
            add_log("Руны дают вам знание. +40 Маны")
        elif reward == "gold":
            money += 60
            add_log("В комнате скрыт тайник! +60 золота")
        else:
            hero.Inventory.append("Зелье Маны")
            add_log("Ты нашёл зелье маны")
    elif method == "enter":
        outcome = choice(["good", "bad", "trap"])
        if outcome == "good":
            money += 40
            add_log("Комната пуста, но на столе лежат 40 монет")
        elif outcome == "bad":
            hero.HP -= 25
            add_log("Ловушка! С потолка падает камень. -25 HP")
            if check_event_death(): return
        else:
            hero.Stamina -= 15
            add_log("Тёмная комната напугала тебя. -15 Стамина")
    update_info()
    show_dungeon_ui()


def event_cursed_weapon():
    clear_buttons()
    add_log("\n В центре комнаты на пьедестале лежит меч. Он пульсирует тьмой...")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    btn1 = Button(row, text="Взять меч", command=lambda: resolve_cursed("take"),
                  anchor="w", justify="left")
    style_btn(btn1)
    btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Уничтожить меч", command=lambda: resolve_cursed("destroy"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Оставить и уйти", command=show_dungeon_ui,
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_cursed(method):
    if method == "take":
        hero.Strength += 3
        if hero.HP == hero.MAX_HP:
            hero.HP -= 20
        hero.MAX_HP -= 20
        add_log("\n Ты теряешь жизненную энергию, но получаешь силу")
    elif method == "destroy":
        hero.MAX_HP += 10
        add_log("\n Меч разрушен! Твоя воля крепнет. +10 Макс. HP")
    update_info()
    show_dungeon_ui()


def event_ghost_encounter():
    clear_buttons()
    add_log("\n Призрак преграждает путь. 'Ответь на мой вопрос' говорит он")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    btn1 = Button(row, text="Что тяжелее: Перо или камень?", command=lambda: resolve_ghost("answer1"),
                  anchor="w", justify="left")
    style_btn(btn1)
    btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Я не боюсь тебя!", command=lambda: resolve_ghost("answer2"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Атаковать", command=lambda: resolve_ghost("attack"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_ghost(method):
    if method == "answer1":
        reward = choice(["good", "bad"])
        if reward == "good":
            hero.Mana = min(getattr(hero, "MaxMana", 50), hero.Mana + 25)
            add_log("\n \"Мудро... Очень мудро\" Призрак дарует вам 25 маны")
        else:
            hero.HP -= 20
            add_log(" \"Неверно...\" Призрак забирает вашу жизненную силу. -20 HP")
            if check_event_death(): return
    elif method == "answer2":
        add_log("\n Призрак смеётся и исчезает. Ты проходишь дальше")
    elif method == "attack":
        hero.Stamina -= 20
        add_log("Твой удар проходит насквозь. -20 Стамина")
    update_info()
    show_dungeon_ui()


def event_collapsing_bridge():
    clear_buttons()
    add_log("\n Вы проходите через мост, внезапно он рушится под ногами!")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    if hero.Agility >= 12:
        btn1 = Button(row, text="Перепрыгнуть (Ловкость)", command=lambda: resolve_bridge("jump"),
                      anchor="w", justify="left")
        style_btn(btn1)
        btn1.pack(side="top", pady=3, fill="x", padx=10)

    if "Верёвка" in hero.Inventory:
        btn2 = Button(row, text="Использовать верёвку", command=lambda: resolve_bridge("rope"),
                      anchor="w", justify="left")
        style_btn(btn2)
        btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Попытаться пробежать", command=lambda: resolve_bridge("run"),
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_bridge(method):
    global money
    if method == "jump":
        add_log("\n Ты перелетел пропасть!")
        if randint(1, 4) == 4:
            add_log("\n Ты нашёл за мостом мешочек золота. +30 монет")
            money += 30
    elif method == "rope":
        hero.Inventory.remove("Верёвка")
        add_log("\n Ты закинул верёвку на другой край и смог выжить!")
        if randint(1, 4) == 4:
            add_log("\n Ты нашёл за мостом мешочек золота. +30 монет")
            money += 30
    elif method == "run":
        if randint(1, 2) == 1:
            add_log("\n Мост обрушился, но ты чудом уцепился")
        else:
            hero.HP -= 30
            add_log("\n Мост обрушился, ты еле как уцепился и получил повреждения. -30 HP")
            if check_event_death(): return
    update_info()
    show_dungeon_ui()


def event_merchant_ghost():
    clear_buttons()
    add_log("\n Призрачный торговец: \"У меня есть товары... За цену воспоминаний\"")

    row = Frame(action_frame, bg=BG_DARK)
    row.pack(side="top", pady=5, fill="x")

    btn1 = Button(row, text="Купить Зелье Исцеления (-30 HP)", command=lambda: resolve_merchant("hp_potion"),
                  anchor="w", justify="left")
    style_btn(btn1)
    btn1.pack(side="top", pady=3, fill="x", padx=10)

    btn2 = Button(row, text="Купить Зелье Маны (-15 HP)", command=lambda: resolve_merchant("mana_potion"),
                  anchor="w", justify="left")
    style_btn(btn2)
    btn2.pack(side="top", pady=3, fill="x", padx=10)

    btn3 = Button(row, text="Уйти", command=show_dungeon_ui,
                  anchor="w", justify="left")
    style_btn(btn3)
    btn3.pack(side="top", pady=3, fill="x", padx=10)

def resolve_merchant(item):
    if hero.HP < 16 and item == "mana_potion":
        add_log("\n Недостаточно жизненной силы для сделки!")
        return
    if hero.HP < 31 and item == "hp_potion":
        add_log("\n Недостаточно жизненной силы для сделки!")
        return
    if item == "hp_potion":
        hero.HP -= 30
        hero.Inventory.append("Зелье Исцеления")
        add_log("\n Ты получил зелье исцеления. -30 HP")
    elif item == "mana_potion":
        hero.HP -= 15
        hero.Inventory.append("Зелье Маны")
        add_log("\n Ты получил Зелье Маны. -15 HP")
    update_info()
    show_dungeon_ui()
"""========================================================="""
Location = "0"

#Начинаем с выбора класса
class_selection()
#combat()
update_info()

root.mainloop()

