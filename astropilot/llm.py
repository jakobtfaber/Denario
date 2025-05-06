import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
#GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY    = os.getenv("GOOGLE_API_KEY") if os.getenv("GOOGLE_API_KEY") else os.getenv("GEMINI_API_KEY")
#OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
#ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


#llm  = ChatGroq(model="llama3-8b-8192", temperature=0)
#llm  = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
#llm  = ChatGroq(model="gemma2-9b-it", temperature=0.7)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7,
                             max_output_tokens=8192)
#llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", temperature=0.7)
#llm2 = ChatOpenAI(model="gpt-4", temperature=0.5)
#llm3 = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
