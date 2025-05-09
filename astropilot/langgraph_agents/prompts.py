from langchain_core.messages import HumanMessage, SystemMessage


def idea_maker_prompt(state):

    return [HumanMessage(content=rf"""Your goal is to generate a groundbreaking idea for a scientific paper. Generate the idea given the data description and. If available, take into account the criticism provided by another agent about the idea.

Iteration {state['idea']['iteration']}
    
Data description:
{state['data_description']}

Previous ideas:
{state['idea']['previous_ideas']}

Critisms:
{state['idea']['criticism']}

Respond in the following format:

\begin{{IDEA}}
<IDEA>
\end{{IDEA}}

In <IDEA>, put the idea together with its description. Try to be brief in the description.
""")]


def idea_hater_prompt(state):

    return [HumanMessage(content=rf"""Your goal is to critic an idea. You will be provided with the idea together with the initial data description used to make the idea. Be a harsh critic of the idea. Take into account feasibility, impact and any other factor you think. The goal of your criticisms is to improve the idea

Data description:
{state['data_description']}

Previous ideas:
{state['idea']['previous_ideas']}

Current idea:
{state['idea']['idea']}

Respond in the following format:

\begin{{CRITIC}}
<CRITIC>
\end{{CRITIC}}

In <CRITIC>, put your criticism to the idea. Try to be brief in the description.
""")]
