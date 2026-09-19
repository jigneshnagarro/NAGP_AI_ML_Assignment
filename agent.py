from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
    SystemMessage,
)

from rag.rag_tool import search_singapore_knowledge
from rag.tools import (
    get_singapore_weather,
    convert_inr_to_sgd,
)

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0
)


tools = [
    search_singapore_knowledge,
    get_singapore_weather,
    convert_inr_to_sgd,
]


tool_map = {
    tool.name: tool
    for tool in tools
}


llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
You are a context-aware Singapore travel planning assistant.

You have access to three tools.

1. search_singapore_knowledge

Use this for relatively stable Singapore travel information:

- attractions
- neighbourhoods
- transportation
- food
- cultural information
- indoor activities
- outdoor activities
- sample itineraries

2. get_singapore_weather

Use this for:

- current weather
- upcoming weather
- rain
- temperature
- weather forecast
- weather for specific travel dates

This information comes from a current MCP weather service.

3. convert_inr_to_sgd

Use this for:

- INR to SGD conversion
- Indian Rupees to Singapore Dollars
- Singapore budget conversion from INR

This information comes from a current MCP currency service.

IMPORTANT RULES:

- Never invent facts.
- Use the knowledge base for relatively stable destination information.
- Use MCP for current weather.
- Use MCP for current currency conversion.
- Do not use the knowledge base for current weather.
- If the knowledge base does not contain enough information, say so clearly.
- Distinguish facts from recommendations.
- Preserve context from previous user messages.
- If the user refers to "this trip", "day 2", "that itinerary", etc.,
  use previous conversation context.
- When using knowledge base information, mention the relevant source.
- When using MCP information, identify it as current MCP information.
"""


def create_conversation_history():
    return [
        SystemMessage(content=SYSTEM_PROMPT)
    ]


def ask_agent(question, conversation_history):
    conversation_history.append(
        HumanMessage(content=question)
    )

    tools_used = []
    sources = []
    mcp_used = False

    while True:

        response = llm_with_tools.invoke(
            conversation_history
        )

        conversation_history.append(response)

        if not response.tool_calls:
            return {
                "answer": response.content,
                "tools_used": list(dict.fromkeys(tools_used)),
                "sources": sources,
                "mcp_used": mcp_used
            }

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            tools_used.append(tool_name)

            if tool_name in [
                "get_singapore_weather",
                "convert_inr_to_sgd"
            ]:
                mcp_used = True

            tool = tool_map.get(tool_name)

            if tool is None:

                result = {
                    "error": f"Tool '{tool_name}' is unavailable."
                }

            else:

                try:

                    result = tool.invoke(tool_args)

                    if tool_name == "search_singapore_knowledge":

                        result_text = str(result)
                        for block in result_text.split("SOURCE TITLE:")[1:]:

                            lines = block.strip().splitlines()

                            if len(lines) >= 2:

                                title = lines[0].strip()

                                url = ""

                                for line in lines:
                                    line = line.strip()
                                    if line.startswith("SOURCE URL:"):
                                        url = line.replace(
                                            "SOURCE URL:",
                                            ""
                                        ).strip()

                                if title and not any(
                                    source["title"] == title
                                    for source in sources
                                ):
                                    sources.append({
                                        "title": title,
                                        "url": url
                                    })

                except Exception as error:

                    result = {
                        "error": f"Tool execution failed: {str(error)}"
                    }

            conversation_history.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id,
                )
            )