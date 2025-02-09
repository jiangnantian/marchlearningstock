import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    df['MACD'] = macd
    df['Signal'] = signal_line
    df['Histogram'] = histogram
    return df


def detect_divergence(df, window=10):
    df['Price_High'] = df['close'].rolling(window=window, center=True).max()
    df['Price_Low'] = df['close'].rolling(window=window, center=True).min()
    df['MACD_High'] = df['MACD'].rolling(window=window, center=True).max()
    df['MACD_Low'] = df['MACD'].rolling(window=window, center=True).min()

    df['Bullish_Divergence'] = (df['close'] == df['Price_Low']) & (df['MACD'] > df['MACD_Low'])
    df['Bearish_Divergence'] = (df['close'] == df['Price_High']) & (df['MACD'] < df['MACD_High'])

    return df


def plot_stock_with_macd(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=df.index,
                                open=df['open'],
                                high=df['high'],
                                low=df['low'],
                                close=df['close'],
                                increasing_line_color='red',
                                decreasing_line_color='green',
                                name='K线'), row=1, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')), row=2,
                col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal', line=dict(color='orange')), row=2,
                col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['Histogram'], name='Histogram'), row=2, col=1)

    # Divergence points
    bullish_divergence = df[df['Bullish_Divergence']]
    bearish_divergence = df[df['Bearish_Divergence']]

    fig.add_trace(go.Scatter(x=bullish_divergence.index, y=bullish_divergence['low'], mode='markers',
                            name='底背离', marker=dict(symbol='triangle-up', size=10, color='green')), row=1, col=1)
    fig.add_trace(go.Scatter(x=bearish_divergence.index, y=bearish_divergence['high'], mode='markers',
                            name='顶背离', marker=dict(symbol='triangle-down', size=10, color='red')), row=1, col=1)

    fig.update_layout(title='股票K线图、MACD指标和背离', xaxis_rangeslider_visible=False, height=800)
    fig.update_xaxes(title_text='日期', row=2, col=1)
    fig.update_yaxes(title_text='价格', row=1, col=1)
    fig.update_yaxes(title_text='MACD', row=2, col=1)

    return fig


def app():
    st.title('股票顶背离和底背离分析')

    stock_code = st.text_input('请输入股票代码(例如sh000001表示上证指数:)','sh000001')

    if st.button('分析'):
        try:
            with st.spinner('正在获取股票数据...'):
                end_date = datetime.now()
                #end_date = datetime(2024, 12, 2)
                start_date = end_date - timedelta(days=90) # 获取最近90天的数据

                if stock_code.startswith('sh') or stock_code.startswith('sz'):
                    df = ak.stock_zh_index_daily(symbol=stock_code)
                else:
                    df = ak.stock_zh_a_daily(symbol=stock_code)

            df = df.rename(columns={
                "date":"Date",
                "open":"open",
                "high":"high",
                "low":"low",
                "close":"close"
                })

            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            df = df.loc[start_date:end_date]

            df = calculate_macd(df)
            df = detect_divergence(df)

            st.plotly_chart(plot_stock_with_macd(df))

            st.subheader('最近的背离信号：')
            recent_divergences = df[df['Bullish_Divergence'] | df['Bearish_Divergence']].tail(5)
            for date, row in recent_divergences.iterrows():
                if row['Bullish_Divergence']:
                    st.write(f"{date.date()}: 底背离 (价格: {row['close']:.2f}, MACD: {row['MACD']:.4f})")
                elif row['Bearish_Divergence']:
                    st.write(f"{date.date()}: 顶背离 (价格: {row['close']:.2f}, MACD: {row['MACD']:.4f})")

        except Exception as e:
            st.error(f'发生错误: {str(e)}')
            st.error('请确保输入了正确的股票代码。对于上证指数，请使用sh000001；对于个股，请使用类似sh600000的格式。')


if __name__ == "__main__":
    app()
