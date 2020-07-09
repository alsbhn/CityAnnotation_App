import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import time
from nltk.tokenize import sent_tokenize
import re
#from newspaper import Article
from selenium import webdriver
#from functions import pred_percent, pred_sent, pred_array
import ast

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table,Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://nnatuggcykjxws:c355bf5344cdb8089eed92b896c3fcf5e7c0656c499f2ef93884c3d09fca047f@ec2-35-153-12-59.compute-1.amazonaws.com:5432/dbc78rvmill0a3", echo = True) # database engine object from SQLAlchemy that manages connections to the database
                                                    # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))
#connection = engine.connect()
#create database table
meta = MetaData()
news = Table('news', meta, Column('ID', Integer, primary_key=True) , Column('city', String), Column('month', Integer),Column('url', String),
Column('text', String),Column('title', String),Column('summary', String),Column('keywords', String),
Column('sents', String),Column('percent', String),Column('doc', String), )
meta.create_all(engine)

DATE_TIME = "date/time"
DATA_URL = (
    "http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz"
)

st.title("Annotation App")
st.markdown(
"""
Cities, Urbanisation and Human Needs Satisfaction | Ali Sobhani
""")
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

i=0
x=0
@st.cache(persist=True,allow_output_mutation=True)
#def load_data(x):
#    df = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval})
    #df = df.iloc [:,:]
#    data=df.iloc[x:x+1,:]
#    df = df.to_dict(orient='record')
#    return df , data

def load_data(x):
    #data = db.execute("SELECT * FROM news WHERE ID = :ID", {"ID": x}).fetchall()
    data = db.execute("SELECT * FROM news WHERE ID = {}".format(x)).fetchall()  
    data = data [0]
    (ID,city,month,url,text,title,summary,keywords,sents,percent,doc)=data
    data = {'ID':ID,'city':city,'month':month,'url':url,'text':text,'title':title,'summary':summary,'keywords':keywords,'sents':sents,'percent':percent,'doc':doc}
    return  data

#def update_data(data,df,x):
#    v = data.to_dict(orient='record')
#    df[x].update(v[0])
#    df_out = pd.DataFrame(df)
#    df_out.to_csv('googlenews_top_monthly_2019_45cities_text_6.csv',index=False)

def update_data(x,col,upd):
    #query = "UPDATE news SET :col = :upd WHERE ID = :x", {"col": col, "upd": upd, "x": x}
    #st.write("UPDATE news SET :col = :upd WHERE ID = :x", {"col": col, "upd": upd, "x": x})
    db.execute("UPDATE news SET :col = :upd WHERE ID = :x", {"col": col, "upd": upd, "x": x})
    db.commit()    

if st.button('db','db'):
    df_1 = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval})
    df_1 = df_1.to_dict(orient='record')
    st.write(len(df_1))
    for row in df_1:
        db.execute('INSERT INTO news (city, month, url, text, title, summary, keywords, sents, percent) VALUES (:city, :month, :url, :text, :title, :summary, :keywords, :sents, :percent)',{"city": row['city'], "month": row['month'], "url": str(row['url']), "text": str(row['text']),"title": str(row['title']), "summary": str(row['summary']), "keywords": str(row['keywords']), "sents": str(row['sents']),"percent": str(row['percent'])})
    #db.execute("SELECT * FROM news city")
    db.commit()
    table = db.execute("SELECT * FROM news WHERE month = :month", {"month": 1}).fetchall()
    db.commit()
    st.write(len(table))
#names=['ID','city','month','url','text','title','summary','keywords','sents','percent']
#### LOAD DATA ####
x = st.number_input(label='News ID',value=1 ,min_value=1,max_value=4000 ,step=1)
#df , data = load_data(x)
data = load_data(x)

#data
#row = data.to_dict(orient='record')[0]

########### db



# import data from csv file
#f = open("googlenews_top_monthly_2019_45cities_text_6.csv")
#reader = csv.reader(f)
#for city, month, url, text, title, suammary, keywords, sents, percent, doc in reader: # loop gives each column a name
#    db.execute("INSERT INTO news (city, month, url, text, title, suammary, keywords, sents, percent, doc) VALUES (:city, :month, :url, :text, :title, :suammary, :keywords, :sents, :percent, :doc)",
#                {"city": city, "month": month, "url": url, "text": text, "title": title, "summary": suammary, "keywords": keywords, "sents": sents, "percent": percent, "doc": doc}) # substitute values from CSV line into SQL command, as per this dict
#db.commit() # transactions are assumed, so close the transaction finished


#######

st.write(engine.table_names())
metadata=MetaData()
c = Table('news',metadata,autoload=True,autoload_with=engine)
st.write(repr(c))

if st.button('insert','insert'):
    db.execute("UPDATE news SET doc = 'document added' WHERE ID = 7")
    db.commit()

if st.button('db','db'):
    df_1 = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval})
    df_1 = df_1.to_dict(orient='record')
    st.write(len(df_1))
    for row in df_1:
        db.execute('INSERT INTO news (city, month, url, text, title, summary, keywords, sents, percent) VALUES (:city, :month, :url, :text, :title, :summary, :keywords, :sents, :percent)',{"city": row['city'], "month": row['month'], "url": str(row['url']), "text": str(row['text']),"title": str(row['title']), "summary": str(row['summary']), "keywords": str(row['keywords']), "sents": str(row['sents']),"percent": str(row['percent'])})
    #db.execute("SELECT * FROM news city")
    db.commit()
    table = db.execute("SELECT * FROM news WHERE month = :month", {"month": 1}).fetchall()
    db.commit()
    st.write(len(table))
    #for item in table:
     #   st.write(item)
    #res = pd.read_sql(table,db.bind)
    #res
##########

#ddd = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv',converters={'percent':eval,'sents':eval})
#ddd
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
text_sents = ast.literal_eval(data['sents'])

if st.button('Update',123432):
        #sent['tag'] = tag_out[f'{i}']
        sent = {'sent':'ammat', 'pred':'ammehat', 'tag':'sdf2f2ff'}
        p = "UPDATE news SET sents = " + '"' + f"{str(sent)}" + '"' + f" WHERE ID = {x}"
        st.write(p)
        #update_data (x,"sents",str(sent))
        db.execute(p)
        db.commit()

for i, sent in enumerate(text_sents):
    st.write(sent['sent'])
    pred = sent['pred']
    st.markdown(f'*<span style="color:grey">Current Model prediction:</span> <span style="color:#f63366">{pred}</span>*', unsafe_allow_html=True)
    #st.write(sent['tag'])
    default = sent['tag']
    tag_out[f'{i}'] = st.multiselect('Tags',tags,key=i,default= default)
    if st.button('Update',i):
        sent['tag'] = tag_out[f'{i}']
        p = "UPDATE news SET sents = " + '"' + f"{str(sent)}" + '"' + f" WHERE ID = {x}"
        st.write(p)
        #update_data (x,"sents",str(sent))
        db.execute(p)
        db.commite()


#        st.write('result: %s' % result)
#for i, sent in enumerate(data.sents[x]):
#    sent['tag'] = tag_out[f'{i}']

#


#st.button('add')

#st.button('add','01')
#st.button('add','02')



