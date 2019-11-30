from flask import Flask, url_for
import click
import config

app = Flask(__name__)
app.config.from_object(config)

# 第一个视图函数
@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

# 一个视图函数允许多个对应的URL
@app.route('/hi')
@app.route('/hello')
def sayHello():
    return "<h1>Hello, Flask!</h1>"

# defaults参数可以设置默认值
@app.route('/greet', defaults={'name':'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return "<h1>Hello, %s!</h1>" % name

# url_for()获取URL
@app.route('/test_url_for')
def test_url_for():
    print(url_for('index'))
    # 默认生成的URL是相对URL，_external=True可以返回绝对URL
    print(url_for('sayHello', _external=True))
    print(url_for('greet', name='Jason'))

    return "Testing function url_for()"

# 创建自定义命令
@app.cli.command()
def hello():
    """TEST COMMAND, just say 'Hello Human!'"""
    click.echo("Hello Human!")

if __name__ == '__main__':
    app.run(debug = app.config['DEBUG'],
            host = app.config['HOST'],
            port = app.config['PORT'])