import random
import os
import sys
import time

class Creature:
    def __init__(self, name, hp, max_hp, attack, defense):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        actual_dmg = max(1, dmg - self.defense)
        self.hp -= actual_dmg
        return actual_dmg

class Player(Creature):
    def __init__(self, name):
        super().__init__(name, hp=100, max_hp=100, attack=15, defense=5)
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 50
        self.gold = 0
        self.potions = 2
        self.floor = 1

    def gain_xp(self, amount):
        self.xp += amount
        log = f"✨ Вы получили {amount} ОП."
        if self.xp >= self.xp_to_next_level:
            self.level += 1
            self.xp -= self.xp_to_next_level
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
            self.max_hp += 15
            self.hp = self.max_hp
            self.attack += 3
            self.defense += 1
            log += f"\n🆙 УРОВЕНЬ ПОВЫШЕН! Теперь вы {self.level} уровня!"
        return log

    def use_potion(self):
        if self.potions > 0:
            heal_amount = int(self.max_hp * 0.4)
            self.hp = min(self.max_hp, self.hp + heal_amount)
            self.potions -= 1
            return f"🧪 Вы выпили зелье и восстановили {heal_amount} ОЗ!"
        return "❌ У вас нет зелий лечения!"

class Enemy(Creature):
    @classmethod
    def create_random(cls, floor):
        names = ["Гоблин", "Скелет", "Орк", "Темный Маг", "Пещерный Паук"]
        name = random.choice(names)
        # Сила врагов масштабируется в зависимости от этажа
        hp = random.randint(30, 50) + (floor * 5)
        attack = random.randint(8, 14) + (floor * 2)
        defense = random.randint(2, 5) + (floor * 1)
        enemy = cls(name, hp, hp, attack, defense)
        enemy.xp_reward = hp // 2
        enemy.gold_reward = random.randint(10, 30) + (floor * 5)
        return enemy

class Game:
    def __init__(self):
        self.width = 10
        self.height = 8
        self.player_obj = None
        self.logs = []
        self.game_over = False

    def init_game(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*40)
        print("       RPG: ПОДЗЕМЕЛЬЕ СУДЬБЫ       ")
        print("="*40)
        name = input("Введите имя вашего героя: ").strip()
        if not name:
            name = "Безымянный"
        self.player_obj = Player(name)
        self.generate_floor()

    def generate_floor(self):
        self.map = [["." for _ in range(self.width)] for _ in range(self.height)]
        self.px, self.py = 1, 1
        self.map[self.py][self.px] = "P"
        
        # Размещаем стены по периметру
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.map[y][x] = "█"

        # Добавляем случайные внутренние стены
        for _ in range(12):
            wx, wy = random.randint(1, self.width-2), random.randint(1, self.height-2)
            if (wx, wy) != (1, 1):
                self.map[wy][wx] = "█"

        # Точка перехода на следующий этаж (Лестница)
        self.sx, self.sy = self.width - 2, self.height - 2
        self.map[self.sy][self.sx] = "E"

        # Разбрасываем золото (G), зелья (T) и монстров (M)
        self.spawn_entities("G", 4)
        self.spawn_entities("T", 2)
        self.spawn_entities("M", 4)
        self.add_log(f"⚔️ Вы спустились на {self.player_obj.floor}-й этаж подземелья.")

    def spawn_entities(self, char, count):
        for _ in range(count):
            while True:
                ex, ey = random.randint(1, self.width-2), random.randint(1, self.height-2)
                if self.map[ey][ex] == ".":
                    self.map[ey][ex] = char
                    break

    def add_log(self, text):
        self.logs.append(text)
        if len(self.logs) > 5:
            self.logs.pop(0)

    def draw(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        p = self.player_obj
        # Вывод интерфейса состояния персонажа
        print(f"👤 {p.name} | Уровень: {p.level} | Этаж: {p.floor}")
        print(f"❤️ ОЗ: {p.hp}/{p.max_hp} | ⭐ ОП: {p.xp}/{p.xp_to_next_level} | 💰 Золото: {p.gold} | 🧪 Зелья: {p.potions}")
        print("=" * (self.width * 2 + 2))
        
        # Отрисовка карты с красивыми иконками
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                cell = self.map[y][x]
                if cell == "P": row += "🧙 "
                elif cell == "█": row += "██"
                elif cell == "E": row += "🪜 "
                elif cell == "G": row += "🪙 "
                elif cell == "T": row += "🧪 "
                elif cell == "M": row += "👹 "
                else: row += " . "
            print(row)
        print("=" * (self.width * 2 + 2))
        
        # Вывод журнала событий
        print("📜 ЖУРНАЛ СОБЫТИЙ:")
        for log in self.logs:
            print(log)
        print("\nУправление: W, A, S, D — движение | H — выпить зелье | Q — выход")

    def battle(self):
        enemy = Enemy.create_random(self.player_obj.floor)
        self.add_log(f"⚠️ Вы столкнулись с монстром: {enemy.name} (❤️ {enemy.hp} ОЗ)!")
        
        while enemy.is_alive() and self.player_obj.is_alive():
            # Ход игрока в бою упрощен для консоли (автобой при столкновении или выбор)
            # Чтобы не ломать отрисовку, сделаем интерактивный текстовый поединок
            self.draw()
            print(f"\nБИТВА с {enemy.name}!")
            action = input("1 - Атаковать | 2 - Использовать зелье лечения: ").strip()
            
            if action == "2":
                self.add_log(self.player_obj.use_potion())
                continue
            
            # Атака игрока
            dmg_to_enemy = self.player_obj.take_damage(self.player_obj.attack) # Расчет через базовые механики
            # Чтобы учитывать броню врага правильно:
            dmg_to_enemy = enemy.take_damage(random.randint(self.player_obj.attack-3, self.player_obj.attack+3))
            self.add_log(f"💥 Вы нанесли {enemy.name} {dmg_to_enemy} урона.")
            
            if enemy.is_alive():
                # Атака врага
                dmg_to_player = self.player_obj.take_damage(random.randint(enemy.attack-2, enemy.attack+2))
                self.add_log(f"🩸 {enemy.name} ударил вас на {dmg_to_player} урона.")
                
            time.sleep(0.5)

        if self.player_obj.is_alive():
            self.player_obj.gold += enemy.gold_reward
            self.add_log(f"🏆 Вы победили {enemy.name}! Получено: 💰 {enemy.gold_reward}, ⭐ {enemy.xp_reward}.")
            xp_log = self.player_obj.gain_xp(enemy.xp_reward)
            self.add_log(xp_log)
            return True
        else:
            self.add_log("💀 Вы погибли в бою...")
            self.game_over = True
            return False

    def move(self, dx, dy):
        nx, ny = self.px + dx, self.py + dy
        target = self.map[ny][nx]
        
        if target == "█":
            self.add_log("🚧 Там стена, путь заблокирован!")
            return
            
        if target == "G":
            gold_found = random.randint(10, 25)
            self.player_obj.gold += gold_found
            self.add_log(f"🪙 Вы нашли мешочек золота: +{gold_found} монет!")
            
        elif target == "T":
            self.player_obj.potions += 1
            self.add_log("🧪 Вы подобрали зелье лечения!")
            
        elif target == "M":
            if not self.battle():
                return
                
        elif target == "E":
            self.player_obj.floor += 1
            self.generate_floor()
            return

        # Перемещаем игрока на карте
        self.map[self.py][self.px] = "."
        self.px, self.py = nx, ny
        self.map[self.py][self.px] = "P"

    def run(self):
        self.init_game()
        while not self.game_over:
            self.draw()
            choice = input("\nВаш ход: ").strip().lower()
            if choice == 'q':
                print("Вы покинули подземелье. Спасибо за игру!")
                break
            elif choice == 'h':
                self.add_log(self.player_obj.use_potion())
            elif choice == 'w': self.move(0, -1)
            elif choice == 's': self.move(0, 1)
            elif choice == 'a': self.move(-1, 0)
            elif choice == 'd': self.move(1, 0)
            
            if not self.player_obj.is_alive():
                self.draw()
                print("\n🛑 ИГРА ОКОНЧЕНА. Ваши подвиги навсегда останутся в памяти этого подземелья...")
                self.game_over = True

if __name__ == "__main__":
    game = Game()
    game.run()
