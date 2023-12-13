import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import zipfile

# API Дрома
# drom_api = "https://api.drom.ru/v1.2/bulls/search"

# URL страницы с объявлениями
start_url = "https://auto.drom.ru/all/page1/?cid[]=23&cid[]=170&order=price&multiselect[]=9_4_15_all&multiselect[]=9_4_16_all&pts=2&damaged=2&unsold=1"

# заголовки для запросов
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

# получаем ссылки на все страницы с объявлениями
start_response = requests.get(start_url)
start_soup = BeautifulSoup(start_response.text, 'html.parser')
pages = [start_url]
for pages_urls in start_soup.find_all('a', class_='css-14wh0pm e1lm3vns0'):
    pages.append(pages_urls['href'])

for i in range(2, 5):
    url = f"https://auto.drom.ru/all/page{i}/?cid[]=23&cid[]=170&order=price&multiselect[]=9_4_15_all&multiselect[]=9_4_16_all&pts=2&damaged=2&unsold=1"
    pages.append(url)

all_ads_dict = {}
for i, page in enumerate(pages):
    req = requests.get(page, headers=headers)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    all_ads_hrefs = soup.find_all(class_=("css-xb5nz8 e1huvdhj1"))
    if not all_ads_hrefs:
        continue
    for class_ in all_ads_hrefs:
        for span in class_.find_all('span'):
            span.append(' ')
        for div in class_.find_all('div'):
            div.append(' ')

    for item in all_ads_hrefs:
        href = item.get("href")     
        item_text = item.text.replace(' ', '') 
        # Очистка и проверка подстрок в URL
        clean_href = href.strip().lower()
        if "/vladivostok/" in clean_href or "/ussuriisk/" in clean_href:        # Если в ссылке есть /vladivostok/ или /ussuriisk/, добавляем ее в словарь
        # условие для проверки наличия "в пути" внутри div
            div_tags = item.find_all('div', class_='css-1r7hfp1 ejipaoe0')
            if div_tags and "в пути" not in div_tags[0].text.lower():
                continue
            span_tags = item.find_all('span', class_='css-1488ad e162wx9x0')
            if any(city.lower() in span.text.lower() for city in ["Уссурийск", "Владивосток"]):
                item_href = "h" + item.get("href")[1:]
                all_ads_dict[item_href] = None  # добавляем только ссылку в словарь

# записываем данные ссылок в json файл
with open('all_ads_links.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_ads_dict.keys()), f, ensure_ascii=False, indent=4)   

# читаем ссылки из файла
with open('all_ads_links.json', 'r', encoding='utf-8') as f:
    all_ads_links = json.load(f)

# создаем папку для сохранения файлов
if not os.path.exists('pages_html'):
    os.makedirs('pages_html')

# создаем папку для сохранения фотографий
if not os.path.exists('photos'):
    os.makedirs('photos')

# проходим по всем ссылкам и сохраняем содержимое страниц в html-файлы
for i, link in enumerate(all_ads_links):
    # print(f"Обработка ссылки {i+1}/{len(all_ads_links)}: {link}")
    filename = f"pages_html/page_{i+1}.html"
    try:
        response = requests.get(link, headers=headers)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
               # Создаем директорию для фотографий данного объявления
        photo_dir = f'photos/ad_{i+1}'
        os.makedirs(photo_dir, exist_ok=True)

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        photos = soup.find_all('div', class_='css-0 epjhnwz2').find("a")

        # Скачиваем и сохраняем фотографии       #  НЕ ТЕ ТЕГИ ПЕРЕДЕЛАТЬ!!!!!!!!!
        for j, photo in enumerate(photos):
            photo_url = photo.get('src')
            photo_filename = f'{photo_dir}/photo_{j+1}.jpg'
            try:
                photo_response = requests.get(photo_url)
                with open(photo_filename, 'wb') as img_f:
                    img_f.write(photo_response.content)
            except Exception as e:
                print(f"Ошибка загрузки фотографии: {str(e)}")

    except Exception as e:
        print(f"Ошибка обработки ссылки {link}: {str(e)}")
        continue
    except:
        print(f"Ошибка обработки ссылки {link}")
        continue
html_files_path = 'pages_html'  # путь к папке с html-файлами
        

# цикл по всем html-файлам
for file in os.listdir(html_files_path):
    with open(os.path.join(html_files_path, file), 'r', encoding='utf-8') as f:
        html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        engine = soup.find("td", class_="css-9xodgi ezjvm5n0")
        power = soup.find(class_="css-9g0qum e162wx9x0").text
        #transmission = soup.find("table", class_="css-xalqz7 eppj3wm0").find("tr") #НАПИСАТЬ
        #drive_unit = soup.find#НАПИСАТЬ
        #body = soup.find(class_="css-1osyw3j ei6iaw00").text  #НАПИСАТЬ
        #mileage = transmission[0]
        #print(power)
        #       И ХАРАКТЕРИСТИКИ ДАЛЕЕ  
# with open('all_ads_links.json', 'r', encoding='utf-8') as f:
#     all_ads_links = json.load(f)

    
# Создаем список для хранения данных из тега <title>
titles = []

# # Проходим по всем файлам в папке pages_html
for filename in os.listdir('pages_html'):
    if filename.endswith('.html'):
        with open(os.path.join('pages_html', filename), 'r', encoding='utf-8') as f:
            html_content = f.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            title_tag = soup.find("title")
            if title_tag:
                titles.append(title_tag.text)

# Запись данных из тега <title> в CSV файл
with open('Data.csv', 'w', newline='', encoding='utf-8') as csv_file:
    writer = csv.writer(csv_file)
    for title in titles:
        writer.writerow([title])

# # Создаем заархивированный файл Result_Crown.zip
# with zipfile.ZipFile('Result_Crown.zip', 'w') as zipf:
#     zipf.write('Data.csv')
    
    
    # # ДРУГОЙ ВАРИАНТ
    # ad_id = link.split('/')[-1].split('.')[0]
    # # получаем марку авто
    # try:
    #     car_brand =  soup.find('div', {'data-ftid': 'header_breadcrumb-item'}).find('span', {'class': 'css-1sk0lam e2rnzmt0'}).text
    # except:
    #     car_brand = 'null'
    # # получаем модель авто
    # try:
    #     car_model = soup.find('h1', class_='css-1tjirrw e18vbajn0').text.split()[2].strip(',')
    # except:
    #     car_model = 'null'
    # #print(car_model)
    
    # # получаем цену продажи
    # try:
    #     car_price = soup.find('span', class_='css-1o5wiw8 e1w4pw4i0').text.strip().replace(' ', '')
    # except:
    #     car_price = 'null'
    
    # # получаем цену Дрома
    # try:
    #     car_drom_price = soup.find('div', class_='css-1vr19r7 e1w4pw4i1').text.strip().replace(' ', '')
    # except:
    #     car_drom_price = 'null'
    
    # # получаем поколение авто
    # try:
    #     car_generation = soup.find('div', class_='css-1psewqh e1w4pw4i2').text.strip()
    # except:
    #     car_generation = 'null'
    
    # # получаем комплектацию авто
    # try:
    #     car_configuration = soup.find('div', class_='css-1hj8y23 e1w4pw4i3').text.strip()
    # except:
    #     car_configuration = 'null'
    
    # # получаем пробег
    # try:
    #     car_mileage = soup.find('li', class_='css-1qkmf8e e1w4pw4i4').text.strip().replace(' ', '')
    # except:
    #     car_mileage = 'null'
    
    # # получаем информацию о пробеге по РФ
    # try:
    #     car_mileage_rus = soup.find('li', class_='css-1m8kpnj e1w4pw4i5').text.strip()
    # except:
    #     car_mileage_rus = 'null'
    
    # # получаем цвет авто
    # try:
    #     car_color = soup.find('li', class_='css-1qkmf8e e1w4pw4i6').text.strip()
    # except:
    #     car_color = 'null'
    
    # # получаем тип кузова
    # try:
    #     car_body_type = soup.find('li', class_='css-1qkmf8e e1w4pw4i7').text.strip()
    # except:
    #     car_body_type = 'null'
    
    # # получаем мощность двигателя
    # try:
    #     car_engine_power = soup.find('li', class_='css-1qkmf8e e1w4pw4i8').text.strip().replace(' ', '')
    # except:
    #     car_engine_power = 'null'
    
    # # получаем тип топлива
    # try:
    #     car_fuel_type = soup.find('li', class_='css-1qkmf8e e1w4pw4i9').text.strip()
    # except:
    #     car_fuel_type = 'null'
    
    # # получаем объем двигателя
    # try:
    #     car_engine_volume = soup.find('li', class_='css-1qkmf8e e1w4pw4ia').text.strip().replace(' ', '')
    # except:
    #     car_engine_volume = 'null'
    
    # # записываем данные в файл Data.csv
    # with open('Data.csv', 'a', encoding='utf-8', newline='') as f:
    #     writer = csv.writer(f)
    #     writer.writerow([ad_id, link, car_brand, car_model, car_price, car_drom_price, car_generation, 
    #                      car_configuration, car_mileage, car_mileage_rus, car_color, car_body_type, 
    #                      car_engine_power, car_fuel_type, car_engine_volume])
    
    # # создаем папку для фотографий объявления
    # photos_dir = f'photos/{all_ads_links}'
    # if not os.path.exists(photos_dir):
    #     os.makedirs(photos_dir)
    
# Архивируем результаты
with zipfile.ZipFile('Result_Crown.zip', 'w') as zipf:
    for i, link in enumerate(all_ads_links):
        ad_dir = f'photos/ad_{i+1}'
        for photo_file in os.listdir(ad_dir):
            zipf.write(os.path.join(ad_dir, photo_file), f"ad_{i+1}/{photo_file}")
    zipf.write('Data.csv')