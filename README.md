# DRF-Library-Group-Project

Cinema service made with DFR for management.

## 💼 Installing using GIT
```
git clone https://github.com/MikhailLyvak/DRF-Library.git
cd DRF-LIBRARY
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
```

# 📝 How to enable scheduled tasks
```python
 1. Ensure than you have installed django-q from requirements
 2. Make migrations: python manage.py migrate
 3. It’s recommended to add task via admin site (localhost + /admin/django_q/schedule/add/). 
    Func = borrowing.tasks.get_borrowings_overdue
    Otherwise, you can create it via Django shell:
    Schedule.objects.create(
       func="borrowing.tasks.get_borrowings_overdue"
       schedule_type=Schedule.MINUTES,
       minutes=1
     )
 4. Run the scheduler:
    python manage.py runserver
    python manage.py qcluster
```


# 🤟 To get access to work with api do next steps
```python
create user via /api/users/register/
get access token via /api/users/token/
```

# 📈 How to user ModHeader
```python
# ModHeader should be already installed
1. + MOD --> Request header
2. Put correct credentials
    2.1. Name --> Authorize ( it`s custom name )
    2.2. Value --> Bearer < Your token >
```

# 📜 Some project Features
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing books:
    - ( for admin only )
    - ( user can only see a list of books )
- Borrowings:
    - ( user can borrow book for 1 week )
    - ( user can`t borrow book if it out of stock )
- Notifications:
    - ( when book borrowed, telegram bot send notification )
    - ( telegram bot send notifications with info about overdue books )
- Payments:
    - (  )
    - (  )
- Filtering movies and movie sessions
