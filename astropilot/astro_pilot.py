from .idea import Idea
from .method import Method
from .experiment import Experiment
from .paper import write_paper
from pydantic import BaseModel, Field
from typing import List, Dict
from IPython.display import display, Markdown
import os
os.environ["CMBAGENT_DEBUG"] = "false"
os.environ["ASTROPILOT_DISABLE_DISPLAY"] = "true"

from .config import REPO_DIR

from cmbagent import CMBAgent
import shutil



class AstroPilot:
    class Research(BaseModel):
        data_description: str = Field(default="", description="The data description of the project")
        idea: str = Field(default="", description="The idea of the project")
        methodology: str = Field(default="", description="The methodology of the project")
        results: str = Field(default="", description="The results of the project")
        plot_paths: List[str] = Field(default_factory=list, description="The plot paths of the project")
        keywords: Dict[str, str] = Field(default_factory=dict, description="The AAS keywords describing the project")


    def __init__(self, input_data: 'AstroPilot.Research' = None, params={}):
        if input_data is None:
            input_data = AstroPilot.Research()  # Initialize with default values
        self.research = input_data
        self.params = params

    def set_data_description(self, data_description: str = None, **kwargs):
        if data_description is None:
            with open(os.path.join(REPO_DIR, 'input_files', 'data_description.md'), 'r') as f:
                data_description = f.read()
            data_description = data_description.replace("{path_to_project_data}", str(REPO_DIR)+ "/project_data/")
        self.research.data_description = data_description

    def show_data_description(self):
        display(Markdown(self.research.data_description))
        return None

    def get_idea(self, **kwargs):
        
        idea = Idea()
        idea = idea.develop_idea(self.research.data_description, **kwargs)
        self.research.idea = idea
        # Write idea to file
        idea_path = os.path.join(REPO_DIR, 'input_files', 'idea.md')
        with open(idea_path, 'w') as f:
            f.write(idea)
        return None
    
    def get_method(self, **kwargs):
        
        if self.research.idea == "":
            with open(os.path.join(REPO_DIR, 'input_files', 'idea.md'), 'r') as f:
                self.research.idea = f.read()

        method = Method(self.research.idea)
        methododology = method.develop_method(self.research.data_description, **kwargs)
        self.research.methodology = methododology

        # Write idea to file
        method_path = os.path.join(REPO_DIR, 'input_files', 'method.md')
        with open(method_path, 'w') as f:
            f.write(methododology)
        return None

    def get_results(self, **kwargs):
        if self.research.methodology == "":
            with open(os.path.join(REPO_DIR, 'input_files', 'method.md'), 'r') as f:
                self.research.methodology = f.read()

        experiment = Experiment(self.research.idea, self.research.methodology)
        run = experiment.run_experiment(self.research.data_description, **kwargs)
        self.research.results = experiment.results
        self.research.plot_paths = experiment.plot_paths

        # move plots to the plots folder in input_files/plots after clearing the folder
        plots_folder = os.path.join(REPO_DIR, 'input_files', 'plots')
        if os.path.exists(plots_folder):
            for file in os.listdir(plots_folder):
                os.remove(os.path.join(plots_folder, file))
        for plot_path in self.research.plot_paths:
            shutil.move(plot_path, plots_folder)

        # Write results to file
        results_path = os.path.join(REPO_DIR, 'input_files', 'results.md')
        with open(results_path, 'w') as f:
            f.write(self.research.results)
        return None
    
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
        self.research.keywords = aas_keywords
        return None
    
    def show_keywords(self):
        AAS_keyword_list = "\n".join(
                            [f"- [{keyword}]({self.research.keywords[keyword]})" for keyword in self.research.keywords]
                        )
        display(Markdown(AAS_keyword_list))
        return None


    def get_paper(self):
        return write_paper(self.params)