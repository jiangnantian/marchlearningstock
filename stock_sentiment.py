import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pywencai


def safe_float(value):
    """Safely convert a value to float, returning 0 if conversion fails"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


# Page config
#st.set_page_config(page_title="市场情绪分析", page_icon="📈", layout="wide")


# Helper functions
def get_market_data(date):
    """获取指定日期的涨停和跌停数据"""
    try:
        date_str = date.strftime("%Y%m%d")
        limit_up_query = f"{date}涨停，成交金额排序"
        limit_down_query = f"{date}跌停，成交金额排序"
        limit_up_df = pywencai.get(query=limit_up_query, sort_key='成交额', sort_order='desc', loop=True)
        limit_down_df = pywencai.get(query=limit_down_query, sort_key='成交额', sort_order='desc', loop=True)
        return limit_up_df, limit_down_df
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None, None


def calculate_metrics(limit_up_df, limit_down_df, date):
    """计算市场指标"""
    if limit_up_df is None or limit_down_df is None:
        return {}

    date_str = date.strftime("%Y%m%d")
    metrics = {
        "涨停数量": len(limit_up_df),
        "跌停数量": len(limit_down_df),
        "涨停比": f"{len(limit_up_df)}:{len(limit_down_df)}",
        "封板率": round(
            len(limit_up_df[limit_up_df[f'最新涨跌幅'].apply(safe_float) >= 9.9]) / len(limit_up_df) * 100,
            2)  if len(limit_up_df) > 0 else 0,
        "连板率": round(
            len(limit_up_df[limit_up_df[f'连续涨停天数[{date_str}]'].apply(safe_float) > 1]) / len(limit_up_df) * 100,
            2)  if len(limit_up_df) > 0 else 0,
    }
    return metrics


def calculate_sentiment(metrics):
    """计算市场情绪指数"""
    if not metrics:
        return 50

    limit_up_count = int(metrics["涨停比"].split(":")[0])
    limit_down_count = int(metrics["涨停比"].split(":")[1])

    sentiment = (
        0.4 * (limit_up_count / (limit_up_count + limit_down_count) * 100) +
        0.3 * metrics["封板率"] +
        0.3 * metrics["连板率"]
    )
    return round(sentiment, 2)


# Main app
def app():
    st.title("A股市场情绪分析")

    # Date selection
    today = datetime.now().date()
    default_date = today - timedelta(days=1) # 默认显示昨天的数据
    selected_date = st.date_input("选择日期", value=default_date, max_value=today)

    if selected_date:
        # 获取数据
        limit_up_df, limit_down_df = get_market_data(selected_date)

        if limit_up_df is not None and limit_down_df is not None:
            # 计算指标
            metrics = calculate_metrics(limit_up_df, limit_down_df, selected_date)
            sentiment = calculate_sentiment(metrics)

            # 显示主要指标
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("涨停比", metrics["涨停比"])
            with col2:
                st.metric("封板率", f"{metrics['封板率']}%")
            with col3:
                st.metric("连板率", f"{metrics['连板率']}%")
            with col4:
                st.metric("情绪指数", sentiment)

            # 情绪温度计
            st.subheader("市场情绪温度计")

            fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=sentiment,
                        domain={'x': [0, 1],'y': [0, 1]},
                        gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color':"darkblue"},
                        'steps': [
                        {'range': [0, 20],'color':'lightgray'},
                        {'range': [20, 40],'color':'gray'},
                        {'range': [40, 60],'color':'lightgreen'},
                        {'range': [60, 80],'color':'orange'},
                        {'range': [80, 100],'color':'red'},
                        ],
                        'threshold': {
                        'line': {'color':"red",'width': 4},
                        'thickness': 0.75,
                        'value': 80
                        }
                        }
            ))

            st.plotly_chart(fig)


            print( limit_up_df)
            # 涨停股票列表
            st.subheader("今日涨停股票")
            date_str = selected_date.strftime("%Y%m%d")
            st.dataframe(
                        limit_up_df[['股票代码','股票简称','最新价','最新涨跌幅', f'成交额[{date_str}]',
                        f'连续涨停天数[{date_str}]']],
                        hide_index=True
            )
            # 跌停股票列表
            st.subheader("今日跌停股票")
            st.dataframe(
                        limit_down_df[
                        ['股票代码','股票简称','最新价','最新涨跌幅', f'成交额[{date_str}]']],
                        hide_index=True
            )
            # 下载数据按钮
            col1, col2 = st.columns(2)
            with col1:
                csv_limit_up = limit_up_df.to_csv(index=False)
                st.download_button(
                label="下载涨停股票数据",
                data=csv_limit_up,
                file_name=f"limit_up_stocks_{selected_date}.csv",
                mime="text/csv",
            )
            with col2:
                csv_limit_down = limit_down_df.to_csv(index=False)
                st.download_button(
                    label="下载跌停股票数据",
                    data=csv_limit_down,
                    file_name=f"limit_down_stocks_{selected_date}.csv",
                    mime="text/csv",
                )

        else:
            st.warning(f"未找到 {selected_date} 的市场数据")


if __name__ =="__main__":
    app()
