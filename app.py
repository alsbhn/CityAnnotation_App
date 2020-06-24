import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
#import time
from nltk.tokenize import sent_tokenize
#import re
#from newspaper import Article
from selenium import webdriver
#from functions import pred_percent, pred_sent, pred_array


st.title("Annotation App")
st.markdown(
"""
Cities, Urabnization and Human Needs Satisfaction | Ali Sobhani
""")
i=0
x=0
@st.cache(persist=True)
def load_data(x):
    data = pd.read_csv('googlenews_top_monthly_2019_45cities_text.csv',skiprows=x,nrows=1)
    data = data.iloc[:,1:]
    return data



st.sidebar.multiselect("ad",('asda','asdad'))

x = st.number_input(label='number',value=0 ,min_value=0,max_value=4000 ,step=1)

st.sidebar.selectbox('select box',('asdasd','asdasd'))


data = load_data(x)
#data
###
st.sidebar.radio("need?",('subsistence','prot','aff'))
#st.text_area("adasd",data.iloc[0,3])

###
# Title
st.subheader(data.iloc[0,4])

#a=Article(data.iloc[0,2])
#a.download()
#a.parse()
#img = list(a.images)[-2]
#st.image(img,width=200)

#DRIVER = 'chromedriver.exe'
#driver = webdriver.Chrome(DRIVER)
#driver.get(data.iloc[0,2])
#screenshot = driver.save_screenshot('my_screenshot.png')
#driver.quit()
#st.image('my_screenshot.png',width=700)

st.subheader("Data")
data.iloc[0,2]
st.write(data.iloc[0,0],data.iloc[0,1],data.iloc[0,6])


st.subheader("Summary")
data.iloc[0,5]


st.subheader("Text")
text = data.iloc[0,3]


#pred_percent(text)

text = text.replace("\n"," ")
#text = re.sub(r"[^A-Za-z0-9^,.'-]", " ", text)
#text = re.sub(' +',' ', text)
for i, sent in enumerate (sent_tokenize(text)):
    st.write(sent)
    #st.write(pred_sent(sent))
    st.multiselect(f"sent {i+1}",('subsistence','protection','affection','participation'))


st.sidebar.subheader("Document Classification")
st.sidebar.checkbox("Relevant")
st.sidebar.checkbox("Document")