from pathlib import Path
import shutil
import sys

def main():
    print("\n=== Запуск скрипта создания .env ===")
    
    env_path = Path('.env')
    example_path = Path('.env.example')
    
    print(f"Путь к .env.example: {example_path.absolute()}")
    print(f"Файл .env.example существует: {example_path.exists()}")
    
    if not env_path.exists() and example_path.exists():
        try:
            shutil.copy(example_path, env_path)
            print("✅ .env успешно создан из .env.example")
            print(f"Файл создан по пути: {env_path.absolute()}")
        except Exception as e:
            print(f"❌ Ошибка при создании: {str(e)}")
    else:
        print("ℹ️ .env уже существует или .env.example отсутствует")

if __name__ == "__main__":
    main()