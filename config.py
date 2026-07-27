import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "kindkart_dev_secret_key_2026"
    )

    DATABASE = os.path.join(
        BASE_DIR,
        "database",
        "kindkart.db"
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }