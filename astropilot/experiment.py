from cmbagent import CMBAgent
import copy
import os
import re
class Experiment:


    def __init__(self, research_idea: str, methodology: str):
        self.planner_append_instructions = rf"""

        {research_idea}

        {methodology}

        Given these datasets, and information on the features and project idea and methodology, we want to perform the project analysis and generate the results, plots and insights.
        The goal is to perform the in-depth research and analysis. 

        The plan must strictly involve only the following agents: 

        - engineer: an expert Python coder who writes entire Python pipelines ready to be executed, and generates results, plots and key statistics. It does not aim to discuss the results of the code, only to write the code.
        - researcher: an expert researcher that produces reasoning but does not run code. This agent also discusses and interprets results. 

        You must not invoke any other agent than the ones listed above.

        In the final step of the plan, researcher should generate extensive insights (around 2000 words), including discussion of quantitative results and plots previously generated. This final report is intended to be the core material of the Results section of a paper.
        The last agent in the plan must be the researcher.

        **Agents roles**:
        - engineer: To generate the results and do the computations, plots and key statistics via code pipelines.
        - researcher: To generate the discussion and interpretation of the results. This agent does not run code or see plots. It only discusses results.

        The goal here is to do the in-depth research and analysis, not the EDAs.
        """

        self.plan_reviewer_append_instructions = rf"""
            {research_idea}

            {methodology}

            Check that the agents called in each sub-task only include, if needed: 
            - engineer: an expert Python coder who writes entire Python pipelines ready to be executed, and generates results, plots and key statistics. It does not aim to discuss the results of the code, only to write the code.
            - researcher: an expert researcher that produces reasoning but does not run code. This agent also discusses and interprets results. 

        **Agents roles**:
        - engineer: To generate the results and do the computations, plots and key statistics via code pipelines.
        - researcher: To generate the discussion and interpretation of the results.

        The goal here is to do the in-depth research and analysis, not the EDAs.

        In the final step of the plan, researcher should generate extensive insights (around 2000 words), including discussion of quantitative results and plots previously generated. This final report is intended to be the core material of the Results section of a paper.
        The last agent in the plan must be the researcher.
        """

        self.engineer_append_instructions = rf"""
        {research_idea}

        {methodology}

        Given these datasets, and information on the features and project idea and methodology, we want to perform the project analysis and generate the results, plots and key statistics.
        The goal is to perform the in-depth research and analysis. This means that you must generate the results, plots and key statistics.

        Warnings for computing and plotting: 
        Some feature columns have around 40k non-null entries. Although vectorized operations (like np.percentile, np.concatenate) are efficient, they do take longer on larger arrays. 
        You must make sure the code is well optimized for operations on large arrays. 

        For plots involving features: 
        - make sure dynamical ranges are well captured (carefully adjust the binning, and log or linear axes scales, for each feature).

        For histograms (if needed):
        -Use log-scale for features with values spanning several orders of magnitudes. 
        -If photometric fatures are needed, use linear scale for Photometrics feature, but in general **log-log in both x and y axes will be useful!**
        -Don't include null or nan values in the histogram counts, nonetheless, although the NaN entries are useless, it might be useful to keep track of the zero counts for some features.

        **IMPORTANT**: You must print out in the console ALL the quantitative information that you think the researcher will need to interpret the results. (The researcher does not have access to saved data files, only to what you print out!)

        **Agents roles**:
        - engineer: To generate the results and do the computations, plots and key statistics via code pipelines.
        - researcher: To generate the discussion and interpretation of the results. This agent does not run code or see plots. It only discusses results.

        """


        self.researcher_append_instructions =  rf"""
        {research_idea}

        {methodology}

        Given the results, plots and key statistics generated by the engineer, your task is to generate a detailed **discussion** and **interpretation** of the results, plots and key statistics, including reporting meaningful quantitative results, tables and references to the plots previously generated in the session.
        At the end the goal is to generate the in-depth research report (around 2000 words) based on the results, plots and key statistics provided by the engineer, which will form the core material of a result section of a paper.

        """

    def run_experiment(self, data_description: str, **kwargs):

        ## planning
        cmbagent = CMBAgent()

        cmbagent.solve(data_description,
                    max_rounds=500,
                    initial_agent="planner",
                    shared_context = {'feedback_left': 1,
                                        'maximum_number_of_steps_in_plan': 3,
                                        'planner_append_instructions': self.planner_append_instructions,
                                        'engineer_append_instructions': self.engineer_append_instructions,
                                        'researcher_append_instructions': self.researcher_append_instructions,
                                        'plan_reviewer_append_instructions': self.plan_reviewer_append_instructions}
                    )
        
        planning_output = copy.deepcopy(cmbagent.final_context)

        ## control

        cmbagent = CMBAgent(
            agent_llm_configs = {
                                'engineer': {
                                    "model": "o3-mini-2025-01-31",
                                    "reasoning_effort": "high",
                                    "api_key": os.getenv("OPENAI_API_KEY"),
                                    "api_type": "openai"},
                                'researcher': {
                                    "model": "o3-mini-2025-01-31",
                                    "reasoning_effort": "high",
                                    "api_key": os.getenv("OPENAI_API_KEY"),
                                    "api_type": "openai"},
            })
            

        cmbagent.solve(data_description,
                        max_rounds=500,
                        initial_agent="control",
                        shared_context = planning_output
                        )
        
        try:
            for obj in cmbagent.chat_result.chat_history[::-1]:
                if obj['name'] == 'researcher_response_formatter':
                    result = obj['content']
                    break
            cmbagent.task_result = result
        except:
            cmbagent.task_result = None
            
        MD_CODE_BLOCK_PATTERN = r"```[ \t]*(?:markdown)[ \t]*\r?\n(.*)\r?\n[ \t]*```"
        extracted_results = re.findall(MD_CODE_BLOCK_PATTERN, cmbagent.task_result, flags=re.DOTALL)[0]
        # print(extracted_methodology)
        clean_results = re.sub(r'^<!--.*?-->\s*\n', '', extracted_results)
        self.results = clean_results
        self.plot_paths = cmbagent.final_context['displayed_images']

        return None


