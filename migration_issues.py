import requests
from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# Настройки
GOGS_URL = 'gogs_api_url'
GOGS_TOKEN = 'your_gogs_token'
GITLAB_URL = 'gitlab_api_url'
GITLAB_TOKEN = 'your_gitlab_token'
REPO_OWNER = 'group_name'  # Имя владельца репозитория Gogs
REPO_NAME = 'repo_name'  # Имя репозитория Gogs
GITLAB_PROJECT_ID = '1'  # ID проекта в GitLab


USER_TOKENS = {
    'user_1': '1',
    'user_2': '2',
    # добавляйте других пользователей Gogs и их ники в GitLab
}



# Получение задач из Gogs
def get_gogs_issues():
    headers = {'Authorization': f'token {GOGS_TOKEN}'}
    all_issues = []

    # Получаем открытые задачи
    page = 1
    while True:
        response = requests.get(f'{GOGS_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues?page={page}&state=open', headers=headers, verify=False)
        
        if response.status_code == 200:
            issues = response.json()
            if not issues:
                break
            all_issues.extend(issues)
            page += 1
        else:
            print(f"Ошибка получения открытых задач: {response.status_code}")
            break

    # Получаем закрытые задачи
    page = 1
    while True:
        response = requests.get(f'{GOGS_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues?page={page}&state=closed', headers=headers, verify=False)
        
        if response.status_code == 200:
            issues = response.json()
            if not issues:
                break
            all_issues.extend(issues)
            page += 1
        else:
            print(f"Ошибка получения закрытых задач: {response.status_code}")
            break

    return all_issues

def get_gogs_issue_comments(issue_number):
    headers = {'Authorization': f'token {GOGS_TOKEN}'}
    response = requests.get(f'{GOGS_URL}/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_number}/comments', headers=headers, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Форматирование даты
def format_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')


def get_gitlab_user_id(username, user_token):
    headers = {'PRIVATE-TOKEN': user_token}
    response = requests.get(f'{GITLAB_URL}/users?username={username}', headers=headers, verify=False)
    
    if response.status_code == 200 and response.json():
        return response.json()[0]['id']  # Возвращаем ID первого найденного пользователя
    else:
        print(f"Ошибка получения ID пользователя GitLab для {username}: {response.text}")
        return None
    

def close_issue_in_gitlab(issue_id, user_token):
    headers = {'PRIVATE-TOKEN': user_token}
    data = {'state_event': 'close'}

    response = requests.put(f'{GITLAB_URL}/projects/{GITLAB_PROJECT_ID}/issues/{issue_id}', headers=headers, json=data, verify=False)
    
    if response.status_code == 200:
        print(f'Задача с ID {issue_id} успешно закрыта в GitLab.')
    else:
        print(f'Ошибка при закрытии задачи с ID {issue_id}: {response.text}')

# Создание задачи в GitLab от имени пользователя
def upload_issue_to_gitlab(issue, comments):
    created_by = issue.get('user', {}).get('login', 'Неизвестно')
    user_token = USER_TOKENS.get(created_by)
    
    if not user_token:
        print(f"Токен для пользователя {created_by} не найден. Пропуск задачи.")
        return

    assignee_username = issue.get('assignee', {}).get('login') if issue.get('assignee') else None
    assignee_id = get_gitlab_user_id(assignee_username, user_token) if assignee_username else None

    headers = {'PRIVATE-TOKEN': user_token}
    
    description = (
        f"{issue.get('body') or issue.get('content', '')}\n"
    )

    labels = [label['name'] for label in issue.get('labels', [])]

    # Определение статуса задачи на основе состояния в Gogs
    state_event = 'reopen' if issue['state'] == 'open' else 'closed'

    data = {
        'title': issue['title'],
        'description': description,
        'state_event': state_event,
        'labels': labels,
        'created_at': format_date(issue['created_at'])  # Дата создания задачи
    }

    if assignee_id:
        data['assignee_ids'] = [assignee_id]
    
    response = requests.post(f'{GITLAB_URL}/projects/{GITLAB_PROJECT_ID}/issues', headers=headers, json=data, verify=False)
    
    if response.status_code == 201:
        gitlab_issue = response.json()
        gitlab_issue_id = gitlab_issue['iid']
        print(f'Задача "{issue["title"]}" успешно загружена в GitLab от имени пользователя {created_by}.')

        if issue['state'] == 'closed':
            close_issue_in_gitlab(gitlab_issue_id, user_token)
        
        # Добавление комментариев
        if comments:
            for comment in comments:
                comment_token = USER_TOKENS.get(comment['user']['login'])
                if comment_token:
                    add_comment_to_gitlab(gitlab_issue_id, comment, comment_token)
                else:
                    print(f"Токен для пользователя {comment['user']['login']} не найден. Пропуск комментария.")
    else:
        print(f'Ошибка при загрузке задачи "{issue["title"]}": {response.text}')



# Добавление комментария к задаче в GitLab
def add_comment_to_gitlab(issue_id, comment, user_token):
    headers = {'PRIVATE-TOKEN': user_token}

    created_at = format_date(comment['created_at'])
    data = {
        'body': f"{comment['body']}",
        'created_at': created_at
    }
    
    print(f"Добавление комментария к задаче ID {issue_id} с данными: {data}")  # Отладочная информация

    response = requests.post(f'{GITLAB_URL}/projects/{GITLAB_PROJECT_ID}/issues/{issue_id}/notes', headers=headers, json=data, verify=False)
    
    if response.status_code == 201:
        print('Комментарий добавлен в задачу.')
    else:
        print(f'Ошибка при добавлении комментария: {response.text}')



# Основная функция
def main():
    target_issues = get_gogs_issues()
    
    if target_issues:
        for target_issue in target_issues:
            comments = get_gogs_issue_comments(target_issue['number'])
            upload_issue_to_gitlab(target_issue, comments)
    else:
        print(f"Задач не найдено.")

if __name__ == "__main__":
    main()
