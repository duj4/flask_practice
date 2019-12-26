# 当使用WTForms创建表单时，表单由Python类表示，这个类继承从WTForms导入的Form基类: class LoginForm(Form):
# 当使用Flask-WTF定义表单时，仍然使用WTForms提供的字段和验证器，创建的方式也完全相同，只不过表单类要继承Flask-WTF提供的FlaskForm类，以便与Flask集成
# Flask-WTF会自动在实例化表单类时添加一个包含CSRF令牌值的隐藏字段csrf_token
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import Form, StringField, PasswordField, BooleanField, IntegerField, SubmitField, MultipleFileField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Email
from flask_ckeditor import CKEditorField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')

# 行内验证器，在表单类中定义方法来进行验证
class FortyTwoForm(FlaskForm):
    answer = IntegerField('The Number')
    submit = SubmitField()

    # 当表单类中以“validate_字段属性名”进行命名方法时，在验证字段数据时会同时调用这个方法来验证对应的字段
    def validate_answer(form, field):
        if field.data != 42:
            raise ValidationError('Must be 42!')

# 使用Flask-WTF的FileField类，它继承了WTForms提供的上传字段FileField，添加了对Flask的集成
class UploadForm(FlaskForm):
    # FileRequired()确保提交的表单字段中包含文件数据
    # FileAllowed()设置允许的文件类型，传入一个包含允许文件类型的后缀名列表
    photo = FileField('Upload Image', validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    submit = SubmitField()

# 多文件上传可以直接使用WTForms提供的MultipleFileField字段
class MultiUploadForm(FlaskForm):
    photo = MultipleFileField('Upload Image', validators=[DataRequired()])
    submit = SubmitField()

# 富文本编辑器在HTML中通过文本区域字段表示，即<textarea></textarea>
# Flask-CKEditor通过包装WTForms提供的TextAreaField字段类型实现了一个CKEditorField字段类
class RichTextForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1,50)])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Publish')

# 包含两个提交按钮的表单
class NewPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1,50)])
    body = TextAreaField('Body', validators=[DataRequired()])
    save = SubmitField('Save') # 保存按钮
    publish = SubmitField('Publish') # 提交按钮

# 多表单-单视图
# 登录
class SigninForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit1 = SubmitField('Sign in')
# 注册
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1,20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1,254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit2 = SubmitField('Register')

# 多表单-多试图
class SigninForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()

class RegisterForm2(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 24)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    submit = SubmitField()

# subscribe form
class SubscribeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Subscribe')