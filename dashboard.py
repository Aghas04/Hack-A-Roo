import pandas as pd
import plotly.express as px
import panel as pn

# Ensure Panel extensions are loaded
pn.extension("plotly")

# Function to create the expenses pie chart for a specific time period
def make_expenses_pie_chart(df, months=None):
    # Convert 'Date' column to datetime using error handling (invalid dates become NaT)
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
    
    # Drop rows where 'Date' is NaT (invalid dates)
    df = df.dropna(subset=['Date'])
    
    # Get the latest date in the dataset
    latest_date = df['Date'].max()
    #print(f"Latest date: {latest_date}")
    
    # Filter for transactions within the specified months (if any)
    if months:
        # Correct filter logic to use `pd.DateOffset`
        start_date = latest_date - pd.DateOffset(months=months)
        sub_df = df[df['Date'] > start_date]
    else:
        sub_df = df
    
    # Filter for 'Debit' transactions and exclude 'Interest' and 'Salary' categories
    sub_df = sub_df[(sub_df['Type'] == 'Debit') & (~sub_df['Category'].isin(['Interest', 'Salary']))]
    
    # Group by 'Category' and calculate the sum of 'Debit Amount'
    category_totals = sub_df.groupby("Category")["Debit Amount"].sum().reset_index()

    # Create a pie chart with custom hover template
    pie_fig = px.pie(
        category_totals,
        values="Debit Amount",
        names="Category",
        title=f"Expense Breakdown by Category ({'Total' if not months else f'Last {months} Month{"s" if months > 1 else ""}'})",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    # Update hover template to show category name and dollar amount
    pie_fig.update_traces(
        textposition='inside', 
        textinfo="percent+label",
        hovertemplate="%{label}: $%{value:,.0f}"
    )
    
    return pie_fig


# Function to create the income pie chart with customized tooltips
def make_income_pie_chart(df):
    # Filter for 'Credit' transactions and include only 'Interest' and 'Salary' categories
    sub_df = df[(df['Type'] == 'Credit') & (df['Category'].isin(['Interest', 'Salary']))]

    # Group by 'Category' and calculate the sum of 'Credit Amount'
    category_totals = sub_df.groupby("Category")["Credit Amount"].sum().reset_index()

    # Create a pie chart with custom hover template
    pie_fig = px.pie(
        category_totals,
        values="Credit Amount",
        names="Category",
        title="Income Breakdown by Category",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    # Update hover template to show category name and dollar amount
    pie_fig.update_traces(
        textposition='inside', 
        textinfo="percent+label",
        hovertemplate="%{label}: $%{value:,.0f}"
    )
    
    return pie_fig

# Load data from CSV file
df = pd.read_csv('Banking-Data.csv', parse_dates=['Date'])

# Create the pie charts for each period
income_pie_fig = make_income_pie_chart(df)
expense_pie_fig_total = make_expenses_pie_chart(df)  # Total period
expense_pie_fig_one_month = make_expenses_pie_chart(df, months=1)  # One-month period
expense_pie_fig_three_months = make_expenses_pie_chart(df, months=3)  # Three-month period
expense_pie_fig_six_months = make_expenses_pie_chart(df, months=6)  # Six-month period

# Create the sub-tabs for the "Expense Analysis" tab
expense_subtabs = pn.Tabs(
    ("Total", pn.pane.Plotly(expense_pie_fig_total, sizing_mode="stretch_both")),
    ("Last 1 Month", pn.pane.Plotly(expense_pie_fig_one_month, sizing_mode="stretch_both")),
    ("Last 3 Months", pn.pane.Plotly(expense_pie_fig_three_months, sizing_mode="stretch_both")),
    ("Last 6 Months", pn.pane.Plotly(expense_pie_fig_six_months, sizing_mode="stretch_both"))
)

# Define the dashboard tabs with more detailed descriptions
tabs = pn.Tabs(
    ("Overview", pn.Column(
        pn.pane.Markdown("### Welcome to the Personal Finance Dashboard"),
        pn.pane.Markdown("This dashboard provides an overview of your income and expense categories, "
                         "helping you track your financial activities. Use the tabs above to explore "
                         "various aspects of your financial data."),
        pn.pane.Markdown("#### Dashboard Guide:"),
        pn.pane.Markdown("1. **Income Analysis** - Explore your income sources and their breakdown.\n"
                         "2. **Expense Analysis** - Get insights into your spending habits by category.\n"
                         "3. **Trends** - Analyze monthly trends and seasonal patterns in your finances.\n")
    )),
    ("Income Analysis", pn.Column(
        pn.pane.Markdown("### Income Breakdown"),
        pn.pane.Markdown("The pie chart below provides a breakdown of your income sources, helping you "
                         "identify the contributions of different income streams, like salary and interest."),
        pn.pane.Plotly(income_pie_fig, sizing_mode="stretch_both")
    )),
    ("Expense Analysis", pn.Column(
        pn.pane.Markdown("### Expense Breakdown"),
        pn.pane.Markdown("Understand your spending patterns with this categorized view of your expenses. "
                         "This analysis can help you pinpoint areas where you may want to reduce spending."),
        expense_subtabs  # Include the sub-tabs for different expense periods
    )),
    ("Trends", pn.Column(
        pn.pane.Markdown("### Financial Trends Analysis"),
        pn.pane.Markdown("Coming soon! This section will display monthly and seasonal financial trends, "
                         "helping you track fluctuations in income and spending.")
    ))
)

# Define the dashboard template with improved sidebar and header
template = pn.template.FastListTemplate(
    title="Personal Finance Dashboard",
    sidebar=[
        pn.pane.Markdown("# Personal Finance Insights"),
        pn.pane.Markdown("Welcome to your personal finance dashboard. Get an overview of your income and expenses, "
                         "visualized through clear, easy-to-understand charts. These insights are generated from "
                         "your banking data using a Local LLM."),
        pn.pane.Markdown("### Navigation Guide"),
        pn.pane.Markdown("Use the tabs on the main screen to explore detailed views of your **Income Analysis**, "
                         "**Expense Analysis**, and **Trends**."),
        pn.pane.PNG("picture.png", sizing_mode="scale_both")
    ],
    main=[
        pn.Row(tabs)
    ],
    accent_base_color="#000000",
    header_background="#000000",
)

# Display the dashboard
template.show()
