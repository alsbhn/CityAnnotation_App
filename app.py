import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import time
from nltk.tokenize import sent_tokenize
import re
from selenium import webdriver
import os
import seaborn as sns

import ast
import pybase64

from sqlalchemy import create_engine
from sqlalchemy.sql import select, update
from sqlalchemy import MetaData, Table,Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://kcxahjdiqiplht:5185547847f6443735fa4d1e9023d729cef3960492920819d276af7f73c8a6b2@ec2-35-174-88-65.compute-1.amazonaws.com:5432/dd99dapkb4d7l2", echo = True)
db = scoped_session(sessionmaker(bind=engine))

#create or define the database table
meta = MetaData()
news = Table('news', meta, Column('ID', Integer, primary_key=True) , Column('city', String), Column('month', Integer),Column('url', String),
Column('text', String),Column('title', String),Column('summary', String),Column('keywords', String),
Column('sents', String),Column('percent', String),Column('doc_rel', String),Column('doc_top', String), )
meta.create_all(engine)
#############
st.sidebar.title("Annotation App")
st.sidebar.markdown("""Cities, Urbanisation and Human Needs Satisfaction | Ali Sobhani""")

tags = pd.read_csv('sentiments.csv',index_col=False).sents.tolist()

## Import Definitions Table csv File ##
definitions = pd.read_csv('definitions.csv',encoding='latin-1')
definitions = definitions.to_dict(orient='record')
#####


#allow_output_mutation=True
#persist=True
@st.cache(allow_output_mutation=True)
def load_data(x):
    s = news.select(news.c.ID == x)
    conn = engine.connect()
    result = conn.execute(s)
    conn.close()
    for row in result:
        data = row
    (ID,city,month,url,text,title,summary,keywords,sents,percent,doc_rel,doc_top)=data
    data = {'ID':ID,'city':city,'month':month,'url':url,'text':text,'title':title,'summary':summary,'keywords':keywords,'sents':sents,'percent':percent,'doc_rel':doc_rel,'doc_top':doc_top}
    return data

def update_data(x,upd):
    stmt = news.update().where(news.c.ID == x).values(sents= upd)
    conn = engine.connect()
    conn.execute(stmt)
    conn.close()

def import_data():
    df_1 = pd.read_csv('googlenews_top_monthly_2019_45cities_text_9.csv', converters={'sents':eval,'percent':eval,'doc_top':eval})
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
    doc_top = st.sidebar.multiselect('Topic',['General about city','Policy','Events and Incidents','Life of Residents'],default=doc_top_def)
    if st.sidebar.button('Update','doc_update'):
        stmt = news.update().where(news.c.ID == x).values(doc_top=str(doc_top),doc_rel=doc_rel)
        conn = engine.connect()
        conn.execute(stmt)
        conn.close()

def doc_class_side():
    st.sidebar.subheader("Document Level Annotation")
    if data['doc_rel'] != None:
        st.sidebar.markdown(f"<span style='border:1px #f63366 solid;padding:5px;border-radius:3px;'>{data['doc_rel']}</span>",unsafe_allow_html=True)
    try:
        for tag in ast.literal_eval(data['doc_top']):
            st.sidebar.markdown(f"<span style='padding:5px;border-radius:3px;background-color:#f63366;color:white;'>{tag}</span>",unsafe_allow_html=True)
    except:
        pass
            
##### FUNCTIONS FOR STYLE ######
def text_box(txt):
    txt = f"<span style='padding:5px;border-radius:3px;background-color:#f63366;color:white;font-size:13px'>{txt}</span>"
    return txt
def text_boarder(txt):
    txt = f"<span style='border:1px #f63366 solid;padding:2px;border-radius:3px;'>{txt}</span>"
    return txt  
def clean_t(r):
    r = str(r)
    r = r.replace("'","")
    r = r.replace("[","")
    r = r.replace("]","")
    return r
def ner_tag(tag):
    tags = ['ct','cz','org','st']
    tag_out = ['CITY','CITIZENS','ORGANIZATION','STATE']
    t=''
    try:
        t = tag_out[tags.index(tag)]
    except:
        pass
    return t
def text_ner(txt):
    txt = txt.split("_")
    txt_out=''
    for t in txt:
        if ":" in t:
            t = t.split(":")
            t = "<span style='border:1px #f63366 solid;padding:3px;border-radius:3px;font-weight: 500;'>"+t[0]+"</span>"+"<span style='padding:2px;border-radius:3px;background-color:#fffd80;color:grey;font-size:13px;margin-left:5px;font-weight: 400;'>"+ner_tag(t[1])+"</span>"
        txt_out = txt_out + t
    return txt_out

##### FUNCTIONS FOR Downloading The Data #######
def get_table_download_link(df):
            csv = df.to_csv(index=False)
            b64 = pybase64.b64encode(
                csv.encode()
            ).decode()  # some strings <-> bytes conversions necessary here
            return f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download csv file</a>'

def get_database(start,end):
    database = []
    p_bar = st.progress(0)
    for y in range(start,end+1):
        d = load_data(y)
        database.append(d)
        p_bar.progress(y/(end+1-start))
    database = pd.DataFrame(database)
    return database

def coocc_matrix(data):
    tags = ['Perception','Fact','Policy','Occasional','General','Local','City-wide']
    tags1 = ['obj', 'space', 'time', 'Imp']
    imp_list=['Slightly important','Very Important','Extreamly important']
    coocc=dict()
    for sent in data:
        for t in sent['tag']:
            for tt in tags:
                coocc.update({f'{t}':{}})
    for co in coocc:
        for t in tags:
            coocc[f'{co}'].update({f'{t}':0})
    for co in coocc:
        for sent in data:
            if co in sent['tag']:
                for t in tags:
                    for tt in tags1:
                        if t in sent[f'{tt}']:
                            try:
                                imp = imp_list.index(sent['Imp'][0])+1
                            except:
                                imp = 0
                            coocc[f'{co}'].update({f'{t}':coocc[f'{co}'][f'{t}']+imp})
    return pd.DataFrame(coocc)



##### FUNCTIONS FOR PAGES #######
def Result():
    st.subheader(data['title'])
    st.markdown(data['city'])
    st.write(data['url'])
    doc_class_side()
    for res in [('tag','Sentiment'),('obj','Objectivity'),('space','Scope | Space'),('time','Scope | Time')]:
        result = []
        l = len (ast.literal_eval(data['sents']))
        st.subheader(res[1])
        for sent in ast.literal_eval(data['sents']):
            imp_list = ['spam','Slightly important','Very Important','Extreamly important']
            try:
                imp = imp_list.index(sent['Imp'][0])
            except:
                imp = 0
            for j in range(imp): 
                result=result+sent[res[0]]
                
        result = dict((x,result.count(x)/l) for x in set(result))
        st.bar_chart(pd.Series(result))
    try:
        coocc = coocc_matrix(ast.literal_eval(data['sents']))
        sns.set(font_scale=0.7)
        sns.heatmap(coocc.T,square=True,cmap='Blues',annot=True,annot_kws={"size":7},robust=True,cbar=False)
        st.pyplot()
        
    except:
        pass

def Guid():
    st.header('Cities, Urbanization and Human Needs Satisfaction')  
    st.subheader('Ali Sobhani | Delft University of Technology')
    st.write('---')
    for definition in definitions:
        st.subheader(definition['Needs'])
        st.markdown(f"{text_boarder('Definition')} {definition['Definition']}",unsafe_allow_html=True)
        st.markdown(f"{text_boarder('Dimensions')} {text_box(definition['Dimensions'])}",unsafe_allow_html=True)
        st.markdown(f"{text_boarder('Satisfiers')} {definition['Satisfiers']}",unsafe_allow_html=True)

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
    components.iframe(data['url'],scrolling=True,height=300)
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
    space_out={}
    time_out={}
    Imp_out={}
    com_out={}
    sent_out={}
    text_sents = ast.literal_eval(data['sents'])
    for i, sent in enumerate(text_sents):
        st.markdown(text_ner(sent['sent']),unsafe_allow_html=True)
        pred = sent['pred']
        st.markdown(f'*<span style="color:grey">Current Model prediction: </span> <span style="color:#f63366;font-size:16px;">{clean_t(pred)}</span>*', unsafe_allow_html=True)
        st.markdown("*<span style='color:grey'>New Tags: </span>*",unsafe_allow_html=True)
        for aspct in ['tag','obj','space','time','Imp']:
            if sent[aspct] != []:
                st.markdown(f"{text_box(clean_t(sent[aspct]))}", unsafe_allow_html=True)
        st.markdown(f"*<span style='color:grey'>Comments: </span><span style='font-size:14px;'>{sent['comment']}</span>*", unsafe_allow_html=True)

        if st.checkbox('Edit',False,f'{x}{i}'):
            st.markdown('---')
            default = sent['tag']
            tag_out[f'{i}'] = st.multiselect('Sentiments',tags,key=i,default= default)
            obj_out[f'{i}'] = st.multiselect('Objectivity',['None','Perception','Fact','Policy'], key=f'{i}-obj',default=sent['obj'])
            space_out[f'{i}'] = st.multiselect('Scope | Space',['Local','City-wide'], key=f'{i}-spa',default=sent['space'])
            time_out[f'{i}'] = st.multiselect('Scope | time',['Occasional','General',],key=f'{i}-tim',default=sent['time'])
            Imp_out[f'{i}'] = st.multiselect('Importance',['Slightly important','Very Important','Extreamly important','Spam'],key=f'{i}-Imp',default=sent['Imp'])
            com_out[f'{i}'] = st.text_area('Comments',value=str(sent['comment']), key=i)
            if st.button('Update',i):
                sent['tag'] = tag_out[f'{i}']
                sent['comment']= com_out[f'{i}']
                sent['obj']= obj_out[f'{i}']
                sent['space']= space_out[f'{i}']
                sent['time']= time_out[f'{i}']
                sent['Imp']= Imp_out[f'{i}']
                update_data(x,str(text_sents))   
            st.markdown('---')
        if st.checkbox('NER',False,f'{x}{i}-ner'):
            sent_out[f'{i}']=st.text_area('ct: City, cz: Citizens, org: Organizations, st: State',value = sent['sent'],key= f"{i}-ner")
            if st.button('Update',f"{i}-ner"):
                if '%' in sent_out[f'{i}']:
                    split = sent_out[f'{i}'].split('%')
                    sent_out[f'{i}']=split[0]
                    text_sents.insert(i+1,{'sent': f'{split[1]}', 'pred': [], 'tag': [], 'comment': '', 'obj': [], 'space': [], 'time': [], 'Imp': []})
                sent['sent']=sent_out[f'{i}']
                update_data(x,str(text_sents))
        st.markdown('---')  
                
#### LOAD DATA ####
########### import data from csv to database
#if st.button('db','db'):
#    import_data()
##########


### LOGIN ##############################
user = st.sidebar.text_input('Username')
if user in ['Ali','Evert','Rodrigo','Martijn']:
########################################
    menu = st.sidebar.selectbox('Menu',['Annotation','Result','Guide','Data'],key='menu')
    x = st.sidebar.number_input(label='News ID',value=1 ,min_value=1,max_value=4206 ,step=1)
    data = load_data(x)
    ### ANNOTATION #########################
    if menu == 'Annotation':
        Annotation()

        ##### SIDE BAR #####
        # Document Classification
        doc_class_side()
        if st.sidebar.checkbox ('Edit',False,'edit-doc'):
            doc_edit()
               
    ########################################
    
    ### RESULT #############################
    if menu == 'Result':
        Result()
    ########################################
    
    ### GUIDE ##############################
    if menu == 'Guide':
        Guid()
    ########################################

    ### Data ###############################
    if menu == 'Data':
        start = st.number_input(label='Start index',value=1 ,min_value=1,max_value=4206 ,step=1)
        end = st.number_input(label='Start index',value=10 ,min_value=2,max_value=4206 ,step=1)
        if st.button(label='Produce Data',key='producedata'):
            database = get_database(start,end)
            st.markdown(get_table_download_link(database), unsafe_allow_html=True)







