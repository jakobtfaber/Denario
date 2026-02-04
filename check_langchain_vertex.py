try:
    from langchain_google_vertexai import ChatVertexAI
    print("ChatVertexAI is available.")
    
    try:
        model = ChatVertexAI(model_name="gemini-3-flash-preview", location="global")
        print("ChatVertexAI accepts location='global'.")
    except Exception as e:
        print(f"ChatVertexAI instantiation failed: {e}")

except ImportError:
    print("langchain_google_vertexai not found.")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("ChatGoogleGenerativeAI is available.")
    try:
        # Check if it accepts location or region
        model = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", location="global", google_api_key="AIza...")
        print("ChatGoogleGenerativeAI accepts location='global'.")
    except TypeError:
         print("ChatGoogleGenerativeAI does NOT accept location='global'.")
    except Exception as e:
         print(f"ChatGoogleGenerativeAI check failed: {e}")

except ImportError:
    print("langchain_google_genai not found.")
