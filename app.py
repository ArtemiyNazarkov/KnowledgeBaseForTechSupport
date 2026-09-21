import os
import re
from datetime import datetime

from flask import Flask, redirect, url_for, render_template, request, g, flash, session, jsonify
from flask_login import logout_user, login_required, login_user, LoginManager, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from forms import LoginForm, AddUserForm, EditUserForm, AddStandardAnswerForm, EditStandardAnswerForm, AddContactForm, \
    EditContactForm, EditSQLRequestForm, AddSQLRequestForm, AddLoaderTemplateForm, EditLoaderTemplateForm, \
    EditUsefulLinkForm, AddUsefulLinkForm, AddReferenceDocumentForm, EditReferenceDocumentForm, AddSystemForm, \
    EditSystemForm, EditModuleForm, AddModuleForm, EditApplicationForm, AddApplicationForm, AddModuleApplicationForm, \
    EditModuleApplicationForm, AddBidForm, EditBidForm


def clean_filename(filename):
    filename = re.sub(r'[^а-яА-Яa-zA-Z0-9_. ()—-]', '', filename)
    return filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ISPETOREKS.db'
app.config['WTF_CSRF_ENABLED'] = False
os.environ['FLASK_ENV'] = 'production'
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32).hex())
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
UPLOAD_FOLDER_1 = 'static/Uploaded_Files/Loader_Template_Files'
UPLOAD_FOLDER_2 = 'static/Uploaded_Files/Reference_Document_Files'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'


# csrf = CSRFProtect()
# csrf.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    fio = db.Column(db.String)
    hashed_password = db.Column(db.String, nullable=False)
    isAdmin = db.Column(db.Boolean, nullable=False)
    bids = db.relationship('Bid', backref='user')


class System(db.Model):
    __tablename__ = 'Systems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naimenovanie_sistemy = db.Column(db.String, nullable=False, unique=True)
    modules = db.relationship('Module', backref='system')
    bids = db.relationship('Bid', backref='system')


class Module(db.Model):
    __tablename__ = 'Modules'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naimenovanie_modulya = db.Column(db.String, nullable=False, unique=True)
    kod_sistemy = db.Column(db.Integer, db.ForeignKey('Systems.id'))
    module_applications = db.relationship('ModuleApplication', backref='module')
    bids = db.relationship('Bid', backref='module')


class Application(db.Model):
    __tablename__ = 'Applications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naimenovanie_prilozheniya = db.Column(db.String, nullable=False, unique=True)
    module_applications = db.relationship('ModuleApplication', backref='application')
    bids = db.relationship('Bid', backref='application')


class ModuleApplication(db.Model):
    __tablename__ = 'ModuleApplications'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kod_modulya = db.Column(db.Integer, db.ForeignKey('Modules.id'))
    kod_prilozheniya = db.Column(db.Integer, db.ForeignKey('Applications.id'))


class Bid(db.Model):
    __tablename__ = 'Bids'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kod_sistemy = db.Column(db.Integer, db.ForeignKey('Systems.id'))
    kod_modulya = db.Column(db.Integer, db.ForeignKey('Modules.id'))
    kod_prilozheniya = db.Column(db.Integer, db.ForeignKey('Applications.id'))
    kod_polzovatelya = db.Column(db.Integer, db.ForeignKey('Users.id'))
    opisanie = db.Column(db.Text)
    reshenie = db.Column(db.Text)
    data_sozdaniya = db.Column(db.Date, default=datetime.now, nullable=False)


class StandardAnswer(db.Model):
    __tablename__ = 'StandardAnswers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naimenovanie_st_otveta = db.Column(db.String)
    standardnyi_otvet = db.Column(db.Text, nullable=False)


class Contact(db.Model):
    __tablename__ = 'Contacts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    kontakt = db.Column(db.Text, nullable=False)


class SQLRequest(db.Model):
    __tablename__ = 'SQLRequests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    zapros = db.Column(db.Text, nullable=False)
    opisanie = db.Column(db.Text)


class UsefulLink(db.Model):
    __tablename__ = 'UsefulLinks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poleznaya_ssilka = db.Column(db.String, nullable=False)


class LoaderTemplate(db.Model):
    __tablename__ = 'LoaderTemplates'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    shablon_path = db.Column(db.String, nullable=False)
    opisanie = db.Column(db.Text)


class ReferenceDocument(db.Model):
    __tablename__ = 'ReferenceDocuments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spravochniy_dokument = db.Column(db.String)
    path_spravochnogo_dokumenta = db.Column(db.String, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.hashed_password, password):
                login_user(user)
                session.pop('_flashes', None)
                return redirect(url_for('home'))
            else:
                flash('Неверное имя пользователя или пароль.', 'warning')
    return render_template('login.html', form=form, title="Вход в систему")


@app.route('/logout')
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))
@app.before_request
def before_request():
    if not hasattr(g, 'breadcrumbs'):
        g.breadcrumbs = [{'url': url_for('home'), 'name': 'Главная'}]
def add_breadcrumb(route, name=None, table=None, **url_args):
    if table:
        g.breadcrumbs.append({'url': url_for(table['route']), 'name': table['name']})
    g.breadcrumbs.append({'url': url_for(route, **url_args), 'name': name or g.title})


@app.route('/tab_users')
@login_required
def tab_users():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            users = User.query.order_by(User.id.asc())
            next_order = 'desc'
        else:
            users = User.query.order_by(User.id.desc())
            next_order = 'asc'
    elif sort_by == 'username':
        if order == 'asc':
            users = User.query.order_by(User.username.asc())
            next_order = 'desc'
        else:
            users = User.query.order_by(User.username.desc())
            next_order = 'asc'
    elif sort_by == 'fio':
        if order == 'asc':
            users = User.query.order_by(User.username.asc())
            next_order = 'desc'
        else:
            users = User.query.order_by(User.username.desc())
            next_order = 'asc'
    elif sort_by == 'isAdmin':
        if order == 'asc':
            users = User.query.order_by(User.username.asc())
            next_order = 'desc'
        else:
            users = User.query.order_by(User.username.desc())
            next_order = 'asc'

    users = users.all()
    g.title = "Доступ к ИС ПЭ АЭС ТОРЭКС"
    add_breadcrumb('tab_users')
    return render_template('Users/tab_users.html', users=users, title=g.title, sort_by=sort_by,
                           order=next_order)


@app.route('/tab_users/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUserForm()
    g.title = "Добавление пользователя"
    add_breadcrumb('add_user', table={'route': 'tab_users', 'name': 'Доступ к ИС ПЭ АЭС ТОРЭКС'})
    if current_user.isAdmin:
        if form.validate_on_submit():
            username = form.username.data
            fio = form.fio.data
            password = form.password.data
            hashed_password = generate_password_hash(password)
            isAdmin = form.isAdmin.data
            if username and password:
                user = User(username=username, fio=fio, hashed_password=hashed_password, isAdmin=isAdmin)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('tab_users'))
        return render_template('Users/add_user.html', form=form, title=g.title)
    else:
        flash('Вы не администратор!', 'danger')
        return redirect(url_for('tab_users'))


@app.route('/tab_users/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = User.query.get(id)
    form = EditUserForm(original_username=user.username, obj=user)
    g.title = "Редактирование пользователя"
    add_breadcrumb('edit_user', table={'route': 'tab_users', 'name': 'Доступ к ИС ПЭ АЭС ТОРЭКС'}, id=id)
    if current_user.isAdmin:
        if form.validate_on_submit():
            user.username = form.username.data
            user.fio = form.fio.data
            password = form.password.data
            if password:
                hashed_password = generate_password_hash(password)
                user.hashed_password = hashed_password
            user.isAdmin = form.isAdmin.data
            db.session.commit()
            return redirect(url_for('tab_users'))
        return render_template('Users/edit_user.html', form=form, user=user, title=g.title)
    else:
        flash('Вы не администратор!', 'danger')
        return redirect(url_for('tab_users'))


@app.route('/tab_users/delete_user/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.isAdmin:
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
    else:
        flash('Вы не администратор!', 'danger')
    return redirect(url_for('tab_users'))


@app.route('/tab_standard_answers')
@login_required
def tab_standard_answers():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.id.asc())
            next_order = 'desc'
        else:
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.id.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_st_otveta':
        if order == 'asc':
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.naimenovanie_st_otveta.asc())
            next_order = 'desc'
        else:
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.naimenovanie_st_otveta.desc())
            next_order = 'asc'
    elif sort_by == 'standardnyi_otvet':
        if order == 'asc':
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.standardnyi_otvet.asc())
            next_order = 'desc'
        else:
            standard_answers = StandardAnswer.query.order_by(StandardAnswer.standardnyi_otvet.desc())
            next_order = 'asc'

    standard_answers = standard_answers.all()
    g.title = "Стандартные ответы"
    add_breadcrumb('tab_standard_answers')
    return render_template('StandardAnswers/tab_standard_answers.html', standard_answers=standard_answers,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_standard_answers/add_standard_answer', methods=['GET', 'POST'])
@login_required
def add_standard_answer():
    form = AddStandardAnswerForm()
    g.title = "Добавление стандартного ответа"
    add_breadcrumb('add_standard_answer', table={'route': 'tab_standard_answers', 'name': 'Стандартные ответы'})
    if form.validate_on_submit():
        naimenovanie_st_otveta = form.naimenovanie_st_otveta.data
        standardnyi_otvet = request.form.get('standardnyi_otvet')
        standard_answer = StandardAnswer(naimenovanie_st_otveta=naimenovanie_st_otveta,
                                         standardnyi_otvet=standardnyi_otvet)
        db.session.add(standard_answer)
        db.session.commit()
        return redirect(url_for('tab_standard_answers'))
    return render_template('StandardAnswers/add_standard_answer.html', form=form, title=g.title)


@app.route('/tab_standard_answers/edit_standard_answer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_standard_answer(id):
    standard_answer = StandardAnswer.query.get(id)
    form = EditStandardAnswerForm(obj=standard_answer)
    g.title = "Редактирование пользователя"
    add_breadcrumb('edit_standard_answer', table={'route': 'tab_standard_answers', 'name': 'Стандартные ответы'}, id=id)
    if form.validate_on_submit():
        standard_answer.naimenovanie_st_otveta = form.naimenovanie_st_otveta.data
        standard_answer.standardnyi_otvet = request.form.get('standardnyi_otvet')
        db.session.commit()
        return redirect(url_for('tab_standard_answers'))
    return render_template('StandardAnswers/edit_standard_answer.html', form=form, standard_answer=standard_answer,
                           title=g.title)


@app.route('/tab_standard_answers/delete_standard_answer/<int:id>', methods=['POST'])
@login_required
def delete_standard_answer(id):
    standard_answer = StandardAnswer.query.get(id)
    db.session.delete(standard_answer)
    db.session.commit()
    return redirect(url_for('tab_standard_answers'))


@app.route('/tab_contacts')
@login_required
def tab_contacts():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            contacts = Contact.query.order_by(Contact.id.asc())
            next_order = 'desc'
        else:
            contacts = Contact.query.order_by(Contact.id.desc())
            next_order = 'asc'
    elif sort_by == 'kontakt':
        if order == 'asc':
            contacts = Contact.query.order_by(Contact.kontakt.asc())
            next_order = 'desc'
        else:
            contacts = Contact.query.order_by(Contact.kontakt.desc())
            next_order = 'asc'

    contacts = contacts.all()
    g.title = "Контакты"
    add_breadcrumb('tab_contacts')
    return render_template('Contacts/tab_contacts.html', contacts=contacts,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_contacts/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    form = AddContactForm()
    g.title = "Добавление контакта"
    add_breadcrumb('add_contact', table={'route': 'tab_contacts', 'name': 'Контакты'})
    if form.validate_on_submit():
        kontakt = form.kontakt.data
        contact = Contact(kontakt=kontakt)
        db.session.add(contact)
        db.session.commit()
        return redirect(url_for('tab_contacts'))
    return render_template('Contacts/add_contact.html', form=form, title=g.title)


@app.route('/tab_contacts/edit_contact/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.get(id)
    form = EditContactForm(obj=contact)
    g.title = "Редактирование контакта"
    add_breadcrumb('edit_contact', table={'route': 'tab_contacts', 'name': 'Контакты'}, id=id)
    if form.validate_on_submit():
        contact.kontakt = form.kontakt.data
        db.session.commit()
        return redirect(url_for('tab_contacts'))
    return render_template('Contacts/edit_contact.html', form=form, contact=contact,
                           title=g.title)


@app.route('/tab_contacts/delete_contact/<int:id>', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.get(id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('tab_contacts'))


@app.route('/tab_sql_requests')
@login_required
def tab_sql_requests():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            sql_requests = SQLRequest.query.order_by(SQLRequest.id.asc())
            next_order = 'desc'
        else:
            sql_requests = SQLRequest.query.order_by(SQLRequest.id.desc())
            next_order = 'asc'
    elif sort_by == 'zapros':
        if order == 'asc':
            sql_requests = SQLRequest.query.order_by(SQLRequest.zapros.asc())
            next_order = 'desc'
        else:
            sql_requests = SQLRequest.query.order_by(SQLRequest.zapros.desc())
            next_order = 'asc'
    elif sort_by == 'opisanie':
        if order == 'asc':
            sql_requests = SQLRequest.query.order_by(SQLRequest.opisanie.asc())
            next_order = 'desc'
        else:
            sql_requests = SQLRequest.query.order_by(SQLRequest.opisanie.desc())
            next_order = 'asc'

    sql_requests = sql_requests.all()
    g.title = "SQL запросы"
    add_breadcrumb('tab_sql_requests')
    return render_template('SQLRequests/tab_sql_requests.html', sql_requests=sql_requests,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_sql_requests/add_sql_request', methods=['GET', 'POST'])
@login_required
def add_sql_request():
    form = AddSQLRequestForm()
    g.title = "Добавление SQL запроса"
    add_breadcrumb('add_sql_request', table={'route': 'tab_sql_requests', 'name': 'SQL запросы'})
    if form.validate_on_submit():
        zapros = form.zapros.data
        opisanie = form.opisanie.data
        sql_request = SQLRequest(zapros=zapros,
                                 opisanie=opisanie)
        db.session.add(sql_request)
        db.session.commit()
        return redirect(url_for('tab_sql_requests'))
    return render_template('SQLRequests/add_sql_request.html', form=form, title=g.title)


@app.route('/tab_sql_requests/edit_sql_request/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_sql_request(id):
    sql_request = SQLRequest.query.get(id)
    form = EditSQLRequestForm(obj=sql_request)
    g.title = "Редактирование SQL запроса"
    add_breadcrumb('edit_sql_request', table={'route': 'tab_sql_requests', 'name': 'SQL запросы'}, id=id)
    if form.validate_on_submit():
        sql_request.zapros = form.zapros.data
        sql_request.opisanie = form.opisanie.data
        db.session.commit()
        return redirect(url_for('tab_sql_requests'))
    return render_template('SQLRequests/edit_sql_request.html', form=form, sql_request=sql_request,
                           title=g.title)


@app.route('/tab_sql_requests/delete_sql_request/<int:id>', methods=['POST'])
@login_required
def delete_sql_request(id):
    sql_request = SQLRequest.query.get(id)
    db.session.delete(sql_request)
    db.session.commit()
    return redirect(url_for('tab_sql_requests'))


@app.route('/tab_useful_links')
@login_required
def tab_useful_links():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            useful_links = UsefulLink.query.order_by(UsefulLink.id.asc())
            next_order = 'desc'
        else:
            useful_links = UsefulLink.query.order_by(UsefulLink.id.desc())
            next_order = 'asc'
    elif sort_by == 'poleznaya_ssilka':
        if order == 'asc':
            useful_links = UsefulLink.query.order_by(UsefulLink.poleznaya_ssilka.asc())
            next_order = 'desc'
        else:
            useful_links = UsefulLink.query.order_by(UsefulLink.poleznaya_ssilka.desc())
            next_order = 'asc'

    useful_links = useful_links.all()
    g.title = "Полезные ссылки"
    add_breadcrumb('tab_useful_links')
    return render_template('UsefulLinks/tab_useful_links.html', useful_links=useful_links,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_useful_links/add_useful_link', methods=['GET', 'POST'])
@login_required
def add_useful_link():
    form = AddUsefulLinkForm()
    g.title = "Добавление полезной ссылки"
    add_breadcrumb('add_useful_link', table={'route': 'tab_useful_links', 'name': 'Полезные ссылки'})
    if form.validate_on_submit():
        poleznaya_ssilka = form.poleznaya_ssilka.data
        useful_link = UsefulLink(poleznaya_ssilka=poleznaya_ssilka)
        db.session.add(useful_link)
        db.session.commit()
        return redirect(url_for('tab_useful_links'))
    return render_template('UsefulLinks/add_useful_link.html', form=form, title=g.title)


@app.route('/tab_useful_links/edit_useful_link/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_useful_link(id):
    useful_link = UsefulLink.query.get(id)
    form = EditUsefulLinkForm(obj=useful_link)
    g.title = "Редактирование полезной ссылки"
    add_breadcrumb('edit_useful_link', table={'route': 'tab_useful_links', 'name': 'Полезные ссылки'}, id=id)
    if form.validate_on_submit():
        useful_link.poleznaya_ssilka = form.poleznaya_ssilka.data
        db.session.commit()
        return redirect(url_for('tab_useful_links'))
    return render_template('UsefulLinks/edit_useful_link.html', form=form, useful_link=useful_link,
                           title=g.title)


@app.route('/tab_useful_links/delete_useful_link/<int:id>', methods=['POST'])
@login_required
def delete_useful_link(id):
    useful_link = UsefulLink.query.get(id)
    db.session.delete(useful_link)
    db.session.commit()
    return redirect(url_for('tab_useful_links'))


@app.route('/tab_loader_templates')
@login_required
def tab_loader_templates():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.id.asc())
            next_order = 'desc'
        else:
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.id.desc())
            next_order = 'asc'
    elif sort_by == 'shablon_path':
        if order == 'asc':
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.shablon_path.asc())
            next_order = 'desc'
        else:
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.shablon_path.desc())
            next_order = 'asc'
    elif sort_by == 'opisanie':
        if order == 'asc':
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.opisanie.asc())
            next_order = 'desc'
        else:
            loader_templates = LoaderTemplate.query.order_by(LoaderTemplate.opisanie.desc())
            next_order = 'asc'

    loader_templates = loader_templates.all()
    g.title = "Шаблоны для Loader'а"
    add_breadcrumb('tab_loader_templates')
    return render_template('LoaderTemplates/tab_loader_templates.html', loader_templates=loader_templates,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_loader_templates/add_loader_template', methods=['GET', 'POST'])
@login_required
def add_loader_template():
    form = AddLoaderTemplateForm()
    g.title = "Добавление шаблона для Loader`а"
    add_breadcrumb('add_loader_template', table={'route': 'tab_loader_templates', 'name': 'Шаблоны для Loaderа'})
    if form.validate_on_submit():
        if form.shablon_path.data:
            file = form.shablon_path.data
            filename = clean_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER_1, filename))
        loader_template = LoaderTemplate(shablon_path=filename, opisanie=form.opisanie.data)

        db.session.add(loader_template)
        db.session.commit()
        return redirect(url_for('tab_loader_templates'))
    return render_template('LoaderTemplates/add_loader_template.html', form=form, title=g.title)


@app.route('/tab_loader_templates/edit_loader_template/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_loader_template(id):
    loader_template = LoaderTemplate.query.get(id)
    form = EditLoaderTemplateForm(obj=loader_template)
    g.title = "Редактирование шаблона для Loader`а"
    add_breadcrumb('edit_loader_template', table={'route': 'tab_loader_templates', 'name': 'Шаблоны для Loaderа'}, id=id)
    if form.validate_on_submit():
        if form.shablon_path.data:
            file = form.shablon_path.data
            filename = clean_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER_1, filename))
        loader_template.opisanie = form.opisanie.data
        loader_template = LoaderTemplate(shablon_path=filename, opisanie=form.opisanie.data)
        db.session.commit()
        return redirect(url_for('tab_loader_templates'))
    return render_template('LoaderTemplates/edit_loader_template.html', form=form, loader_template=loader_template,
                           title=g.title)


@app.route('/tab_loader_templates/delete_loader_template/<int:id>', methods=['POST'])
@login_required
def delete_loader_template(id):
    loader_template = LoaderTemplate.query.get(id)
    if loader_template.shablon_path:
        file_path = os.path.join(UPLOAD_FOLDER_1, loader_template.shablon_path)
        if os.path.isfile(file_path):
            os.remove(file_path)
    db.session.delete(loader_template)
    db.session.commit()
    return redirect(url_for('tab_loader_templates'))


@app.route('/tab_reference_documents')
@login_required
def tab_reference_documents():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.id.asc())
            next_order = 'desc'
        else:
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.id.desc())
            next_order = 'asc'
    elif sort_by == 'path_spravochnogo_dokumenta':
        if order == 'asc':
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.path_spravochnogo_dokumenta.asc())
            next_order = 'desc'
        else:
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.path_spravochnogo_dokumenta.desc())
            next_order = 'asc'
    elif sort_by == 'spravochniy_dokument':
        if order == 'asc':
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.spravochniy_dokument.asc())
            next_order = 'desc'
        else:
            reference_documents = ReferenceDocument.query.order_by(ReferenceDocument.spravochniy_dokument.desc())
            next_order = 'asc'

    reference_documents = reference_documents.all()
    g.title = "Справочные документы"
    add_breadcrumb('tab_reference_documents')
    return render_template('ReferenceDocuments/tab_reference_documents.html', reference_documents=reference_documents,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_reference_documents/add_reference_document', methods=['GET', 'POST'])
@login_required
def add_reference_document():
    form = AddReferenceDocumentForm()
    g.title = "Добавление справочного документа"
    add_breadcrumb('add_reference_document', table={'route': 'tab_reference_documents', 'name': 'Справочные документы'})
    if form.validate_on_submit():
        if form.path_spravochnogo_dokumenta.data:
            file = form.path_spravochnogo_dokumenta.data
            filename = clean_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER_2, filename))
        reference_document = ReferenceDocument(path_spravochnogo_dokumenta=filename,
                                               spravochniy_dokument=form.spravochniy_dokument.data)

        db.session.add(reference_document)
        db.session.commit()
        return redirect(url_for('tab_reference_documents'))
    return render_template('ReferenceDocuments/add_reference_document.html', form=form, title=g.title)


@app.route('/tab_reference_documents/edit_reference_document/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reference_document(id):
    reference_document = ReferenceDocument.query.get(id)
    form = EditReferenceDocumentForm(obj=reference_document)
    g.title = "Редактирование справочного документа"
    add_breadcrumb('edit_reference_document', table={'route': 'tab_reference_documents', 'name': 'Справочные документы'}, id=id)
    if form.validate_on_submit():
        if form.path_spravochnogo_dokumenta.data:
            file = form.path_spravochnogo_dokumenta.data
            filename = clean_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER_2, filename))
        reference_document.spravochniy_dokument = form.spravochniy_dokument.data
        reference_document = ReferenceDocument(path_spravochnogo_dokumenta=filename,
                                               spravochniy_dokument=form.spravochniy_dokument.data)
        db.session.commit()
        return redirect(url_for('tab_reference_documents'))
    return render_template('ReferenceDocuments/edit_reference_document.html', form=form,
                           reference_document=reference_document,
                           title=g.title)


@app.route('/tab_reference_documents/delete_reference_document/<int:id>', methods=['POST'])
@login_required
def delete_reference_document(id):
    reference_document = ReferenceDocument.query.get(id)
    if reference_document.path_spravochnogo_dokumenta:
        file_path = os.path.join(UPLOAD_FOLDER_2, reference_document.path_spravochnogo_dokumenta)
        if os.path.isfile(file_path):
            os.remove(file_path)
    db.session.delete(reference_document)
    db.session.commit()
    return redirect(url_for('tab_reference_documents'))


@app.route('/tab_systems')
@login_required
def tab_systems():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            systems = System.query.order_by(System.id.asc())
            next_order = 'desc'
        else:
            systems = System.query.order_by(System.id.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_sistemy':
        if order == 'asc':
            systems = System.query.order_by(System.naimenovanie_sistemy.asc())
            next_order = 'desc'
        else:
            systems = System.query.order_by(System.naimenovanie_sistemy.desc())
            next_order = 'asc'

    systems = systems.all()
    g.title = "Системы"
    add_breadcrumb('tab_systems')
    return render_template('SysModPril/Systems/tab_systems.html', systems=systems,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_systems/add_system', methods=['GET', 'POST'])
@login_required
def add_system():
    form = AddSystemForm()
    g.title = "Добавление системы"
    add_breadcrumb('add_system', table={'route': 'tab_systems', 'name': 'Системы'})
    if form.validate_on_submit():
        naimenovanie_sistemy = form.naimenovanie_sistemy.data
        system = System(naimenovanie_sistemy=naimenovanie_sistemy)
        db.session.add(system)
        db.session.commit()
        return redirect(url_for('tab_systems'))
    return render_template('SysModPril/Systems/add_system.html', form=form, title=g.title)


@app.route('/tab_systems/edit_system/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_system(id):
    system = System.query.get(id)
    form = EditSystemForm(obj=system, original_naimenovanie_sistemy=system.naimenovanie_sistemy)
    g.title = "Редактирование системы"
    add_breadcrumb('edit_system', table={'route': 'tab_systems', 'name': 'Системы'}, id=id)
    if form.validate_on_submit():
        system.naimenovanie_sistemy = form.naimenovanie_sistemy.data
        db.session.commit()
        return redirect(url_for('tab_systems'))
    return render_template('SysModPril/Systems/edit_system.html', form=form, system=system,
                           title=g.title)


@app.route('/tab_systems/delete_system/<int:id>', methods=['POST'])
@login_required
def delete_system(id):
    system = System.query.get(id)
    db.session.delete(system)
    db.session.commit()
    return redirect(url_for('tab_systems'))


@app.route('/tab_modules')
@login_required
def tab_modules():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            modules = Module.query.order_by(Module.id.asc())
            next_order = 'desc'
        else:
            modules = Module.query.order_by(Module.id.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_modulya':
        if order == 'asc':
            modules = Module.query.order_by(Module.naimenovanie_modulya.asc())
            next_order = 'desc'
        else:
            modules = Module.query.order_by(Module.naimenovanie_modulya.desc())
            next_order = 'asc'
    elif sort_by == 'kod_sistemy':
        if order == 'asc':
            modules = Module.query.order_by(Module.kod_sistemy.asc())
            next_order = 'desc'
        else:
            modules = Module.query.order_by(Module.kod_sistemy.desc())
            next_order = 'asc'
    systems = System.query.all()
    modules = modules.all()
    g.title = "Модули"
    add_breadcrumb('tab_modules')
    return render_template('SysModPril/Modules/tab_modules.html', modules=modules,
                           title=g.title, sort_by=sort_by, order=next_order, systems=systems)


@app.route('/tab_modules/add_module', methods=['GET', 'POST'])
@login_required
def add_module():
    form = AddModuleForm()
    systems = System.query.all()
    g.title = "Добавление модуля"
    add_breadcrumb('add_module', table={'route': 'tab_modules', 'name': 'Модули'})
    if form.validate_on_submit():
        naimenovanie_modulya = form.naimenovanie_modulya.data
        naimenovanie_sistemy = form.kod_sistemy.data
        system = System.query.filter_by(naimenovanie_sistemy=naimenovanie_sistemy).first()
        if system is None:
            flash('Система не определена', 'danger')
            return redirect(url_for('add_module'))
        kod_sistemy = system.id
        module = Module(naimenovanie_modulya=naimenovanie_modulya,
                        kod_sistemy=kod_sistemy)
        db.session.add(module)
        db.session.commit()
        return redirect(url_for('tab_modules'))
    return render_template('SysModPril/Modules/add_module.html', form=form, systems=systems, title=g.title)


@app.route('/tab_modules/edit_module/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_module(id):
    module = Module.query.get(id)
    form = EditModuleForm(obj=module, original_naimenovanie_modulya=module.naimenovanie_modulya)
    systems = System.query.all()
    g.title = "Редактирование модуля"
    add_breadcrumb('edit_module', table={'route': 'tab_modules', 'name': 'Модули'}, id=id)
    if request.method == 'GET':
        system = System.query.get(module.kod_sistemy)
        if system is None:
            form.kod_sistemy.data = None
        else:
            form.kod_sistemy.data = system.naimenovanie_sistemy
    if form.validate_on_submit():
        naimenovanie_modulya = form.naimenovanie_modulya.data
        naimenovanie_sistemy = form.kod_sistemy.data
        system = System.query.filter_by(naimenovanie_sistemy=naimenovanie_sistemy).first()
        if system is None:
            flash('Система не определена', 'danger')
            return redirect(url_for('edit_modules', id=id))
        kod_sistemy = system.id
        module.naimenovanie_modulya = naimenovanie_modulya
        module.kod_sistemy = kod_sistemy
        db.session.commit()
        return redirect(url_for('tab_modules'))
    return render_template('SysModPril/Modules/edit_module.html', form=form, systems=systems, module=module,
                           title=g.title)


@app.route('/tab_modules/delete_module/<int:id>', methods=['POST'])
@login_required
def delete_module(id):
    module = Module.query.get(id)
    db.session.delete(module)
    db.session.commit()
    return redirect(url_for('tab_modules'))


@app.route('/tab_applications')
@login_required
def tab_applications():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            applications = Application.query.order_by(Application.id.asc())
            next_order = 'desc'
        else:
            applications = Application.query.order_by(Application.id.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_prilozheniya':
        if order == 'asc':
            applications = Application.query.order_by(Application.naimenovanie_prilozheniya.asc())
            next_order = 'desc'
        else:
            applications = Application.query.order_by(Application.naimenovanie_prilozheniya.desc())
            next_order = 'asc'

    applications = applications.all()
    g.title = "Приложения"
    add_breadcrumb('tab_applications')
    return render_template('SysModPril/Applications/tab_applications.html', applications=applications,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_applications/add_application', methods=['GET', 'POST'])
@login_required
def add_application():
    form = AddApplicationForm()
    g.title = "Добавление приложения"
    add_breadcrumb('add_application', table={'route': 'tab_applications', 'name': 'Приложения'})
    if form.validate_on_submit():
        naimenovanie_prilozheniya = form.naimenovanie_prilozheniya.data
        application = Application(naimenovanie_prilozheniya=naimenovanie_prilozheniya)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('tab_applications'))
    return render_template('SysModPril/Applications/add_application.html', form=form, title=g.title)


@app.route('/tab_applications/edit_application/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    application = Application.query.get(id)
    form = EditApplicationForm(obj=application,
                               original_naimenovanie_prilozheniya=application.naimenovanie_prilozheniya)
    g.title = "Редактирование приложения"
    add_breadcrumb('edit_application', table={'route': 'tab_applications', 'name': 'Приложения'}, id=id)
    if form.validate_on_submit():
        application.naimenovanie_prilozheniya = form.naimenovanie_prilozheniya.data
        db.session.commit()
        return redirect(url_for('tab_applications'))
    return render_template('SysModPril/Applications/edit_application.html', form=form, application=application,
                           title=g.title)


@app.route('/tab_applications/delete_application/<int:id>', methods=['POST'])
@login_required
def delete_application(id):
    application = Application.query.get(id)
    db.session.delete(application)
    db.session.commit()
    return redirect(url_for('tab_applications'))


@app.route('/tab_module_applications')
@login_required
def tab_module_applications():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            module_applications = ModuleApplication.query.order_by(ModuleApplication.id.asc())
            next_order = 'desc'
        else:
            module_applications = ModuleApplication.query.order_by(ModuleApplication.id.desc())
            next_order = 'asc'
    elif sort_by == 'kod_modulya':
        if order == 'asc':
            module_applications = ModuleApplication.query.order_by(ModuleApplication.kod_modulya.asc())
            next_order = 'desc'
        else:
            module_applications = ModuleApplication.query.order_by(ModuleApplication.kod_modulya.desc())
            next_order = 'asc'
    elif sort_by == 'kod_prilozheniya':
        if order == 'asc':
            module_applications = ModuleApplication.query.order_by(ModuleApplication.kod_prilozheniya.asc())
            next_order = 'desc'
        else:
            module_applications = ModuleApplication.query.order_by(ModuleApplication.kod_prilozheniya.desc())
            next_order = 'asc'
    elif sort_by == 'system':
        if order == 'asc':
            module_applications = ModuleApplication.query.join(Module).join(System).order_by(
                System.naimenovanie_sistemy.asc())
            next_order = 'desc'
        else:
            module_applications = ModuleApplication.query.join(Module).join(System).order_by(
                System.naimenovanie_sistemy.desc())
            next_order = 'asc'

    module_applications = module_applications.all()
    g.title = "Связь модулей и приложений"
    add_breadcrumb('tab_module_applications')
    return render_template('SysModPril/ModuleApplications/tab_module_applications.html',
                           module_applications=module_applications,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_module_applications/add_module_application', methods=['GET', 'POST'])
@login_required
def add_module_application():
    form = AddModuleApplicationForm()
    # form.kod_modulya.choices = [(m.id, f"{m.naimenovanie_modulya} ({m.system.naimenovanie_sistemy})") if m.system else (
    # m.id, m.naimenovanie_modulya) for m in Module.query.all()]
    # form.kod_prilozheniya.choices = [(a.id, a.naimenovanie_prilozheniya) for a in Application.query.all()]
    modules = Module.query.all()
    applications = Application.query.all()
    g.title = "Добавление связи модуля и приложения"
    add_breadcrumb('add_module_application', table={'route': 'tab_module_applications', 'name': 'Связь модулей и приложений'})
    if form.validate_on_submit():
        # kod_modulya = form.kod_modulya.data
        naimenovanie_modulya = form.kod_modulya.data
        module = Module.query.filter_by(naimenovanie_modulya=naimenovanie_modulya).first()
        if module is None:
            flash('Модуль не определен', 'danger')
            return redirect(url_for('add_module_applications', id=id))
        kod_modulya = module.id
        # kod_prilozheniya = form.kod_prilozheniya.data
        naimenovanie_prilozheniya = form.kod_prilozheniya.data
        application = Application.query.filter_by(naimenovanie_prilozheniya=naimenovanie_prilozheniya).first()
        if application is None:
            flash('Приложение не определено', 'danger')
            return redirect(url_for('add_module_applications', id=id))
        kod_prilozheniya = application.id
        module_application = ModuleApplication(kod_modulya=kod_modulya, kod_prilozheniya=kod_prilozheniya)
        db.session.add(module_application)
        db.session.commit()
        return redirect(url_for('tab_module_applications'))
    return render_template('SysModPril/ModuleApplications/add_module_application.html', form=form, title=g.title,
                           modules=modules, applications=applications)


@app.route('/tab_module_applications/edit_module_application/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_module_application(id):
    module_application = ModuleApplication.query.get(id)
    form = EditModuleApplicationForm(obj=module_application)
    # form.kod_modulya.choices = [(m.id, f"{m.naimenovanie_modulya} ({m.system.naimenovanie_sistemy})") for m in Module.query.all()]
    # form.kod_prilozheniya.choices = [(a.id, a.naimenovanie_prilozheniya) for a in Application.query.all()]
    modules = Module.query.all()
    applications = Application.query.all()
    g.title = "Редактирование связи модуля и приложения"
    add_breadcrumb('edit_module_application', table={'route': 'tab_module_applications', 'name': 'Связь модулей и приложений'}, id=id)
    if request.method == 'GET':
        module = Module.query.get(module_application.kod_modulya)
        if module is None:
            form.kod_modulya.data = None
        else:
            form.kod_modulya.data = module.naimenovanie_modulya
        application = Application.query.get(module_application.kod_prilozheniya)
        if application is None:
            form.kod_prilozheniya.data = None
        else:
            form.kod_prilozheniya.data = application.naimenovanie_prilozheniya
    if form.validate_on_submit():
        # module_application.kod_modulya = form.kod_modulya.data
        naimenovanie_modulya = form.kod_modulya.data
        naimenovanie_prilozheniya = form.kod_prilozheniya.data
        module = Module.query.filter_by(naimenovanie_modulya=naimenovanie_modulya).first()
        application = Application.query.filter_by(naimenovanie_prilozheniya=naimenovanie_prilozheniya).first()
        if module is None:
            flash('Модуль не определен', 'danger')
            return redirect(url_for('edit_module_applications', id=id))
        # module_application.kod_prilozheniya = form.kod_prilozheniya.data
        if application is None:
            flash('Приложение не определено', 'danger')
            return redirect(url_for('edit_module_applications', id=id))
        kod_modulya = module.id
        kod_prilozheniya = application.id
        module_application.kod_modulya = kod_modulya
        module_application.kod_prilozheniya = kod_prilozheniya
        db.session.commit()
        return redirect(url_for('tab_module_applications'))
    return render_template('SysModPril/ModuleApplications/edit_module_application.html',
                           form=form, module_application=module_application, title=g.title,
                           modules=modules, applications=applications)


@app.route('/tab_module_applications/delete_module_application/<int:id>', methods=['POST'])
@login_required
def delete_module_application(id):
    module_application = ModuleApplication.query.get(id)
    db.session.delete(module_application)
    db.session.commit()
    return redirect(url_for('tab_module_applications'))


@app.route('/tab_bids')
@login_required
def tab_bids():
    sort_by = request.args.get('sort', 'id')  # Параметр сортировки по умолчанию - 'id'
    order = request.args.get('order', 'asc')  # Порядок сортировки по умолчанию - 'asc'
    if sort_by == 'id':
        if order == 'asc':
            bids = Bid.query.order_by(Bid.id.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.order_by(Bid.id.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_sistemy':
        if order == 'asc':
            bids = Bid.query.join(System).order_by(System.naimenovanie_sistemy.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.join(System).order_by(System.naimenovanie_sistemy.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_modulya':
        if order == 'asc':
            bids = Bid.query.join(Module).order_by(Module.naimenovanie_modulya.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.join(Module).order_by(Module.naimenovanie_modulya.desc())
            next_order = 'asc'
    elif sort_by == 'naimenovanie_prilozheniya':
        if order == 'asc':
            bids = Bid.query.join(Application).order_by(Application.naimenovanie_prilozheniya.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.join(Application).order_by(Application.naimenovanie_prilozheniya.desc())
            next_order = 'asc'
    elif sort_by == 'username':
        if order == 'asc':
            bids = Bid.query.join(User).order_by(User.username.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.join(User).order_by(User.username.desc())
            next_order = 'asc'
    elif sort_by == 'opisanie':
        if order == 'asc':
            bids = Bid.query.order_by(Bid.opisanie.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.order_by(Bid.opisanie.desc())
            next_order = 'asc'
    elif sort_by == 'reshenie':
        if order == 'asc':
            bids = Bid.query.order_by(Bid.reshenie.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.order_by(Bid.reshenie.desc())
            next_order = 'asc'
    elif sort_by == 'data_sozdaniya':
        if order == 'asc':
            bids = Bid.query.order_by(Bid.data_sozdaniya.asc())
            next_order = 'desc'
        else:
            bids = Bid.query.order_by(Bid.data_sozdaniya.desc())
            next_order = 'asc'
    bids = bids.all()
    g.title = "Заявки"
    add_breadcrumb('tab_bids')
    return render_template('Bids/tab_bids.html', bids=bids,
                           title=g.title, sort_by=sort_by, order=next_order)


@app.route('/tab_bids/add_bid', methods=['GET', 'POST'])
@login_required
def add_bid():
    form = AddBidForm()
    systems = System.query.all()
    modules = Module.query.all()
    applications = Application.query.all()
    # form.kod_sistemy.default = "Общее"
    # form.kod_modulya.default = "Интеграция"
    # form.kod_prilozheniya.default = "Прочие приложения"
    # form.process()
    g.title = "Добавление заявки"
    add_breadcrumb('add_bid', table={'route': 'tab_bids', 'name': 'Заявки'})
    if form.validate_on_submit():
        naimenovanie_sistemy = form.kod_sistemy.data
        system = System.query.filter_by(naimenovanie_sistemy=naimenovanie_sistemy).first()
        if system is None:
            flash('Система не определена', 'danger')
            return redirect(url_for('add_bid'))
        kod_sistemy = system.id
        naimenovanie_modulya = form.kod_modulya.data
        module = Module.query.filter_by(naimenovanie_modulya=naimenovanie_modulya).first()
        if module is None:
            flash('Модуль не определен', 'danger')
            return redirect(url_for('add_bid'))
        kod_modulya = module.id
        naimenovanie_prilozheniya = form.kod_prilozheniya.data
        application = Application.query.filter_by(naimenovanie_prilozheniya=naimenovanie_prilozheniya).first()
        if application is None:
            flash('Приложение не определено', 'danger')
            return redirect(url_for('add_bid'))
        kod_prilozheniya = application.id
        kod_polzovatelya = current_user.id
        opisanie = request.form.get('opisanie')
        reshenie = request.form.get('reshenie')
        bid = Bid(kod_sistemy=kod_sistemy, kod_modulya=kod_modulya,
                  kod_prilozheniya=kod_prilozheniya, kod_polzovatelya=kod_polzovatelya,
                  opisanie=opisanie, reshenie=reshenie)
        db.session.add(bid)
        db.session.commit()
        return redirect(url_for('tab_bids'))
    else:
        print(form.errors)
    return render_template('Bids/add_bid.html', form=form, title=g.title, systems=systems, modules=modules,
                           applications=applications)


@app.route('/tab_bids/edit_bid/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_bid(id):
    bid = Bid.query.get(id)
    form = EditBidForm(obj=bid)
    systems = System.query.all()
    modules = Module.query.filter_by(kod_sistemy=bid.kod_sistemy).all()
    applications = Application.query.join(ModuleApplication).join(Module).filter(Module.id == bid.kod_modulya).all()
    g.title = "Редактирование заявки"
    add_breadcrumb('edit_bid', table={'route': 'tab_bids', 'name': 'Заявки'}, id=id)
    if request.method == 'GET':
        system = System.query.get(bid.kod_sistemy)
        if system is None:
            form.kod_sistemy.data = None
        else:
            form.kod_sistemy.data = system.naimenovanie_sistemy
        module = Module.query.get(bid.kod_modulya)
        if module is None:
            form.kod_modulya.data = None
        else:
            form.kod_modulya.data = module.naimenovanie_modulya
        application = Application.query.get(bid.kod_prilozheniya)
        if application is None:
            form.kod_prilozheniya.data = None
        else:
            form.kod_prilozheniya.data = application.naimenovanie_prilozheniya
    if form.validate_on_submit():
        naimenovanie_sistemy = form.kod_sistemy.data
        system = System.query.filter_by(naimenovanie_sistemy=naimenovanie_sistemy).first()
        if system is None:
            flash('Система не определена', 'danger')
            return redirect(url_for('edit_bid', id=id))
        kod_sistemy = system.id
        bid.kod_sistemy = kod_sistemy
        naimenovanie_modulya = form.kod_modulya.data
        module = Module.query.filter_by(naimenovanie_modulya=naimenovanie_modulya).first()
        if module is None:
            flash('Модуль не определен', 'danger')
            return redirect(url_for('edit_bid', id=id))
        kod_modulya = module.id
        bid.kod_modulya = kod_modulya
        naimenovanie_prilozheniya = form.kod_prilozheniya.data
        application = Application.query.filter_by(naimenovanie_prilozheniya=naimenovanie_prilozheniya).first()
        if application is None:
            flash('Приложение не определено', 'danger')
            return redirect(url_for('edit_bid', id=id))
        kod_prilozheniya = application.id
        bid.kod_prilozheniya = kod_prilozheniya
        bid.opisanie = request.form.get('opisanie')
        bid.reshenie = request.form.get('reshenie')
        db.session.commit()
        return redirect(url_for('tab_bids'))
    return render_template('Bids/edit_bid.html',
                           form=form, bid=bid, title=g.title, systems=systems, modules=modules,
                           applications=applications)


@app.route('/tab_bids/delete_bid/<int:id>', methods=['POST'])
@login_required
def delete_bid(id):
    bid = Bid.query.get(id)
    db.session.delete(bid)
    db.session.commit()
    return redirect(url_for('tab_bids'))


@app.route('/update_module_and_app_choices', methods=['POST'])
def update_module_and_app_choices():
    selected_system_name = request.form.get('kod_sistemy')
    print('Selected system name:', selected_system_name)
    selected_system = System.query.filter_by(naimenovanie_sistemy=selected_system_name).first()
    if selected_system:
        modules = Module.query.filter_by(kod_sistemy=selected_system.id).all()
        return jsonify({
            'modules': [(module.naimenovanie_modulya) for module in modules]
        })
    return jsonify({'modules': []})


@app.route('/update_app_choices', methods=['POST'])
def update_app_choices():
    selected_module_name = request.form.get('kod_modulya')
    print('Selected module name:', selected_module_name)
    selected_module = Module.query.filter_by(naimenovanie_modulya=selected_module_name).first()
    if selected_module:
        applications = Application.query.join(ModuleApplication).join(Module).filter(
            Module.id == selected_module.id).all()
        return jsonify({
            'applications': [(application.naimenovanie_prilozheniya) for application in applications]
        })
    return jsonify({'applications': []})


@app.context_processor
def inject_record():
    if current_user.is_authenticated:
        record = StandardAnswer.query.filter(StandardAnswer.naimenovanie_st_otveta.ilike("%конфигурационная единица%")
                                             | StandardAnswer.naimenovanie_st_otveta.ilike("%КЕ%")).first()
        return {'record': record}
    return {}


@app.route('/')
def home():
    if current_user.is_authenticated:
        g.title = "База знаний ИС ПЭ АЭС ТОРЭКС"
        return render_template('home.html', title=g.title)
    else:
        return redirect(url_for('login'))


with app.app_context():
    db.create_all()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5454)
