import os

DEBUG = True
HOST = '0.0.0.0'
PORT = '5000'
SECRET_KEY = 'secret string'
MAX_CONTENT_LENGTH = 3 * 1024 * 1024 # 限制上传文件的大小为3M
UPLOAD_PATH = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
CKEDITOR_SERVE_LOCAL = True

