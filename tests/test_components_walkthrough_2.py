import os
import shutil
import sys
from pathlib import Path
from denario import Denario, Journal, models
import denario as denario_module
print(f"DEBUG: Denario module file: {denario_module.__file__}")

# Define test project directory
TEST_PROJECT_DIR = os.path.join(os.getcwd(), "TestProject_Walkthrough_2")

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
    description = """
    We have a dataset of simple harmonic oscillator simulations.
    The goal is to analyze the period of oscillation as a function of mass and spring constant.
    Data is not provided, but we can simulate it using Python.
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
        # Use a cheaper/faster model if possible
        model = models["gpt-4o-mini"]
        denario.get_idea(mode="fast", llm=model)
        if denario.research.idea:
            print("✅ get_idea successful.")
            print(f"Idea snippet: {denario.research.idea[:100]}...")
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
            print(f"Method snippet: {denario.research.methodology[:100]}...")
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
        # Reduce attempts/steps for test
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
            print(f"Results snippet: {denario.research.results[:100]}...")
        else:
            print("❌ get_results failed: Results are empty.")
    except Exception as e:
        print(f"❌ get_results failed: {e}")
        # Don't exit here, let's see if we can continue to paper generation if we have results manually set
        # But for this test, we want to see if it works.

def test_get_paper(denario):
    print("\n>>> Testing get_paper...")
    try:
        model = models["gpt-4o-mini"]
        denario.get_paper(journal=Journal.NONE, llm=model, add_citations=False) 
        
        # Check if PDF exists
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
    # Manually set dummy results if get_results failed, just to test get_paper
    if not denario.research.results:
        denario.set_results("Dummy results because execution failed.")
    test_get_paper(denario)
    print("\n>>> Walkthrough Complete.")
