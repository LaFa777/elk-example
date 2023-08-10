# stdlib
import os

# thirdparty
from flask import Flask

# project
from src.urls import elk_routes

app = Flask(__name__)

# считываем конфиг
environ = "dev"
if os.environ.get("STAGE"):
    environ = os.environ["STAGE"].lower()
app.config.from_pyfile(f"settings/{environ}.py")

# регистрируем view
app.register_blueprint(elk_routes)
