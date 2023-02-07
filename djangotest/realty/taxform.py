from django import forms
from django.core.exceptions import ValidationError



rus_mounth = {
    1:('Январь'), 2:('Февраль'), 3:('Март'), 4:('Апрель'),
    5:('Май'), 6:('Июнь'), 7:('Июль'), 8:('Август'),
    9:('Сентябрь'), 10:('Октябрь'), 11:('Ноябрь'), 12:('Декабрь')
}


class TaxForm(forms.Form):
    buy_method_choises = (
        ('buy_ready', 'Покупка готовой квартиры'),
        ('buy_ddu', 'Покупка строящейся квартиры по ДДУ'),
        ('inheritance', 'Наследство'),
        ('privatisation', 'Приватизация'),
        ('gift', 'Дарение'),
        ('rent', 'Рента')
    )
    buy_method = forms.ChoiceField(choices = buy_method_choises, label='Метод покупки')

    years_template = tuple(x for x in range(1970,2031))
    date = forms.DateField(label='Дата регистрации собственности', widget= forms.SelectDateWidget(months = rus_mounth, years = years_template))
    
    buy_cost = forms.FloatField(label='Стоимость покупки', required = False)
    
    is_single_choises = (
        ('Yes', 'Да'),
        ('No', 'Нет')
    )
    is_single = forms.ChoiceField(choices = is_single_choises, label='Единственное жильё?', required = False)
    
    kad_cost = forms.FloatField(label='Кадастровая стоимость')
    
    sell_cost = forms.FloatField(label='Сумма продажи')
    
    sell_date = forms.DateField(label='Предполагаемая дата продажи', widget= forms.SelectDateWidget(months = rus_mounth, years = years_template))

    def clean_buy_cost(self):
        data = self.cleaned_data['buy_cost']
        if data < 0:
            raise ValidationError("Стоимость покупки не может быть меньше чем 0")
        return data
    
    def clean_kad_cost(self):
        buy_cost = self.cleaned_data['kad_cost']
        if buy_cost < 0:
            raise ValidationError("Кадастровая стоимость не может быть меньше чем 0")
        return buy_cost

    def clean_sell_cost(self):
        sell_cost = self.cleaned_data['sell_cost']
        if sell_cost < 0:
            raise ValidationError("Стоимость продажи не может быть меньше чем 0")
        return sell_cost
    
    def clean_sell_date(self):
        sell_date = self.cleaned_data['sell_date']
        if sell_date <= self.cleaned_data['date']:
            raise ValidationError("Дата продажи должна быть хотя бы на один день позже чем дата покупки")
        return sell_date

class TaxAnswer:
    def __init__(self, sell_cost = '0.00', base = '0.00', tax = '0.00', no_tax_date = '--', min_sell_cost = '0.00', min_tax = 0.0, comment = '') -> None:
        self.sell_cost = sell_cost
        self.base = base
        self.tax = tax
        self.no_tax_date = no_tax_date
        self.min_sell_cost = min_sell_cost
        self.min_tax = min_tax
        self.comment = comment
    
