import pandas as pd
import plotly.express as px
import panel as pn
import subprocess
from privateGPT import get_answer
# Ensure Panel extensions are loaded
pn.extension("plotly")

# Function to create the expenses pie chart for a specific time period
def make_expenses_pie_chart(df, months=None):
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
    df = df.dropna(subset=['Date'])

    df['Type'] = df['Type'].str.strip()
    df['Category'] = df['Category'].str.strip()

    latest_date = df['Date'].max()
    
    if months:
        start_date = latest_date - pd.DateOffset(months=months)
        
        sub_df = df[df['Date'] > start_date]
        
    else:
        sub_df = df
    


    sub_df = sub_df[(sub_df['Type'] == 'Debit') & (~sub_df['Category'].isin(['Interest', 'Salary']))]
    
    category_totals = sub_df.groupby("Category")["Debit Amount"].sum().reset_index()
    
    if category_totals.empty:
        return px.scatter(title="No data available for selected period")

    pie_fig = px.pie(
        category_totals,
        values="Debit Amount",
        names="Category",
        title=f"Expense Breakdown by Category ({'Total' if not months else f'Last {months} Month' + ('s' if months > 1 else '')})",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    pie_fig.update_traces(
        textposition='inside', 
        textinfo="percent+label",
        hovertemplate="%{label}: $%{value:,.0f}"
    )
    
    return pie_fig


# Function to create the income pie chart for a specific time period
def make_income_pie_chart(df, months=None):
    # Clean the 'Type' and 'Category' columns by removing leading/trailing spaces
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
    df['Type'] = df['Type'].str.strip()
    df['Category'] = df['Category'].str.strip()

    latest_date = df['Date'].max()
    
    if months:
        start_date = latest_date - pd.DateOffset(months=months)
        
        sub_df = df[df['Date'] > start_date]
        
    else:
        sub_df = df

    # Filter for 'Credit' transactions and 'Interest' or 'Salary' categories
    sub_df = sub_df[(sub_df['Type'] == 'Credit') & (sub_df['Category'].isin(['Interest', 'Salary']))]

    # Group by Category and sum the Credit Amount
    category_totals = sub_df.groupby("Category")["Credit Amount"].sum().reset_index()

    # If there is no data after filtering, return a message
    if category_totals.empty:
        return px.scatter(title="No data available for income")

    # Create the pie chart for income breakdown
    pie_fig = px.pie(
        category_totals,
        values="Credit Amount",
        names="Category",
        title=f"Income Breakdown by Category ({'Total' if not months else f'Last {months} Month' + ('s' if months > 1 else '')})",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )

    # Update the pie chart for better visualization
    pie_fig.update_traces(
        textposition='inside', 
        textinfo="percent+label",
        hovertemplate="%{label}: $%{value:,.0f}"
    )
    
    return pie_fig

# Function to create the trendline chart for monthly income and expenses
def make_trendline_chart(df):
    # Ensure the 'Date' column is in datetime format and clean data
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
    df = df.dropna(subset=['Date'])

    # Filter for the last 8 months
    latest_date = df['Date'].max()
    start_date = latest_date - pd.DateOffset(months=8)
    df = df[df['Date'] >= start_date]

    # Clean and prepare the data
    df['Type'] = df['Type'].str.strip()
    df['Category'] = df['Category'].str.strip()
    
    # Extract year and month for grouping
    df['YearMonth'] = df['Date'].dt.to_period("M")

    # Aggregate data by month for both income and expenses
    monthly_totals = df.groupby(['YearMonth', 'Type']).agg({
        'Debit Amount': 'sum',
        'Credit Amount': 'sum'
    }).reset_index()

    # Pivot the data to have 'Income' and 'Expense' columns for each month
    monthly_totals['Income'] = monthly_totals.apply(lambda x: x['Credit Amount'] if x['Type'] == 'Credit' else 0, axis=1)
    monthly_totals['Expenses'] = monthly_totals.apply(lambda x: x['Debit Amount'] if x['Type'] == 'Debit' else 0, axis=1)
    
    # Sum up income and expenses by month
    monthly_totals = monthly_totals.groupby('YearMonth').agg({'Income': 'sum', 'Expenses': 'sum'}).reset_index()

    # Convert YearMonth back to a date format for plotting
    monthly_totals['YearMonth'] = monthly_totals['YearMonth'].dt.to_timestamp()

    # Create the line chart with separate lines for income and expenses
    trendline_fig = px.line(
        monthly_totals, 
        x='YearMonth', 
        y=['Income', 'Expenses'], 
        title="Monthly Income and Expense Trends (Last 8 Months)",
        labels={"value": "Amount ($)", "YearMonth": "Month"},
        color_discrete_sequence=['#17BECF', '#FF7F0E']  # Color for income and expenses
    )

    trendline_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Total Amount ($)",
        legend_title_text="Type",
    )
    
    return trendline_fig

# Function to interact with the LLM model
def ask_llm(question):
    # Replace this with actual LLM call 
    answer = get_answer(question)
    return answer

# Load data from CSV file
df = pd.read_csv('Banking-Data.csv', parse_dates=['Date'])

# Create the pie charts for each period for both income and expenses
income_pie_fig_total = make_income_pie_chart(df)  # Total period
income_pie_fig_one_month = make_income_pie_chart(df, months=1)  # One-month period
income_pie_fig_three_months = make_income_pie_chart(df, months=3)  # Three-month period
income_pie_fig_six_months = make_income_pie_chart(df, months=6)  # Six-month period

expense_pie_fig_total = make_expenses_pie_chart(df)  # Total period
expense_pie_fig_one_month = make_expenses_pie_chart(df, months=1)  # One-month period
expense_pie_fig_three_months = make_expenses_pie_chart(df, months=3)  # Three-month period
expense_pie_fig_six_months = make_expenses_pie_chart(df, months=6)  # Six-month period

# Generate the trendline figure
trendline_fig = make_trendline_chart(df)

# Create the sub-tabs for the "Expense Analysis" tab
expense_subtabs = pn.Tabs(
    ("Total", pn.pane.Plotly(expense_pie_fig_total, sizing_mode="stretch_both")),
    ("Last 1 Month", pn.pane.Plotly(expense_pie_fig_one_month, sizing_mode="stretch_both")),
    ("Last 3 Months", pn.pane.Plotly(expense_pie_fig_three_months, sizing_mode="stretch_both")),
    ("Last 6 Months", pn.pane.Plotly(expense_pie_fig_six_months, sizing_mode="stretch_both"))
)

# Create the sub-tabs for the "Income Analysis" tab
income_subtabs = pn.Tabs(
    ("Total", pn.pane.Plotly(income_pie_fig_total, sizing_mode="stretch_both")),
    ("Last 1 Month", pn.pane.Plotly(income_pie_fig_one_month, sizing_mode="stretch_both")),
    ("Last 3 Months", pn.pane.Plotly(income_pie_fig_three_months, sizing_mode="stretch_both")),
    ("Last 6 Months", pn.pane.Plotly(income_pie_fig_six_months, sizing_mode="stretch_both"))
)


# Panel widgets for question and response
question_input = pn.widgets.TextInput(name="Ask a Question", placeholder="Type your question here...")
submit_button = pn.widgets.Button(name="Submit", button_type="primary")
response_area = pn.pane.Markdown("")  # Removed 'style' argument

# Define the submit action
def on_submit(event):
    question = question_input.value
    response = ask_llm(question)
    response_area.object = f"**Response:** {response}"

submit_button.on_click(on_submit)

#load data from csv file
def run_private_gpt():
    try:
        # Run privateGPT.py as a separate process
        process = subprocess.Popen(['python', 'privateGPT.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Print output and error in real-time
        for line in process.stdout:
            print(line.decode(), end='')

        # Check for errors after process completes
        stdout, stderr = process.communicate()
        if stderr:
            print("Error:", stderr.decode())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Starting privateGPT from dashboard...")
    run_private_gpt()
    

# Define the dashboard tabs with detailed descriptions
tabs = pn.Tabs(
    ("Overview", pn.Column(
        pn.pane.Markdown("### Welcome to the Personal Finance Dashboard"),
        pn.pane.Markdown("This dashboard provides an overview of your income and expense categories, "
                         "helping you track your financial activities. Use the tabs above to explore "
                         "various aspects of your financial data."),
        pn.Row(question_input, submit_button),
        response_area,  # Display the response here
        pn.pane.Markdown("#### Dashboard Guide:"),
        pn.pane.Markdown("1. **Income Analysis** - Explore your income sources and their breakdown.\n"
                         "2. **Expense Analysis** - Get insights into your spending habits by category.\n"
                         "3. **Trends** - Analyze monthly trends and seasonal patterns in your finances.\n")
    )),
    ("Income Analysis", pn.Column(
        pn.pane.Markdown("### Income Breakdown"),
        pn.pane.Markdown("The pie chart below provides a breakdown of your income sources, helping you "
                         "identify the contributions of different income streams, like salary and interest."),
        income_subtabs  # Add income subtabs for different periods
    )),
    ("Expense Analysis", pn.Column(
        pn.pane.Markdown("### Expense Breakdown"),
        pn.pane.Markdown("Understand your spending patterns with this categorized view of your expenses. "
                         "This analysis can help you pinpoint areas where you may want to reduce spending."),
        expense_subtabs
    )),
    ("Trends", pn.Column(
        pn.pane.Markdown("### Financial Trends Analysis"),
        pn.pane.Markdown("This section displays Income and expense TrendLine"),
        pn.pane.Plotly(trendline_fig, sizing_mode="stretch_both")  # Add the trendline chart here
    ))
)

# Define the dashboard template with improved sidebar and header
template = pn.template.FastListTemplate(
    title="Summit Finance Analytics",
    sidebar=[
        pn.pane.Markdown("# Personal Finance Insights"),
        pn.pane.Markdown("Welcome to your personal finance dashboard. Get an overview of your income and expenses, "
                         "visualized through clear, easy-to-understand charts. These insights are generated from "
                         "your banking data using a Local LLM."),
        pn.pane.Markdown("### Navigation Guide"),
        pn.pane.Markdown("Use the tabs on the main screen to explore detailed views of your **Income Analysis**, "
                         "**Expense Analysis**, and **Trends**."),
        pn.pane.PNG("logo.png", sizing_mode="scale_both")
    ],
    main=[
        pn.Row(tabs, sizing_mode="stretch_both")
    ],
    accent_base_color="#000000",
    header_background="#000000",
)

run_private_gpt()
# Display the dashboard
template.show()