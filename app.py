import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide', page_title='Startup Analysis')

df = pd.read_csv('startup_cleaned.csv')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month


def show_overall_analysis():
    col1,col2,col3 = st.columns(3)

    with col1:
        # total invested amount
        total = round(df['amount'].sum(), 2)
        st.metric('Total: ', str(total) + ' Cr')
    with col2:
        # maximum amount infused in a startup
        max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1)[0]
        st.metric('Maximum Funding: ', str(max_funding) + ' Cr')
    with col3:
        avg_funding = round(df.groupby('startup')['amount'].sum().mean(),2)
        st.metric('Average Funding: ', str(avg_funding) + ' Cr')

    st.subheader('MoM Funding')
    choice = st.selectbox('Select Type', ['Total','Count'])
    if choice == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['date'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')
    fig = px.line(temp_df, x=temp_df['date'], y=temp_df['amount'])
    st.plotly_chart(fig, use_container_width=True)

    col4,col5 = st.columns(2)
    with col4:
        st.subheader('Top Funding Startups Year wise')
        year_df = df.groupby('year')
        data = pd.DataFrame(columns=df.columns)

        for group, df1 in year_df:
            data = data._append(df1[df1['amount'] == df1['amount'].max()])

        top_funded_startups = data[['startup','amount','year']]
        st.dataframe(top_funded_startups)

    with col5:
        st.subheader('Top Investors Year wise')
        top_investors = data[['investors', 'amount', 'year']]
        st.dataframe(top_investors)

def load_startup_details(startup):
    st.title(startup)

    st.subheader('Industry')
    st.info(df[df['startup'] == startup].head(1)['vertical'].values[0])

    st.subheader('Sub-industry')
    st.info(df[df['startup'] == startup].head(1)['subvertical'].values[0])

    st.subheader('Location')
    st.info(df[df['startup'] == startup].head(1)['city'].values[0])

    st.subheader('Investors')
    st.info(df[df['startup'] == startup].head(1)['investors'].values[0])

def load_investor_details(investor):
    st.title(investor)
    # load recent investments
    recent_investments = df[df['investors'].str.contains(investor)].head()[
        ['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader('Most Recent Investments')
    st.dataframe(recent_investments)

    col1, col2 = st.columns(2)
    with col1:
        # biggest Investments
        biggest_investments = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(
            ascending=False).head()
        st.subheader('Biggest Investments')
        fig = px.pie(biggest_investments, values=biggest_investments.values, names=biggest_investments.index,
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor)].groupby('vertical')['amount'].sum()
        st.subheader('Sector wise Investments')
        fig2 = px.pie(vertical_series, values=vertical_series.values, names=vertical_series.index,
                      color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum()
        st.subheader('YoY Investments')
        fig3 = px.line(year_series, x=year_series.index, y=year_series.values)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        city_series = df[df['investors'].str.contains(investor)].groupby('city')['amount'].sum()
        st.subheader('City wise Investments')
        fig4 = px.pie(city_series, values=city_series.values, names=city_series.index,
                      color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig4, use_container_width=True)


st.sidebar.title('Startup Funding Analysis')

option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'Startup', 'Investor'])

if option == 'Overall Analysis':
    st.title('Overall Analysis')
    show_overall_analysis()

elif option == 'Startup':
    st.title('Startup Analysis')
    selected_startup = st.sidebar.selectbox('Select Startup', sorted(df['startup'].unique().tolist()))
    btn1 = st.sidebar.button('Find Startup Details')
    if btn1:
        load_startup_details(selected_startup)
else:
    st.title('Investor Analysis')
    selected_investor = st.sidebar.selectbox('Select investor', sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
