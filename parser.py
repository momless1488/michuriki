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
        
        cards = soup.find_all('div', class_='vacancy-card')
        if not cards:
            print(f"⚠️ Не найдены карточки на Habr, возможно изменился дизайн")
            return result
            
        for card in cards:
            title_tag = card.find('a', class_='vacancy-card__title-link')
            if not title_tag:
                continue
            
            # Поиск названия компании
            company_container = card.find('div', class_='vacancy-card__company')
            company_name = 'Неизвестно'
            if company_container:
                company_link = company_container.find('a')
                if company_link:
                    company_name = company_link.text.strip()
                else:
                    company_name = company_container.text.strip()
            
            if company_name == 'Неизвестно' or not company_name:
                company_tag = card.find('div', class_='vacancy-card__company-title')
                if company_tag:
                    company_name = company_tag.text.strip()
            
            salary_tag = card.find('div', class_='vacancy-card__salary')
            salary = salary_tag.text.strip() if salary_tag else 'Не указана'
            
            result.append({
                'company': company_name,
                'title': title_tag.text.strip(),
                'salary': salary,
                'url': 'https://career.habr.com' + title_tag.get('href', ''),
                'source': 'habr.com'
            })
            
        print(f"✅ Habr: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка Habr: {e}")
    return result

# ============ 2. ПАРСЕР SUPERJOB (ИСПРАВЛЕННЫЙ) ============
def fetch_superjob(keyword='Python'):
    """Парсинг вакансий с SuperJob (Уфа)"""
    url = f'https://ufa.superjob.ru/vacancy/search/?keywords={keyword}'
    result = []
    try:
        print(f"🌐 Парсинг SuperJob: {keyword} ...")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Обновленные селекторы для SuperJob
        cards = soup.find_all('div', {'data-testing': 'vacancy-item'})
        if not cards:
            # Альтернативный поиск
            cards = soup.find_all('div', class_='_1czty _2xY2D _1sR1G')
        
        if not cards:
            # Пробуем найти через data-атрибуты
            cards = soup.find_all('div', attrs={'data-testing': True})
            cards = [card for card in cards if 'vacancy' in str(card.get('data-testing', ''))]
            
        if not cards:
            print(f"⚠️ Не найдены карточки на SuperJob, пробую альтернативный метод...")
            # Поиск по ссылкам с вакансиями
            links = soup.find_all('a', href=True)
            for link in links:
                if '/vacancy/' in link.get('href', ''):
                    parent = link.find_parent('div')
                    if parent and parent not in cards:
                        cards.append(parent)
        
        if not cards:
            print(f"⚠️ Не найдены карточки на SuperJob")
            return result
            
        for card in cards:
            # Поиск заголовка
            title_tag = card.find('a', class_='icMQ_') or card.find('a', href=lambda x: x and '/vacancy/' in x)
            
            # Поиск компании
            company_tag = None
            company_selectors = [
                ('span', {'class': 'f-test-text-vacancy-item-company-name'}),
                ('span', {'data-testing': 'company-name'}),
                ('div', {'class': '_1czty _3iMha'})
            ]
            
            for tag, attrs in company_selectors:
                company_tag = card.find(tag, attrs)
                if company_tag:
                    break
            
            # Поиск зарплаты
            salary_tag = None
            salary_selectors = [
                ('span', {'class': 'f-test-text-company-item-salary'}),
                ('span', {'data-testing': 'salary'}),
                ('span', {'class': '_1czty _1Uxyi'})
            ]
            
            for tag, attrs in salary_selectors:
                salary_tag = card.find(tag, attrs)
                if salary_tag:
                    break
            
            if title_tag:
                href = title_tag.get('href', '')
                if href.startswith('/'):
                    href = 'https://ufa.superjob.ru' + href
                
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': href,
                    'source': 'superjob.ru'
                })
        print(f"✅ SuperJob: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка SuperJob: {e}")
    return result

# ============ 3. ПАРСЕР РАБОТА.РУ (ИСПРАВЛЕННЫЙ) ============
def fetch_rabota(keyword='Python'):
    """Парсинг вакансий с Работа.ру (Уфа)"""
    url = f'https://ufa.rabota.ru/vacancy/?query={keyword}'
    result = []
    try:
        print(f"🌐 Парсинг Работа.ру: {keyword} ...")
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Обновленные селекторы для Работа.ру
        cards = soup.find_all('div', class_='vacancy-preview-card')
        
        if not cards:
            # Пробуем найти через data-атрибуты
            cards = soup.find_all('div', attrs={'data-vacancy-id': True})
            
        if not cards:
            # Поиск по ссылкам с вакансиями
            cards = soup.find_all('div', class_='_1czty _2xY2D _1sR1G')
            
        if not cards:
            print(f"⚠️ Не найдены карточки на Работа.ру")
            return result
            
        for card in cards:
            # Поиск заголовка
            title_tag = card.find('a', class_='vacancy-preview-card__title-link')
            if not title_tag:
                title_tag = card.find('a', href=lambda x: x and '/vacancy/' in x)
            
            # Поиск компании
            company_tag = None
            company_selectors = [
                ('span', {'class': 'vacancy-preview-card__company-name'}),
                ('span', {'data-testing': 'company-name'}),
                ('div', {'class': '_1czty _1f9wN'})
            ]
            
            for tag, attrs in company_selectors:
                company_tag = card.find(tag, attrs)
                if company_tag:
                    break
            
            # Поиск зарплаты
            salary_tag = None
            salary_selectors = [
                ('span', {'class': 'vacancy-preview-card__salary'}),
                ('span', {'data-testing': 'salary'}),
                ('div', {'class': '_1czty _2ZJjO'})
            ]
            
            for tag, attrs in salary_selectors:
                salary_tag = card.find(tag, attrs)
                if salary_tag:
                    break
            
            if title_tag:
                href = title_tag.get('href', '')
                if href.startswith('/'):
                    href = 'https://ufa.rabota.ru' + href
                
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': href,
                    'source': 'rabota.ru'
                })
        print(f"✅ Работа.ру: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка Работа.ру: {e}")
    return result

# ============ 4. ПАРСЕР HH.RU (НОВЫЙ) ============
def fetch_hh(keyword='Python'):
    """Парсинг вакансий с HH.ru (Уфа)"""
    url = f'https://ufa.hh.ru/search/vacancy?text={keyword}&area=99'
    result = []
    try:
        print(f"🌐 Парсинг HH.ru: {keyword} ...")
        headers = HEADERS.copy()
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Поиск карточек вакансий
        cards = soup.find_all('div', class_='vacancy-serp-item')
        if not cards:
            cards = soup.find_all('div', {'data-qa': 'vacancy-serp__vacancy'})
            
        if not cards:
            print(f"⚠️ Не найдены карточки на HH.ru")
            return result
            
        for card in cards:
            # Поиск заголовка
            title_tag = card.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
            if not title_tag:
                title_tag = card.find('a', class_='serp-item__title')
            
            # Поиск компании
            company_tag = card.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
            if not company_tag:
                company_tag = card.find('div', {'data-qa': 'vacancy-serp__vacancy-employer'})
            
            # Поиск зарплаты
            salary_tag = card.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            if not salary_tag:
                salary_tag = card.find('span', class_='bloko-header-section-3')
            
            if title_tag:
                href = title_tag.get('href', '')
                if href.startswith('/'):
                    href = 'https://hh.ru' + href
                
                result.append({
                    'company': company_tag.text.strip() if company_tag else 'Неизвестно',
                    'title': title_tag.text.strip(),
                    'salary': salary_tag.text.strip() if salary_tag else 'Не указана',
                    'url': href,
                    'source': 'hh.ru'
                })
        print(f"✅ HH.ru: найдено {len(result)} вакансий")
    except Exception as e:
        print(f"❌ Ошибка HH.ru: {e}")
    return result

# ============ 5. ОСНОВНАЯ ФУНКЦИЯ ============
def main():
    all_vacancies = []
    keywords = ['Python', 'Java', 'JavaScript']
    
    # Выбор источников (можно заменить SuperJob и Работа.ру на HH.ru)
    use_hh_instead = True  # Если True, используем HH.ru вместо SuperJob и Работа.ру
    
    for keyword in keywords:
        print(f"\n📝 Обработка запроса: {keyword}")
        print("=" * 40)
        
        # Habr всегда парсим
        all_vacancies.extend(fetch_habr(keyword))
        print("⏳ Пауза 2 секунды...")
        time.sleep(2)
        
        if use_hh_instead:
            # Используем HH.ru
            all_vacancies.extend(fetch_hh(keyword))
            print("⏳ Пауза 2 секунды...")
            time.sleep(2)
        else:
            # Парсим SuperJob
            all_vacancies.extend(fetch_superjob(keyword))
            print("⏳ Пауза 2 секунды...")
            time.sleep(2)
            
            # Парсим Работа.ру
            all_vacancies.extend(fetch_rabota(keyword))
            print("⏳ Пауза 2 секунды...")
            time.sleep(2)
        
        print("⏳ Пауза 3 секунды перед следующим запросом...")
        time.sleep(3)
    
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
            print(f"  {i}. {v['title']} - {v['company']} ({v['source']})")
    else:
        print("⚠️ Вакансий не найдено. Попробуйте позже или проверьте интернет.")

if __name__ == '__main__':
    print("🚀 ЗАПУСК ПАРСЕРА ВАКАНСИЙ")
    print("=" * 40)
    main()