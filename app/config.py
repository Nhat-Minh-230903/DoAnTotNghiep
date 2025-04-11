# app/config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:0963230903@localhost:5432/DoAn"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Tắt tính năng theo dõi các thay đổi trong DB
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "superjwtsecretkey")

    # Cấu hình Gmail SMTP
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'nguyennhatminh230203@gmail.com'  # Gmail của bạn
    MAIL_PASSWORD = 'inya kohq ohmd iujt'  # App Password của bạn
    MAIL_DEFAULT_SENDER = 'nguyennhatminh230203@gmail.com'
    
