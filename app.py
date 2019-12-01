from flask import Flask, url_for, request
import click
import config

app = Flask(__name__)
app.config.from_object(config)

# 第一个视图函数
@app.route('/')
def index():
    return "<h1>Hello World!</h1>"

# 一个视图函数允许多个对应的URL
@app.route('/hola')
@app.route('/hi')
def sayHello():
    return "<h1>Hola, Flask!</h1>"

# defaults参数可以设置默认值
@app.route('/greet', defaults={'name':'Programmer'})
@app.route('/greet/<name>')
def greet(name):
    return "<h1>Hello, %s!</h1>" % name

# 获取URL请求中的查询字符串
# 这种写法包含安全漏洞，要避免直接将用户传入的数据直接作为响应返回
@app.route('/hello')
def hello():
    # 直接用key作为索引，如果没有对应的key，会返回HTTP 400(bad request)，而不是抛出KeyError异常
    # name = request.args['name']
    # werkzeug.exceptions.BadRequestKeyError: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.
    # KeyError: 'name'
    # 为了避免这个问题，应该用get方法代替，如果没有对应的value则返回None；第二个参数用来设置默认值，即如果name的值不存在，则将其返回
    name = request.args.get('name', 'Flask')
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