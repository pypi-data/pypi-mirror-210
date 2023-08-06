# Ebdesk Google Account Management

### How To Install
```python
pip install --trusted-host 192.168.20.26 --index-url http://192.168.20.26:6060/simple/ ebdesk-email-executor
```

### Example 

##### Get one email
```python
from ebdesk_email_executor.main import ExecutorAccount
ex = ExecutorAccount()

data = ex.get_email()
#return {'email': 'nasri@mail.com', 'password': 'sirrah', 'status': 'ACTIVE', 'active': False}
```

##### Bulk Email
```python
from ebdesk_email_executor.main import ExecutorAccount
ex = ExecutorAccount()

temp = [{
    "email": "nasri@mail.com",
    "password": "sirrah",
    "status": "ACTIVE",
    "active": False
},{
    "email": "nasri1@mail.com",
    "password": "sirrah",
    "status": "ACTIVE",
    "active": False
},{
    "email": "nasri2@mail.com",
    "password": "sirrah",
    "status": "ACTIVE",
    "active": False
}]
ex.bulk_email(model=temp)
```

##### Add Email (single)
```python
from ebdesk_email_executor.main import ExecutorAccount
ex = ExecutorAccount()

ex.add_email(email="email@mail.com", password="rahasia2023", status="ACTIVE")
```

##### Update Active Status
after execute chat gpt, use this function to update status active into `False`, to usable email 
```python
from ebdesk_email_executor.main import ExecutorAccount
ex = ExecutorAccount()

ex.update_active("email@mail.com")
```

##### Handle Timeout
if account has blocket from open api, use this function
```python
from ebdesk_email_executor.main import ExecutorAccount
ex = ExecutorAccount()

ex.update_active("email@mail.com")
```

