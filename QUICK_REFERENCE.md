# Медми Клиника - Быстрая справка

## 🚀 Запуск в 3 шага

```powershell
cd c:\hospital_project
python manage.py migrate
python manage.py runserver
```

Откройте http://127.0.0.1:8000

---

## 👥 Три типа пользователей

| Тип | Вход | Создание | Доступ |
|-----|------|----------|--------|
| **Администратор** | `/admin/` | `createsuperuser` | Полный контроль |
| **Врач** | `/doctor/login/` | Только админ | Кабинет + записи |
| **Пациент** | `/patient/login/` | Самостоятельно | Регистрация + кабинет |

---

## 📋 Основные URL

```
/ ........................ Главная (с новостями, врачами)
/admin/ .................. Администрирование
/patient/register/ ....... Регистрация пациента
/patient/login/ .......... Вход пациента
/patient/dashboard/ ...... Личный кабинет пациента
/patient/bookings/ ....... История записей
/doctor/login/ ........... Вход врача
/doctor/dashboard/ ....... Кабинет врача
/doctor/<id>/ ............ Профиль врача
```

---

## 🔐 Тестовые учётные записи

Если использовали `populate_*.py`:

**Пациент**
- Логин: `patient1`
- Пароль: `Patient123!`

**Админ** (создать самостоятельно)
```powershell
python manage.py createsuperuser
```

---

## 📱 Контакты - только телефон

- ❌ Email **не требуется** для пациентов
- ✅ Телефон **обязателен** (нормализуется автоматически)
- 📞 Используется для поиска записей и уведомлений

---

## 🏥 Функции по ролям

### Пациент
✅ Самостоятельная регистрация (имя, телефон, пароль)
✅ Просмотр профиля врача
✅ Запись на приём
✅ История записей
✅ Оставление отзыва

### Врач
✅ Просмотр всех записей
✅ Управление статусом записи (новая → подтверждена → завершена)
✅ Список уникальных пациентов
✅ Создание записи вручную
✅ Просмотр рейтинга

### Администратор
✅ Создание врачей и пациентов
✅ Управление новостями (опубликовать на главной)
✅ Просмотр отзывов и записей
✅ Управление локациями (клиники)

---

## 🔧 Команды для администратора

```powershell
# Проверка здоровья системы
python manage.py check

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Заполнение БД тестовыми данными
python manage.py populate_doctors.py
python manage.py populate_locations.py
python manage.py populate_reviews.py

# Создание учётных записей врачей
python manage.py create_doctor_accounts.py
```

---

## 🗄️ Модели данных

```
Patient
├── user (User)
├── phone (char) ← Основной контакт
├── first_name, last_name
├── date_of_birth (optional)
└── address (optional)

Doctor
├── user (User)
├── phone
├── specialization
├── is_featured (для отображения на главной)
└── start_time, end_time (график работы)

DoctorBooking
├── doctor (FK)
├── patient_phone ← Связь с пациентом
├── patient_name
├── appointment_date
├── reason
└── status (pending/confirmed/completed/cancelled)

Review
├── doctor (FK)
├── rating
├── comment
└── is_verified

News
├── title
├── content
├── is_published ← Показывается на главной
└── published_at
```

---

## ⚠️ Типичные ошибки

**"No such table: doctors_doctor"**
→ Примените миграции: `python manage.py migrate`

**Не работает вход пациента**
→ Проверьте телефон (без спецсимволов) и пароль

**Врач не видит записи**
→ Убедитесь, что врач создан в админке с User

**Новости не отображаются на главной**
→ В админке отметьте флаг `is_published` и установите дату

---

## 📚 Файлы конфигурации

```
hospital/settings.py ......... Основные настройки Django
hospital/urls.py ............ Маршруты приложения
requirements.txt (если есть) . Зависимости Python
.env (если используется) .... Переменные окружения
```

---

## 💾 База данных

По умолчанию используется **SQLite** (`db.sqlite3`)

```powershell
# Резервная копия БД
Copy-Item db.sqlite3 db.sqlite3.backup

# Удалить ВСЕ данные (осторожно!)
# Remove-Item db.sqlite3
# python manage.py migrate
```

---

## 🌐 Frontend Stack

- **Bootstrap 5** - Responsive design
- **FontAwesome** - Иконки
- **jQuery** - JavaScript
- **Django Templates** - Серверный рендеринг

---

## 📞 Поддержка

При проблемах:
1. Проверьте консоль Django для ошибок
2. Запустите `python manage.py check`
3. Смотрите документацию в `STARTUP_GUIDE.md` и `CHANGES_SUMMARY.md`
