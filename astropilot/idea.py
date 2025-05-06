import re
import os
import cmbagent

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
    - Ask `idea_maker` to report the best idea in the form of a scientific paper title with a 1 sentence description. 

    Args:
        work_dir: working directory.
    """
    def __init__(self, work_dir = None):
        if work_dir is None:
            raise ValueError("workdir must be provided")
        
        self.idea_dir = os.path.join(work_dir, "idea_generation_output")
        # Create directory if it doesn't exist
        os.makedirs(self.idea_dir, exist_ok=True)

        self.planner_append_instructions = r"""
Given these datasets, and information, make a plan according to the following instructions: 

- Ask idea_maker to generate 5 new research project ideas related to the datasets.
- Ask idea_hater to critique these ideas.
- Ask idea_maker to select and improve 2 out of the 5 research project ideas given the output of the idea_hater.
- Ask idea_hater to critique the 2 improved ideas. 
- Ask idea_maker to select the best idea out of the 2. 
- Ask idea_maker to report the best idea in the form of a scientific paper title with a 1 sentence description. 

The goal of this task is to generate a research project idea based on the data of interest. 
Don't suggest to perform any calculations or analyses here. The only goal of this task is to obtain the best possible project idea.
    """

#         self.plan_reviewer_append_instructions = r"""
# Check that the agents called in each sub-task only include, if needed: 
# - idea_maker: to generate new ideas.
# - idea_hater: to critique new ideas.

# The goal of this task is to generate a research project idea based on the data of interest. 
# Don't suggest to perform any calculations or analyses here. The only goal of this task is to obtain the best possible project idea.
#     """
        
    def develop_idea(self, data_description: str, **kwargs):
        """
        Develops an idea based on the data description.

        Args:
            data_description: description of the data and tools to be used.
        """

        # ## planning
        # cmbagent = CMBAgent()
        # cmbagent.solve(data_description,
        #             max_rounds=100,
        #             initial_agent="planner",
        #             shared_context = {'feedback_left': 1,
        #                                 'maximum_number_of_steps_in_plan': 6,
        #                                 'planner_append_instructions': self.planner_append_instructions,
        #                                 'plan_reviewer_append_instructions': self.plan_reviewer_append_instructions}
        #             )
        # planning_output = copy.deepcopy(cmbagent.final_context)

        # ## control
        # cmbagent.solve(data_description,
        #        max_rounds=500,
        #        initial_agent="control",
        #        shared_context = planning_output
        #       )
        
        results = cmbagent.planning_and_control(data_description,
                              n_plan_reviews = 1,
                              max_n_attempts = 4,
                              max_plan_steps = 6,
                              engineer_model = "gpt-4.1-2025-04-14",
                              plan_instructions=self.planner_append_instructions,
                              work_dir = self.idea_dir
                             )

        chat_history = results['chat_history']
        # final_context = results['final_context']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'idea_maker_response_formatter':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None


        pattern = r'\*\*Ideas\*\*\s*\n- Idea 1:'
        replacement = "Project Idea:"
        task_result = re.sub(pattern, replacement, task_result)

        return task_result
