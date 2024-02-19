# shareholder

Install Django verison
4.2.10 (LTS)

use the bellow command to install dependencies
pip install -r requirements.txt

install pgAdmin(postgres sql)
create database shareholders
username and password is 'postgres'

example

'ENGINE': 'django.db.backends.postgresql',
'NAME': 'shareholders',
'USER': 'postgres',
'PASSWORD': 'postgres',
'HOST': 'localhost',
'PORT': '5432',

Run the command 
python manage.py makemigrations
python manage.py migrate

