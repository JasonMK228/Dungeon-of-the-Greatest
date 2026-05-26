class Entity:
    def __init__(self, class_name, hp, stamina, strength, agility, intellect, inventory=None, max_hp=None, max_stamina=None):
        self.Class = class_name
        self.HP = hp
        self.Stamina = stamina
        self.Strength = strength
        self.Agility = agility
        self.Intellect = intellect
        self.Inventory = inventory if inventory is not None else []
        self.MAX_HP = max_hp if max_hp is not None else hp
        self.MAX_STAMINA = max_stamina if max_stamina is not None else stamina

CLASS_TEMPLATES = {
    "Рыцарь": {
        "hp": 150, "stamina": 50,
        "strength": 10, "agility": 9, "intellect": 6,
        "inventory": ["Длинный меч", "Щит", "Зелье Исцеления"],
        "MAX_HP": 150, "MAX_STAMINA": 50
    },
    "Воин": {
        "hp": 200, "stamina": 40,
        "strength": 13, "agility": 6, "intellect": 6,
        "inventory": ["Двуручный меч", "Зелье Исцеления", "Зелье Исцеления"],
        "MAX_HP": 200, "MAX_STAMINA": 40
    },
    "Маг": {
        "hp": 100, "stamina": 40,
        "strength": 6, "agility": 8, "intellect": 10,
        "inventory": ["Посох", "Кинжал", "Зелье Исцеления", "Книга заклинаний", "Зелье Маны"],
        "MAX_HP": 100, "MAX_STAMINA": 40
    },
    "Бард": {
        "hp": 125, "stamina": 30,
        "strength": 8, "agility": 8, "intellect": 8,
        "inventory": ["Гитерн", "Музыкальная книга", "Зелье Исцеления"],
        "MAX_HP": 125, "MAX_STAMINA": 30
    },
    "Паладин": {
        "hp": 175, "stamina": 70,
        "strength": 12, "agility": 5, "intellect": 9,
        "inventory": ["Святой меч", "Щит", "Набор священника"],
        "MAX_HP": 175, "MAX_STAMINA": 70
    },
    "Вор": {
        "hp": 125, "stamina": 70,
        "strength": 8, "agility": 12, "intellect": 4,
        "inventory": ["Кинжал", "Талисман вора", "Зелье Исцеления", "Отмычка"],
        "MAX_HP": 125, "MAX_STAMINA": 70
    },
    "Нищий": {
        "hp": 85, "stamina": 30,
        "strength": 3, "agility": 3, "intellect": 3,
        "inventory": ["Палка"],
        "MAX_HP": 80, "MAX_STAMINA": 30
    }
}

def get_hero(class_name):
    data = CLASS_TEMPLATES[class_name]
    return Entity(class_name,
                  data["hp"],
                  data["stamina"],
                  data["strength"],
                  data["agility"],
                  data["intellect"],
                  data["inventory"],
                  data["MAX_HP"],
                  data["MAX_STAMINA"])

WEAPON_DAMAGE = {
    "Длинный меч": (8, 12),
    "Двуручный меч": (12, 18),
    "Посох": (6, 10),
    "Кинжал": (4, 6),
    "Гитерн": (6, 10),
    "Святой меч": (10, 14),
    "Огромный меч":(14,17),
    "Боевой топор":(10,12),
    "Копьё":(9,13),
    "Алебарда":(10,20),
    "Булава":(6,8),
    "Рапира":(6,10),
    "Без оружия": (1, 3),
    "Палка":(0,1)
}

def get_hero_damage(hero):
    if hero is None or not getattr(hero, "Inventory", []):
        return (1, 3)

    best_dmg = (1, 3)
    for item in hero.Inventory:
        if item in WEAPON_DAMAGE:
            if WEAPON_DAMAGE[item][1] > best_dmg[1]:
                best_dmg = WEAPON_DAMAGE[item]
    return best_dmg