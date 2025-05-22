import os
import re
import cmbagent

from .key_manager import KeyManager
from .utils import get_model_config_from_env

class Method:
    """
    This class is used to develop a research project methodology based on the data of interest and the project idea.

    Args:
        work_dir: working directory.
    """

    def __init__(self,
                 research_idea: str,
                 keys: KeyManager,
                 researcher_model = "gpt-4.1-2025-04-14",
                 work_dir = None):
        
        self.researcher_model = researcher_model

        self.config = {}
        self.config["researcher"] = get_model_config_from_env(self.researcher_model, keys)

        if work_dir is None:
            raise ValueError("workdir must be provided")

        self.method_dir = os.path.join(work_dir, "method_generation_output")
        # Create directory if it doesn't exist
        os.makedirs(self.method_dir, exist_ok=True)
        self.planner_append_instructions = rf"""

        {research_idea}

        Instruction for planning:

        Given these datasets, and information on the features and project idea, we want to design a methodology to implement this idea.
        The goal of the task is to write a plan that will be used to generate a detailed description of the methodology that will be used to perform the research project.

        - Start by requesting the *researcher* to provide reasoning  relevant to the given project idea.
        - Clarify the specific hypotheses, assumptions, or questions that should be investigated.
        - This can be done in multiple steps. 



        - The focus should be strictly on the methods and workflow for this specific project to be performed. **Do not include** any discussion of future directions, future work, project extensions, or limitations.
        - The description should be written as if it were a senior researcher explaining to her research assistant how to perform the research necessary for this project.


        The final step of the plan must be entirely dedicated to writing the full Methodology description (it will be subsequently be saved under the name "full_methodology.md").

        The only agent involved in this workflow is the researcher.

        In this task we do not perform any calculations or analyses, only outline the methodology. 


        """

        self.researcher_append_instructions = rf"""
       {research_idea}

        Given this information, we want to design a methodology to implement this idea.
        The goal of the task is to develop a detailed methodology that will be used to carry out the research project.

        - You should focus on the methods for this specific project to be performed. **Do not include** any discussion of future directions, future work, project extensions, or limitations.
        - The methodology description should be written as if it were a senior researcher explaining to her research assistant how to perform the project. 

        The designed methodology should focus on describing the research and analysis that will be performed.

        The full methodology description will be saved under the name "full_methodology.md" and should be written in markdown format and include all the details of the designed methodology.
        It should be roughly 500 words long.
        """

    def develop_method(self, data_description: str):
        """
        Develops the methods based on the data description.

        Args:
            data_description: description of the data and tools to be used.
        """

        results = cmbagent.planning_and_control_context_carryover(data_description,
                              n_plan_reviews = 1,
                              max_n_attempts = 4,
                              max_plan_steps = 4,
                              researcher_model = self.researcher_model,
                              plan_instructions=self.planner_append_instructions,
                              researcher_instructions=self.researcher_append_instructions,
                              work_dir = self.method_dir
                             )
        
        chat_history = results['chat_history']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'researcher_response_formatter':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None
        MD_CODE_BLOCK_PATTERN = r"```[ \t]*(?:markdown)[ \t]*\r?\n(.*)\r?\n[ \t]*```"
        extracted_methodology = re.findall(MD_CODE_BLOCK_PATTERN, task_result, flags=re.DOTALL)[0]
        clean_methodology = re.sub(r'^<!--.*?-->\s*\n', '', extracted_methodology)
        return clean_methodology
