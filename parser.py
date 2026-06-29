import requests
import json
import time
from bs4 import BeautifulSoup

# Общие заголовки для всех запросов
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}

# ============ 1. ПАРСЕР HABR CAREER ============
def fetch_habr(keyword='Python'):
    """Парсинг вакансий с Habr Career"""
    url = f'https://career.habr.com/vacancies?q={keyword}'
    result = []
    try:
        print(f"🌐 Парсинг Habr: {keyword} ...")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Ищем карточки вакансий
        cards = soup.find_all('div', class_='vacancy-card')
        if not cards:
            print(f"⚠️ Не найдены карточки на Habr, возможно изменился дизайн")
            return result
            
        for card in cards:
            title_tag = card.find('a', class_='vacancy-card__title-link')
            company_tag = card.find('div', class_='vacancy-card__company-title')
            salary_tag = card.find('div', class_='vacancy-card__salary')
            
            if title_tag:
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': 'https://career.habr.com' + title_tag.get('href', ''),
                    'source': 'habr.com'
                })
        print(f"✅ Habr: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка Habr: {e}")
    return result

# ============ 2. ПАРСЕР SUPERJOB (через HTML) ============
def fetch_superjob(keyword='Python'):
    """Парсинг вакансий с SuperJob (Уфа)"""
    url = f'https://ufa.superjob.ru/vacancy/search/?keywords={keyword}'
    result = []
    try:
        print(f"🌐 Парсинг SuperJob: {keyword} ...")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Ищем карточки вакансий
        cards = soup.find_all('div', class_='f-test-vacancy-item')
        if not cards:
            cards = soup.find_all('div', class_='_1czty _2xY2D _1sR1G _1zUpe')
            
        if not cards:
            print(f"⚠️ Не найдены карточки на SuperJob, возможно изменился дизайн")
            return result
            
        for card in cards:
            title_tag = card.find('a', class_='icMQ_')
            company_tag = card.find('span', class_='f-test-text-vacancy-item-company-name')
            salary_tag = card.find('span', class_='f-test-text-company-item-salary')
            
            if title_tag:
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': 'https://ufa.superjob.ru' + title_tag.get('href', '') if title_tag.get('href', '').startswith('/') else title_tag.get('href', ''),
                    'source': 'superjob.ru'
                })
        print(f"✅ SuperJob: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка SuperJob: {e}")
    return result

# ============ 3. ПАРСЕР РАБОТА.РУ ============
def fetch_rabota(keyword='Python'):
    """Парсинг вакансий с Работа.ру (Уфа)"""
    url = f'https://ufa.rabota.ru/vacancy/?query={keyword}'
    result = []
    try:
        print(f"🌐 Парсинг Работа.ру: {keyword} ...")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Ищем карточки вакансий
        cards = soup.find_all('div', class_='vacancy-preview-card')
        if not cards:
            print(f"⚠️ Не найдены карточки на Работа.ру, возможно изменился дизайн")
            return result
            
        for card in cards:
            title_tag = card.find('a', class_='vacancy-preview-card__title-link')
            company_tag = card.find('span', class_='vacancy-preview-card__company-name')
            salary_tag = card.find('span', class_='vacancy-preview-card__salary')
            
            if title_tag:
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': 'https://ufa.rabota.ru' + title_tag.get('href', '') if title_tag.get('href', '').startswith('/') else title_tag.get('href', ''),
                    'source': 'rabota.ru'
                })
        print(f"✅ Работа.ру: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка Работа.ру: {e}")
    return result

# ============ 4. ОСНОВНАЯ ФУНКЦИЯ С ЗАДЕРЖКАМИ ============
def main():
    all_vacancies = []
    keywords = ['Python', 'Java', 'JavaScript']
    
    for keyword in keywords:
        print(f"\n📝 Обработка запроса: {keyword}")
        print("=" * 40)
        
        # Парсим Habr
        all_vacancies.extend(fetch_habr(keyword))
        print("⏳ Пауза 2 секунды...")
        time.sleep(2)  # 👈 Задержка 2 секунды
        
        # Парсим SuperJob
        all_vacancies.extend(fetch_superjob(keyword))
        print("⏳ Пауза 2 секунды...")
        time.sleep(2)  # 👈 Задержка 2 секунды
        
        # Парсим Работа.ру
        all_vacancies.extend(fetch_rabota(keyword))
        print("⏳ Пауза 3 секунды перед следующим запросом...")
        time.sleep(3)  # 👈 Задержка 3 секунды (перед новым ключевым словом)
    
    # Убираем дубли по ссылке
    unique = {v['url']: v for v in all_vacancies if v['url']}.values()
    final_list = list(unique)
    
    print("\n" + "=" * 40)
    print(f"✅ Итого уникальных вакансий: {len(final_list)}")
    
    if final_list:
        with open('vacancies.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=2)
        print("📁 Данные сохранены в vacancies.json")
        print(f"📊 Первые 5 вакансий:")
        for i, v in enumerate(final_list[:5], 1):
            print(f"  {i}. {v['title']} - {v['company']}")
    else:
        print("⚠️ Вакансий не найдено. Попробуйте позже или проверьте интернет.")

if __name__ == '__main__':
    print("🚀 ЗАПУСК ПАРСЕРА ВАКАНСИЙ")
    print("=" * 40)
    main()