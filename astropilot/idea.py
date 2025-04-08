from cmbagent import CMBAgent
import copy
import re


class Idea:
    """
    This class is used to develop a research project idea based on the data of interest.
    """

    def __init__(self):
        self.planner_append_instructions = r"""
Given these datasets, and information, make a plan according to the following instructions: 

- Ask idea_maker to generate 5 new research project ideas related to the datasets and primordial non-Gaussianity.
- Ask idea_hater to critique these ideas.
- Ask idea_maker to select and improve 2 out of the 5 research project ideas given the output of the idea_hater.
- Ask idea_hater to critique the 2 improved ideas. 
- Ask idea_maker to select the best idea out of the 2. 
- Ask idea_maker to report the best idea in the form of a scientific paper title with a 1 sentence description. 


The plan must strictly involve only the following agents: 
- idea_maker: to generate new ideas.
- idea_hater: to critique new ideas.

You must not invoke any other agent than the ones listed above.


The goal of this task is to generate a research project idea based on the data of interest. 
Don't suggest to perform any calculations or analyses here. The only goal of this task is to obtain the best possible project idea.
    """

        self.plan_reviewer_append_instructions = r"""
Check that the agents called in each sub-task only include, if needed: 
- idea_maker: to generate new ideas.
- idea_hater: to critique new ideas.

The goal of this task is to generate a research project idea based on the data of interest. 
Don't suggest to perform any calculations or analyses here. The only goal of this task is to obtain the best possible project idea.
    """
        
    def develop_idea(self, data_description: str, **kwargs):

        ## planning
        cmbagent = CMBAgent()
        cmbagent.solve(data_description,
                    max_rounds=100,
                    initial_agent="planner",
                    shared_context = {'feedback_left': 1,
                                        'maximum_number_of_steps_in_plan': 6,
                                        'planner_append_instructions': self.planner_append_instructions,
                                        'plan_reviewer_append_instructions': self.plan_reviewer_append_instructions}
                    )
        planning_output = copy.deepcopy(cmbagent.final_context)

        ## control
        cmbagent.solve(data_description,
               max_rounds=500,
               initial_agent="control",
               shared_context = planning_output
              )
        
        try:
            for obj in cmbagent.chat_result.chat_history[::-1]:
                if obj['name'] == 'idea_maker_response_formatter':
                    result = obj['content']
                    break
            cmbagent.task_result = result
        except:
            cmbagent.task_result = None


        pattern = r'\*\*Ideas\*\*\s*\n- Idea 1:'
        replacement = "Project Idea:"
        cmbagent.task_result = re.sub(pattern, replacement, cmbagent.task_result)

        return cmbagent.task_result
