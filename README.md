# night_owl
Backend for night owl market
I deploy api to heroku. Check at: https://www.nguyendinhhuy.dev/market

## How to run this project
### 1. Install Python from https://www.python.org/downloads/
### 2. Clone this github project
Open terminal or Command Prompt on Window and paste this code in
```
git clone https://github.com/HuyNguyenDinh/night_owl.git
```
### 3. Install PostgreSQL and create a database for project, you can check at this link https://www.postgresql.org/
### 4. Register account and get the API Key, API secret for Cloudinary Configuration in this project at https://cloudinary.com/
### 5. Register Firebase account and register Firebase Cloud Messaging to get configuration then download the credentials.json and put at the project root directory (at the same manage.py directory)
### 6. Set the environment varialbe
- SECRET_KEY: the SECRET_KEY for Django project include ASCII unicode
- EMAIL_HOST_USER: the email for the system to send email for customer
- EMAIL_HOST_PASSWORD: the password for the email
- CLOUD_API_KEY: the Cloudinary API key
- CLOUD_API_SECRET: the Cloudinary API Secret
- CLOUD_NAME: the Cloudinary cloud name
- DB_HOST: IP of database server use for this project (If you have created database at the current machine use "localhost". )
- DB_NAME: The database name
- DB_USER: The database's user
- DB_PASSWORD: The database's user's password
### 7. Install the package
Go to the directory at requirements.txt and paste this to the terminal
```
python -m pip install -r requirements.txt
```
### 8. Start project
Go to the directory at manage.py then open terminal
- Migrate the project
```
python manage.py migrate
```
- Create the super user for project
```
python manage.py createsuperuser
```
- Start server
```
python manage.py runserver
```
Go to http://127.0.0.1:8000/market/ to check the DEBUG UI
