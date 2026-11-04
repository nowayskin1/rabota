import time
import sys
import os

def play_beep():
    # Звуковой сигнал (работает на Windows и большинстве Unix-систем)
    if os.name == "nt":
        import winsound
        winsound.Beep(1000, 1000)  # Частота 1000 Гц, длительность 1 секунда
    else:
        sys.stdout.write('\a')
        sys.stdout.flush()

def start_timer(minutes, label):
    seconds = minutes * 60
    total_seconds = seconds
    
    print(f"\n🚀 Старт сессии: [{label}] на {minutes} мин.")
    
    while seconds > 0:
        # Считаем минуты и секунды для красивого вывода
        mins, secs = divmod(seconds, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        
        # Рисуем красивый прогресс-бар (всего 20 делений)
        progress = int((total_seconds - seconds) / total_seconds * 20)
        bar = "▓" * progress + "░" * (20 - progress)
        
        # Выводим в консоль так, чтобы строка перезаписывалась (\r)
        sys.stdout.write(f"\r⏳ {time_format} [{bar}]")
        sys.stdout.flush()
        
        time.sleep(1)
        seconds -= 1
        
    print(f"\r🔔 {label} завершено!                      ")
    play_beep()

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*40)
    print("      КОНСОЛЬНЫЙ ПОМОДОРО-ТАЙМЕР      ")
    print("="*40)
    
    # Настройки времени в минутах (для быстрого теста можно поставить 0.1 и 0.05)
    WORK_TIME = 25  
    SHORT_BREAK = 5
    
    try:
        while True:
            input("\nНажмите Enter, чтобы начать ФОКУС-сессию...")
            start_timer(WORK_TIME, "ВРЕМЯ РАБОТЫ")
            
            input("\nНажмите Enter, чтобы начать ОТДЫХ...")
            start_timer(SHORT_BREAK, "ОТДЫХ")
            
            print("\n" + "-"*40)
            cont = input("Хотите начать следующий цикл? (да/нет): ").strip().lower()
            if cont != 'да':
                print("\nОтличная работа сегодня! До скорого. 👋")
                break
    except KeyboardInterrupt:
        print("\n\n⏱️ Таймер остановлен. Возвращайтесь к работе позже!")

if __name__ == "__main__":
    main()
