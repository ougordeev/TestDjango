from django.shortcuts import render
from django.http import HttpResponse
from .taxform import TaxForm,TaxAnswer
import datetime

# Create your views here.

def index(request):
    form = TaxForm()
    return render(request, "index.html", {'form': form})

def add_date_years(date, years):
    try:
        return date.replace(year = date.year + years)
    except ValueError:
        delta = datetime.timedelta(days=1)
        new_date = date + delta
        return add_date_years(new_date, years)

def get_tax(request):
    if request.method == 'POST':

        form = TaxForm(request.POST)
        
        if form.is_valid():
            answer = TaxAnswer()

            date = form.cleaned_data['date']
            sell_date = form.cleaned_data['sell_date']

            kad_cost = form.cleaned_data['kad_cost']
            buy_cost = 0.0
            if form.data['buy_cost'] != '':
                buy_cost = float(form.data['buy_cost'])
            sell_cost = form.cleaned_data['sell_cost']
            base_tax = 0.0

            if form.data['buy_method'] in ['buy_ready', 'buy_ddu']:
                if form.data['is_single'] == 'Yes':
                    need_date = add_date_years(date, 3)
                    if need_date > sell_date:
                        base_tax = sell_cost - buy_cost
                        answer.no_tax_date = need_date.strftime("%d.%m.%Y")
                else:
                    need_date = add_date_years(date, 5)
                    if need_date > sell_date:
                        base_tax = sell_cost - buy_cost
                        answer.no_tax_date = need_date.strftime("%d.%m.%Y")
            elif form.data['buy_method'] in ['inheritance','privatisation','rent','gift']:
                buy_cost = 0.0
                need_date = add_date_years(date, 3)
                if need_date > sell_date:
                        base_tax = sell_cost
                        answer.no_tax_date = need_date.strftime("%d.%m.%Y")
            
            answer.base = str(f'{base_tax:,.2f}').replace(',',' ') if base_tax >= 0 else '0.00'
            answer.tax = str(f'{(base_tax * 0.13):,.2f}').replace(',',' ') if base_tax >= 0 else '0.00'
            if base_tax < 0:
                answer.no_tax_date = '--'
            
            if base_tax > 0.0:
                if buy_cost > (kad_cost * 0.7):
                    answer.min_sell_cost = str(f'{buy_cost:,.2f}').replace(',',' ')
                    answer.comment = 'Ваш минимальный срок владения ещё не прошёл. При продаже придётся заплатить налог в размере ' + answer.tax + ' рублей. При этом есть способ избежать налога. Он не совсем законный, применяйте на свой страх и риск. По договоренности с покупателем можно указать в договоре купли-продажи сумму ' + answer.min_sell_cost + ' что соответствует сумме при покупке квартиры. Тогда по документам вы не получите прибыль и налог платить не придётся. Чтобы понять точный порядок действий поищите в интеренете "Занижение стоимости" или спросите об этом какого-нибудь риэлтора.'
                else:
                    answer.min_sell_cost = str(f'{(kad_cost * 0.7):,.2f}').replace(',',' ')
                    answer.min_tax = str(f'{((kad_cost * 0.7 - buy_cost) * 0.13):,.2f}').replace(',',' ')
                    if form.data['buy_method'] in ['buy_ready', 'buy_ddu']:
                        answer.comment = 'Ваш минимальный срок владения ещё не прошёл. При продаже придётся заплатить налог в размере ' + answer.tax + ' рублей. При этом есть способ уменьшить сумму налога. Он не совсем законный, применяйте на свой страх и риск. По договоренности с покупателем можно указать в договоре купли-продажи сумму ' + answer.min_sell_cost + ' что соответствует кадастровой стомости квартиры умноженной на 0,7 (Минимальная стоимость, за которую закон позволяет продать квартиру. Ваша стоимость покупки  ' + str(f'{buy_cost:,.2f}').replace(',',' ') + ' меньше минимальной стоимости по закону, и вы не можете указать её в договоре купли-продажи, чтобы не платить налог совсем). В этом случае по документам вы получите меньшую прибыль, налог станет меньше и составит ' + answer.min_tax +' рублей. Чтобы понять точный порядок действий поищите в интеренете "Занижение стоимости" или спросите об этом какого-нибудь риэлтора.'
                    else:
                        answer.comment = 'Ваш минимальный срок владения ещё не прошёл. При продаже придётся заплатить налог в размере ' + answer.tax + ' рублей. При этом есть способ уменьшить сумму налога. Он не совсем законный, применяйте на свой страх и риск. По договоренности с покупателем можно указать в договоре купли-продажи сумму ' + str('%.2f' %(kad_cost * 0.7)) + ' что соответствует кадастровой стомости квартиры умноженной на 0.7 (Минимальная стоимость, за которую закон позволяет продать квартиру). В этом случае по документам вы получите меньшую прибыль, налог станет меньше и составит ' + answer.min_tax +' рублей. Чтобы понять точный порядок действий поищите в интеренете "Занижение стоимости" или спросите об этом какого-нибудь риэлтора.'
            elif base_tax == 0.0:
                answer.comment = 'Ваш минимальный срок владения уже закончился. Вы указали день в пункте "Предполагаемая дата продажи". При продаже квартиры в этот день или позже налог начисляться не будет'
            else:
                answer.comment = 'Вы продаёте квартиру дешевле чем купили. В этом случае налог начисляться не будет'
            return render(request, "tax.html",{'answer': answer})
        else:
            return render(request, "index.html", {'form': form})