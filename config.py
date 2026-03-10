import os

# Database Settings
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "edutool"
COLLECTION_NAME = "books"
USER_COLLECTION = "users"
INTERACTION_COLLECTION = "interaction"
SECRET_KEY = 'my_secret_key'

WISHLIST_COLLECTION = "wishlists"


# Email Settings (Gmail)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'lahirugimhan2001@gmail.com'  # ඔබේ ඊමේල් ලිපිනය
MAIL_PASSWORD = 'iezt dyuo kjff odol'   # පියවර 2 දී ලබාගත් App Password එක