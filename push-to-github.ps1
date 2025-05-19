# Скрипт для пуша проекта на GitHub

# Перейти в директорию проекта
Set-Location -Path "$PSScriptRoot"

# Проверить, инициализирован ли git-репозиторий
if (-not (Test-Path ".git")) {
    git init
}

# Добавить удалённый репозиторий (если не добавлен)
$remote = git remote
if ($remote -notcontains "origin") {
    git remote add origin https://github.com/robotverter1/roslaw.git
}

# Добавить .gitignore, если его нет
if (-not (Test-Path ".gitignore")) {
    New-Item -Path ".gitignore" -ItemType File
}

# Добавить все файлы и сделать коммит
git add .
git commit -m "Initial commit"

# Установить основную ветку main
git branch -M main

# Пуш на GitHub
git push -u origin main
