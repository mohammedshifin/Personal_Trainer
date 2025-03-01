from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

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
    # Updated memory implementation
    memory = ConversationBufferMemory(return_messages=True)
    
    # Create chains using the newer approach
    return {
        "workout": lambda params: llm.invoke(templates["workout"].format(**params)),
        "tip": lambda params: llm.invoke(templates["tip"].format(**params)),
        "general": lambda params: llm.invoke(templates["general"].format(
            input=params["input"], 
            history=memory.load_memory_variables({})["history"]
        ))
    }
