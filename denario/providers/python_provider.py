"""Python provider for Denario using Matplotlib/SciencePlots."""

import io
import time
import base64
import uuid
import traceback
import os
from typing import Dict, Any, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import scienceplots

from .base import MathematicalProvider, ComputationResult, ComputationError

class PythonProvider(MathematicalProvider):
    """
    Local Python provider specializing in visualization using SciencePlots.
    
    This provider executes Python code in a stateful local environment.
    It is specifically configured to generate publication-quality figures.
    """
    
    def __init__(self, work_dir: str = None, **kwargs):
        super().__init__(
            capabilities=['visualization', 'numeric', 'statistics', 'plotting'],
            cost_per_query=0.0,
            max_complexity="medium",
            priority=10, # High priority for visualization
            **kwargs
        )
        self.work_dir = work_dir or "/tmp/denario_plots"
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir, exist_ok=True)
        
        # Ensure we are using a non-interactive backend that writes to file
        import matplotlib
        matplotlib.use('Agg')
            
        # Initialize persistent session state
        self.local_namespace = {
            'np': np,
            'plt': plt,
            'os': os,
        }
        
        # Configure SciencePlots style
        try:
            plt.style.use(['science', 'notebook'])
        except Exception as e:
            print(f"Warning: Could not load SciencePlots style: {e}")
            
    def compute(self, query: str) -> ComputationResult:
        """
        Execute Python code to generate plots or computations.
        """
        start_time = time.time()
        
        # Capture stdout
        import sys
        from contextlib import redirect_stdout
        
        stdout_capture = io.StringIO()
        image_paths = []
        error = None
        result_val = None
        
        try:
            # Clear previous plots - BUT do not close figures inside the execution context
            # We want to allow the user code to create figures.
            # plt.clf() and plt.close('all') might be clearing what the user just created if called at wrong time.
            # But here we call it BEFORE exec, so it should be fine.
            # Wait, `plt.get_fignums()` returns list of figure numbers.
            # If user does `plt.plot()`, it creates a figure.
            
            # Reset state for new run
            plt.close('all') 
            
            with redirect_stdout(stdout_capture):
                exec(query, self.local_namespace)
                
            # Check if any plot was generated
            # Note: plt.get_fignums() works if the backend keeps track of figures.
            # In non-interactive backends, we might need to be careful.
            
            if plt.get_fignums():
                # Iterate over all open figures and save them
                for i, fig_num in enumerate(plt.get_fignums()):
                    fig = plt.figure(fig_num)
                    # Only save if the figure has content (axes)
                    if fig.get_axes():
                        filename = f"plot_{uuid.uuid4().hex[:8]}.png"
                        filepath = os.path.join(self.work_dir, filename)
                        
                        # Save with high DPI for publication quality
                        fig.savefig(filepath, dpi=300, bbox_inches='tight')
                        image_paths.append(filepath)
                
                # Also define 'last_plot' in namespace
                if image_paths:
                    self.local_namespace['last_plot'] = image_paths[-1]
            
            # Explicitly check for GCF if fignums is empty/not saved but GCF exists with axes
            # This handles the case where implicit plotting (plt.plot) was used but no explicit figure management
            if not image_paths:
                fig = plt.gcf()
                if fig.get_axes():
                     filename = f"plot_{uuid.uuid4().hex[:8]}.png"
                     filepath = os.path.join(self.work_dir, filename)
                     fig.savefig(filepath, dpi=300, bbox_inches='tight')
                     image_paths.append(filepath)
                     self.local_namespace['last_plot'] = filepath
            
            # Fallback: Check if user code created a file directly (e.g. plt.savefig)
            # This is hard to track without spying on FS. 
            # We assume for now relying on open figures is enough for the "agent" workflow.

            result_val = stdout_capture.getvalue()
            
            if not result_val and image_paths:
                result_val = f"Generated {len(image_paths)} plot(s): {', '.join(image_paths)}"
                
        except Exception as e:
            error = str(e)
            result_val = traceback.format_exc()
            
        execution_time = time.time() - start_time
        self._record_execution(execution_time)
        
        if error:
            raise ComputationError(f"Python execution failed: {error}")
            
        return ComputationResult(
            plaintext=str(result_val).strip(),
            images=image_paths,
            provider='python_scienceplots',
            cost=0.0,
            execution_time=execution_time,
            query=query
        )
        
    def get_session_keys(self) -> List[str]:
        """Return list of variables in the current session."""
        return list(self.local_namespace.keys())
