from flask import Flask, url_for, request, redirect, abort, make_response, jsonify, session
from urllib.parse import urlparse, urljoin
import json
import click
import config

app = Flask(__name__)
app.config.from_object(config)
#secret_key也可以保存在.env中
app.secret_key = app.config['SECRET_KEY']

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
# /hello?name=Jason
def hello():
    # 直接用key作为索引(name = request.args['name'])，如果没有对应的key，会返回HTTP 400(bad request)，而不是抛出KeyError异常:
    # werkzeug.exceptions.BadRequestKeyError: 400 Bad Request: The browser (or proxy) sent a request that this server could not understand.
    # KeyError: 'name'
    # 为了避免这个问题，应该用get方法代替，如果没有对应的value则返回None；第二个参数用来设置默认值，即如果name的值不存在，则将其返回
    # name = request.args.get('name', 'Flask')
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
        response = "<h1>Hello, %s!</h1>" % name

    # 根据用户认证状态返回不同的内容
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'

    # return "<h1>Hello, %s!</h1>" % name
    return response

# url_for()获取URL
@app.route('/test_url_for')
def test_url_for():
    print(url_for('index'))
    # 默认生成的URL是相对URL，_external=True可以返回绝对URL
    print(url_for('sayHello', _external=True))
    print(url_for('greet', name='Jason'))

    return "Testing function url_for()"

# URL处理
@app.route('/goback/<int:year>') # 为year增加一个int转换器，会将string转成int型便于视图函数处理
def go_back(year):
    return "<p>Welcome to %d!</p>" % (2019 - year)

@app.route('/colors/<any(blue, white, red):color>') # any转换器后添加括号给出可选值
# # 如果想传入一个自定义的列表，然后从列表中进行取值访问，可以按照如下写法:
# colors = ['blue', 'white', 'red']
# @app.route('/colors/<any(%s):color>' % str(colors)[1:-1])
def three_colors(color):
    return "<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>"

# 创建自定义命令
@app.cli.command()
def hello():
    """TEST COMMAND, just say 'Hello Human!'"""
    click.echo("Hello Human!")

# 重定向
@app.route('/redirect')
def redirectToSomewhere():
    return redirect(url_for('sayHello'))
    # return redirect('https://www.baidu.com')

# 单击链依然返回到foo页面
# 手动加入当前页面URL的查询参数next，next = request.full_path获取当前页面的完整路径
@app.route('/foo')
def foo():
    return '<h1>Foo Page</h1><a href="%s">Do Something and redirect</a>' % url_for("do_something", next=request.full_path)

@app.route('/bar')
def bar():
    return '<h1>Bar Page</h1><a href="%s">Do Something and redirect</a>' % url_for("do_something", next=request.full_path)

# 验证URL安全性
def is_safe_url(target):
    # request.host_url获取程序内的主机URL
    # target: /foo?
    # request.host_url: http://192.168.0.103:5000/
    ref_url = urlparse(request.host_url)
    # ref_url: ParseResult(scheme='http', netloc='192.168.0.103:5000', path='/', params='', query='', fragment='')

    # urljoin用来将目标URL转换为绝对URL
    test_url = urlparse(urljoin(request.host_url, target))
    # test_url: ParseResult(scheme='http', netloc='192.168.0.103:5000', path='/foo', params='', query='', fragment='')
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# referrer是一个用来记录请求发源地址的HTTP首部字段(HTTP_REFERRER)
# 当用户在某个站点单击链接，浏览器向新连接的服务器发起请求，请求的时间中包含的HTTP_REFERRER字段记录了用户所在的原站点URL
# 将next和referrer结合到一起，写成重定向function如下:
def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

#在do_something视图中，获取next值，然后重定向到对应的路径(若next为空，则重定向到hello视图)
@app.route('/do_something')
def do_something():
    # do something
    # return redirect(url_for('hello'))
    # return redirect(request.args.get('next', url_for('hello')))
    return redirect_back()

# 错误响应
@app.route('/404')
def not_found():
    abort(404)

# 响应格式
@app.route('/returnType')
def returnType():
    # text/plain
    # response = make_response(
    #     'Note\n'
    #     'to: Peter\n'
    #     'from: Jane\n'
    #     'heading: Reminder\n'
    #     'body: Don\'t forget the party\n'
    # )
    # response.mimetype = 'text/plain'

    # text/html
    # response = make_response(
    #     '<!DOCTYPE html>'
    #     '<html>'
    #     '<head></head>'
    #     '<body>'
    #        '<h1>Note</h1>'
    #        '<p>to: Peter</p>'
    #        '<p>from: Jane</p>'
    #        '<p>heading: Reminder</p>'
    #        '<p>body: <strong>Don\'t forget the party!</strong></p>'
    #     '</body>'
    #     '</html>'
    # )
    # response.mimetype = 'text/html'

    # application/json
    data = {
        "note":{
            "to": "Peter",
            "from": "Jane",
            "heading": "Reminder",
            "body": "Don't forget the party!"
        }
    }

    # Flask通过包装json的原生方法形成了一个jsonify()函数
    # 通过该函数只需要传入数据或者参数，它就会对其进行序列化然后转换成JSON字符串作为响应主体，再生成响应对象并设置正确的MIME类型
    # response = make_response(json.dumps(data))
    # response.mimetype = 'application/json'
    # return response
    return jsonify(data)

# Cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect((url_for('hello'))))
    response.set_cookie('name', name)

    return response

# 模拟认证
# 默认情况下，session cookie会在用户关闭浏览器时删除
# 通过将session.permanent属性设为True可以将session的有效期延长为Flask.permanent_session_lifetime属性值对应的datetime.timedelta对象
# 也可以通过配置变量PERMANENT_SESSION_LIFETIME设置，默认为31天
@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hello'))

# 模拟后台
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)

    return 'Welcome to admin page.'

# 登出用户
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')

    return redirect(url_for('hello'))

if __name__ == '__main__':
    app.run(debug = app.config['DEBUG'],
            host = app.config['HOST'],
            port = app.config['PORT'])