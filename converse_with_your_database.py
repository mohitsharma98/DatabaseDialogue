from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
import streamlit as st
import os

def retrieve_from_db(query: str) -> str:
    db_context = db_chain(query)
    db_context = db_context['result'].strip()
    return db_context

def generate(query: str) -> str:
    db_context = retrieve_from_db(query)
    
    system_message = """You are a professional representative of an employment agency. You are MySQL Expert.
        You have to answer user's queries and provide relevant information to help in their job search. 
        Example:
        
        Input:
        Where are the most number of jobs for an English Teacher in Canada?
        
        Context:
        The most number of jobs for an English Teacher in Canada is in the following cities:
        1. Ontario
        2. British Columbia
        
        Output:
        The most number of jobs for an English Teacher in Canada is in Toronto and British Columbia
        """
    
    human_qry_template = HumanMessagePromptTemplate.from_template(
        """Input:
        {human_input}
        
        Context:
        {db_context}
        
        Output:
        """
    )
    messages = [
      SystemMessage(content=system_message),
      human_qry_template.format(human_input=query, db_context=db_context)
    ]
    response = llm(messages).content
    return response

if "__main__"==__name__:
    OPENAI_API_KEY = "<YOUR OPENAI KEY HERE>"
    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)

    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    st.image("new_image.png", use_column_width=True)
    st.title("🤖 DataDialogue: Talk to your Database")

    selected_option = st.selectbox(
        'Please select a Database',
        ('Customers Database', 'Employee Database')
    )
    if selected_option is not None:
        if selected_option == "Employee Database":
            schema_name = "employee"
            table_list = ["employees", "jobs", "departments"]
            st.image("emp_database_erd.png", use_column_width=True)

        elif selected_option == "Customers Database":
            schema_name = "classicmodels"
            table_list = ["customers", "orders", "payments"]
            st.image("customers_database_erd.png", use_column_width=True)

    host = 'localhost'
    port = '3306'
    username = 'root'
    password = '<YOUR ROOT PASSWORD>'
    database_schema = schema_name
    mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"
    
    prompt = st.text_input('Ask me anything related to this Database.')

    if len(prompt) > 0:
        db = SQLDatabase.from_uri(mysql_uri, include_tables=table_list,sample_rows_in_table_info=2)
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        response = generate(prompt)
        st.write(response)
