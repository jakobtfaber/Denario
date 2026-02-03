import os
import shutil
import sys
from pathlib import Path
from denario import Denario, Journal, models
import denario as denario_module

# Define test project directory
TEST_PROJECT_DIR = os.path.join(os.getcwd(), "TestProject_Walkthrough_3")

def test_initialization():
    print(">>> Testing Initialization...")
    try:
        denario = Denario(project_dir=TEST_PROJECT_DIR, clear_project_dir=True)
        print("✅ Initialization successful.")
        return denario
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)

def test_set_data(denario):
    print("\n>>> Testing set_data_description...")
    # Use a very simple description to avoid complex dependency installation
    description = """
    We want to calculate the first 10 Fibonacci numbers using Python.
    No external libraries should be required.
    Plot the values.
    """
    try:
        denario.set_data_description(description)
        print("✅ set_data_description successful.")
    except Exception as e:
        print(f"❌ set_data_description failed: {e}")
        sys.exit(1)

def test_get_idea(denario):
    print("\n>>> Testing get_idea (fast mode)...")
    try:
        model = models["gpt-4o-mini"]
        denario.get_idea(mode="fast", llm=model)
        if denario.research.idea:
            print("✅ get_idea successful.")
        else:
            print("❌ get_idea failed: Idea is empty.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ get_idea failed: {e}")
        sys.exit(1)

def test_get_method(denario):
    print("\n>>> Testing get_method (fast mode)...")
    try:
        model = models["gpt-4o-mini"]
        denario.get_method(mode="fast", llm=model)
        if denario.research.methodology:
            print("✅ get_method successful.")
        else:
            print("❌ get_method failed: Methodology is empty.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ get_method failed: {e}")
        sys.exit(1)

def test_get_results(denario):
    print("\n>>> Testing get_results...")
    try:
        model = models["gpt-4o-mini"]
        denario.get_results(
            engineer_model=model,
            researcher_model=model,
            planner_model=model,
            plan_reviewer_model=model,
            orchestration_model=model,
            formatter_model=model,
            max_n_attempts=3,
            max_n_steps=3
        )
        if denario.research.results:
            print("✅ get_results successful.")
        else:
            print("❌ get_results failed: Results are empty.")
    except Exception as e:
        print(f"❌ get_results failed: {e}")

def test_get_paper(denario):
    print("\n>>> Testing get_paper...")
    try:
        model = models["gpt-4o-mini"]
        # Use NONE journal to avoid complex latex requirements
        denario.get_paper(journal=Journal.NONE, llm=model, add_citations=False, cmbagent_keywords=True) 
        
        pdf_path = Path(TEST_PROJECT_DIR) / "paper" / "paper.pdf"
        if pdf_path.exists():
            print(f"✅ get_paper successful. PDF created at {pdf_path}")
        else:
            print("❌ get_paper failed: PDF not found.")
    except Exception as e:
        print(f"❌ get_paper failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    denario = test_initialization()
    test_set_data(denario)
    test_get_idea(denario)
    test_get_method(denario)
    test_get_results(denario)
    # Ensure results exist for paper generation even if execution failed
    if not denario.research.results:
        denario.set_results("Results could not be generated automatically. These are placeholder results.")
    test_get_paper(denario)
    print("\n>>> Walkthrough Complete.")
