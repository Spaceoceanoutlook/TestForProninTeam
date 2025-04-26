from pathlib import Path
import shutil
import sys

def main():
    print("\n=== ⚙️  Запуск скрипта создания .env ===")
    
    BASE_DIR = Path(__file__).resolve().parent.parent

    env_path = BASE_DIR / '.env'
    example_path = BASE_DIR / '.env.example'
    
    if not example_path.exists():
        print(f"❌ Файл .env.example не найден! Ожидался по пути: {example_path}")
        sys.exit(1)
    
    if env_path.exists():
        print(f"ℹ️ Файл .env уже существует: {env_path}")
    else:
        try:
            shutil.copy(example_path, env_path)
            print(f"✅ Файл .env успешно создан из .env.example")
            print(f"📄 Путь к файлу: {env_path}")
        except Exception as e:
            print(f"❌ Ошибка при копировании: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
