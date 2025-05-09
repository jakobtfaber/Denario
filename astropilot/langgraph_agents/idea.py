from langchain_core.runnables import RunnableConfig
import sys,os

from ..paper_agents.tools import json_parser, extract_latex_block, LLM_call, temp_file, clean_section
from .prompts import idea_maker_prompt, idea_hater_prompt
from .parameters import GraphState


def idea_maker(state: GraphState, config: RunnableConfig):
    
    PROMPT = idea_maker_prompt(state)
    state, result = LLM_call(PROMPT, state)
    text = extract_latex_block(state, result, "IDEA")

    # remove LLM added lines
    text = clean_section(text, "IDEA")

    print(state['idea']['iteration'])

    state['idea']['idea'] = text
    state['idea']['previous_ideas'] = f"""
{state['idea']['previous_ideas']}

Iteration {state['idea']['iteration']}:
Idea: {text}
"""
    state['idea']['iteration'] += 1

    print(text)
    
    return {"idea": state['idea']}


def idea_hater(state: GraphState, config: RunnableConfig):

    PROMPT = idea_hater_prompt(state)
    state, result = LLM_call(PROMPT, state)
    text = extract_latex_block(state, result, "CRITIC")

    # remove LLM added lines
    text = clean_section(text, "CRITIC")
    
    state['idea']['criticism'] = text

    print(text)

    return {"idea": state['idea']}


def router(state: GraphState):

    if state['idea']['iteration']<3:
        return "hater"
    else: 
        return "__end__"
