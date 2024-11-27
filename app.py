import pandas as pd
pd.options.plotting.backend = "plotly"
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

add = lambda delta: lambda x: x+delta
multiply = lambda delta: lambda x: float(x)*(1+delta)

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

old_young_image = 'https://media.istockphoto.com/id/523749933/photo/age-is-mind-over-matter.jpg?s=612x612&w=0&k=20&c=g5wSEodREftE2nE3oo1zjK1wpFMKWscb5N5X9oVFvjw='

def produce_card(title,image,fields):
    content = [html.H5(title, className="card-title"),]
    for id_, name, min_val,max_val,value,step in fields:
        content.extend([html.P([name,dcc.Input(id=id_, type='number', min=min_val, max=max_val, step=1, value = value)],className="card-text"),
                        ])
    image_ = dbc.Col(dbc.CardImg(src=image,className="img-fluid rounded-start"),className="col-md-4")
    card = dbc.Card([dbc.Row([image_, dbc.Col(dbc.CardBody(content),className="col-md-8")],
                     className="g-0 d-flex align-items-center")
                    ],className="mb-3",style={"maxWidth": "540px"})
    return card

ages_fields = [('current_age','Your age',18,50,25,1),
               ('RETIREMENT_AGE','Retirement age',50,70,60,1),
               ('DEAD','Planned death',70,100,90,1)]



ages_card = produce_card('Your life stages',old_young_image,ages_fields)

pension_image = 'https://i0.wp.com/www.titanui.com/wp-content/uploads/2013/09/29/Locked-Money-Stacks-Vector.jpg'

pension_fields = [('current_pension',"Current pension pot ",0,1000,10,1),
                  ('pension_contrib',"Annual contribution ",0,100,5,1),
                  ('PENSION_CONTRIB_INCREASE',"Increase x% per year ",0,10,1,1),
                  ('PENSION_CONTRIB_CAP',"Until annual contrib cap of ",10,100,60,1)]


pension_card = produce_card("Your pension (in '000s)",pension_image,pension_fields)

savings_image = 'https://www.moneysavingexpert.com/content/dam/mse/editorial-image-library/guide-images/rhs-guide-images-/hero-banking-taxfree-savings.jpg'

savings_fields = [('savings',"Current savings ",0,1000,10,1),
                  ('savings_contrib',"Annual contribution ",0,100,5,1),
                  ('SAVINGS_CONTRIB_GROWTH',"Increase x% per year ",0,10,1,1)]

savings_card = produce_card("Your savings (in '000s)",savings_image,savings_fields)

capital_image = 'https://images.moneycontrol.com/static-mcnews/2023/05/Healing-Space-54-Bouncebackability-markets-and-mental-health-bounce-back-770x433.jpg?impolicy=website&width=770&height=431'

capital_fields = [('CAPITAL_GROWTH',"Annual capital growth %",0,10,4,1)]

capital_card = produce_card("Investment growth",capital_image,capital_fields)

expenses_image = 'https://www.topdoctors.co.uk/files/Image/large/5bd9bdd8-dbf8-41a5-a429-248025bbab96.png'

expenses_fields = [('ANNUAL_EXPENSE_RETIREMENT',"Expenses per year ",0,200,30,1),
                  ('EXPENSE_GROWTH',"Increase x% per year ",0,10,1,1)]

expenses_card = produce_card("Your retirement expenses (in '000s)",expenses_image,expenses_fields)

rent_image = 'https://www.avail.co/wp-content/uploads/2021/08/8-tips-for-renting-out-a-house-for-the-first-time-min.jpg'

rent_fields = [('housing_expense_retirement',"Annual rent ",0,50,10,1),
                  ('rent_increase',"Increase x% per year ",0,10,0,1)]

rent_card = produce_card("Where will you live?",rent_image,rent_fields)


first_row = dbc.Row([ages_card,expenses_card,rent_card])
second_row = dbc.Row([pension_card,savings_card,capital_card])


app.layout = html.Div([
    html.H1(children='How f*cked are you?', style={'textAlign':'center'}),
    html.P('Saving for retirement is important. This simulator allows you to plan ahead and avoid misery', style={'textAlign':'center'}),
    first_row,
    second_row,
    html.Div(dbc.Row([
                        dbc.Col(dcc.Graph(id='graph-content'),width=6),
                        dbc.Col(dcc.Graph(id='graph-misery'),width=6)
                      ]))
])

@callback(
    [Output('graph-content', 'figure'),
     Output('graph-misery', 'figure')],
    Input('current_age', 'value'),
    Input('DEAD', 'value'),
    Input('current_pension', 'value'),
    Input('pension_contrib', 'value'),
    Input('savings', 'value'),
    Input('savings_contrib', 'value'),
    Input('RETIREMENT_AGE', 'value'),
    Input('PENSION_CONTRIB_INCREASE', 'value'),
    Input('PENSION_CONTRIB_CAP', 'value'),
    Input('SAVINGS_CONTRIB_GROWTH', 'value'),
    Input('CAPITAL_GROWTH', 'value'),
    Input('ANNUAL_EXPENSE_RETIREMENT', 'value'),
    Input('EXPENSE_GROWTH', 'value'),
    Input('housing_expense_retirement', 'value'),
    Input('rent_increase', 'value')
    
)
def update_graph(current_age,DEAD,current_pension,pension_contrib,savings,savings_contrib,RETIREMENT_AGE,
                PENSION_CONTRIB_INCREASE,PENSION_CONTRIB_CAP,SAVINGS_CONTRIB_GROWTH,CAPITAL_GROWTH,
                ANNUAL_EXPENSE_RETIREMENT,EXPENSE_GROWTH,housing_expense_retirement,rent_increase):
    
    args = dict()
    args['current_age'] = current_age
    args['DEAD'] = DEAD
    args['RETIREMENT_AGE'] = RETIREMENT_AGE
    
    args['ANNUAL_EXPENSE_RETIREMENT'] = ANNUAL_EXPENSE_RETIREMENT
    args['EXPENSE_GROWTH'] = EXPENSE_GROWTH/100
    
    args['housing_expense_retirement'] = housing_expense_retirement
    args['rent_increase'] = rent_increase/100
    
    args['current_pension'] = current_pension
    args['pension_contrib'] = pension_contrib
    args['PENSION_CONTRIB_INCREASE'] = PENSION_CONTRIB_INCREASE/100
    args['PENSION_CONTRIB_CAP'] = PENSION_CONTRIB_CAP
    
    args['savings'] = savings
    args['savings_contrib'] = savings_contrib
    args['SAVINGS_CONTRIB_GROWTH'] = SAVINGS_CONTRIB_GROWTH/100
    args['CAPITAL_GROWTH'] = CAPITAL_GROWTH/100
    
    
    data = process(args)
    fig = show(data)
    
    impact = sensitivity(args)
    return [fig,impact]



def process(args):
    # current_age,current_pension,pension_contrib,savings,savings_contrib,housing_expense_retirement,rent_increase,PENSION_CONTRIB_INCREASE,PENSION_CONTRIB_CAP,RETIREMENT_AGE,CAPITAL_GROWTH,SAVINGS_CONTRIB_GROWTH,ANNUAL_EXPENSE_RETIREMENT,EXPENSE_GROWTH,DEAD = args
    args = {k:v for k,v in args.items()}

    data = []

    misery = 0
    for age in range(args['current_age'],args['RETIREMENT_AGE']):
        args['current_pension'] *= 1+args['CAPITAL_GROWTH']
        args['pension_contrib'] = min(args['PENSION_CONTRIB_CAP'],args['pension_contrib']*(1+args['PENSION_CONTRIB_INCREASE']))
        args['current_pension'] += args['pension_contrib']

        args['savings'] *= 1+args['CAPITAL_GROWTH']
        args['savings_contrib'] *= 1+args['SAVINGS_CONTRIB_GROWTH']
        args['savings'] += args['savings_contrib']

        row = [age,args['current_pension'],args['savings'],misery]
        data.append(row)

    for age in range(args['RETIREMENT_AGE'],args['DEAD']):
        args['current_pension'] *= 1+args['CAPITAL_GROWTH']
        args['housing_expense_retirement'] *= 1+args['rent_increase']

        args['ANNUAL_EXPENSE_RETIREMENT'] *= 1+args['EXPENSE_GROWTH']
        expenses = args['ANNUAL_EXPENSE_RETIREMENT'] + args['housing_expense_retirement']

        pension_drawdown = min(args['current_pension'],expenses)
        remainder = expenses - pension_drawdown

        args['current_pension'] -= pension_drawdown
        args['savings'] -= remainder
        misery = max(0,-args['savings'])

        row = [age,args['current_pension'],args['savings'],misery]
        data.append(row)

    data = pd.DataFrame(data, columns = 'age pension savings misery'.split()).set_index('age')
    return data

def get_final(data):
    return data['savings pension'.split()].iloc[-1].sum()

def sensitivity(args,delta=0.01,fields=[('pension_contrib',multiply),
                         ('savings_contrib',multiply),
                         ('housing_expense_retirement',multiply),
                         ('rent_increase',add),
                         ('PENSION_CONTRIB_INCREASE',add),
                         ('CAPITAL_GROWTH',add),
                         ('SAVINGS_CONTRIB_GROWTH',multiply),
                         ('ANNUAL_EXPENSE_RETIREMENT',multiply),
                         ('EXPENSE_GROWTH',add)
                    ]):
    effect = dict()
    for field,operator in fields:
        new_args = {k:v for k,v in args.items()}
        new_args[field] = operator(delta)(args[field])
        plus_data = process(new_args)
        new_args[field] = operator(-delta)(args[field])
        minus_data = process(new_args)
        effect[field] =  int((get_final(plus_data) - get_final(minus_data))/2)
    effect = pd.DataFrame(effect.items(), columns = 'modified impact'.split()).sort_values('impact',ascending=False)
    fig = effect.set_index('modified').plot.barh(title='What if I changed something by 1% ?')
    return fig

def show(data):
    not_fucked = (data['misery'] > 0).sum() == 0

    fucked = None if not_fucked else data[data['misery'] > 0].index[0]

    title = 'Congratulations ! You made it to the end :-)' if not_fucked else f'You will be fucked at {fucked} :-('


    fig = data['pension savings misery'.split()].astype(int).plot(title=title)

    fig.update_yaxes(range=[0, data.sum(axis=1).max()], row=1, col=1)
    # fig.show()
    return fig



if __name__ == '__main__':
    app.run_server()
