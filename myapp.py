import os
import streamlit as st
from langchain.chains import create_sql_query_chain
from langchain_google_genai import GoogleGenerativeAI
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
from googletrans import Translator


# Load environment variables
load_dotenv()

# Database connection parameters
db_user = "root"
db_password = "sujalsinha02022004"
db_host = "localhost"
db_name = "retail_sales_db"

# Set Streamlit page configuration
st.set_page_config(
    page_title="Multilingual Talking SQL",
    page_icon="🧠",
    layout="centered",
)

# Inject custom CSS for linear gradient background
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #0d1117, #1b2836);
            color: #c9d1d9;
            font-family: 'Arial', sans-serif;
        }
        .stTextInput > div > div > input {
            background-color: #161b22;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        .stButton > button {
            background-color: #238636;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5em 1em;
            font-size: 16px;
        }
        .stButton > button:hover {
            background-color: #2ea043;
        }
        .stMarkdown h1, .stMarkdown h3 {
            color: #58a6ff;
        }
        .stCodeBlock {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# Database connection setup
try:
    engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")
    db = SQLDatabase(engine, sample_rows_in_table_info=3)
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# Initialize LLM
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    st.error("Missing GOOGLE_API_KEY environment variable.")
    st.stop()

llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
chain = create_sql_query_chain(llm, db)

# Function to execute the query
def execute_query(question):
    try:
        response = chain.invoke({"question": question})
        sql_query = response.strip("```sql\n").strip("\n```")
        result = db.run(sql_query)
        return sql_query, result
    except ProgrammingError as e:
        st.error(f"SQL Execution Error: {e}")
        return None, None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, None

# Streamlit interface
st.title("🧠 MultiLingual Talking SQL")
st.subheader("Ask questions and generate SQL queries with results in different languages")

# Language selection dropdown
languages = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese": "zh-cn",
    "Hindi": "hi",
    "Japanese": "ja"
}

selected_language = st.selectbox("Select your language:", list(languages.keys()))
input_question = st.text_input("Enter your question:", placeholder="e.g., How many unique customers are there for each product category")

# Translate question to English
translator = Translator()
translated_question = translator.translate(input_question, src=languages[selected_language], dest="en").text


if st.button("Execute"):
    if translated_question.strip():
        sql_query, query_result = execute_query(translated_question)
        if sql_query and query_result is not None:
            st.markdown("### Generated SQL Query:")
            st.code(sql_query, language="sql")
            st.markdown("### Query Result:")
            st.write(query_result)
        else:
            st.warning("No result returned.")
    else:
        st.warning("Please enter a question.")
