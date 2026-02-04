import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Tool, Part
import vertexai.generative_models as gm

# Initialize Vertex AI
PROJECT_ID = 'dsa110-contimg-project'
LOCATION = 'global'
vertexai.init(project=PROJECT_ID, location=LOCATION)

def execute_python_code(code: str):
    return "Executed: " + code

# NO TOOLS registered with the model (Simulating Execution Only / Hallucination)
model = GenerativeModel("gemini-1.5-flash-001") # Using 1.5 because 3 is preview and might behave differently?
# I should use the ACTUAL model I am using: gemini-3-flash-preview
# But I might need to verify if it exists.
# I'll try gemini-1.5-flash first as proxy, OR gemini-exp-1114.
# The user script uses "gemini-3-flash-preview".

try:
    model_3 = GenerativeModel("gemini-3-flash-preview") 
except:
    model_3 = GenerativeModel("gemini-1.5-flash")

chat = model_3.start_chat()

print("Sending message to provoke hallucination...")
try:
    # Explicitly ask for the tool call
    response = chat.send_message(
        "Please use the tool 'execute_python_code' to print 'Hello World'. "
        "The tool signature is execute_python_code(code: str). DO NOT output text, just the tool call."
    )
    print("Response received (Unexpected Success):")
    print(response)
except Exception as e:
    print(f"\nCaught Exception type: {type(e).__name__}")
    print(f"Exception string: {str(e)}")
    print("\nDir(e):", dir(e))
    if hasattr(e, 'args'):
        print("\nArgs:", e.args)
    
    
    if hasattr(e, 'responses'):
        print("\nhasattr(e, 'responses') is True")
        # e.responses is typically a list of GenerationResponse
        try:
            resp_list = list(e.responses)
            print(f"e.responses length: {len(resp_list)}")
            
            for i, r in enumerate(resp_list):
                 print(f"\nResponse {i}:")
                 # Check candidates
                 print(f"  Candidates count: {len(r.candidates)}")
                 if r.candidates:
                     cand = r.candidates[0]
                     print(f"  Candidate 0 Finish Reason: {cand.finish_reason}")
                     # Inspect content parts
                     for part in cand.content.parts:
                         print(f"  Part: {part}")
                         if part.function_call:
                              print(f"  FOUND FUNCTION CALL: {part.function_call}")
        except Exception as inner_e:
            print(f"Error inspecting responses: {inner_e}")

