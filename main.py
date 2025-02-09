import streamlit as st

import home
#import stock_uptop
#import stock_chanlun
import stock_boll
#import stock_kdj
#import stock_macd
#import stock_volume
#import stock_day_analyse
#import stock_springfestival_pnl
#import stock_month_pnl
#import stock_rsi
#import stock_jingjia
#import stock_sentiment
#import stock_up_analyse

PAGES = { "主页": home,
        #"涨停分析": stock_uptop,
        #"RSI": stock_rsi,   
        #"MACD": stock_macd,
        "BOLL": stock_boll,
        #"KDJ": stock_kdj,
        #"VOLUME": stock_volume,
        #"SPRINGFESTIVAL": stock_springfestival_pnl,
        #"MONTH_PNL": stock_month_pnl,
        #"CHANLUN": stock_chanlun,
        #"VOLUME": stock_volume,
        #"DAY_ANALYSE":stock_day_analyse,
        #"JINGJIA":stock_jingjia,
        #"SENTIMENT":stock_sentiment,
        #"DEEPSEEK1":deep1,
        #"DEEPSEEK3":deep3,
        #"STOCK_UP_ANAYLSE":stock_up_analyse
        }



def main():
    #st.set_page_config(page_title="MARCH股票分析应用",initial_sidebar_state="auto")
    st.sidebar.title("美弛股票分析导航:heart:")
    st.header("March investment!")
    selection = st.sidebar.radio("跳转到", list(PAGES.keys()))
    page = PAGES[selection]  
    page.app()

   


if __name__ == "__main__":  
    
    main()