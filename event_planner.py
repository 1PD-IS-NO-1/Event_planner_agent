import os
from typing import List, Dict, Any, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, Tool
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain.agents.format_scratchpad import format_log_to_messages
from langchain.agents.agent import AgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnablePassthrough
from langgraph.graph import Graph, StateGraph
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import JsonOutputParser

class CustomOutputParser(JsonOutputParser):
    def parse(self, text: str) -> dict:
        try:
            return super().parse(text)
        except ValueError:
            # Try to parse the output even if it's not perfectly formatted JSON
            cleaned_text = text.replace("'", '"').replace("\n", "")
            return json.loads(cleaned_text)
        except Exception as e:
            # Handle other errors
            return self.handle_parsing_error(e)

    def handle_parsing_error(self, error: Exception) -> dict:
        print(f"Error parsing output: {error}")
        return {"error": "Unable to parse model output"}

class GraphState(TypedDict):
    event_topic: str
    event_description: str
    event_city: str
    tentative_date: str
    expected_participants: int
    budget: float
    venue_type: str
    venue_result: Dict[str, Any]
    logistics_result: Dict[str, Any]
    marketing_result: Dict[str, Any]

# Set up environment variables
os.environ["GOOGLE_API_KEY"] = "AIzaSyCF-jMEoZr2ji5kmJvYg4HQGWG--Bq8n84"
os.environ["SERPAPI_API_KEY"] = "570ad04ec98b63d10b8a46022d0a3b91e63f39fe943df842cfd56dadc5db4274"

# Initialize Gemini model with temperature
llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# Define tools
search = SerpAPIWrapper()
ddg_search = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events",
    ),
    Tool(
        name="DuckDuckGo Search",
        func=ddg_search.run,
        description="useful for when you need to do a web search",
    ),
]

def create_agent(role: str, goal: str) -> AgentExecutor:
    # Modified prompt template without system message
    prompt = ChatPromptTemplate.from_messages([
        ("human", f"""You are an AI assistant with the role of {role}.
Your goal is: {goal}

Available tools:
{chr(10).join([f'- {tool.name}: {tool.description}' for tool in tools])}

Please help with the following task:
{{input}}"""),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the runnable agent
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_log_to_messages(x["intermediate_steps"])
        )
        | prompt
        | llm
        | CustomOutputParser()
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)
# Custom Markdown Output Parser
def format_result_to_markdown(result: Dict[str, Any]) -> str:
    markdown_output = []
    for key, value in result.items():
        if isinstance(value, dict):
            markdown_output.append(f"### {key.replace('_', ' ').title()}")
            for sub_key, sub_value in value.items():
                markdown_output.append(f"- *{sub_key}:* {sub_value}")
        else:
            markdown_output.append(f"- *{key.replace('_', ' ').title()}:* {value}")
    return "\n".join(markdown_output)

# Create agents with modified roles and goals
venue_coordinator = create_agent(
    role="Venue Coordinator",
    goal="Find appropriate venues based on event requirements and suggest venues that fit with event's theme, expected participants, and budget constraints."
)

logistics_manager = create_agent(
    role="Logistics Manager",
    goal="Plan event logistics, including catering and equipment needs, based on the best-fit venue."
)

marketing_communications_agent = create_agent(
    role="Marketing Agent",
    goal="Create marketing strategies and communication plans to maximize event exposure and participation."
)

# Define graph tasks
def venue_task(state: GraphState) -> GraphState:
    try:
        prompt = f"""Research and suggest venues in {state['event_city']} for:
- Event: {state['event_topic']}
- Attendees: {state['expected_participants']}
- Venue type needed: {state['venue_type']}
- Budget: ${state['budget']}

Please provide 3 specific venue recommendations with details that fits with event's theme, expected_participants and budget constraints."""
        result = venue_coordinator.invoke({"input": prompt})
        state['venue_result'] = result
    except Exception as e:
        state['venue_result'] = {"error": str(e)}
    return state

def logistics_task(state: GraphState) -> GraphState:
    try:
        prompt = f"""Plan logistics in {state['event_city']} for:
- Event: {state['event_topic']}
- Date: {state['tentative_date']}
- Attendees: {state['expected_participants']}
- Budget: ${state['budget']}

Please provide specific recommendations for catering and equipment."""
        result = logistics_manager.invoke({"input": prompt})
        state['logistics_result'] = result
    except Exception as e:
        state['logistics_result'] = {"error": str(e)}
    return state

def marketing_task(state: GraphState) -> GraphState:
    try:
        prompt = f"""Create a marketing strategy for:
- Event: {state['event_topic']}
- Description: {state['event_description']}
- Target attendance: {state['expected_participants']}
- Date: {state['tentative_date']}
- City: {state['event_city']}

Please provide only 3 or 4 specific marketing recommendations and channels."""
        result = marketing_communications_agent.invoke({"input": prompt})
        state['marketing_result'] = result
    except Exception as e:
        state['marketing_result'] = {"error": str(e)}
    return state

# Define graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("venue", venue_task)
workflow.add_node("logistics", logistics_task)
workflow.add_node("marketing", marketing_task)

# Add edges
workflow.add_edge("venue", "logistics")
workflow.add_edge("logistics", "marketing")

# Set entry point
workflow.set_entry_point("venue")
workflow.set_finish_point("marketing")
graph = workflow.compile()

def run_event_planning_workflow(event_details: Dict[str, Any]) -> Dict[str, Any]:
    try:
        initial_state: GraphState = {
            'event_topic': event_details['event_topic'],
            'event_description': event_details['event_description'],
            'event_city': event_details['event_city'],
            'tentative_date': event_details['tentative_date'],
            'expected_participants': event_details['expected_participants'],
            'budget': event_details['budget'],
            'venue_type': event_details['venue_type'],
            'venue_result': {},
            'logistics_result': {},
            'marketing_result': {}
        }

        result_state = graph.invoke(initial_state)
        return result_state
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {'error': str(e)}