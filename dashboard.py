import pandas as pd
import numpy as np
#import plotly.express as px
import panel as pn


# # Read csv file **NOTICE** PANDAS (pd) has built in functions to read csv files
df = pd.read_csv('Banking-Data.csv', parse_dates=['Date'])

# # Display the DataFrame to check the structure
print(df)  # <--------I'm here

# def make_pie_chart(df, year, label):
#     # Filter the dataset for expense transactions
#     sub_df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]

#     color_scale = px.colors.qualitative.Set2
    
#     pie_fig = px.pie(sub_df, values='Amount (EUR)', names='Category', color_discrete_sequence = color_scale)
#     pie_fig.update_traces(textposition='inside', direction ='clockwise', hole=0.3, textinfo="label+percent")

#     total_expense = df[(df['Expense/Income'] == 'Expense') & (df['Year'] == year)]['Amount (EUR)'].sum() 
#     total_income = df[(df['Expense/Income'] == 'Income') & (df['Year'] == year)]['Amount (EUR)'].sum()
    
#     if label == 'Expense':
#         total_text = "€ " + str(round(total_expense))

#         # Saving rate:
#         saving_rate = round((total_income - total_expense)/total_income*100)
#         saving_rate_text = ": Saving rate " + str(saving_rate) + "%"
#     else:
#         saving_rate_text = ""
#         total_text = "€ " + str(round(total_income))

#     pie_fig.update_layout(uniformtext_minsize=10, 
#                         uniformtext_mode='hide',
#                         title=dict(text=label+" Breakdown " + str(year) + saving_rate_text),
#                         # Add annotations in the center of the donut.
#                         annotations=[
#                             dict(
#                                 text=total_text, 
#                                 # Square unit grid starting at bottom left of page
#                                 x=0.5, y=0.5, font_size=12,
#                                 # Hide the arrow that points to the [x,y] coordinate
#                                 showarrow=False
#                             )
#                         ]
#                     )
#     return pie_fig

# income_pie_fig_2022 = make_pie_chart(df, 2022, 'Income')
# income_pie_fig_2022

# def make_monthly_bar_chart(df, year, label):
#     df = df[(df['Expense/Income'] == label) & (df['Year'] == year)]
#     total_by_month = (df.groupby(['Month', 'Month Name'])['Amount (EUR)'].sum()
#                         .to_frame()
#                         .reset_index()
#                         .sort_values(by='Month')  
#                         .reset_index(drop=True))
#     if label == "Income":
#         color_scale = px.colors.sequential.YlGn
#     if label == "Expense":
#         color_scale = px.colors.sequential.OrRd
    
#     bar_fig = px.bar(total_by_month, x='Month Name', y='Amount (EUR)', text_auto='.2s', title=label+" per month", color='Amount (EUR)', color_continuous_scale=color_scale)
#     # bar_fig.update_traces(marker_color='lightslategrey')
    
#     return bar_fig

# income_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Income')
# income_monthly_2022

#  Pie charts
# income_pie_fig_2022 = make_pie_chart(df, 2022, 'Income')
# expense_pie_fig_2022 = make_pie_chart(df, 2022, 'Expense')  
# income_pie_fig_2023 = make_pie_chart(df, 2023, 'Income')
# expense_pie_fig_2023 = make_pie_chart(df, 2023, 'Expense')

# # Bar charts
# income_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Income')
# expense_monthly_2022 = make_monthly_bar_chart(df, 2022, 'Expense')
# income_monthly_2023 = make_monthly_bar_chart(df, 2023, 'Income')
# expense_monthly_2023 = make_monthly_bar_chart(df, 2023, 'Expense')

# these are the TABS used in the YT video
# tabs = pn.Tabs(
#                         ('2022', pn.Column(pn.Row(income_pie_fig_2022, expense_pie_fig_2022),
#                                                 pn.Row(income_monthly_2022, expense_monthly_2022))),
#                         ('2023', pn.Column(pn.Row(income_pie_fig_2023, expense_pie_fig_2023),
#                                                 pn.Row(income_monthly_2023, expense_monthly_2023))
#                         )
#                 )
# tabs.show()

# Create a generic set of tabs with placeholder content
tabs = pn.Tabs(
    ("Overview", pn.pane.Markdown("This is the Overview tab content")),
    ("Income Analysis", pn.pane.Markdown("Income Analysis content goes here")),
    ("Expense Analysis", pn.pane.Markdown("Expense Analysis content goes here")),
    ("Trends", pn.pane.Markdown("Trends content goes here"))
)

# Create the dashboard template <------We got a working dashboard
template = pn.template.FastListTemplate(
    title='Personal Finance Dashboard',
    sidebar=[
        pn.pane.Markdown("# Income Expense Analysis"), 
        pn.pane.Markdown("Overview of income and expense based on my bank transactions. Categories are obtained using local LLMs."),
        pn.pane.PNG("picture.png", sizing_mode="scale_both")
    ],
    main=[pn.Row(pn.Column(tabs))],
    accent_base_color="#88d8b0",
    header_background="#c0b9dd",
)

# Display the dashboard
template.show() 