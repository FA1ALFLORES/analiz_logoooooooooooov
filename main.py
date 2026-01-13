#!/usr/bin/env python3
"""
Главный файл для запуска анализатора логов.
Использование:
    python main.py access.log      # Анализ файла логов
    python main.py --test          # Запуск тестов
"""

import sys
import argparse

# Пробуем импортировать функции
try:
    # Импортируем из analizator.py
    from analizator import analyze_log_file, print_result
except ImportError as e:
    print(f"❌ Ошибка импорта из analizator.py: {e}")
    print("Убедитесь, что файл analizator.py находится в той же папке")
    sys.exit(1)

try:
    # Импортируем из test1.py
    from test1 import run_all_tests
except ImportError:
    print("⚠️  Файл test1.py не найден или в нём нет функции run_all_tests()")
    print("Тесты будут недоступны")


def main():
    """Основная функция приложения"""
    parser = argparse.ArgumentParser(
        description='Анализатор логов веб-сервера'
    )
    
    parser.add_argument(
        'filename', 
        nargs='?', 
        help='Путь к файлу логов (например: access.log)'
    )
    parser.add_argument(
        '--test', 
        action='store_true', 
        help='Запустить тесты'
    )
    
    args = parser.parse_args()
    
    if args.test:
        # Запускаем тесты
        print("\n" + "=" * 50)
        print("ТЕСТИРОВАНИЕ АНАЛИЗАТОРА ЛОГОВ".center(50))
        print("=" * 50)
        
        try:
            run_all_tests()
        except NameError:
            print("❌ Функция run_all_tests() не найдена")
            print("Проверьте содержимое файла test1.py")
            sys.exit(1)
            
    elif args.filename:
        # Анализируем файл логов
        print(f"\n📊 Анализ логов из файла: {args.filename}")
        try:
            results = analyze_log_file(args.filename)
            print_result(results)
        except FileNotFoundError:
            print(f"❌ Ошибка: файл '{args.filename}' не найден")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Ошибка при анализе: {e}")
            sys.exit(1)
            
    else:
        # Если не указаны аргументы
        parser.print_help()
        print("\n" + "-" * 50)
        print("Примеры использования:")
        print("  python main.py access.log    # Анализ логов")
        print("  python main.py --test        # Запуск тестов")


if __name__ == "__main__":
    main()