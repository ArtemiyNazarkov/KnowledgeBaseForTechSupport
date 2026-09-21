from flask import flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Войти")


class AddUserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(max=64)])
    fio = StringField('ФИО', validators=[Length(max=128)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    isAdmin = BooleanField('Администратор')
    submit = SubmitField('Сохранить')

    def validate_username(self, field):
        from app import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(flash('Пользователь уже существует', 'danger'))


class EditUserForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(max=64)])
    fio = StringField('ФИО', validators=[Length(max=128)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])
    isAdmin = BooleanField('Администратор')
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, field):
        from app import User
        if field.data != self.original_username:
            if User.query.filter_by(username=self.username.data).first():
                raise ValidationError(flash('Пользователь уже существует', 'danger'))



class AddStandardAnswerForm(FlaskForm):
    naimenovanie_st_otveta = StringField('Тема стандартного ответа')
    standardnyi_otvet = TextAreaField('Стандартный ответ', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class EditStandardAnswerForm(FlaskForm):
    naimenovanie_st_otveta = StringField('Тема стандартного ответа')
    standardnyi_otvet = TextAreaField('Стандартный ответ', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddContactForm(FlaskForm):
    kontakt = TextAreaField('Контакт', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class EditContactForm(FlaskForm):
    kontakt = TextAreaField('Контакт', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddSQLRequestForm(FlaskForm):
    zapros = TextAreaField('SQL запрос', validators=[DataRequired()])
    opisanie = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class EditSQLRequestForm(FlaskForm):
    zapros = TextAreaField('SQL запрос', validators=[DataRequired()])
    opisanie = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class AddLoaderTemplateForm(FlaskForm):
    shablon_path = FileField('Шаблон для Loader`а', validators=[DataRequired(), FileAllowed(['xls', 'xlsx', 'ods'],
                                                                                            'Вы можете загрузить только электронные таблицы!')])
    opisanie = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class EditLoaderTemplateForm(FlaskForm):
    shablon_path = FileField('Шаблон для Loader`а', validators=[DataRequired(), FileAllowed(['xls', 'xlsx', 'ods'],
                                                                                            'Вы можете загрузить только электронные таблицы!')])
    opisanie = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class AddUsefulLinkForm(FlaskForm):
    poleznaya_ssilka = TextAreaField('Полезная ссылка', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class EditUsefulLinkForm(FlaskForm):
    poleznaya_ssilka = TextAreaField('Полезная ссылка', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddReferenceDocumentForm(FlaskForm):
    path_spravochnogo_dokumenta = FileField('Справочный документ', validators=[DataRequired(), FileAllowed(
        ['xls', 'xlsx', 'odt', 'doc', 'docx', 'pdf'],
        'Вы можете загрузить только электронные таблицы, документы Word и PDF!')])
    spravochniy_dokument = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class EditReferenceDocumentForm(FlaskForm):
    path_spravochnogo_dokumenta = FileField('Справочный документ', validators=[DataRequired(), FileAllowed(
        ['xls', 'xlsx', 'ods', 'odt', 'doc', 'docx', 'pdf'],
        'Вы можете загрузить только электронные таблицы, документы Word и PDF!')])
    spravochniy_dokument = TextAreaField('Описание')
    submit = SubmitField('Сохранить')


class AddSystemForm(FlaskForm):
    naimenovanie_sistemy = StringField('Система', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def validate_naimenovanie_sistemy(self, field):
        from app import System
        if System.query.filter_by(naimenovanie_sistemy=field.data).first():
            raise ValidationError(flash('Система уже существует', 'danger'))


class EditSystemForm(FlaskForm):
    naimenovanie_sistemy = StringField('Система', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, original_naimenovanie_sistemy, *args, **kwargs):
        super(EditSystemForm, self).__init__(*args, **kwargs)
        self.original_naimenovanie_sistemy = original_naimenovanie_sistemy

    def validate_naimenovanie_sistemy(self, field):
        from app import System
        if field.data != self.original_naimenovanie_sistemy:
            if System.query.filter_by(naimenovanie_sistemy=field.data).first():
                raise ValidationError(flash('Система уже существует', 'danger'))


# class AddModuleForm(FlaskForm):
#     naimenovanie_modulya = StringField('Модуль', validators=[DataRequired()])
#     kod_sistemy = SelectField('Система', choices=[])
#     submit = SubmitField('Сохранить')
class AddModuleForm(FlaskForm):
    naimenovanie_modulya = StringField('Модуль', validators=[DataRequired()])
    kod_sistemy = StringField('Система')
    submit = SubmitField('Сохранить')

    def validate_naimenovanie_modulya(self, field):
        from app import Module
        if Module.query.filter_by(naimenovanie_modulya=field.data).first():
            raise ValidationError(flash('Модуль уже существует', 'danger'))


class EditModuleForm(FlaskForm):
    naimenovanie_modulya = StringField('Модуль', validators=[DataRequired()])
    kod_sistemy = StringField('Система')
    submit = SubmitField('Сохранить')

    def __init__(self, original_naimenovanie_modulya, *args, **kwargs):
        super(EditModuleForm, self).__init__(*args, **kwargs)
        self.original_naimenovanie_modulya = original_naimenovanie_modulya

    def validate_naimenovanie_modulya(self, field):
        from app import Module
        if field.data != self.original_naimenovanie_modulya:
            if Module.query.filter_by(naimenovanie_modulya=field.data).first():
                raise ValidationError(flash('Модуль уже существует', 'danger'))



class AddApplicationForm(FlaskForm):
    naimenovanie_prilozheniya = StringField('Приложение', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def validate_naimenovanie_prilozheniya(self, field):
        from app import Application
        if Application.query.filter_by(naimenovanie_prilozheniya=field.data).first():
            raise ValidationError(flash('Приложение уже существует', 'danger'))


class EditApplicationForm(FlaskForm):
    naimenovanie_prilozheniya = StringField('Приложение', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

    def __init__(self, original_naimenovanie_prilozheniya, *args, **kwargs):
        super(EditApplicationForm, self).__init__(*args, **kwargs)
        self.original_naimenovanie_prilozheniya = original_naimenovanie_prilozheniya

    def validate_naimenovanie_prilozheniya(self, field):
        from app import Application
        if field.data != self.original_naimenovanie_prilozheniya:
            if Application.query.filter_by(naimenovanie_prilozheniya=field.data).first():
                raise ValidationError(flash('Приложение уже существует', 'danger'))


class AddModuleApplicationForm(FlaskForm):
    kod_modulya = StringField('Модуль')
    kod_prilozheniya = StringField('Приложение')
    submit = SubmitField('Сохранить')


class EditModuleApplicationForm(FlaskForm):
    kod_modulya = StringField('Модуль')
    kod_prilozheniya = StringField('Приложение')
    submit = SubmitField('Сохранить')


# class AddBidForm(FlaskForm):
#     kod_sistemy = StringField('Система')
#     kod_modulya = StringField('Модуль')
#     kod_prilozheniya = StringField('Приложение')
#     opisanie = TextAreaField('Описание')
#     reshenie = TextAreaField('Решение')
#     submit = SubmitField('Добавить')
class AddBidForm(FlaskForm):
    kod_sistemy = StringField('Система')
    kod_modulya = StringField('Модуль')
    kod_prilozheniya = StringField('Приложение')
    # kod_sistemy = SelectField('Система', choices=[], validators=[DataRequired()])
    # kod_modulya = SelectField('Модуль', choices=[], validators=[DataRequired()])
    # kod_prilozheniya = SelectField('Приложение', choices=[], validators=[DataRequired()])
    opisanie = TextAreaField('Описание')
    reshenie = TextAreaField('Решение')
    # update_choices = SubmitField('Обновить выбор')
    submit = SubmitField('Добавить')


class EditBidForm(FlaskForm):
    kod_sistemy = StringField('Система')
    kod_modulya = StringField('Модуль')
    kod_prilozheniya = StringField('Приложение')
    opisanie = TextAreaField('Описание')
    reshenie = TextAreaField('Решение')
    submit = SubmitField('Сохранить изменения')
