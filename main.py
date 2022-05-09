import streamlit as st
import numpy as np
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import datetime

# "/Users/scarlett/Documents/AlphaROC/DP4/DP4_Sample_May5/Data/sample.csv"

# Create sections of the web
header = st.container()
dataset = st.container()
single_company_daily = st.container()
single_company_iso_weekly = st.container()
single_company_quarterly = st.container()
single_company_monthly = st.container()
multi_company_daily = st.container()

# Change the web bg color to gray, could also be changed to any other color
st.markdown(
    """
    <style>
    .main{
    background-color:#F5F5F5;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Trying to let the web read the dataset only once using cache
# Otherwise, every time it runs, the dataset will be read again
@st.cache
def get_data(filename):
    df = pd.read_csv(filename)
    return df


# Header/Introduction section, explain what the web offers.
with header:
    st.title("This is the title")
    st.text("This is the description")

# Dataset section, do some modifications about the names and the format to make it presented better.
with dataset:
    st.header("This is the sample dataset")
    sample_data = get_data("/Users/scarlett/Documents/AlphaROC/DP4/DP4_Sample_May5/Data/sample.csv")
    col_names = list(sample_data.columns)
    new_col_names = col_names[1:]
    new_col_names[4] = "obs_sales"
    new_col_names[5] = "obsn_txn"
    new_col_names[6] = "qr_start"
    new_col_names[7] = "qr_end"
    fig_table = go.Figure(data=go.Table(columnwidth=[1, 1.5, 1.5, 1, 1, 1, 1, 1, 1.5],
                                        header=dict(values=new_col_names,
                                                    fill_color='#c2d4dd',
                                                    align='left'),
                                        cells=dict(values=[sample_data.ticker, sample_data.company_name,
                                                           sample_data.brand_name,
                                                           sample_data.date, sample_data.observed_sales,
                                                           sample_data.observed_transactions,
                                                           sample_data.quarter_start_date, sample_data.quarter_end_date,
                                                           sample_data.revenue],
                                                   fill_color='#f0efef',
                                                   align='left')))

    fig_table.update_layout(margin=dict(l=5, r=5, b=10, t=10),
                            paper_bgcolor='#F5F5F5')

    st.write(fig_table)
    company_options = sample_data['company_name'].unique().tolist()
    count = 0

# Global min date and end date: 2016-10-29 to 2021-11-22
with single_company_daily:
    st.text("Choose a company and time period, we could see the daily observed sales line graph.")
    company_daily = st.selectbox('which company would you like to see?', company_options,
                                 key=count)  # default value is Amazon
    count += 1
    company_daily_data = sample_data.loc[sample_data['company_name'] == company_daily]

    # For the company selected above, the first day with data is min_date, the last day is max_date.
    # Selection of time period should be within this scope.
    company_min_date = datetime.datetime.strptime(min(company_daily_data['date']), "%Y-%m-%d").date()
    min_date_count = 0
    company_max_date = datetime.datetime.strptime(max(company_daily_data['date']), "%Y-%m-%d").date()
    max_date_count = 0

    start_date = st.date_input('Please select your start date:',
                               value=company_min_date,
                               min_value=company_min_date,
                               max_value=company_max_date,
                               key=min_date_count)
    min_date_count += 1
    end_date = st.date_input('Please select your end date:',
                             value=company_max_date,
                             min_value=start_date,  # end_date should not be prior to start date
                             max_value=company_max_date,
                             key=max_date_count)
    max_date_count += 1

    # date column in the dataset is str, also change start_date and end_date to string to do comparison.
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # Only graph data in the selected time range
    company_daily_data = company_daily_data.loc[
        (company_daily_data['date'] >= start_date) & (company_daily_data['date'] <= end_date)]

    company_daily_sales = company_daily_data.groupby('date')['observed_sales'].sum().reset_index(name="daily_obs_sales")

    st.write(company_daily_sales.head())

    daily_line = px.line(company_daily_sales, x="date", y="daily_obs_sales", title="Daily observed sales")
    daily_line.update_traces(line_color='#E74C3C', line_width=1.5)

    daily_line.update_layout(
        showlegend=True, width=800, height=500,
        font=dict(color='#454140', size=15),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#F5F5F5')

    st.write(daily_line)

with single_company_iso_weekly:
    st.text("Choose a company and time period, we could see the iso weekly observed sales line graph.")
    company_iso_weekly = st.selectbox('which company would you like to see?', company_options, key=count)
    count += 1
    company_iso_weekly_data = sample_data.loc[sample_data['company_name'] == company_iso_weekly]
    company_iso_weekly_data['datetime64'] = pd.to_datetime(company_iso_weekly_data['date'])
    company_iso_weekly_data['week_num'] = company_iso_weekly_data['datetime64'].apply(lambda x: x.weekofyear)

    company_iso_weekly_data['iso'] = company_iso_weekly_data['datetime64'].dt.strftime('%G-%V')

    split_year_week = company_iso_weekly_data["iso"].str.split("-", n=1, expand=True)
    company_iso_weekly_data["iso_year"] = split_year_week[0]
    company_iso_weekly_data["iso_week"] = split_year_week[1]

    company_min_iso_week = min(company_iso_weekly_data["iso"])
    company_max_iso_week = max(company_iso_weekly_data["iso"])

    iso_week_range = company_iso_weekly_data["iso"].unique().tolist()

    iso_week_start = st.selectbox('Start iso week:', iso_week_range, 0)
    iso_week_start_index = iso_week_range.index(iso_week_start)
    new_iso_week_range = iso_week_range[iso_week_start_index:]
    default_last_iso_week_index = new_iso_week_range.index(company_max_iso_week)
    iso_week_end = st.selectbox('End iso week:', new_iso_week_range, default_last_iso_week_index)

    company_iso_weekly_data = company_iso_weekly_data.loc[
        (company_iso_weekly_data['iso'] >= iso_week_start) & (company_iso_weekly_data['iso'] <= iso_week_end)]

    company_iso_weekly_sales = company_iso_weekly_data.groupby('iso')['observed_sales']. \
        sum().reset_index(name="iso_weekly_obs_sales")

    iso_weekly_line = px.line(company_iso_weekly_sales, x="iso", y="iso_weekly_obs_sales",
                              title="iso weekly observed sales")
    iso_weekly_line.update_traces(line_color='#E74C3C', line_width=1.5)

    iso_weekly_line.update_xaxes(tickangle=45, title_text='iso week', type='category')

    iso_weekly_line.update_layout(
        showlegend=True, width=800, height=500,
        font=dict(color='#454140', size=15),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#F5F5F5')

    st.write(company_iso_weekly_sales.head())

    st.write(iso_weekly_line)

with single_company_quarterly:
    st.text("Choose a company and time period, we could see the iso quarterly observed sales line graph.")
    company_quarterly = st.selectbox('which company would you like to see?', company_options, key=count)
    count += 1
    company_quarterly_data = sample_data.loc[sample_data['company_name'] == company_quarterly]
    company_quarterly_sales = company_quarterly_data.groupby('quarter_start_date')['observed_sales']. \
        sum().reset_index(name="quarterly_obs_sales")
    company_quarterly_sales[['year', 'month', 'day']] = company_quarterly_sales['quarter_start_date']. \
        str.split('-', expand=True)

    quarter_conditions = [
        (company_quarterly_sales['month'] <= "03"),
        (company_quarterly_sales['month'] > "03") & (company_quarterly_sales['month'] <= "06"),
        (company_quarterly_sales['month'] > "06") & (company_quarterly_sales['month'] <= "09"),
        (company_quarterly_sales['month'] > "09")]

    quarter_values = ['Qt1', 'Qt2', 'Qt3', 'Qt4']

    company_quarterly_sales['quarter'] = np.select(quarter_conditions, quarter_values)

    company_quarterly_sales['year-quarter'] = company_quarterly_sales.year.str.cat(company_quarterly_sales['quarter'],
                                                                                   sep='-')

    company_min_qt = min(company_quarterly_sales['year-quarter'])
    company_max_qt = max(company_quarterly_sales['year-quarter'])

    qt_range = company_quarterly_sales['year-quarter'].unique().tolist()

    qt_start = st.selectbox('Start year and quarter:', qt_range, 0)
    qt_start_index = qt_range.index(qt_start)
    new_qt_range = qt_range[qt_start_index:]
    default_last_qt_index = new_qt_range.index(company_max_qt)
    qt_end = st.selectbox('End year and quarter:', new_qt_range, default_last_qt_index)

    company_quarterly_sales = company_quarterly_sales.loc[
        (company_quarterly_sales['year-quarter'] >= qt_start) & (company_quarterly_sales['year-quarter'] <= qt_end)]

    company_quarterly_sales = company_quarterly_sales[["year-quarter", "quarterly_obs_sales"]]

    st.write(company_quarterly_sales)

    qt_line = px.line(company_quarterly_sales, x="year-quarter", y="quarterly_obs_sales",
                      title="quarterly observed sales")
    qt_line.update_traces(line_color='#E74C3C', line_width=1.5)

    qt_line.update_xaxes(tickangle=45, type='category')

    qt_line.update_layout(
        showlegend=True, width=800, height=500,
        font=dict(color='#454140', size=15),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#F5F5F5')

    st.write(qt_line)

with single_company_monthly:
    st.text("Choose a company and time period, we could see the monthly observed sales line graph.")
    company_monthly = st.selectbox('which company would you like to see?', company_options, key=count)
    count += 1
    company_monthly_data = sample_data.loc[sample_data['company_name'] == company_monthly]
    company_monthly_data[['year', 'month', 'day']] = company_monthly_data['date'].str.split('-', expand=True)
    company_monthly_data['year-month'] = company_monthly_data.year.str.cat(company_monthly_data['month'], sep='-')

    company_min_date = datetime.datetime.strptime(min(company_monthly_data['date']), "%Y-%m-%d").date()
    company_max_date = datetime.datetime.strptime(max(company_monthly_data['date']), "%Y-%m-%d").date()

    month_range = pd.date_range(company_min_date, company_max_date, freq='MS').strftime("%Y-%m").tolist()
    last_month = month_range[-1]

    monthly_start = st.selectbox('Start month:', month_range, 0)
    monthly_start_index = month_range.index(monthly_start)
    new_month_range = month_range[monthly_start_index:]
    default_last_month_index = new_month_range.index(last_month)
    monthly_end = st.selectbox('End month:', new_month_range, default_last_month_index)

    company_monthly_data = company_monthly_data.loc[
        (company_monthly_data['year-month'] >= monthly_start) & (company_monthly_data['year-month'] <= monthly_end)]

    company_monthly_sales = company_monthly_data.groupby('year-month')['observed_sales']. \
        sum().reset_index(name="monthly_obs_sales")

    monthly_line = px.line(company_monthly_sales, x="year-month", y="monthly_obs_sales", title="Monthly observed sales")
    monthly_line.update_traces(line_color='#E74C3C', line_width=1.5)

    monthly_line.update_layout(
        showlegend=True, width=800, height=500,
        font=dict(color='#454140', size=15),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#F5F5F5')

    st.write(company_monthly_sales.head())

    st.write(monthly_line)

with multi_company_daily:
    st.text("Choose several companies and time period, we could see the daily observed sales line graph.")
    multi_company_daily = st.multiselect('Which companies would you like to see?',
                                         company_options, [company_options[0], company_options[1]],
                                         key=count)
    count += 1
    multi_company_daily_data = sample_data.loc[sample_data['company_name'].isin(multi_company_daily)]

    # global min&max for selected companies
    multi_company_min_date = datetime.datetime.\
        strptime(min(multi_company_daily_data['date']), "%Y-%m-%d").date()
    multi_company_max_date = datetime.datetime.\
        strptime(max(multi_company_daily_data['date']), "%Y-%m-%d").date()

    multi_start_date = st.date_input('Please select your start date:',
                                     value=multi_company_min_date,
                                     min_value=multi_company_min_date,
                                     max_value=multi_company_max_date, )
    multi_end_date = st.date_input('Please select your end date:',
                                   value=multi_company_max_date,
                                   min_value=multi_start_date,  # end_date should not be prior to start date
                                   max_value=multi_company_max_date, )

    # date column in the dataset is str, also change start_date and end_date to string to do comparison.
    multi_start_date = multi_start_date.strftime("%Y-%m-%d")
    multi_end_date = multi_end_date.strftime("%Y-%m-%d")

    # Only graph data in the selected time range
    multi_company_daily_data = multi_company_daily_data.loc[
        (multi_company_daily_data['date'] >= start_date) & (multi_company_daily_data['date'] <= end_date)]

    multi_company_sales = multi_company_daily_data.groupby(['company_name', 'date'])['observed_sales'].sum().reset_index(
        name="daily_obs_sales")

    st.write(multi_company_sales.head())

    multi_daily_line = px.line(multi_company_sales, x="date", y="daily_obs_sales", color='company_name',
                               title="Multi companies daily observed sales")
    multi_daily_line.update_traces(line_width=1.5)

    multi_daily_line.update_layout(
        showlegend=True, width=800, height=500,
        font=dict(color='#454140', size=15),
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#F5F5F5')

    st.write(multi_daily_line)
