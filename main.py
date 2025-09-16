import os
from datetime import datetime, timedelta
import requests
import time
from terminaltables import AsciiTable
from dotenv import load_dotenv  

 
def get_hh_vacancies(language, area_id):
    url = 'https://api.hh.ru/vacancies'
    all_vacancies = []
    page = 0
    pages_count = 1
    days_ago = 30
    date_from = (datetime.now() - timedelta(days = days_ago)).isoformat()
    while page < pages_count:
        payload = {
            'text' : f'Программист {language}',
            'area' : area_id,
            'date_from' : date_from,
            'page' : page 
        }
        response = requests.get(url, params = payload)
        response.raise_for_status()
        hh_vacancies = response.json()
        all_vacancies.extend(hh_vacancies.get('items',[]))
        pages_count = hh_vacancies.get('pages',1)
        page += 1
        time.sleep(0.5)
    return all_vacancies, hh_vacancies.get('found', 0)


def get_superjob_vacancies(language, api_key):  
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
            'keyword': f'Программист {language}',
            'town' : 'Москва',
            'date_published_from' : date_from, 
            'count': 100,
            'page': page,
        }
    
        url = 'https://api.superjob.ru/2.0/vacancies/'
    
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() 
        superjob_vacancies = response.json()
        if 'objects' in superjob_vacancies:
        	all_vacancies.extend(superjob_vacancies['objects'])
        more_pages = superjob_vacancies.get('more', False)
        if more_pages:
            page +=1
            time.sleep(0.5)
    vacancies_found = superjob_vacancies.get('total', 0)
    return all_vacancies, vacancies_found


def process_hh_vacancies(vacancies, vacancies_count):
    salaries = [] 
    for vacancy in vacancies:
        salary = vacancy.get('salary')
        if salary and salary['currency'] =='RUR':
            payment_from = salary['from']
            payment_to = salary['to']
            expected_salary = calculate_salary(payment_from, payment_to)
            if expected_salary:
                salaries.append(expected_salary)
    vacancies_processed = len(salaries)
    average_salary = int(sum(salaries)/vacancies_processed) if vacancies_processed else 0
    return {
        "vacancies_found" : vacancies_count,
        "vacancies_processed" : vacancies_processed,
        "average_salary" : average_salary
    }

    

def calculate_salary(payment_from, payment_to):
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    elif payment_from:
        return payment_from
    elif payment_to:
        return payment_to
    return None


def process_superjob_vacancies(vacancies, vacancies_count):
    salaries = []
    for job in vacancies:
        payment_from = job.get('payment_from')
        payment_to = job.get('payment_to') 
        expected_salary = calculate_salary(payment_from, payment_to)
        if expected_salary:
            salaries.append(expected_salary)
    processed_vacancies = len(salaries)
    average_salary = int(sum(salaries)/processed_vacancies) if processed_vacancies else 0
    return {
        "vacancies_found" : vacancies_count,
        "vacancies_processed": processed_vacancies,
        "average_salary": average_salary
    }


def print_salary_table(stats, title):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for lang, stats in stats.items():
        table_data.append([lang, stats['vacancies_found'], stats['vacancies_processed'], stats['average_salary']])
    table = AsciiTable(table_data, title)
    print(table.table)

if __name__ == '__main__':
    load_dotenv()
    languages = ["Python", "Java", "JavaScript", "C#", "Ruby"]
    superjob_api_key = os.getenv('SUPJOB_KEY')
    area_id = '1'
    hh_stats = {}
    supjob_stats = {}
    for language in languages:
        vacancies, vacancies_count = get_superjob_vacancies(language, superjob_api_key)
        stats = process_superjob_vacancies(vacancies, vacancies_count)
        supjob_stats[language] = stats
        vacancies,vacancies_count = get_hh_vacancies(language, area_id)
        hh_stats[language] = process_hh_vacancies(vacancies, vacancies_count)
    title = 'SuperJob'
    print_salary_table(supjob_stats, title)
    title = 'HeadHunters'
    print_salary_table(hh_stats, title)