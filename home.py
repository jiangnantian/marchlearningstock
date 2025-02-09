import streamlit as st
import time


def mock_login(username,pwd):
    time.sleep(5)
    return username=="tlj" and pwd=="99999"



username=st.text_input("Username:","tlj")
password=st.text_input("Password:","99999")



def app():
     
    if st.button("Login"):
        with st.spinner("Loding..."):
            login_result=mock_login(username,password)
            text= "success" if login_result else "failed"
            st.write(f"HELLO!{username},welcome longin {text}")
            st.title("欢迎来到美弛投资分析应用系统:heart:") 
            st.title("Home:heart:")  
            st.write("使用左侧的导航菜单来浏览不同的页面。")

    
if __name__ == "__main__":
    app()