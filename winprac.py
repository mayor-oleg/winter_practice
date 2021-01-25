# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 20:39:19 2021

@author: jr
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 18:57:58 2020

@author: jr
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 16:19:02 2020

@author: jr
"""

#Import ganeral libs
import pandas as pd
import numpy as np
import dateparser
import os
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from datetime import date



# dash imports based on flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

#viz imports
from plotly import graph_objs as go
import seaborn as sns


df =  pd.read_excel('Orders (PowerBI) 2020.xlsx')
print (df.columns)
def best_manager(df):
    managers_df = df[['Manager','Margin Actual, $ ', 'Margin Target, $ ', 'Status']]
    managers = managers_df.groupby(['Manager']).sum()
    #print (managers)
    done_target_proc = []
    for num in range(len(managers)):
        proc = managers['Margin Actual, $ '].iloc[num]*100/managers['Margin Target, $ '].iloc[num]
        done_target_proc.append(np.round(proc)) 
    managers['% of target'] = done_target_proc
    return managers
    
def best_month(df):
    month_df = df[['Payment Date','Margin Actual, $ ', 'Margin Target, $ ', 'Status']]
    # wihtout Status = In progress or Lost
    month_df = month_df.loc[df['Status'] == 'Finished']
    month_df = month_df.groupby(['Payment Date']).sum()
    done_target_proc = []
    for num in range(len(month_df)):
        proc = month_df['Margin Actual, $ '].iloc[num]*100/month_df['Margin Target, $ '].iloc[num]
        done_target_proc.append(np.round(proc)) 
    month_df['% of target'] = done_target_proc
    return month_df

def best_region(df):
    city_df = df[['City','Margin Actual, $ ', 'Margin Target, $ ' ]]
    city = city_df.groupby(['City']).sum()
    #print (managers)
    done_target_proc = []
    for num in range(len(city)):
        if city['Margin Actual, $ '].iloc[num] ==0:
            proc = 0
        else:
            proc = (city['Margin Actual, $ '].iloc[num])*100/city['Margin Target, $ '].iloc[num]
        done_target_proc.append(np.round(proc)) 
    city['% of target'] = done_target_proc
    city = city.sort_values(by=['% of target'])
    return city.sort_values(by=['% of target'])


def best_channel_plan(df):
    channels_df = df[['Sales channel','Margin Actual, $ ', 'Margin Target, $ ', 'Status' ]]
    channels_df = channels_df.loc[df['Status'] == 'Finished']
    channels_df = channels_df.groupby(['Sales channel']).sum()
    done_target_proc = []
    for num in range(len(channels_df)):
        proc = (channels_df['Margin Actual, $ '].iloc[num])*100/channels_df['Margin Target, $ '].iloc[num]
        done_target_proc.append(np.round(proc)) 
    channels_df['% of target'] = done_target_proc
    channels_df = channels_df.sort_values(by=['% of target'])
    return channels_df
 
def best_channel_convertion(df):
    channels_df = df[['Sales channel', 'Status' ]]
    channels = channels_df.groupby(['Sales channel']).count()
    channels_finish = channels_df.loc[df['Status'] == 'Finished']
    channels_finish = channels_finish.groupby(['Sales channel']).count()
    channels['Status finish'] = channels_finish['Status']
    done_target_proc = []
    for num in range(len(channels)):
        proc = (channels['Status finish'].iloc[num]/channels['Status'].iloc[num])*100
        done_target_proc.append(np.round(proc)) 
    channels['% of convertion'] = done_target_proc
    channels = channels.sort_values(by=['% of convertion'])
    return channels

def best_channel_plan_duration(df):

    channels_df = df[['Sales channel', 'Days between deal and payment', 'Status' ]]
    channels_finish = channels_df.loc[df['Status'] == 'Finished']
    channels_finish = channels_finish.drop(['Status'], axis = 1)
    avrg = []
    unique = sorted(channels_finish['Sales channel'].unique())
    print (unique)
    for el in unique:
        check = channels_finish.loc[channels_finish['Sales channel'] == el]    
        avrg.append(np.round(np.mean(check['Days between deal and payment'].tolist())))
        print (el, '=' , np.round(np.mean(check['Days between deal and payment'].tolist())))
    channels = channels_finish.groupby(['Sales channel']).sum()
    channels['Mean delta days'] = avrg
    channels = channels.drop(['Days between deal and payment'], axis =1)
    #channels_finish = channels_finish.groupby(['Sales channel']).mean()
    return channels

def best_goods_customer(df):
    goods = df[['Product segment','Customer']]
    best_goods = goods.groupby(['Product segment']).count()
    return best_goods.sort_values(by=['Customer'])

def best_goods_margin(df):
    goods = df[['Product segment','Margin Actual, $ ']]
    best_goods = goods.groupby(['Product segment']).sum()
    return best_goods.sort_values(by=['Margin Actual, $ '])

list_options = ['Best manager', 'Best plan', 'Best region', 'Best channel by plan','Best channel by conversion','Best channel by duration of deal', 'Best goods by clients', 'Best goods by margin' ]
#style
PLOTLY_THEME ='simple_white'
STYLE = [dbc.themes.FLATLY]

#building server
app = dash.Dash('winter practice', external_stylesheets=STYLE)
server = app.server


#controls
controls =  dbc.Card(
        [
             dbc.Row([
                 dbc.Col(dbc.FormGroup(
                 [
                     dbc.Label("Choose an option:"),
                     dcc.Dropdown(
                             id = "option-selector",
                             options = [{"label":x, "value":x} for x in list_options],
                             value ="Best plan"#, multi = True
                     )
                 ]
                 )),
              ], align = 'center')  
        ],
        body = True
)
                 
   
# inicialisation Graph                 
graph = dcc.Graph (id = 'graph')


#general layout
app.layout = dbc.Container(
    [
     html.H1("Winter practice"),
     html.Hr(),
     dbc.Row([dbc.Col(controls, width = 6)]),
     dbc.Row([dbc.Col(html.Div("Dashboard"),width = 6)]),
     dbc.Row([dbc.Col(graph, width = 6)]
              #dbc.Col(qtygraph, width = 6)]
                , align =  "center")
     
    ], fluid = True
)


@app.callback(Output (component_id = 'graph', component_property = 'figure'),
              [Input(component_id = 'option-selector', component_property = 'value')])
def update_date_graph (option):
    print ()
    print ()
    print (option)
    print ()
    print ()
    if option == 'Best manager':
        print (best_manager(df))
        managers = best_manager(df).index.tolist()
        proc_targ = best_manager(df)['% of target']
        figure={
            'data': [
                {'x': managers, 'y': proc_targ, 'type': 'bar'}
                ],
            'layout': {
                'title': '% of target'
                    }
                }
        return figure    
    if option == 'Best plan':
        date_stamp = best_month(df).index.tolist()
        date_lst = []
        for num in date_stamp:
            date_lst.append(num.date().strftime("%m-%d-%Y"))
        targets_lst = best_month(df)['% of target'].tolist()
        fig = go.Figure(layout=go.Layout(height=400, width=1024))
        fig.add_trace(go.Scatter(x = date_lst,
                             y = targets_lst,
                             fill = 'tozeroy', mode = 'lines+markers',
                             name = '% of target', line = {'color':'blue'}))
        fig.update_traces(opacity=1)
        fig.update_layout(#template=PLOT_THEME,
                title_text = "", xaxis_title = 'Date',
                          yaxis_title = '% of target')
        return fig
    if option == 'Best region':
        print (best_region(df))
        city = best_region(df).index.tolist()
        proc_targ = best_region(df)['% of target']
        figure={
            'data': [
                {'x': city, 'y': proc_targ, 'type': 'bar', 'name': u'Montréal'}
                ],
            'layout': {
                'title': '% of target'
                    }
                }
        return figure    
    if option == 'Best channel by plan':
        print (best_channel_plan(df))
        channel = best_channel_plan(df).index.tolist()
        proc_targ = best_channel_plan(df)['% of target']
        figure={
            'data': [
                {'x': channel, 'y': proc_targ, 'type': 'bar'}
                ],
            'layout': {
                'title': '% of target'
                    }
                }
        return figure 
    if option == 'Best channel by conversion':
        print (best_channel_convertion(df))
        channel = best_channel_convertion(df).index.tolist()
        proc_targ = best_channel_convertion(df)['% of convertion']
        figure={
            'data': [
                {'x': channel, 'y': proc_targ, 'type': 'bar'}
                ],
            'layout': {
                'title': '% of convertion'
                    }
                }
        return figure     
    if option == 'Best channel by duration of deal':
        print (best_channel_plan_duration(df))
        channel = best_channel_plan_duration(df).index.tolist()
        proc_targ = best_channel_plan_duration(df)['Mean delta days']
        figure={
            'data': [
                {'x': channel, 'y': proc_targ, 'type': 'bar'}
                ],
            'layout': {
                'title': 'Mean delta days between deal and payment '
                    }
                }
        return figure 
    if option == 'Best goods by clients':
        print (best_goods_customer(df))
        goods = best_goods_customer(df).index.tolist()
        goods_count = best_goods_customer(df)['Customer']
        figure={
            'data': [
                {'x': goods, 'y': goods_count, 'type': 'bar'}
                ],
            'layout': {
                'title': 'Best goods by clients '
                    }
                }
        return figure 
    if option == 'Best goods by margin':
        print (best_goods_margin(df))
        goods = best_goods_margin(df).index.tolist()
        goods_margin = best_goods_margin(df)['Margin Actual, $ ']
        figure={
            'data': [
                {'x': goods, 'y': goods_margin, 'type': 'bar'}
                ],
            'layout': {
                'title': 'Best goods by margin '
                    }
                }
        return figure 

    
if __name__ =="__main__":
    app.run_server()
    
                 