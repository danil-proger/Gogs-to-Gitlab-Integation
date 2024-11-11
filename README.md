# Gogs-to-Gitlab-Integation

# Gogs-to-GitLab Issue Migration Tool

### Описание

Этот проект представляет собой инструмент для переноса задач и комментариев из системы управления репозиториями Gogs в GitLab. Скрипт разработан для автоматической миграции задач вместе с комментариями, сохраняя при этом оригинальные даты и автора для каждой задачи и комментария. Он также поддерживает фильтрацию задач по назначенным пользователям и перенаправляет их в GitLab от имени соответствующих пользователей.

## Функции

- Миграция задач из Gogs в GitLab, включая как открытые, так и закрытые задачи.
- Сохранение временных меток для задач и комментариев, чтобы сохранить историю переписки.
- Назначение задач пользователям в GitLab, основываясь на назначении из Gogs.
- Добавление комментариев к задачам, с указанием даты и времени публикации.
- Использование токенов для выполнения действий от имени пользователей в GitLab.
- Поддержка нескольких страниц задач, что позволяет переносить большие проекты.

## Требования

- Python 3.6 или выше
- Установленные пакеты Python:
  - requests
- Токены доступа для Gogs и GitLab с правами доступа:
  - Gogs: Административный или пользовательский токен доступа.
  - GitLab: Токены доступа с правами на создание задач и комментариев.

## Установка

1. Клонируйте репозиторий:

        git clone <URL этого репозитория>
    cd <папка репозитория>
    

2. Установите необходимые библиотеки:

        pip install requests
    

3. Настройте конфигурацию, добавив свои токены доступа и идентификаторы проектов в переменные, указанные в начале файла скрипта:

        GOGS_URL = 'https://example.com/api/v1'
        GOGS_TOKEN = 'your_gogs_token'
        GITLAB_URL = 'https://gitlab.example.com/api/v4'
        GITLAB_TOKEN = 'your_gitlab_token'
        REPO_OWNER = 'repo_owner'
        REPO_NAME = 'repo_name'
        GITLAB_PROJECT_ID = 'project_id'
    

## Использование

1. Запустите скрипт, чтобы начать перенос:

        python migration_issues.py
    

2. Скрипт будет обрабатывать задачи постранично, загружая комментарии для каждой задачи и добавляя их в GitLab.

## Пример кода

### Структура скрипта

- get_gogs_issues(): Получает список задач из Gogs.
- upload_issue_to_gitlab(): Создаёт задачи в GitLab, включая назначенных пользователей и метки.
- add_comment_to_gitlab(): Добавляет комментарии к задачам в GitLab, сохраняя дату создания.

### Пример добавления защищённой ветки

```python
def protect_gitlab_branch(branch_name):
    headers = {'PRIVATE-TOKEN': GITLAB_TOKEN}
    data = {
        'name': branch_name,
        'push_access_level': 0,  # Только администраторы могут вносить изменения
        'merge_access_level': 30  # Доступ на слияние
    }
    response = requests.post(f'{GITLAB_URL}/projects/{GITLAB_PROJECT_ID}/protected_branches', headers=headers, json=data)
    if response.status_code == 201:
        print(f'Ветка {branch_name} защищена.')
    else:
        print(f'Ошибка при защите ветки: {response.text}')
