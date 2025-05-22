import re
import os
import cmbagent

from .key_manager import KeyManager
from .utils import get_model_config_from_env

class Idea:
    """
    This class is used to develop a research project idea based on the data of interest.
    It makes use of two types of agents:

    - `idea_maker`: to generate new ideas.
    - `idea_hater`: to critique new ideas.
    
    The LLMs are provided the following instructions:

    - Ask `idea_maker` to generate 5 new research project ideas related to the datasets.
    - Ask `idea_hater` to critique these ideas.
    - Ask `idea_maker` to select and improve 2 out of the 5 research project ideas given the output of the `idea_hater`.
    - Ask `idea_hater` to critique the 2 improved ideas. 
    - Ask `idea_maker` to select the best idea out of the 2. 
    - Ask `idea_maker` to report the best idea in the form of a scientific paper title with a 5-sentence description. 

    Args:
        work_dir: working directory.
    """
    def __init__(self, 
                 keys : KeyManager,
                 idea_maker_model = "gpt-4o", 
                 idea_hater_model = "claude-3-7-sonnet",
                 work_dir = None, 
                ):
        
        if work_dir is None:
            raise ValueError("workdir must be provided")
        
        self.idea_dir = os.path.join(work_dir, "idea_generation_output")
        self.idea_maker_model = idea_maker_model
        self.idea_hater_model = idea_hater_model

        self.config = {}
        self.config["idea_maker"] = get_model_config_from_env(self.idea_maker_model, keys)
        self.config["idea_hater"] = get_model_config_from_env(self.idea_hater_model, keys)

        # Create directory if it doesn't exist
        os.makedirs(self.idea_dir, exist_ok=True)

        self.planner_append_instructions = r"""
        Given these datasets, and information, make a plan according to the following instructions: 

        - Ask idea_maker to generate 5 new research project ideas related to the datasets.
        - Ask idea_hater to critique these ideas.
        - Ask idea_maker to select and improve 2 out of the 5 research project ideas given the output of the idea_hater.
        - Ask idea_hater to critique the 2 improved ideas. 
        - Ask idea_maker to select the best idea out of the 2. 
        - Ask idea_maker to report the best idea in the form of a scientific paper title with a 5-sentence description. 

        The goal of this task is to generate a research project idea based on the data of interest. 
        Don't suggest to perform any calculations or analyses here. The only goal of this task is to obtain the best possible project idea.
        """
        
    def develop_idea(self, data_description: str):
        """
        Develops an idea based on the data description.

        Args:
            data_description: description of the data and tools to be used.
        """
        
        results = cmbagent.planning_and_control(data_description,
                              n_plan_reviews = 1,
                              max_plan_steps = 6,
                              idea_maker_model = self.idea_maker_model,
                              idea_hater_model = self.idea_hater_model,
                              plan_instructions=self.planner_append_instructions,
                              work_dir = self.idea_dir,
                              config = self.config
                             )

        chat_history = results['chat_history']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'idea_maker_nest':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None

        pattern = r'\*\*Ideas\*\*\s*\n- Idea 1:'
        replacement = "Project Idea:"
        task_result = re.sub(pattern, replacement, task_result)

        return task_result
