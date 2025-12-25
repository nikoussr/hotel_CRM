# О проекте
Для бронирования номеров требуется позвонить администратору по телефону. Клиенты могут быть размещены в 1-, 2-х и 3-х местных номерах категорий стандарт, комфорт и люкс. По желанию можно поставить детскую кровать в любой из номеров. На разные дни недели стоимость номеров различается. При бронировании номера на длительное время предусмотрена система скидок. Система должна позволять отменять бронь, фиксировать фактические даты заезда и выезда постояльцев. Информационная система предназначена для администратора гостиницы.

## Ключевые возможности
### Управление номерами
1. Создание и редактирование номеров различных категорий и вместимостей: Стандарт, Комфорт, Люкс.
2. Возможность добавления детской кровати в любой номер
3. Управление статусами номеров
4. На разные дни недели стоимость номеров различается
5. При бронировании номера на длительное время предусмотрена система скидок

### Бронирование номеров
1. Полноценная система бронирования
2. Календарь занятости с визуализацией
3. Управление гостями и их данными
5. Регистрация фактических дат заезда и выезда
6. Заселение, выселение, отмена бронирования

### Гости
1. Добавление гостей (ФИ, номер телефона, паспортные данные, потча)
2. Посчёт числа бронирований для данного гостя

## Технические требования
Python 3.13+
Django 4.2+
SQLite

## Установка и запуск
Клонирование репозитория

```git clone https://github.com/nikoussr/hotel_CRM```

```python -m venv venv```

```venv\Scripts\activate```

```pip install -r requirements.txt```

```cd hotel_system```

```python manage.py makemigrations```

```python manage.py migrate```

```python manage.py createsuperuser```

```python manage.py runserver```

Приложение: http://127.0.0.1:8000/

## Скриншоты
### Авторизация
<img width="2559" height="488" alt="image" src="https://github.com/user-attachments/assets/82e45da5-a348-4308-8927-651d240babdd" />


### Календарь занятости
<img width="2559" height="1244" alt="image" src="https://github.com/user-attachments/assets/cb33fbd4-1d55-49f2-abd3-cbe433558591" />

### Управление номерами
<img width="2546" height="1167" alt="image" src="https://github.com/user-attachments/assets/d535c3e0-5aea-4015-82ab-1e37250a0526" />
<img width="2559" height="1118" alt="image" src="https://github.com/user-attachments/assets/9f160bfe-5251-458d-aaba-f7fd50d5e09f" />
<img width="2559" height="626" alt="image" src="https://github.com/user-attachments/assets/505d361d-4bd5-4e8c-b732-b76282fbb794" />


### Создание бронирования
<img width="2559" height="891" alt="image" src="https://github.com/user-attachments/assets/250823ba-5588-4560-bf5d-296567eac0f1" />


### Управление бронированием
<img width="2559" height="914" alt="image" src="https://github.com/user-attachments/assets/91ba52b9-c076-47ce-9616-7101a1fadd30" />
<img width="2549" height="1088" alt="image" src="https://github.com/user-attachments/assets/11302e80-6cf2-4227-955c-54c9bbffd2d4" />
<img width="2559" height="671" alt="image" src="https://github.com/user-attachments/assets/6eadd566-f49d-43e0-8dce-bcb85f490d64" />


### Управление гостями)
<img width="2546" height="654" alt="image" src="https://github.com/user-attachments/assets/883c66ac-e8a5-4aff-ac8b-585e23f1ca41" />

