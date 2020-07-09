import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import time
from nltk.tokenize import sent_tokenize
import re
#from newspaper import Article

#from functions import pred_percent, pred_sent, pred_array
import ast

from selenium import webdriver
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

from sqlalchemy import create_engine
from sqlalchemy.sql import select, update
from sqlalchemy import MetaData, Table,Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///data_15.db", echo = True)
db = scoped_session(sessionmaker(bind=engine))
conn = engine.connect()
#create or define the database table
meta = MetaData()
news = Table('news', meta, Column('ID', Integer, primary_key=True) , Column('city', String), Column('month', Integer),Column('url', String),
Column('text', String),Column('title', String),Column('summary', String),Column('keywords', String),
Column('sents', String),Column('percent', String),Column('doc', String), )
meta.create_all(engine)
#############
st.sidebar.title("Annotation App")
st.sidebar.markdown("""Cities, Urbanisation and Human Needs Satisfaction | Ali Sobhani""")
tags = ['Physiology-sent-pos','Physiology-sent-neg','Physiology-trnd-pos','Physiology-trnd-neg',
 'Space-sent-pos','Space-sent-neg','Space-trnd-pos','Space-trnd-neg',
 'Mobility-sent-pos','Mobility-sent-neg','Mobility-trnd-pos','Mobility-trnd-neg',
 'Health-sent-pos','Health-sent-neg','Health-trnd-pos','Health-trnd-neg',
 'Saf&Sec-sent-pos','Saf&Sec-sent-neg','Saf&Sec-trnd-pos','Saf&Sec-trnd-neg',
 'Intimacy-sent-pos','Intimacy-sent-neg','Intimacy-trnd-pos','Intimacy-trnd-neg',
 'Aesthetics-sent-pos','Aesthetics-sent-neg','Aesthetics-trnd-pos','Aesthetics-trnd-neg',
 'Knowledge-sent-pos','Knowledge-sent-neg','Knowledge-trnd-pos','Knowledge-trnd-neg',
 'Innovation-sent-pos','Innovation-sent-neg','Innovation-trnd-pos','Innovation-trnd-neg',
 'Community-sent-pos','Community-sent-neg','Community-trnd-pos','Community-trnd-neg',
 'Society-sent-pos','Society-sent-neg','Society-trnd-pos','Society-trnd-neg',
 'Recreation-sent-pos','Recreation-sent-neg','Recreation-trnd-pos','Recreation-trnd-neg',
 'Relaxation-sent-pos','Relaxation-sent-neg','Relaxation-trnd-pos','Relaxation-trnd-neg',
 'Creativity-sent-pos','Creativity-sent-neg','Creativity-trnd-pos','Creativity-trnd-neg',
 'Productivity-sent-pos','Productivity-sent-neg','Productivity-trnd-pos','Productivity-trnd-neg',
 'Belonging-sent-pos','Belonging-sent-neg','Belonging-trnd-pos','Belonging-trnd-neg',
 'Recognition-sent-pos','Recognition-sent-neg','Recognition-trnd-pos','Recognition-trnd-neg',
 'Autonomy-sent-pos','Autonomy-sent-neg','Autonomy-trnd-pos','Autonomy-trnd-neg',
 'Liberty-sent-pos','Liberty-sent-neg','Liberty-trnd-pos','Liberty-trnd-neg',
 'spam']




#allow_output_mutation=True
#persist=True
@st.cache(allow_output_mutation=True)
def load_data(x):
    s = news.select(news.c.ID == x)
    result = conn.execute(s)
    for row in result:
        data = row
    (ID,city,month,url,text,title,summary,keywords,sents,percent,doc)=data
    data = {'ID':ID,'city':city,'month':month,'url':url,'text':text,'title':title,'summary':summary,'keywords':keywords,'sents':sents,'percent':percent,'doc':doc}
    return data

#def update_data(data,df,x):
#    v = data.to_dict(orient='record')
#    df[x].update(v[0])
#    df_out = pd.DataFrame(df)
#    df_out.to_csv('googlenews_top_monthly_2019_45cities_text_6.csv',index=False)

def update_data(x,upd):
    stmt = news.update().where(news.c.ID == x).values(sents= upd)
    conn.execute(stmt)

def import_data():
    df_1 = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval})
    df_1 = df_1.to_dict(orient='record')
    st.write(len(df_1))
    for row in df_1:
        db.execute('INSERT INTO news (city, month, url, text, title, summary, keywords, sents, percent) VALUES (:city, :month, :url, :text, :title, :summary, :keywords, :sents, :percent)',{"city": row['city'], "month": row['month'], "url": str(row['url']), "text": str(row['text']),"title": str(row['title']), "summary": str(row['summary']), "keywords": str(row['keywords']), "sents": str(row['sents']),"percent": str(row['percent'])})
    db.commit() 

##### FUNCTIONS FOR STYLE ######
def text_box(txt):
    txt = f"<span style='padding:4px;border-radius:3px;background-color:#f63366;color:white;font-size:12px'>{txt}</span>"
    return txt

#names=['ID','city','month','url','text','title','summary','keywords','sents','percent']

#st.markdown("Ali Sobhani is a <span style='border:1px #f63366 solid;padding:2px;border-radius:3px;'>nice</span> PhD Candidate",unsafe_allow_html=True)
#st.markdown("Ali Sobhani is a <span style='padding:2px;border-radius:3px;background-color:#f63366;color:white;'>nice</span> PhD Candidate",unsafe_allow_html=True)

#st.markdown(text_box("Ali Aghaye gol"),unsafe_allow_html=True)

#### LOAD DATA ####
########### import data from csv to database
if st.button('db','db'):
    import_data()
##########
x = st.sidebar.number_input(label='News ID',value=1 ,min_value=1,max_value=4000 ,step=1)
data = load_data(x)
#def load_data(x):
#    df = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval})
    #df = df.iloc [:,:]
#    data=df.iloc[x:x+1,:]
#    df = df.to_dict(orient='record')
#    return df , data


#data

##########



##### SIDE BAR #####
# Document Classification
st.sidebar.subheader("Document Level Annotation")
doc = st.sidebar.radio('Document Classification',('Direct Relevance','Indirect Relevance','Not Relevant'))
if st.sidebar.button('Update','doc_update'):
    data.doc[x] = doc
    update_data (data,df,x)

#### NEWS DATA ####
# Title
st.subheader(data['title'])

####### SCREEN SHOT ########
if st.button('Screenshot'):
    DRIVER = 'chromedriver.exe'
    driver = webdriver.Chrome(DRIVER)
    driver.get(data.iloc[0,2])
    screenshot = driver.save_screenshot('my_screenshot.png')
    driver.quit()
    st.image('my_screenshot.png',width=700)

# City
st.markdown(data['city'])
# url
st.write(data['url'])
# Summary
st.subheader("Summary")
st.write(data['summary'])
# Percent prediction
try:
    percent = ast.literal_eval(data['percent'])
    percent = pd.DataFrame.from_dict(percent, orient='index')
    percent.columns = ['percent']
    st.bar_chart(percent)
except:
    st.write("No sentiment has been predicted!")

# Keywords
st.write(data['keywords'])

st.markdown('---') # visual separation

st.subheader("Text")

tag_out={}
com_out={}
text_sents = ast.literal_eval(data['sents'])
for i, sent in enumerate(text_sents):
    st.write(sent['sent'])
    pred = sent['pred']
    st.markdown(f'*<span style="color:grey">Current Model prediction: </span> <span style="color:#f63366;font-size:14px;">{pred}</span>*', unsafe_allow_html=True)
    st.markdown(f"*<span style='color:grey'>New Tags: </span>*{text_box(sent['tag'])}", unsafe_allow_html=True)
    st.markdown(f"*<span style='color:grey'>Comments: </span><span style='font-size:14px;'>{sent['comment']}</span>*", unsafe_allow_html=True)
    
    #for tag in sent['tag']:
    #    st.markdown(text_box(tag),unsafe_allow_html=True)
    #st.write(sent['tag'])
    if st.checkbox('Edit',False,f'{x}{i}'):
        st.markdown('---')
        default = sent['tag']
        tag_out[f'{i}'] = st.multiselect('Tags',tags,key=i,default= default)
        com_out[f'{i}'] = st.text_area('Comments',value=str(sent['comment']), key=i)
        if st.button('Update',i):
            sent['tag'] = tag_out[f'{i}']
            sent['comment']=com_out[f'{i}']
            update_data(x,str(text_sents))   
        st.markdown('---')
    st.markdown('---')  
            #st.write(str(text_sents))


#        st.write('result: %s' % result)
#for i, sent in enumerate(data.sents[x]):
#    sent['tag'] = tag_out[f'{i}']

#


#st.button('add')

#st.button('add','01')
#st.button('add','02')



