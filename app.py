from flask import Flask, url_for, request, redirect, abort, make_response, jsonify, session, render_template, Markup, flash, send_from_directory
from flask_wtf.csrf import validate_csrf
from flask_ckeditor import CKEditor, upload_success, upload_fail
from urllib.parse import urlparse, urljoin
from jinja2.utils import generate_lorem_ipsum
import os
import uuid
import json
import click
import config
from forms import LoginForm, FortyTwoForm, UploadForm, MultiUploadForm, RichTextForm, NewPostForm, SigninForm, RegisterForm

app = Flask(__name__)
app.config.from_object(config)
#secret_key也可以保存在.env中
# Flask-WTF默认为每个表单启用CSRF保护，会自动为我们生成和验证CSRF令牌， 默认情况下它会使用程序密钥来对CSRF令牌进行签名，所以需要设置密钥
app.secret_key = app.config['SECRET_KEY']

# 实例化Flask-CKEditor提供的CKEditor类
ckeditor = CKEditor(app)

# 第一个视图函数
# @app.route('/')
# def index():
#     return "<h1>Hello World!</h1>"

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
def sayHello():
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
# def foo():
#     return '<h1>Foo Page</h1><a href="%s">Do Something and redirect</a>' % url_for("do_something", next=request.full_path)

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

# AJAX异步请求
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n = 2)
    return """
    <h1>A very long post</h1>
    <div class="body">%s</div>
    <button id="load">Load More</button>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type="text/javascript">
    $(function() {
        $('#load').click(function() {
            $.ajax({
                url: '/more',
                type: 'get',
                success: function(data){
                    $('.body').append(data);
                }
            })
        })
    })
    </script>""" % post_body
# 接上面，点击“load more”时，会执行事件回调函数，通过url将目标URL设置为/more，并通过append方法将返回的数据append到body底部
@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)

# 错误响应
@app.route('/404')
def not_found():
    abort(404)

@app.route('/500')
def internalServerError():
    abort(500)

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

# chapter 3-template=======================================================================================
user = {
    'username': 'Grey Li',
    'bio': 'A boy who loves movies and music.'
}
movies = [
    {'name': 'My Neighbor Totoro', 'year': '1988'},
    {'name': 'Three Colours trilogy', 'year': '1993'},
    {'name': 'Forrest Gump', 'year': '1994'},
    {'name': 'Perfect Blue', 'year': '1997'},
    {'name': 'The Matrix', 'year': '1999'},
    {'name': 'Memento', 'year': '2000'},
    {'name': 'The Bucket list', 'year': '2007'},
    {'name': 'Black Swan', 'year': '2010'},
    {'name': 'Gone Girl', 'year': '2014'},
    {'name': 'CoCo', 'year': '2017'}
]

@app.route('/watchlist')
def watchlist():
    return render_template('watchlist.html', user=user, movies=movies)

# 注册模板全局函数
@app.template_global()
def bar():
    return 'I am bar.'
foo = 'I am foo.'
# 添加自定义全局对象
# 全局对象是指在所有的模板中都可以直接使用的对象，包括在模板中导入的模板
# 和注册模板全局函数不同，直接操作globals字典允许传入任意python对象，而不仅仅是函数，类似于上下文处理
# 下面代码即向模板中添加全局函数bar和foo
app.jinja_env.globals['bar'] = bar
app.jinja_env.globals['foo'] = foo

# 通过模板环境对象删除jinja2语句导致的HTML代码空白
# 宏内的空白控制不受trim_blocks和lstrip_blocks属性控制
app.jinja_env.trim_blocks = True # 删除Jinja2语句后的第一个空行，仅针对{%……%}中的代码块
app.jinja_env.lstrip_blocks = True # 删除Jinja2语句所在行之前的空格和制表符


# 注册自定义过滤器
# musical过滤器会在被国旅的变量字符后添加一个音符图标，即s是被传入/被过滤的字符
@app.template_filter()
def musical(s):
    return s + Markup('&#9835;')
# 向模板中添加过滤器
app.jinja_env.filters['musical'] = musical

# 注册自定义测试器
@app.template_test()
def baz(n):
    if n == 'baz':
        return True
    return False
# 向模板中添加测试器
app.jinja_env.tests['baz'] = baz

# 使用flash函数“闪现”消息
# 如果flash消息中包含中文，在Python2.x中，那么需要在字符串前添加u前缀，告诉Python把这个字符串编码成Unicode字符串
# 还需要在Python文件的首行添加编码声明“#-*- coding: utf-8 -*-”,这会让Python使用UTF-8来解码字符串
# Python3则不需要，因为默认就是Unicode编码
@app.route('/flash')
def just_flash():
    flash('我是闪电，谁找我?')
    return redirect(url_for('index'))

# 错误处理函数
# 错误处理函数需要附加app.errorhandler()装饰器，并传入错误状态码作为参数
# 错误处理函数本身需要接受异常类作为参数，并在返回值中注明对应的HTTP状态码。当发生错误时，对应的错误处理函数会被调用，它的返回值会作为错误响应的主体
# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    # 内置的异常对象提供了以下参数：
    print(e.code) # code: 状态码
    print(e.name) # name: 原因短语
    print(e.description) # description: 错误描述，另外使用get_description()方法还可以获取HTML格式的错误描述代码
    print(e.get_description())
    return render_template('errors/404.html'), 404

# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    print(e.code)  # code: 状态码
    print(e.name)  # name: 原因短语
    print(e.description)  # description: 错误描述，另外使用get_description()方法还可以获取HTML格式的错误描述代码
    print(e.get_description())
    return render_template('errors/500.html'), 500

@app.route('/')
def index():
    return render_template('index.html')

# chapter 4-form=========================================================================================
# Flask为路由设置默认监听的HTTP方法为GET，为了支持接收表单提交发送的POST请求，必须在装饰器里使用methods关键字为路由指定POST方法
@app.route('/basic', methods=['GET', 'POST'])
def basic():
    form = LoginForm()
    # validate_on_submit()合并了request.POST方法检查和form.validate()验证
    # PUT、PATCH和DELETE方法也可以使用该方法
    if form.validate_on_submit():
        username = form.username.data # 表单类的data属性是一个匹配所有字段与对应数据的字典
        flash('Welcome home, %s!' % username)
        # 当刷新页面时，浏览器的默认行为是发送上一个请求，如果上一个请求是POST，那么就会弹出一个确认窗口，询问客户是否再次提交
        # 尽量避免提交表单的POST作为最后一个请求，所以在这里return一个重定向响应，让浏览器重新发送一个GET请求到目标URL
        # 这种用来防止重复提交表单的技术称为PRG(Post/Redirect/Get)模式
        return redirect(url_for('index'))
    return render_template('basic.html', form = form)

@app.route('/custom-validator', methods=['GET', 'POST'])
def custom_validator():
    form = FortyTwoForm()

    if form.validate_on_submit():
        flash('Bingo!')
        return redirect(url_for('index'))
    return render_template('custom_validator.html', form=form)

# 为了让上传后的文件能够通过URL获取，创建以下视图函数返回上传后的文件
@app.route('/uploads/<path:filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

# 显示已上传的文件
@app.route('/uploaded-images')
def show_images():
    return render_template('uploaded.html')

# 对上传文件重命名
# 如果能够确定文件的来源安全，可以直接使用原文件名f.filename
# 考虑到恶意用户在文件名中加入表示上级目录的..(/../../../home/username/.bashrc或../../../etc/passwd)j进而对系统文件进行篡改或执行恶意脚本，需要对文件名进行安全处理
# from werkzeug import secure_filename, secure_filename()可以过滤掉危险字符，但是对非ASCII字符组成的文件名只能返回空值
# 避免上述情况出现，使用下述办法对文件名进行随机处理
def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

# FileAllowed验证器，返回bool值
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 上传文件
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # 上传的文件会被Flask解析为Werkzeug的FileStorage对象，使用Flask-WTF时，它会自动帮我们获取对应的文件对象
        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        flash('Upload success!')
        session['filenames'] = [filename]
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)

# 多文件上传
# 由于Flask-WTF当前版本0.14.2中并未添加对多文件上传的渲染和验证支持，所以需要在视图函数中手动获取文件并进行验证
@app.route('/multi-upload', methods=['GET', 'POST'])
def multi_upload():
    form = MultiUploadForm()
    if request.method == 'POST':
        filenames = []
        # 验证CSRF令牌
        try:
            validate_csrf(form.csrf_token.data)
        except:
            flash('CSRF token error.')
            return redirect(url_for('multi_upload'))
        # 检查文件是否存在
        # 如果用户没有选择文件就提交表单则request.files为空，相当于FileRequired验证器
        if 'photo' not in request.files:
            flash('This field is required.')
            return redirect(url_for('multi_upload'))

        # 传入字段的name属性值会返回包含所有上传文件对象的列表
        for f in request.files.getlist('photo'):
            # 检查文件类型
            # 相当于FileAllowed验证器
            if f and allowed_file(f.filename):
                filename = random_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                filenames.append(filename)
            else:
                flash('Invalid file type.')
                return redirect(url_for('multi_upload'))
        flash('Upload success!')
        session['filenames'] = filenames
        return redirect(url_for('show_images'))
    return render_template('upload.html', form=form)

# ckeditor界面，目前支持get
@app.route('/ckeditor', methods=['GET', 'POST'])
def ckeditor():
    form = RichTextForm()
    if form.validate_on_submit():
        pass
    return render_template('ckeditor.html', form=form)

# two-submits
# 当表单数据通过POST请求提交时，Flask会把表单数据解析到request.form字典
# 如果表单中有两个提交字段，那么只有被单击的提交字段才会出现在这个字典中
# 当我们对表单类实例或特定的字段属性调用data属性时，WTForms会对数据做进一步处理。对于提交字段的值，它会将其转换为布尔值：被单击的提交字段的值将是True，未被单击的值则是False
@app.route('/two-submits', methods=['GET', 'POST'])
def two_submits():
    form = NewPostForm()
    if form.validate_on_submit():
        if form.save.data: # 保存按钮被点击
            # save it...
            flash('You click the "Save" button!')
        elif form.publish.data: # 发布按钮被点击
            # publish it...
            flash('You click the "Publish" button!')
        return redirect(url_for('index'))
    return render_template('2submit.html', form=form)

@app.route('/multi-form', methods=['GET', 'POST'])
def multi_form():
    signin_form = SigninForm()
    register_form = RegisterForm()

    if signin_form.submit1.data and signin_form.validate():
        username = signin_form.username.data
        flash('%s, you just submit the Signin Form.' % username)
        return redirect(url_for('index'))

    if register_form.submit2.data and register_form.validate():
        username = register_form.username.data
        flash('%s, you just submit the Register Form.' % username)
        return redirect(url_for('index'))

    return render_template('2form.html', signin_form=signin_form, register_form=register_form)

if __name__ == '__main__':
    app.run(debug = app.config['DEBUG'],
            host = app.config['HOST'],
            port = app.config['PORT'])