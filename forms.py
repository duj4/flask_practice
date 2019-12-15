# 当使用WTForms创建表单时，表单由Python类表示，这个类继承从WTForms导入的Form基类: class LoginForm(Form):
# 当使用Flask-WTF定义表单时，仍然使用WTForms提供的字段和验证器，创建的方式也完全相同，只不过表单类要继承Flask-WTF提供的FlaskForm类，以便与Flask集成
# Flask-WTF会自动在实例化表单类时添加一个包含CSRF令牌值的隐藏字段csrf_token
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

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

