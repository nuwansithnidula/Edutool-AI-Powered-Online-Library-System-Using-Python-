from flask_mail import Mail
from flask_login import LoginManager

# මෙහිදී අපි app එක සම්බන්ධ නොකර හිස්ව ඔබ්ජෙක්ට් සාදා ගනිමු.
mail = Mail()
login_manager = LoginManager()