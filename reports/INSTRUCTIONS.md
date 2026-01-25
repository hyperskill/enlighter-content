# 🚀 Инструкция по использованию процесса аудита контента

## 📋 Что уже сделано

✅ Репозиторий склонирован в `/Users/nikkononov/enlighter-content`  
✅ Создана ветка `content-audit-2026-01-25`  
✅ Разработан скрипт автоматизации `scripts/audit_script.py`  
✅ Проведен аудит первых 2 проектов  
✅ Созданы детальные отчеты  
✅ Исправлена найденная опечатка  
✅ Изменения закоммичены

---

## 📊 Текущее состояние

**Всего проектов в репозитории:** 27  
**Проверено:** 2 (project_10, project_11)  
**Осталось проверить:** 25

### Проверенные проекты:
1. ✅ project_10_rag_based_support_agent - 4.6/5 (отлично)
2. ✅ project_11_how_to_build_your_first_mcp_server - 5.0/5 (идеально)

---

## 🔄 Как продолжить проверку

### Вариант 1: Проверить следующую пачку (5 проектов)

```bash
# Перейти в директорию репозитория
cd /Users/nikkononov/enlighter-content

# Убедиться что на правильной ветке
git status

# Модифицировать скрипт для проверки следующих 5 проектов
# Откройте scripts/audit_script.py и измените:
# projects_to_audit = all_projects[:2]  # было
# projects_to_audit = all_projects[2:7]  # станет

# Запустить проверку
python3 scripts/audit_script.py

# Просмотреть результаты
cat reports/audit_summary.json
```

### Вариант 2: Проверить все оставшиеся проекты

```bash
cd /Users/nikkononov/enlighter-content

# Измените в scripts/audit_script.py:
# projects_to_audit = all_projects[2:]  # все кроме первых двух

python3 scripts/audit_script.py
```

### Вариант 3: Проверить конкретный проект

```bash
cd /Users/nikkononov/enlighter-content

# Измените в scripts/audit_script.py:
# projects_to_audit = [p for p in all_projects if 'project_36' in p.name]

python3 scripts/audit_script.py
```

---

## 🔍 Детальная проверка контента (ручная)

После автоматической проверки рекомендуется проверить ключевые файлы вручную:

```bash
# Просмотреть HTML файлы проекта
cd /Users/nikkononov/enlighter-content
ls project_XX_название/*.html

# Прочитать содержимое
cat project_XX_название/file.html

# Искать упоминания технологий
grep -i "cursor\|mcp\|python\|node" project_XX_название/*.html

# Проверить ссылки
grep -o "https\?://[^\s<>\"']*" project_XX_название/*.html
```

---

## 📝 Создание детальных отчетов

Для каждого проверенного проекта создайте markdown отчет:

```bash
# Создать файл отчета
touch reports/detailed_analysis_project_XX.md

# Использовать шаблон:
# - Проверенные файлы
# - Актуальные технологии
# - Найденные проблемы
# - Рекомендации
# - Оценка качества
# - Действия для обновления

# См. примеры:
# reports/detailed_analysis_project_10.md
# reports/detailed_analysis_project_11.md
```

---

## ✏️ Внесение исправлений

Когда найдены проблемы:

```bash
cd /Users/nikkononov/enlighter-content

# Исправить файл (пример с опечаткой)
cat > project_XX_название/file.html << 'EOF'
<!-- исправленное содержимое -->
EOF

# Или редактировать в текстовом редакторе
nano project_XX_название/file.html

# Закоммитить изменения
git add project_XX_название/file.html
git commit -m "fix: описание исправления"
```

---

## 📤 Пуш изменений и создание PR

### Шаг 1: Пуш в remote репозиторий

```bash
cd /Users/nikkononov/enlighter-content

# Запушить ветку
git push origin content-audit-2026-01-25

# Если это первый пуш ветки, используйте:
git push -u origin content-audit-2026-01-25
```

### Шаг 2: Создать Pull Request

Перейти на GitHub:
```
https://github.com/hyperskill/enlighter-content/pulls
```

Создать PR со следующей информацией:

**Название:**
```
Content Audit 2026-01-25: Projects 10-11 Review
```

**Описание:**
```markdown
## Content Audit Summary

Проведен детальный аудит первых 2 проектов на актуальность контента.

### Проверено проектов: 2
- ✅ project_10_rag_based_support_agent (4.6/5)
- ✅ project_11_how_to_build_your_first_mcp_server (5.0/5)

### Найденные проблемы: 1
- Исправлена опечатка "Assystant" → "Assistant" в project 10

### Добавлено:
- Автоматический скрипт проверки (audit_script.py)
- Детальные отчеты по каждому проекту
- Инфраструктура для проверки остальных 25 проектов

### Общий статус:
🟢 Оба проекта в отличном состоянии, используют актуальные технологии

См. детали в reports/AUDIT_SUMMARY_2026-01-25.md
```

---

## 📊 Анализ отчетов

### JSON отчеты (автоматические)

```bash
# Сводный отчет
cat reports/audit_summary.json | python3 -m json.tool

# Отчет по конкретному проекту
cat reports/project_10_rag_based_support_agent_report.json | python3 -m json.tool
```

### Markdown отчеты (детальные)

```bash
# Сводный
cat reports/AUDIT_SUMMARY_2026-01-25.md

# По проекту
cat reports/detailed_analysis_project_10.md
```

---

## 🔧 Доработка скрипта audit_script.py

### Добавить новые проверки:

```python
# В классе ContentAuditor добавьте методы:

def check_code_blocks(self, filename, content, lines):
    """Check Python/JS code blocks for syntax errors"""
    # Ваша логика

def check_image_urls(self, filename, content):
    """Verify all images are accessible"""
    # Проверка ucarecdn URLs

def check_api_endpoints(self, filename, content):
    """Validate API endpoints mentioned"""
    # Проверка актуальности API
```

### Модифицировать список проектов для проверки:

```python
# В функции main():

# Опция 1: Проверить диапазон
projects_to_audit = all_projects[2:7]  # проекты 3-7

# Опция 2: Проверить по фильтру
projects_to_audit = [p for p in all_projects 
                     if 'mcp' in p.name.lower()]

# Опция 3: Проверить по списку ID
project_ids = [10, 11, 19, 29, 31]
projects_to_audit = [p for p in all_projects 
                     if any(f"project_{id}_" in p.name for id in project_ids)]
```

---

## 📈 Мониторинг прогресса

### Создать трекер прогресса:

```bash
# Создать файл progress.md
cat > reports/progress.md << 'EOF'
# Progress Tracker

## Проверено: 2/27 (7.4%)

### ✅ Завершено:
- [x] project_10_rag_based_support_agent
- [x] project_11_how_to_build_your_first_mcp_server

### 🔄 В процессе:
- [ ] ...

### ⏳ Ожидает проверки:
- [ ] project_19_agent_all_dry
- [ ] project_29_console_chat_with_llm
- [ ] ...
EOF
```

---

## 🎯 Рекомендованный план действий

### Этап 1: Проверка всех проектов (1-2 недели)
- [ ] Пачка 1 (проекты 10-11) ✅ ГОТОВО
- [ ] Пачка 2 (проекты 19, 29, 31, 33, 35)
- [ ] Пачка 3 (проекты 36, 37, 38, 39, 40)
- [ ] Пачка 4 (проекты 41, 42, 43, 44, 45)
- [ ] Пачка 5 (проекты 46, 47, 48, 49, 50)
- [ ] Пачка 6 (проекты 52, 54, 55, 56, 68)

### Этап 2: Применение исправлений (3-5 дней)
- [ ] Исправить все критические проблемы
- [ ] Обновить устаревшие ссылки
- [ ] Актуализировать версии инструментов

### Этап 3: Документация (1-2 дня)
- [ ] Сводный отчет по всем 27 проектам
- [ ] Рекомендации по поддержанию актуальности
- [ ] Чеклист для новых проектов

### Этап 4: Автоматизация (опционально)
- [ ] CI/CD для автоматической проверки
- [ ] GitHub Actions workflow
- [ ] Scheduled audits

---

## 💡 Полезные команды

```bash
# Статистика по проектам
cd /Users/nikkononov/enlighter-content
ls -d project_* | wc -l

# Подсчет HTML файлов
find . -name "*.html" -path "./project_*" | wc -l

# Поиск устаревших упоминаний
grep -r "2023\|2024" project_*/*.html

# Проверка всех ссылок
grep -roh "https\?://[^\s<>\"']*" project_*/

# Размер проектов
du -sh project_*
```

---

## 🆘 Troubleshooting

### Проблема: Скрипт не запускается

```bash
# Проверить Python версию
python3 --version  # должна быть 3.8+

# Установить зависимости если нужно
# В данном случае используются только стандартные библиотеки

# Проверить права
chmod +x scripts/audit_script.py
```

### Проблема: Git push отклонен

```bash
# Обновить локальную ветку
git pull origin main --rebase

# Решить конфликты если есть
git status
git add .
git rebase --continue

# Запушить снова
git push origin content-audit-2026-01-25
```

### Проблема: Нужно изменить уже закоммиченные файлы

```bash
# Внести изменения
nano file.html

# Добавить к последнему коммиту
git add file.html
git commit --amend --no-edit

# Force push (осторожно!)
git push origin content-audit-2026-01-25 --force
```

---

## 📞 Контакты и ресурсы

- **Репозиторий:** https://github.com/hyperskill/enlighter-content
- **Документация:** https://docs.google.com/document/d/1i8C5gUZSSsArFpDyg735-QBMmDlO1lKwxBrUJLq53BM/
- **Discord:** https://discord.gg/VfAzUvUxRM

---

## ✅ Чеклист перед PR

- [ ] Все проекты проверены
- [ ] Отчеты созданы (JSON + Markdown)
- [ ] Исправления применены
- [ ] Изменения закоммичены с понятными сообщениями
- [ ] Ветка запушена в remote
- [ ] PR создан с детальным описанием
- [ ] Reviewers добавлены
- [ ] Labels присвоены (audit, documentation, content)

---

**Готов к работе!** 🚀

Удачи в проверке остальных 25 проектов! 💪
