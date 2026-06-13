import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "projects")
    PROFILE_UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "profile")
    RESUME_UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "resumes")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_PROJECT_FOLDER = os.getenv("CLOUDINARY_PROJECT_FOLDER", "portfolio/projects")
    CLOUDINARY_PROFILE_FOLDER = os.getenv("CLOUDINARY_PROFILE_FOLDER", "portfolio/profile")
    CLOUDINARY_RESUME_FOLDER = os.getenv("CLOUDINARY_RESUME_FOLDER", "portfolio/resumes")
    CLOUDINARY_CERTIFICATE_FOLDER = os.getenv("CLOUDINARY_CERTIFICATE_FOLDER", "portfolio/certificates")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16")) * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_RESUME_EXTENSIONS = {"pdf"}
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
