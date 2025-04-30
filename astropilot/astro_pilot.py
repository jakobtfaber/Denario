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

from .config import REPO_DIR as repo_dir_default

from cmbagent import CMBAgent
import shutil



class AstroPilot:


    def __init__(self, input_data: 'AstroPilot.Research' = None, params={}, repo_dir: str = repo_dir_default):
        if input_data is None:
            input_data = AstroPilot.Research()  # Initialize with default values
        self.research = input_data
        self.params = params
        self.repo_dir = repo_dir    

    class Research(BaseModel):
        data_description: str = Field(default="", description="The data description of the project")
        idea: str = Field(default="", description="The idea of the project")
        methodology: str = Field(default="", description="The methodology of the project")
        results: str = Field(default="", description="The results of the project")
        plot_paths: List[str] = Field(default_factory=list, description="The plot paths of the project")
        keywords: Dict[str, str] = Field(default_factory=dict, description="The AAS keywords describing the project")


    def set_data_description(self, data_description: str = None, **kwargs):
        if data_description is None:
            with open(os.path.join(self.repo_dir, 'input_files', 'data_description.md'), 'r') as f:
                data_description = f.read()
            data_description = data_description.replace("{path_to_project_data}", str(self.repo_dir)+ "/project_data/")

        elif data_description.endswith(".md"):
            with open(data_description, 'r') as f:
                data_description = f.read()

        elif isinstance(data_description, str):
            pass

        else:
            raise ValueError("Data description must be a string, a path to a markdown file or None if you want to load data description from input_files/data_description.md")
        

        self.research.data_description = data_description
        # overwrite the data_description.md file
        with open(os.path.join(self.repo_dir, 'input_files', 'data_description.md'), 'w') as f:
            f.write(data_description)
        return None

    def show_data_description(self):
        display(Markdown(self.research.data_description))
        return None

    def get_idea(self, **kwargs):
        
        idea = Idea()
        idea = idea.develop_idea(self.research.data_description, **kwargs)
        self.research.idea = idea
        # Write idea to file
        idea_path = os.path.join(self.repo_dir, 'input_files', 'idea.md')
        with open(idea_path, 'w') as f:
            f.write(idea)
        return None
    
    def set_idea(self, idea: str = None):
        # write idea to idea.md file
        with open(os.path.join(self.repo_dir, 'input_files', 'idea.md'), 'w') as f:
            f.write(idea)
        return None
    
    def show_idea(self):
        display(Markdown(self.research.idea))
        return None
    
    def get_method(self, **kwargs):

        if self.research.data_description == "":
            with open(os.path.join(self.repo_dir, 'input_files', 'data_description.md'), 'r') as f:
                self.research.data_description = f.read()        

        if self.research.idea == "":
            with open(os.path.join(self.repo_dir, 'input_files', 'idea.md'), 'r') as f:
                self.research.idea = f.read()

        method = Method(self.research.idea)
        methododology = method.develop_method(self.research.data_description, **kwargs)
        self.research.methodology = methododology

        # Write idea to file
        method_path = os.path.join(self.repo_dir, 'input_files', 'methods.md')
        with open(method_path, 'w') as f:
            f.write(methododology)
        return None
    
    def set_method(self, method: str = None):
        # write method to method.md file
        with open(os.path.join(self.repo_dir, 'input_files', 'methods.md'), 'w') as f:
            f.write(method)
        return None
    
    def show_method(self):
        display(Markdown(self.research.methodology))
        return None

    def get_results(self, involved_agents: List[str] = ['engineer', 'researcher'], **kwargs):

        if self.research.data_description == "":
            with open(os.path.join(self.repo_dir, 'input_files', 'data_description.md'), 'r') as f:
                self.research.data_description = f.read()

        if self.research.idea == "":
            with open(os.path.join(self.repo_dir, 'input_files', 'idea.md'), 'r') as f:
                self.research.idea = f.read()

        if self.research.methodology == "":
            with open(os.path.join(self.repo_dir, 'input_files', 'methods.md'), 'r') as f:
                self.research.methodology = f.read()


        experiment = Experiment(self.research.idea, self.research.methodology, involved_agents=involved_agents)
        run = experiment.run_experiment(self.research.data_description, **kwargs)
        self.research.results = experiment.results
        self.research.plot_paths = experiment.plot_paths

        # move plots to the plots folder in input_files/plots 
        plots_folder = os.path.join(self.repo_dir, 'input_files', 'plots')
        # Ensure the folder exists
        os.makedirs(plots_folder, exist_ok=True)
        ## Clearing the folder
        if os.path.exists(plots_folder):
            for file in os.listdir(plots_folder):
                file_path = os.path.join(plots_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        for plot_path in self.research.plot_paths:
            shutil.move(plot_path, plots_folder)

        # Write results to file
        results_path = os.path.join(self.repo_dir, 'input_files', 'results.md')
        with open(results_path, 'w') as f:
            f.write(self.research.results)
        return None
    
    def show_results(self):
        display(Markdown(self.research.results))
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
    

    def research_pilot(self, data_description: str = None):
        self.set_data_description(data_description)
        self.get_idea()
        self.get_method()
        self.get_results()
        self.get_paper()
        return None