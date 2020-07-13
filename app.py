import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import time
from nltk.tokenize import sent_tokenize
import re
from selenium import webdriver
import os

import ast

from sqlalchemy import create_engine
from sqlalchemy.sql import select, update
from sqlalchemy import MetaData, Table,Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://teebxnrpxkbgqo:f2c165c6d6271064b9504093d8f0a32264be230256bc867fec08e8a8891c1225@ec2-52-72-65-76.compute-1.amazonaws.com:5432/d1mb8mo4gt4v3s", echo = True)
db = scoped_session(sessionmaker(bind=engine))
conn = engine.connect()
#create or define the database table
meta = MetaData()
news = Table('news', meta, Column('ID', Integer, primary_key=True) , Column('city', String), Column('month', Integer),Column('url', String),
Column('text', String),Column('title', String),Column('summary', String),Column('keywords', String),
Column('sents', String),Column('percent', String),Column('doc_rel', String),Column('doc_top', String), )
meta.create_all(engine)
#############
st.sidebar.title("Annotation App")
st.sidebar.markdown("""Cities, Urbanisation and Human Needs Satisfaction | Ali Sobhani""")
tags = ['Physiology-sent-pos','Physiology-sent-neg','Physiology-trnd-pos','Physiology-trnd-neg','Physiology neut',
 'Space-sent-pos','Space-sent-neg','Space-trnd-pos','Space-trnd-neg','Space neut',
 'Mobility-sent-pos','Mobility-sent-neg','Mobility-trnd-pos','Mobility-trnd-neg','Mobility neut',
 'Health-sent-pos','Health-sent-neg','Health-trnd-pos','Health-trnd-neg','Health neut',
 'Saf&Sec-sent-pos','Saf&Sec-sent-neg','Saf&Sec-trnd-pos','Saf&Sec-trnd-neg','Saf&Sec neut',
 'Intimacy-sent-pos','Intimacy-sent-neg','Intimacy-trnd-pos','Intimacy-trnd-neg','Intimacy neut',
 'Aesthetics-sent-pos','Aesthetics-sent-neg','Aesthetics-trnd-pos','Aesthetics-trnd-neg','Aesthetics neut',
 'Knowledge-sent-pos','Knowledge-sent-neg','Knowledge-trnd-pos','Knowledge-trnd-neg','Knowledge neut',
 'Innovation-sent-pos','Innovation-sent-neg','Innovation-trnd-pos','Innovation-trnd-neg','Innovation neut',
 'Community-sent-pos','Community-sent-neg','Community-trnd-pos','Community-trnd-neg','Community neut',
 'Society-sent-pos','Society-sent-neg','Society-trnd-pos','Society-trnd-neg','Society neut',
 'Recreation-sent-pos','Recreation-sent-neg','Recreation-trnd-pos','Recreation-trnd-neg','Recreation neut',
 'Relaxation-sent-pos','Relaxation-sent-neg','Relaxation-trnd-pos','Relaxation-trnd-neg','Relaxation neut',
 'Creativity-sent-pos','Creativity-sent-neg','Creativity-trnd-pos','Creativity-trnd-neg','Creativity neut',
 'Productivity-sent-pos','Productivity-sent-neg','Productivity-trnd-pos','Productivity-trnd-neg','Productivity neut',
 'Belonging-sent-pos','Belonging-sent-neg','Belonging-trnd-pos','Belonging-trnd-neg','Belonging neut',
 'Recognition-sent-pos','Recognition-sent-neg','Recognition-trnd-pos','Recognition-trnd-neg','Recognition neut',
 'Autonomy-sent-pos','Autonomy-sent-neg','Autonomy-trnd-pos','Autonomy-trnd-neg','Autonomy neut',
 'Liberty-sent-pos','Liberty-sent-neg','Liberty-trnd-pos','Liberty-trnd-neg','Liberty neut']




#allow_output_mutation=True
#persist=True
@st.cache(allow_output_mutation=True)
def load_data(x):
    s = news.select(news.c.ID == x)
    result = conn.execute(s)
    for row in result:
        data = row
    (ID,city,month,url,text,title,summary,keywords,sents,percent,doc_rel,doc_top)=data
    data = {'ID':ID,'city':city,'month':month,'url':url,'text':text,'title':title,'summary':summary,'keywords':keywords,'sents':sents,'percent':percent,'doc_rel':doc_rel,'doc_top':doc_top}
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
    df_1 = pd.read_csv('googlenews_top_monthly_2019_45cities_text_6.csv', converters={'sents':eval,'percent':eval,'doc_top':eval})
    df_1 = df_1.to_dict(orient='record')
    st.write(len(df_1))
    for row in df_1:
        db.execute('INSERT INTO news (city, month, url, text, title, summary, keywords, sents, percent) VALUES (:city, :month, :url, :text, :title, :summary, :keywords, :sents, :percent)',{"city": row['city'], "month": row['month'], "url": str(row['url']), "text": str(row['text']),"title": str(row['title']), "summary": str(row['summary']), "keywords": str(row['keywords']), "sents": str(row['sents']),"percent": str(row['percent'])})
    db.commit() 

def doc_edit():
    if data['doc_rel'] == 'Not Relevant':
        doc_rel_ind = 1
    elif data['doc_rel'] == 'Relevant':
        doc_rel_ind = 2
    else:
        doc_rel_ind = 0
    doc_rel = st.sidebar.radio('Document Relevance',('Not Annotated','Not Relevant','Relevant'), index=doc_rel_ind)
    if data['doc_top'] == None:
        doc_top_def = []
    else:
        doc_top_def = ast.literal_eval(data['doc_top'])
    doc_top = st.sidebar.multiselect('Topic',['Strongly about city','Policy','Events and Incidents'],default=doc_top_def)
    if st.sidebar.button('Update','doc_update'):
        stmt = news.update().where(news.c.ID == x).values(doc_top=str(doc_top),doc_rel=doc_rel)
        conn.execute(stmt)
            
##### FUNCTIONS FOR STYLE ######
def text_box(txt):
    txt = f"<span style='padding:5px;border-radius:3px;background-color:#f63366;color:white;font-size:13px'>{txt}</span>"
    return txt
def clean_t(r):
    r = str(r)
    r = r.replace("'","")
    r = r.replace("[","")
    r = r.replace("]","")
    return r

##### FUNCTIONS FOR PAGES #######
def Guid():
    st.header('Cities, Urbanization and Human Needs Satisfaction')  
    st.subheader('Ali Sobhani | Delft University of Technology')

def Annotation():
    #### NEWS DATA ####
    # Title
    st.subheader(data['title'])

    ####### SCREEN SHOT ########
    if st.button('Screenshot'):
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

            driver.get(data['url'])
            driver.save_screenshot('my_screenshot.png')
            driver.quit()
            st.image('my_screenshot.png',width=700)
        except:
            st.write('Sorry! Cannot Load the Screenshot.')

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
    #st.markdown(f"Keywords: <span style='border:1px #f63366 solid;padding:2px;border-radius:3px;'>{data['keywords']}</span>",unsafe_allow_html=True)
    st.write(data['keywords'])

    st.markdown('---') # visual separation

    st.subheader("Text")

    tag_out={}
    obj_out={}
    scope_out={}
    veen_out={}
    Imp_out={}
    com_out={}
    text_sents = ast.literal_eval(data['sents'])
    for i, sent in enumerate(text_sents):
        st.write(sent['sent'])
        pred = sent['pred']
        st.markdown(f'*<span style="color:grey">Current Model prediction: </span> <span style="color:#f63366;font-size:16px;">{clean_t(pred)}</span>*', unsafe_allow_html=True)
        st.markdown("*<span style='color:grey'>New Tags: </span>*",unsafe_allow_html=True)
        for aspct in ['tag','obj','scope','veen','Imp']:
            if sent[aspct] != []:
                st.markdown(f"{text_box(clean_t(sent[aspct]))}", unsafe_allow_html=True)
        st.markdown(f"*<span style='color:grey'>Comments: </span><span style='font-size:14px;'>{sent['comment']}</span>*", unsafe_allow_html=True)

        if st.checkbox('Edit',False,f'{x}{i}'):
            st.markdown('---')
            default = sent['tag']
            tag_out[f'{i}'] = st.multiselect('Sentiments',tags,key=i,default= default)
            obj_out[f'{i}'] = st.multiselect('Objectivity',['None','Perception','Fact','Policy'], key=f'{i}-obj',default=sent['obj'])
            scope_out[f'{i}'] = st.multiselect('Scope',['None','Occasional','General','Local','City-wide'], key=f'{i}-sco',default=sent['scope'])
            veen_out[f'{i}'] = st.multiselect('Veenhoven Quadrant',['None','Presence of Satisfiers','Capabilities','Externalities','Subjective Satisfaction'],key=f'{i}-vee',default=sent['veen'])
            Imp_out[f'{i}'] = st.multiselect('Importance',['Not important','Slightly important','Important','Very Important','Extreamly important','Spam'],key=f'{i}-Imp',default=sent['Imp'])
            com_out[f'{i}'] = st.text_area('Comments',value=str(sent['comment']), key=i)
            if st.button('Update',i):
                sent['tag'] = tag_out[f'{i}']
                sent['comment']= com_out[f'{i}']
                sent['obj']= obj_out[f'{i}']
                sent['scope']= scope_out[f'{i}']
                sent['veen']= veen_out[f'{i}']
                sent['Imp']= Imp_out[f'{i}']
                update_data(x,str(text_sents))   
            st.markdown('---')
        st.markdown('---')  
                


#names=['ID','city','month','url','text','title','summary','keywords','sents','percent']

#st.markdown("Ali Sobhani is a <span style='border:1px #f63366 solid;padding:2px;border-radius:3px;'>nice</span> PhD Candidate",unsafe_allow_html=True)
#st.markdown("Ali Sobhani is a <span style='padding:2px;border-radius:3px;background-color:#f63366;color:white;'>nice</span> PhD Candidate",unsafe_allow_html=True)

#st.markdown(text_box("Ali Aghaye gol"),unsafe_allow_html=True)

#### LOAD DATA ####
########### import data from csv to database
if st.button('db','db'):
    import_data()
##########


### LOGIN ##############################
user = st.sidebar.text_input('Username')
if user in ['Ali','Evert','Rodrigo']:
########################################
    menue = st.sidebar.selectbox('Menue',['Annotation','Result','Guide'],key='menue')
    x = st.sidebar.number_input(label='News ID',value=1 ,min_value=1,max_value=4000 ,step=1)
    data = load_data(x)
    ### ANNOTATION #########################
    if menue == 'Annotation':
        Annotation()

        ##### SIDE BAR #####
        # Document Classification
        st.sidebar.subheader("Document Level Annotation")
        if data['doc_rel'] != None:
            st.sidebar.markdown(f"<span style='border:1px #f63366 solid;padding:5px;border-radius:3px;'>{data['doc_rel']}</span>",unsafe_allow_html=True)
        try:
            for tag in ast.literal_eval(data['doc_top']):
                st.sidebar.markdown(f"<span style='padding:5px;border-radius:3px;background-color:#f63366;color:white;'>{tag}</span>",unsafe_allow_html=True)
        except:
            pass
        if st.sidebar.checkbox ('Edit',False,'edit-doc'):
            doc_edit()
               
    ########################################

    ### GUIDE ##############################
    if menue == 'Guide':
        Guid()
         

