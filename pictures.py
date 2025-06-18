import asyncio
import aiohttp
import os
from tabulate import tabulate
from typing import List, Tuple
import urllib.parse
import ssl

async def download_image(session: aiohttp.ClientSession, url: str, save_path: str) -> Tuple[str, str]:
    try:
        # Проверяем, что URL валидный
        parsed_url = urllib.parse.urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return url, "Ошибка"

        # Создаем SSL-контекст, который игнорирует проверку сертификатов
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with session.get(url, timeout=30, ssl=ssl_context) as response:
            if response.status == 200:
                # Получаем имя файла из URL
                filename = os.path.basename(urllib.parse.urlparse(url).path)
                if not filename:
                    filename = "image.jpg"
                
                filepath = os.path.join(save_path, filename)
                
                # Проверяем тип контента
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    return url, "Ошибка"
                
                # Сохраняем изображение
                content = await response.read()
                if not content:
                    return url, "Ошибка"
                    
                with open(filepath, 'wb') as f:
                    f.write(content)
                return url, "Успех"
            else:
                return url, "Ошибка"
    except asyncio.TimeoutError:
        return url, "Ошибка"
    except aiohttp.ClientError as e:
        return url, "Ошибка"
    except Exception as e:
        return url, "Ошибка"

async def main():
    # Запрашиваем путь для сохранения
    while True:
        save_path = input("Введите путь для сохранения изображений: ").strip()
        try:
            # Создаем директорию, если она не существует
            os.makedirs(save_path, exist_ok=True)
            if os.access(save_path, os.W_OK):
                break
            print("Нет прав на запись в указанную директорию. Попробуйте другой путь.")
        except Exception as e:
            print(f"Ошибка при создании директории: {str(e)}. Попробуйте другой путь.")

    # Список для хранения ссылок
    urls = []
    
    # Собираем ссылки
    while True:
        url = input("Введите ссылку на изображение (пустая строка для завершения): ").strip()
        if not url:
            break
        urls.append(url)

    if not urls:
        print("Не введено ни одной ссылки.")
        return

    print("\nНачинаем загрузку изображений...")
    
    # Создаем сессию для HTTP-запросов
    async with aiohttp.ClientSession() as session:
        # Создаем задачи для скачивания
        tasks = [download_image(session, url, save_path) for url in urls]
        # Ждем завершения всех задач
        results = await asyncio.gather(*tasks)

    # Выводим результаты
    print("\nРезультаты загрузки:")
    print(tabulate(results, headers=["Ссылка", "Статус"], tablefmt="pipe"))

if __name__ == "__main__":
    asyncio.run(main())

