from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import DateTimeField
from wtforms import validators
from models import Holiday
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

class HolidayView(ModelView):
    column_list = ['date', 'name', 'type']
    form_columns = ['date', 'name', 'type']
    
    column_labels = {
        'date': 'Data święta',
        'name': 'Nazwa święta',
        'type': 'Typ'
    }
    
    form_args = {
        'date': {
            'label': 'Data święta',
            'validators': [validators.DataRequired()]
        },
        'name': {
            'label': 'Nazwa święta',
            'validators': [validators.DataRequired(), validators.Length(max=200)]
        },
        'type': {
            'label': 'Typ święta',
            'validators': [validators.DataRequired()]
        }
    }
    
    column_searchable_list = ['name']
    column_filters = ['date', 'type']
    
    def on_model_change(self, form, model, is_created):
        """Validate date format and other rules before saving"""
        if isinstance(model.date, str):
            try:
                model.date = datetime.strptime(model.date, '%Y-%m-%d').date()
            except ValueError:
                raise validators.ValidationError('Nieprawidłowy format daty. Użyj YYYY-MM-DD')

def init_admin(app, db):
    admin = Admin(app, name='Panel administracyjny', template_mode='bootstrap3')
    admin.add_view(HolidayView(Holiday, db.session, name='Święta'))
    
    return admin