import streamlit as st
from personal_trainer import initialize_llm, setup_chains
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY") 

# App configuration
st.set_page_config(page_title="Fitness AI Coach", page_icon="💪")


def main():
    st.title("💬 Fitness Chat Assistant")
    st.caption("Your personal AI fitness coach powered by Gemini")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "llm_initialized" not in st.session_state:
        st.session_state.llm_initialized = False

    with st.sidebar:
        st.header("Settings")
        
        fitness_level = st.selectbox(
            "Your Fitness Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        if st.button("Initialize Chatbot"):
            if api_key:
                try:
                    llm = initialize_llm(api_key)
                    st.session_state.chains = setup_chains(llm)
                    st.session_state.llm_initialized = True
                    st.success("Chatbot initialized!")
                except Exception as e:
                    st.error(f"Error initializing chatbot: {e}")
            else:
                st.error("Please enter an API key")

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your fitness question"):
        if not st.session_state.llm_initialized:
            st.error("Please initialize the chatbot in the sidebar first")
            return

        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.spinner("Thinking..."):
            try:
                if "tip" in prompt.lower():
                    response = st.session_state.chains["tip"].run(
                        {"fitness_level": fitness_level}
                    )
                elif "workout" in prompt.lower():
                    response = st.session_state.chains["workout"].run({
                        "duration": 30,
                        "fitness_level": fitness_level,
                        "workout_focus": "full-body",
                        "equipment": "bodyweight"
                    })
                else:
                    response = st.session_state.chains["general"].run({
                        "input": prompt
                    })
            except Exception as e:
                response = f"Error generating response: {e}"

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()