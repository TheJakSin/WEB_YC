from flask import Flask, render_template, redirect
from data import db_session
from flask_login import LoginManager, login_user, login_manager, login_required, logout_user, current_user

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired

from data.users import User
from data.shop import Shop
from forms.user import RegisterForm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/cart')
def cart():
    if current_user.is_authenticated:
        user_id = current_user.id
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        user_bag = user.bag.split(';') if user.bag else []

        return render_template('cart.html', user_bag=user_bag)
    else:
        return "Пожалуйста, войдите на сайт, чтобы просмотреть корзину."


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_to_cart/<int:id>')
def add(id):
    if current_user.is_authenticated:
        user_id = current_user.id
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        user.bag = user.bag.split(';') if user.bag else ''
        user.bag = user.bag + f' {id};'
        db_sess.commit()

        return redirect("/")
    else:
        return "Пожалуйста, войдите на сайт, чтобы просмотреть корзину."


@app.route('/')
def index():
    db_sess = db_session.create_session()
    shop_items = db_sess.query(Shop).all()
    global shop_data
    shop_data = [[item.id, item.title, item.info.split(';'), item.type, item.price] for item in shop_items]
    return render_template('base.html', shop=shop_data)


def main():
    db_session.global_init("db/main.sqlite")
    app.run()


if __name__ == '__main__':
    main()
