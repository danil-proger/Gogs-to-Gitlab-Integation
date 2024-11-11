import os
import subprocess

# Настройки
GOGS_URL = 'your_gogs_url'
GITLAB_URL = 'your_gitlab_url'
GOGS_TOKEN = 'your_gogs_token'
GITLAB_TOKEN = 'your_gitlab_token'
GOGS_USERNAME = 'gogs_group_name'
REPO_NAME = 'repo_name'
GITLAB_GROUP_PATH = 'gitlab_group_name'
gogs_repo_url = f"{GOGS_URL}/{GOGS_USERNAME}/{REPO_NAME}.git"
gitlab_repo_url_with_token = f"{GITLAB_URL}/{GITLAB_GROUP_PATH}/{REPO_NAME}.git"

# Директории для репозиториев
local_repo_path = f'./{REPO_NAME}'

# Клонирование репозитория из Gogs с отключением SSL-проверки
def clone_gogs_repo():
    # Команда для клонирования всех веток из Gogs
    clone_cmd = [
        'git', '-c', 'http.sslVerify=false', 'clone', '--mirror', gogs_repo_url, local_repo_path
    ]
    subprocess.run(clone_cmd, check=True)
    print("Репозиторий успешно клонирован с Gogs.")

# Настройка и пуш репозитория в GitLab
def push_to_gitlab():
    os.chdir(local_repo_path)
    # Настраиваем удаленный репозиторий GitLab
    set_remote_cmd = [
        'git', 'remote', 'set-url', '--push', 'origin', gitlab_repo_url_with_token
    ]
    subprocess.run(set_remote_cmd, check=True)

    # Отправляем все ветки и теги в GitLab
    push_cmd = [
        'git', '-c', 'http.sslVerify=false', 'push', '--mirror', gitlab_repo_url_with_token
    ]
    subprocess.run(push_cmd, check=True)
    print("Все ветки и теги успешно отправлены в GitLab.")


# Основная функция
def main():
    clone_gogs_repo()
    push_to_gitlab()

if __name__ == "__main__":
    main()
