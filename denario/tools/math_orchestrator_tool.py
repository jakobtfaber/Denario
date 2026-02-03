"""
Tool wrapper for the PremiumMathematicalOrchestrator.
Allows agents to perform complex mathematical reasoning using intelligent routing
between MATLAB and Wolfram Alpha.
"""

from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from denario.providers.orchestrator import PremiumMathematicalOrchestrator

class MathOrchestratorInput(BaseModel):
    query: str = Field(description="The mathematical query or problem to solve. Can be symbolic, numeric, or a request for data analysis.")

class MathOrchestratorTool(BaseModel):
    """
    A tool that routes mathematical queries to the best available provider 
    (MATLAB for heavy numerics/signal processing, Wolfram Alpha for symbolic/knowledge).
    """
    name: str = "math_orchestrator"
    description: str = (
        "Useful for solving mathematical problems, performing signal processing, "
        "statistical analysis, optimization, and symbolic math. "
        "Automatically selects the best engine (MATLAB or Wolfram Alpha)."
    )
    orchestrator: PremiumMathematicalOrchestrator = Field(default_factory=PremiumMathematicalOrchestrator)

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:
            result = self.orchestrator.compute(query)
            return str(result)
        except Exception as e:
            return f"Computation failed: {str(e)}"

    def _arun(self, query: str):
        """Async run."""
        raise NotImplementedError("Async not implemented yet")

def create_math_tool(config: Optional[dict] = None) -> BaseTool:
    """Factory to create a LangChain-compatible math tool."""
    
    # We need to wrap the orchestrator in a class that LangChain accepts.
    # Since BaseTool is Pydantic v1 usually in LangChain but v2 in newer, 
    # the cleanest way is to use the 'tool' decorator or subclass BaseTool properly.
    
    # Let's define it dynamically to avoid Pydantic conflicts or use the standard subclass approach.
    
    class PremiumMathTool(BaseTool):
        name: str = "mathematical_computation"
        description: str = (
            "A powerful math engine. Use this for ANY mathematical computation, "
            "including integrals, derivatives, signal processing (FFT), statistics, "
            "matrix operations, and unit conversions. It automatically uses MATLAB "
            "or Wolfram Alpha as needed."
        )
        orchestrator: PremiumMathematicalOrchestrator = Field(default_factory=lambda: PremiumMathematicalOrchestrator(config))

        def _run(self, query: str) -> str:
            try:
                # The orchestrator returns a ComputationResult object
                result = self.orchestrator.compute(query)
                return str(result)
            except Exception as e:
                return f"Error executing math query: {str(e)}"
        
        def _arun(self, query: str):
            raise NotImplementedError("Async not supported")

    return PremiumMathTool()
