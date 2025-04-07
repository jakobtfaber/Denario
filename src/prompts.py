from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage


def idea_prompt(topic):
    return [
        SystemMessage(content='''You are a cosmologist and your role is to generate a groundbreaking idea for a PhD student thesis.'''),
        HumanMessage(content=f'''Given the topic, generate a groundbreaking idea for a PhD thesis. Please provide a **title** for the idea, its **description**, and the **challenges** associated with it. Also provide a number for the **novelty** of the idea from 0 (not novel) to 10 (very novel).
        
**Topic**: {topic}

Respond in **valid JSON format** as follows:

```json
{{
  "title": "Title of the idea",
  "description": "Brief explanation of the idea",
  "challenges": ["List of challenges associated with the idea"],
  "novelty": "the novelty of the idea from 0 (not novel) to 10 (very novel)"
}}
```''')]

    
def reflection_prompt(topic, ideas):

    return [
        SystemMessage(content="You are a cosmologist professor and your task is to revise and improve a scientific idea for a PhD thesis."),
        HumanMessage(content=f"""Revise and improve the ideas below following these guidelines:
- Consider the quality, novelty, and feasibility of the idea
- Include any factor you think is import to evaluate the idea
- Ensure the idea is clear and concise
- Do not create a very complicated idea
- Do not create a very generic idea
- If you think the idea is good enough, finish
- Make sure the idea follows the suggested topic
- If you think the idea needs improvements, you will have another round to improve it
- Stick to the spirt of the original idea

**Topic**: {topic}

**Previous ideas**: {ideas}

Respond in the following format:

**Decision**: <DECISION>

**Thought**: <THOUGHT>

**New idea**:
```json
{{
   "title": "the title of the idea",
   "description": "the description of the idea",
   "challenges": ["List of challenges associated with the idea"],
   "novelty": "the novelty of the idea from 0 (not novel) to 10 (very novel)"        
}}
```
""")]


# prompt to address whether an idea is novel or not
def novelty_prompt(idea_round, idea, papers):

    return [SystemMessage(content="You are a cosmology professor and your task is to decide whether an idea is novel or not."),
            HumanMessage(content=f"""Given the idea and associated papers, reason whether the idea is novel or not. Novel means that it doesnt strongly overlaps with existing literature or already explored. Be a harsh critic for novelty, ensure there is a sufficient contribution in the idea for a scientific publication. You will be given access to the Semantic Scholar API, which you may use to survey the literature and find relevant papers to help you make your decision. The top 10 results for any search query will be presented to you with their abstracts.

Decide an idea is novel if, after sufficient searching, you have not found a paper that significantly overlaps with your idea.  Decide an idea is not novel if you have found a paper that significantly overlaps with your idea. Pay attention to the details and search for strong similarities in all angles to decide is not novel. An idea cant be novel in the first round.
            
Round {idea_round}/10. Here is the idea

**Idea Title**: {idea['title']}
**Idea Description**: {idea['description']}

The papers our search have found are these (empty for Round 1):

{papers}

Respond in the following format:
            
```json
{{
   "Reason": "reason whether the idea is novel or not",
   "Decision": "determine whether the idea is novel or not. Return novel, not novel, or query",
   "Thought": "briefly reason over the idea and identify any query that could help you make your decision",
   "Query": "An optimal search query to search the literature (e.g. cosmology with one galaxy). You must make a query if you have not decided this round",
}}
```
""")]


def novelty_reflection(round, reason, decision, previous_reasons):
    return [HumanMessage(content="""An AI agent was asked to reason whether an idea was novel or not. Below, you can find its reason and its decision. You can also see previous reasonings. Given this, determine whether the idea is novel or not. There are only three possible decisions:
1) novel: if there is enough justification in the reasoning to believe the idea is novel
2) not novel: if there is enough justification for the idea being explored in a previous work
3) query: if you need to search for more papers to make the decision
Check if the decision taken made sense given the reason. If not, you can change it. Note that an idea cant be classified as novel in the first round

**Round**: round
**Previous reasons**: {previous_reasons}
**Reason**: {reason}
**Decision**: {decision}
    
Respond in the following format:
    
```json
{{
    "Decision": "The decision made; either novel, not novel, or query"
}}
```
    """)]



def abstract_prompt(idea):
    
    return [SystemMessage(content="""You are a scientific writer"""),
            HumanMessage(content=f"""Given the context below, get a title and write an abstract for a scientific paper. Please, follow these guidelines:
- What are we trying to do and why is it relevant?
- Why is this hard? 
- How do we solve it (i.e. our contribution!)
- How do we verify that we solved it (e.g. Experiments and results)
- Write the abstract in LaTex

Please make sure the abstract reads smoothly and is well-motivated. This should be one continuous paragraph with no breaks between the lines.

Context:
{idea}

Please respond in this format:

```json
{{"Title": "The title of the paper",
"Abstract": "The abstract of the paper"}}
```

Make sure the text is in LaTex. 
""")]


def abstract_reflection(state):

    return [SystemMessage(content="""Your are a cosmologist writing a scientific paper."""),
            HumanMessage(content=rf"""Rewrite the above abstract given the current abstract and the original idea to make it more clear. Abstract should be a single paragraph, no sections, subsections, or breaks between lines.

Original Idea
Title: {state['paper']['Title']}
Description: {state['idea']['idea']}

Abstract: {state['paper']['Abstract']}

Respond with in the following format:

\\begin{{Abstract}}
<ABSTRACT>
\\end{{Abstract}}
In <ABSTRACT>, place the Abstract of the paper. Follow these guidelines:
- What are we trying to do and why is it relevant?
- Why is this hard? 
- How do we solve it (i.e. our contribution!)
- How do we verify that we solved it (e.g. Experiments and results)

Please make sure the abstract reads smoothly and is well-motivated. This should be one continuous paragraph with no breaks between the lines.
""")]


def introduction_prompt(state):

    return [SystemMessage(content="You are a cosmologist."),
            HumanMessage(content=rf"""Given the title, idea, and methods below, write an introduction for a paper in LaTex.

Title: 
{state['paper']['Title']}

Description: 
{state['idea']['idea']}

Methods:
{state['idea']['Methods']}

Paper abstract: 
{state['paper']['Abstract']}

Please respond in this format:

\\begin{{Introduction}}
<INTRODUCTION>
\\end{{Introduction}}

In <INTRODUCTION>, place the introduction of the paper. Please, follow these guidelines:
- Write in LaTex
- Longer version of the Abstract, i.e. of the entire paper
- Text should contain at least 10 paragraphs. Each paragraph should have 5 sentences
- What are we trying to do and why is it relevant?
- Why is this hard? 
- How do we solve it (i.e. our contribution!)
- How do we verify that we solved it (e.g. Experiments and results)
- Extra space? Future work!

Please make sure the introduction reads smoothly and is well-motivated. If you use equations, please write them in LaTeX.
""")]


def introduction_reflection(state):

    return [SystemMessage(content="""Your are a cosmologist writing a scientific paper."""),
            HumanMessage(content=rf"""Rewrite the introduction below to make it more clear. Take into account the previous introduction and the original idea to make it more clear.

Original Idea
Title: 
{state['paper']['Title']}

Description: 
{state['idea']['Idea']}

Methods:
{state['idea']['Methods']}

Abstract: 
{state['paper']['Abstract']}

Introduction: 
{state['paper']['Introduction']}

Respond with in the following format:

\begin{{Introduction}}
<INTRODUCTION>
\end{{Introduction}}
In <INTRODUCTION>, place the Introduction of the paper. Follow these guidelines:
- Write in LaTex
- Longer version of the Abstract, i.e. of the entire paper
- Text should contain at least 10 paragraphs. Each paragraph should have 5 sentences
- What are we trying to do and why is it relevant?
- Why is this hard? 
- How do we solve it (i.e. our contribution!)
- How do we verify that we solved it (e.g. Experiments and results)
- Extra space? Future work!

Please make sure the introduction reads smoothly and is well-motivated. If you use equations, please write them in LaTex.
""")]


def methods_prompt(state):

    return [SystemMessage(content='''You are a cosmologist writing a scientific paper'''),
            HumanMessage(content=rf"""Given the idea and methods below, write a detailed and technical method section describing the methods and techniques used in the paper. Describe each method in detail.

Title: 
{state['paper']['Title']}

Description: 
{state['idea']['Idea']}

Methods:
{state['idea']['Methods']}

Paper abstract: 
{state['paper']['Abstract']}

Follow these guidelines:
- Reason about the steps needed to solve the problem and write them with detail.
- Describe in detail each step and write about the datatset, numerical simulations, evaluation metrics or any other element needed.
- Do not write the bibliography.
- Write in LaTex.

Respond in this format:

\begin{{Methods}}
<METHODS>
\end{{Methods}}
""")]


def results_prompt(state):

    return [SystemMessage(content='''You are a cosmologist writing a scientific paper'''),
            HumanMessage(content=rf"""Given the title, idea and results below, write a detailed and technical results section describing results obtained.

Title: 
{state['paper']['Title']}

Description: 
{state['idea']['Idea']}

Results: 
{state['idea']['Results']}

Follow these guidelines:
- Explain carefully the experiment conducted and its outcome
- Do not put placeholders for plots
- Describe what we have learned from the experiments
- Do not write the bibliography
- Write in LaTex

Respond in this format:

\begin{{Results}}
<Results>
\end{{Results}}

In <Results> put the results section writen in LaTeX.
""")]


def refine_results_prompt(state):
    return [
        SystemMessage(content='You are a cosmologist writing a scientific paper.'),
        HumanMessage(content=fr"""You are given the Results section of a paper that contains text and figures. The text and the figures were added independently, so there may not be a clear flow of integration between the two.

Your task is to revise the text so that it refers explicitly to the figures and forms a coherent narrative. Follow these rules:

- **Do not remove any figures. All figures must remain in the section**
- Add appropriate LaTeX references to the figures using \ref{{fig:...}} syntax.
- Modify or reorganize the text to improve clarity and flow.
- Reorder figures and paragraphs only if it improves the structure.
- Do not remove technical or scientific content.
- Write the text in LaTeX.

Results section:
{state['paper']['Results']}

**Respond in exactly this format**:

\\begin{{Results}}
<Results>
\\end{{Results}}

In <Results> put the new Results section.
""")
    ]

def conclusions_prompt(state):

    return [SystemMessage(content='''You are a cosmologist writing a scientific paper'''),
            HumanMessage(content=rf"""Given the title, idea and results below, write the conclusions for the scientific paper.

Title: 
{state['paper']['Title']}

Description: 
{state['idea']['Idea']}

Methods:
{state['paper']['Methods']}

Results: 
{state['idea']['Results']}

Follow these guidelines:
- Explain the idea of the project
- Describe what datasets and methods used
- Describe the results obtained
- Describe what we have learned from the results and this paper
- Do not write the bibliography
- Write in LaTex

Respond in this format:

\begin{{Conclusions}}
<Conclusions>
\end{{Conclusions}}

In <Conclusions> put the conclusion section writen in LaTeX.
""")]


def caption_prompt(state, image, name=None):
    return [
        SystemMessage(content="You are a cosmologist."),
        HumanMessage(content=[
            {"type": "text", "text": rf"""You are a cosmologist and your task is to create a caption for the figure. Create the caption to describe the image. Use the name of the image to know what quantity its being shown. Describe the outcome of the image. E.g. large differences are seen or small differences are found. Respond in the following format:
\begin{{Caption}}
<Caption>
\end{{Caption}}

In <Caption> place the figure caption writen in LaTeX.
"""},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}"}}
        ])
    ]

def plot_prompt(state, images):
    return [SystemMessage(content="""You are a cosmologist writing a scientific paper."""),
            HumanMessage(content=rf"""Your task is to insert a set of images in the section of a paper. You are given the current Results section and a dictionary that contains the name and the caption of each image. Your task is to place these images in the best locations in the text together with their captions.

section:
{state['paper']['Results']}

images dictionary
{images}

Respond in this format:

\begin{{Section}}
<Section>
\end{{Section}}

In <Section>, put the new section with the images and their captions. The location of each image should be '../Input_Files/plots/image_name'. Choose a label for each image given its caption. The width of the images should be half the page. Note that all text in <Section> should be compatible with LaTex.
""")]


def LaTeX_prompt(text):
    
    return [HumanMessage(content=fr'''Take the text below and check if it is compatible with LaTeX. If not, make minimal corrections to ensure compatibility. Do not introduce new sections or subsections unless they already exist in the text. If sections are present, convert them to subsections. Only return the corrected LaTeX code. Do not ask for user feedback.

Text: 
{text}

Respond in this format:

\\begin{{LaTeX}}
<LaTeX>
\\end{{LaTeX}}

In <LaTeX>, insert the correct LaTeX text.
''')]


def summary_prompt(summary, text):

    return [SystemMessage(content="""You are a cosmologist."""),
            HumanMessage(content=rf"""Summarize the text below and combine with the summarized text. 

Summarized text:
{summary}

Text to summarize:
{text}

Respond in this format:
\begin{{Summary}}
<Summary>
\end{{Summary}}

In <Summary> put the total summary.
""")]


def fixer_prompt(text, section_name):

    return [HumanMessage(content=fr"""Given the text below, please extract all the text inside the {section_name} section. 

Text:
{text}

Respond in this format:

\\begin{{{section_name}}}
<{section_name}>
\\end{{{section_name}}}

In <{section_name}> put the extracted text. In the extracted text, do not include any of the following lines

```latex
\\documentclass{{article}}
\\usepackage{{graphicx}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\begin{{document}}
\\section{{Results}}
\\end{{document}}
```

""")]
