from .idea import Idea
from .method import Method
from .experiment import Experiment
from pydantic import BaseModel, Field
from typing import List, Dict
from IPython.display import display, Markdown
from .graph import build_graph
import asyncio
import time
import os
os.environ["CMBAGENT_DEBUG"] = "false"
os.environ["ASTROPILOT_DISABLE_DISPLAY"] = "true"

from .config import REPO_DIR as repo_dir_default
import cmbagent
import shutil

class Research(BaseModel):
    data_description: str = Field(default="", description="The data description of the project")
    idea: str = Field(default="", description="The idea of the project")
    methodology: str = Field(default="", description="The methodology of the project")
    results: str = Field(default="", description="The results of the project")
    plot_paths: List[str] = Field(default_factory=list, description="The plot paths of the project")
    keywords: Dict[str, str] = Field(default_factory=dict, description="The AAS keywords describing the project")

class AstroPilot:
    """
    AstroPilot main class.

    Args:
        input_data: Input data to be used. Employ default data if `None`.
        project_dir: Directory project. If `None`, use the current directory.
        clear_project_dir: Clear directory if `True`.
    """

    def __init__(self, input_data: Research | None = None, params={}, project_dir: str = repo_dir_default, clear_project_dir: bool = True):
        if input_data is None:
            input_data = Research()  # Initialize with default values
        self.clear_project_dir = clear_project_dir
        self.research = input_data
        self.params = params
        if project_dir != repo_dir_default:
            # Create directory if it doesn't exist, or clear it if it does
            new_dir = os.path.join(repo_dir_default, os.path.basename(project_dir))
            if os.path.exists(new_dir):
                if clear_project_dir:
                    shutil.rmtree(new_dir)
                else:
                    pass
            os.makedirs(new_dir, exist_ok=True)
            self.project_dir = new_dir 
        else:
            self.project_dir = project_dir

        self._setup_input_files()

    def _setup_input_files(self):
        input_files_dir = os.path.join(self.project_dir, 'input_files')
        
        # If directory exists, remove it and all its contents
        if os.path.exists(input_files_dir) and self.clear_project_dir:
            shutil.rmtree(input_files_dir)
            
        # Create fresh input_files directory
        os.makedirs(input_files_dir, exist_ok=True)

    def set_data_description(self, data_description: str | None = None, **kwargs) -> None:
        """
        Set the description of the data and tools to be used by the agents.

        Args:
            data_description: string or path to markdown file including the description of the tools and data. If None, assume that a `data_description.md` is present in `project_dir/input_files`.
        """

        if data_description is None:
            try:
                with open(os.path.join(self.project_dir, 'input_files', 'data_description.md'), 'r') as f:
                    data_description = f.read()
                data_description = data_description.replace("{path_to_project_data}", str(self.project_dir)+ "/project_data/")
            except FileNotFoundError:
                raise FileNotFoundError("Please provide an input string or markdown file with the data description.")

        elif data_description.endswith(".md"):
            with open(data_description, 'r') as f:
                data_description = f.read()

        elif isinstance(data_description, str):
            pass

        else:
            raise ValueError("Data description must be a string, a path to a markdown file or None if you want to load data description from input_files/data_description.md")

        self.research.data_description = data_description

        # overwrite the data_description.md file
        with open(os.path.join(self.project_dir, 'input_files', 'data_description.md'), 'w') as f:
            f.write(data_description)

    def show_data_description(self) -> None:
        """Show the data description set by the `set_data_description` method."""
        
        # display(Markdown(self.research.data_description))
        print(self.research.data_description)

    def get_idea(self, **kwargs) -> None:
        """Generate an idea making use of the data and tools described by the `set_data_description` method."""
        
        if self.research.data_description == "":
            with open(os.path.join(self.project_dir, 'input_files', 'data_description.md'), 'r') as f:
                self.research.data_description = f.read()

        idea = Idea(work_dir = self.project_dir)
        idea = idea.develop_idea(self.research.data_description, **kwargs)
        self.research.idea = idea
        # Write idea to file
        idea_path = os.path.join(self.project_dir, 'input_files', 'idea.md')
        with open(idea_path, 'w') as f:
            f.write(idea)
    
    def set_idea(self, idea: str = None):
        if idea is None:
            with open(os.path.join(self.project_dir, 'input_files', 'idea.md'), 'r') as f:
                idea = f.read()
        elif idea.endswith(".md"):
            with open(idea, 'r') as f:
                idea = f.read()
        elif isinstance(idea, str):
            pass
        else:
            raise ValueError("Idea must be a string, a path to a markdown file or None if you want to load idea from input_files/idea.md")
        
        self.research.idea = idea
        # write idea to idea.md file
        with open(os.path.join(self.project_dir, 'input_files', 'idea.md'), 'w') as f:
            f.write(idea)
        return None
    
    def show_idea(self):
        # display(Markdown(self.research.idea))
        print(self.research.idea)
        return None
    
    def get_method(self, **kwargs):

        if self.research.data_description == "":
            with open(os.path.join(self.project_dir, 'input_files', 'data_description.md'), 'r') as f:
                self.research.data_description = f.read()        

        if self.research.idea == "":
            with open(os.path.join(self.project_dir, 'input_files', 'idea.md'), 'r') as f:
                self.research.idea = f.read()

        method = Method(self.research.idea, work_dir = self.project_dir)
        methododology = method.develop_method(self.research.data_description, **kwargs)
        self.research.methodology = methododology

        # Write idea to file
        method_path = os.path.join(self.project_dir, 'input_files', 'methods.md')
        with open(method_path, 'w') as f:
            f.write(methododology)
        return None
    
    def set_method(self, method: str = None):
        # write method to method.md file
        with open(os.path.join(self.project_dir, 'input_files', 'methods.md'), 'w') as f:
            f.write(method)
        return None
    
    def show_method(self):
        display(Markdown(self.research.methodology))
        return None

    def get_results(self, involved_agents: List[str] = ['engineer', 'researcher'], **kwargs):

        if self.research.data_description == "":
            with open(os.path.join(self.project_dir, 'input_files', 'data_description.md'), 'r') as f:
                self.research.data_description = f.read()

        if self.research.idea == "":
            with open(os.path.join(self.project_dir, 'input_files', 'idea.md'), 'r') as f:
                self.research.idea = f.read()

        if self.research.methodology == "":
            with open(os.path.join(self.project_dir, 'input_files', 'methods.md'), 'r') as f:
                self.research.methodology = f.read()


        experiment = Experiment(self.research.idea, self.research.methodology, involved_agents=involved_agents, work_dir = self.project_dir)
        run = experiment.run_experiment(self.research.data_description, **kwargs)
        self.research.results = experiment.results
        self.research.plot_paths = experiment.plot_paths

        # move plots to the plots folder in input_files/plots 
        plots_folder = os.path.join(self.project_dir, 'input_files', 'plots')
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
        results_path = os.path.join(self.project_dir, 'input_files', 'results.md')
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
        
        aas_keywords = cmbagent.get_keywords(input_text, n_keywords = n_keywords)
        self.research.keywords = aas_keywords
        return None
    
    def show_keywords(self):
        AAS_keyword_list = "\n".join(
                            [f"- [{keyword}]({self.research.keywords[keyword]})" for keyword in self.research.keywords]
                        )
        display(Markdown(AAS_keyword_list))
        return None


    def get_paper(self):
        # Start timer
        start_time = time.time()
        config = {"configurable": {"thread_id": "1"}, "recursion_limit":100}


        # build graph
        graph = build_graph(mermaid_diagram=False)
        path_to_input_files = os.path.join(self.project_dir, "input_files")
        
        # run the graph
        result = asyncio.run(graph.ainvoke(
            {"files":{  "Folder":      path_to_input_files,   #name of folder containing input files
                        "Idea":         "idea.md",    #name of file containing idea description
                        "Methods":      "methods.md", #name of file with methods description
                        "Results":      "results.md", #name of file with results description
                        "Plots":        "plots"},     #name of folder containing plots
            "llm": {"model": "gemini-2.0-flash"},  #name of the LLM model to use
            }, config))

        # End timer and report duration in minutes and seconds
        end_time = time.time()
        elapsed_time = end_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        print(f"Paper written in {minutes} min {seconds} sec.")
        return None
    

    def research_pilot(self, data_description: str = None):
        self.set_data_description(data_description)
        self.get_idea()
        self.get_method()
        self.get_results()
        self.get_paper()
        return None