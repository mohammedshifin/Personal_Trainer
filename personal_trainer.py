from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory ,ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

def initialize_llm(api_key):
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        google_api_key=api_key,
        temperature=0.7
    )

def create_prompt_templates():
    return {
        "workout": PromptTemplate(
            input_variables=["duration", "fitness_level", "workout_focus", "equipment"],
            template="""Create a {duration}-minute {workout_focus} workout for {fitness_level} level.
            Equipment: {equipment}. Include warm-up and cool-down. Format with bullet points."""
        ),
        "tip": PromptTemplate(
            input_variables=["fitness_level"],
            template="Give one random fitness tip suitable for {fitness_level} users."
        ),
        "general": PromptTemplate(
            input_variables=["input", "history"],
            template="""As a professional fitness coach, answer this:
            {input}
            Conversation history: {history}
            Response:"""
        )
    }

def setup_chains(llm):
    templates = create_prompt_templates()
    memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=2000)
    workout_chain = templates["workout"] | llm | StrOutputParser()
    tip_chain = templates["tip"] | llm | StrOutputParser()
    general_chain = (templates["general"].partial(history=memory.load_memory_variables({})["history"])
                     | llm | StrOutputParser())

    return {
        "workout": lambda params: workout_chain.invoke(params),
        "tip": lambda params: tip_chain.invoke(params),
        "general": lambda params: general_chain.invoke({"input": params["input"]}),
        "memory": memory
    }
