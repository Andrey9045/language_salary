import requests
from datetime import datetime, timedelta
import time
from terminaltables import AsciiTable

def get_hh_vacancies(language):
    url = 'https://api.hh.ru/vacancies'
    all_vacancies = []
    page = 0
    pages_count = 1
    days_ago = 30
    date_from = (datetime.now() - timedelta(days = days_ago)).isoformat()
    while page < pages_count:
        payload = {
            'text' : f'Программист {language}',
            'area' : '1',
            'date_from' : date_from,
            'page' : page 
        }
        response = requests.get(url, params = payload)
        response.raise_for_status()
        data = response.json()
        all_vacancies.extend(data.get('items',[]))
        pages_count = data.get('pages',1)
        page += 1
        time.sleep(0.5)
    return all_vacancies, data.get('found', 0)


def get_superjob_vacancies(language):
    api_key = 'v3.r.132806648.118e4bd266a41943689b775c1199faaf65811395.2ab73f0c69ddc080205984d0ae7fbc6b3475043f'  # Замените на ваш реальный токен
    days_ago = 30
    all_vacancies = []
    page = 0
    more_pages = True
    date_from = (datetime.now() - timedelta(days = days_ago)).isoformat()
    while more_pages:
        headers = {
            'X-Api-App-Id': api_key
        }

        params = {
            'keyword': f'Программист {language}',  # Например, ищем вакансии для программистов
            'town' : 'Москва',
            'date_published_from' : date_from, 
            'count': 100,  # Количество вакансий, которые нужно получить
            'page': page,
        }
    
        url = 'https://api.superjob.ru/2.0/vacancies/'
    
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() 
        data = response.json()
        if 'objects' in data:
        	all_vacancies.extend(data['objects'])
        more_pages = data.get('more', False)
        if more_pages:
            page +=1
            time.sleep(0.5)
    return all_vacancies

def predict_rub_salary(vacancy):
    salary = vacancy.get('salary')
    if salary:
        if salary['currency'] =='RUR':
            if salary['from'] and salary['to']:
                return (salary['from'] + salary['to'])/2
            elif salary['from']:
                return salary['from']
            elif salary['to']:
                return salary['to']
    return None

def hh_vacancies_info(vacancies, vacancies_count):
    salaries = []
    for vacancy in vacancies:
        expected_salary = predict_rub_salary(vacancy)
        if expected_salary:
            salaries.append(expected_salary)
    vacancies_processed = len(salaries)
    average_salary = int(sum(salaries)/vacancies_processed) if vacancies_processed > 0 else 0
    return {
        "vacancies_found" : vacancies_count,
        "vacancies_processed" : vacancies_processed,
        "average_salary" : average_salary
    }


def superjob_vacancies_info(vacancies):
    processed_vacancies = 0
    total_salary = 0
    for job in vacancies:
        payment_from = job.get('payment_from')
        payment_to = job.get('payment_to')
        if payment_from and payment_to:
            total_salary += (payment_from + payment_to)/2
            processed_vacancies += 1
        elif payment_from:
            total_salary += payment_from
            processed_vacancies += 1
        elif payment_to:
            total_salary += payment_to
            processed_vacancies += 1
    average_salary = 0
    if processed_vacancies > 0:
        average_salary = int(total_salary/processed_vacancies)
    return {
        "vacancies_found" : len(vacancies),
        "vacancies_processed": processed_vacancies,
        "average_salary": average_salary
    }
def print_salary_table(stats_dict, title):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for lang, stats in stats_dict.items():
        table_data.append([lang, stats['vacancies_found'], stats['vacancies_processed'], stats['average_salary']])
    table = AsciiTable(table_data, title)
    print(table.table)

if __name__ == '__main__':
    languages = ["Python", "Java", "JavaScript", "C#", "Ruby"]
    hh_stats = {}
    supjob_stats = {}
    for language in languages:
        vacancies = get_superjob_vacancies(language)
        stats = superjob_vacancies_info(vacancies)
        supjob_stats[language] = stats
        vacancies,vacancies_count = get_hh_vacancies(language)
        hh_stats[language] = hh_vacancies_info(vacancies, vacancies_count)
    title = 'SuperJob'
    print_salary_table(supjob_stats, title)
    title = 'HeadHunters'
    print_salary_table(hh_stats, title)