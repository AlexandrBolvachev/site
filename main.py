from datetime import datetime

from flask import Flask, render_template, request, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from data import db_session
from data.users import User
from data.posts import News
from data.razdel import Razdel
from data.branch import Branch
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.news import NewsForm
from forms.add import AddForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        news = db_sess.query(News)
        item = db_sess.query(Razdel)

        return render_template("index.html", news=news, item=item)

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_r():
        form = AddForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            addr = Razdel()
            addr.name = form.title.data
            addr.created_date = datetime.now()
            addr.user_id = current_user.id
            addr.status = 'True'
            db_sess.add(addr)
            db_sess.commit()
            return redirect('/')
        return render_template('add.html', title='Добавление', form=form)

    @app.route('/add/<int:r_id>', methods=['GET', 'POST'])
    @login_required
    def add_b(r_id):
        form = AddForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            addb = Branch()
            addb.name = form.title.data
            addb.created_date = datetime.now()
            addb.user_id = current_user.id
            addb.razdel_id = r_id
            addb.status = 'True'
            db_sess.add(addb)
            db_sess.commit()
            return redirect(f'/razdel/{r_id}')
        return render_template('add.html', title='Добавление', form=form)


    @app.route('/razdel/<int:id>', methods=['GET', 'POST'])
    def branch(id):
        db_sess = db_session.create_session()
        branch = db_sess.query(Branch).filter(Razdel.id == Branch.razdel_id, Razdel.id == id)
        razdel_name = db_sess.query(Razdel).filter(Razdel.id == id).first()

        return render_template("branch.html", branch=branch, r_id=id, r_n=razdel_name)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html', message="Неправильный логин или пароль", form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/razdel/<int:r_id>/branch/<int:b_id>', methods=['GET', 'POST'])
    def posts(r_id, b_id):
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.branch_id == b_id)
        branch = db_sess.query(Branch).filter(Branch.id == b_id).first()
        razdel_name = db_sess.query(Razdel).filter(Razdel.id == r_id).first()
        return render_template('posts.html', news=news, r_n=razdel_name, b_n=branch)

    @app.route('/newsadd/<int:id>', methods=['GET', 'POST'])
    @login_required
    def add_news(id):
        form = NewsForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            b = db_sess.query(Branch).filter(Branch.id == id).first()
            news = News()
            news.title = form.title.data
            news.content = form.content.data
            news.created_date = datetime.now()
            news.user_id = current_user.id
            news.branch_id = id
            news.razdel_id = b.razdel_id

            current_user.news.append(news)
            db_sess.merge(current_user)
            db_sess.commit()
            branch = db_sess.query(Branch).filter(Branch.id == id).first()
            return redirect(f'/razdel/{branch.razdel_id}/branch/{branch.id}')
        return render_template('news.html', title='Добавление новости', form=form)


    @app.route('/news/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_news(id):
        form = NewsForm()
        if request.method == "GET":
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
            if news:
                form.title.data = news.title
                form.content.data = news.content
            else:
                abort(404)
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
            if news:
                news.title = form.title.data
                news.content = form.content.data
                db_sess.commit()
                branch = db_sess.query(Branch).filter(Branch.id == id).first()
                return redirect(f'/razdel/{branch.razdel_id}/branch/{branch.id}')
            else:
                abort(404)
        return render_template('news.html', title='Редактирование новости', form=form)

    @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def delete_news(id):
        db_sess = db_session.create_session()

        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()
        if news:
            db_sess.delete(news)
            db_sess.commit()
        else:
            abort(404)
        branch = db_sess.query(Branch).filter(Branch.id == id).first()
        return redirect(f'/razdel/{branch.razdel_id}/branch/{branch.id}')

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    app.run()


if __name__ == '__main__':
    main()
