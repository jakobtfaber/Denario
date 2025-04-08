from .idea import develop_idea
from .method import design_method
from .experiment import run_experiment
from .paper import write_paper
import os

from cmbagent import CMBAgent

os.environ["CMBAGENT_DEBUG"] = "false"
os.environ["ASTROPILOT_DISABLE_DISPLAY"] = "true"


class AstroPilot:
    def __init__(self, params={}):
        self.params = params

    def get_idea(self, **kwargs):
        return develop_idea(self.params, **kwargs)

    def get_method(self, **kwargs):
        return design_method(self.params, **kwargs)

    def run_experiment(self, **kwargs):
        return run_experiment(self.params, **kwargs)
    
    def get_keywords(self, input_text: str, n_keywords: int = 5, **kwargs):
        """
        Get AAS keywords from input text using astropilot.

        Args:
            input_text (str): Text to extract keywords from
            n_keywords (int, optional): Number of keywords to extract. Defaults to 5.
            **kwargs: Additional keyword arguments

        Returns:
            dict: Dictionary mapping AAS keywords to their URLs
        """
        cmbagent = CMBAgent()
        PROMPT = f"""
        {input_text}
        """
        cmbagent.solve(task="Find the relevant AAS keywords",
                max_rounds=50,
                initial_agent='aas_keyword_finder',
                mode = "one_shot",
                shared_context={
                'text_input_for_AAS_keyword_finder': PROMPT,
                'N_AAS_keywords': n_keywords,
                                }
                )
        aas_keywords = cmbagent.final_context['aas_keywords'] ## here you get the dict with urls
        return aas_keywords


    def get_paper(self):
        return write_paper(self.params)