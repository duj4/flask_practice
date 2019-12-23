import os

DEBUG = True
HOST = '0.0.0.0'
PORT = '5000'
SECRET_KEY = 'secret string'
MAX_CONTENT_LENGTH = 3 * 1024 * 1024 # 限制上传文件的大小为3M
UPLOAD_PATH = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
CKEDITOR_SERVE_LOCAL = True
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////' + os.path.join(os.path.dirname(os.path.abspath('app.py')), 'data.db'))
# 这个配置变量决定是否追踪对象的修改，这用于Flask-SQLAlchemy的事件通知系统，默认值为None，如果没有特殊需要，可以将其改为False
SQLALCHEMY_TRACK_MODIFICATIONS = False
