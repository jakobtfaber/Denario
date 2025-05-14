from typing import List
import os
import re
import cmbagent

class Experiment:
    """
    This class is used to perform the experiment.
    TODO: improve docstring
    """

    def __init__(self, research_idea: str, methodology: str, involved_agents: List[str] = ['engineer', 'researcher'], work_dir = None):
        if work_dir is None:
            raise ValueError("workdir must be provided")

        self.experiment_dir = os.path.join(work_dir, "experiment_generation_output")
        # Create directory if it doesn't exist
        os.makedirs(self.experiment_dir, exist_ok=True)


        involved_agents_str = ', '.join(involved_agents)

        self.planner_append_instructions = rf"""

        {research_idea}

        {methodology}


        Given these datasets, project idea and methodology, we want to perform the project analysis and generate the results, plots and insights.
        
        The goal is to perform the in-depth research and analysis. 

        The plan must strictly involve only the following agents: {involved_agents_str}.
        
        The goal here is to do the in-depth research and analysis, not an exploratory data analysis.

        The final step of the plan, carried out by the researcher agent, must be entirely dedicated to writting the full Results section of the paper or report. If this research project involves code implementation, this final step should report on all the qualitative and quantitative results, interpretations of the plots and key statistics, and references to the plots generated in the previous steps.
        The final result report will be what will be passed on to the paper writer agents, so all relevant information must be included in the final report (everything else will be discarded).
        
        """

        self.engineer_append_instructions = rf"""
        {research_idea}

        {methodology}


        Given these datasets, and information on the features and project idea and methodology, we want to perform the project analysis and generate the results, plots and key statistics.
        The goal is to perform the in-depth research and analysis. This means that you must generate the results, plots and key statistics.

        Warnings for computing and plotting: 
        - make sure dynamical ranges are well captured (carefully adjust the limits, binning, and log or linear axes scales, for each feature).

        For histograms (if needed):
        -Use log-scale for features with values spanning several orders of magnitudes.


        **GENERAL IMPORTANT INSTRUCTIONS**: You must print out in the console ALL the quantitative information that you think the researcher will need to interpret the results. (The researcher does not have access to saved data files, only to what you print out!)
        Remember that the researcher agent can not load information from files, so you must print ALL necessary info in the console (without truncation). For this, it may be necessary to change pandas (if using it) display options.

        """


        self.researcher_append_instructions =  rf"""
        {research_idea}

        {methodology}


        At the end of the session, your task is to generate a detailed/extensive **discussion** and **interpretation** of the results. 
        If quantitative results were derived you should provide interpretations of the plots and interpretations of the key statistics, including reporting meaningful quantitative results, tables and references to matarial previously generated in the session.
        The results should be reported in full (not a summary) and in academic style. The results report/section should be around 2000 words.

        The final result report will be what will be passed on to the paper writer agents, so all relevant information must be included in the final report (everything else will be discarded).

        """

    def run_experiment(self, data_description: str, engineer_model: str = "claude-3-7-sonnet-20250219", researcher_model: str = "o3-mini-2025-01-31", **kwargs):
        """
        Run the experiment.
        TODO: improve docstring
        """

        results = cmbagent.planning_and_control_context_carryover(data_description,
                            n_plan_reviews = 1,
                            max_n_attempts = 6,
                            max_plan_steps = 6,
                            max_rounds_control = 500,
                            engineer_model = engineer_model,
                            researcher_model = researcher_model,
                            plan_instructions=self.planner_append_instructions,
                            researcher_instructions=self.researcher_append_instructions,
                            engineer_instructions=self.engineer_append_instructions,
                            work_dir = self.experiment_dir
                            )
        chat_history = results['chat_history']
        final_context = results['final_context']
        
        try:
            for obj in chat_history[::-1]:
                if obj['name'] == 'researcher_response_formatter':
                    result = obj['content']
                    break
            task_result = result
        except:
            task_result = None
            
        MD_CODE_BLOCK_PATTERN = r"```[ \t]*(?:markdown)[ \t]*\r?\n(.*)\r?\n[ \t]*```"
        extracted_results = re.findall(MD_CODE_BLOCK_PATTERN, task_result, flags=re.DOTALL)[0]
        clean_results = re.sub(r'^<!--.*?-->\s*\n', '', extracted_results)
        self.results = clean_results
        self.plot_paths = final_context['displayed_images']

        return None


