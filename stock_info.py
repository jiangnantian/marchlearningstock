import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


def get_stock_info(stock_code):
    """获取股票详细信息"""    
    try:        
        stock_info = ak.stock_individual_info_em(symbol=stock_code)        
        return stock_info    
    except Exception as e:        
        st.error(f"获取股票信息时出错: {str(e)}")        
        return None
    
def get_stock_news(stock_code):    
    """获取股票相关新闻"""    
    try:        
        stock_news_em_df = ak.stock_news_em(symbol=stock_code)        
        return stock_news_em_df.head(10)  
    # 返回最新的5条新闻    
    except Exception as e:        
        st.error(f"获取新闻数据时出错: {str(e)}")        
        return None

def get_stock_data(stock_code):    
    """获取股票数据并绘制K线图"""    
    try:        
        # 获取3个月K线图        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        #使用akshare获取股票数据    
        df = ak.stock_zh_a_hist(symbol=stock_code, start_date=start_date, end_date=end_date, adjust="qfq")
        # 创建K线图        

        fig = go.Figure(data=[go.Candlestick(x=df['日期'],
                        open=df['开盘'],
                        high=df['最高'], 
                        low=df['最低'],
                        close=df['收盘'],
                        increasing_line_color = 'red',  # Red for positive changes    
                        decreasing_line_color = 'green'
                        ),  # Green for negative changes
                    ])
        # 更新布局        
        fig.update_layout(title=f'{stock_code} 股票K线图', xaxis_title='日期', yaxis_title='价格')
        return fig, df    
    except Exception as e:        
        st.error(f"获取股票数据时出错: {str(e)}")        
        return None, None

def app():
    st.title("增强版股票分析系统")
    stock_code=''
    stock_code=st.text_input("请输入股票代码。eg:'600519'")
    if stock_code:
        if st.button('分析'):
            with st.spinner('正在获取股票数据...'):
                info=get_stock_info(stock_code)
                st.subheader("基本信息：")

                st.write(info)
                news=get_stock_news(stock_code)
                st.subheader("相关新闻：")
                st.write(news)
                #get_stock_data(stock_code)
                fig,df=get_stock_data(stock_code)
                st.subheader("KLINE DATA：")
                st.write(df)
                st.plotly_chart(fig)
        elif st.button('是否进行AI智能分析（Y）ENTER！'):
            with st.spinner('AI正在综合分析数据...'):    
                st.subheader("AI分析结果以及投资结果：")
                st.subheader("这属于AI分析结果，敬请参考，切勿实际投资！")
                #analyze_stock_trend(stock_code, df, stock_info, news_df)


if __name__ == "__main__":
    app()