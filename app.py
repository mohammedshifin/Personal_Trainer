import streamlit as st
from personal_trainer import initialize_llm, setup_chains
from dotenv import load_dotenv
import os
from PIL import Image
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

def main():
    st.set_page_config(page_title="Fitness AI Coach", page_icon="💪")
    st.title("💬 Fitness Chat Assistant")
    st.caption("Your personal AI fitness coach powered by Gemini")
    
    uploaded_file = st.file_uploader("Choose an image...",type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image=image,caption="Uploaded Image.",use_column_width=True) 
        st.write("")
        st.write("Classifying")

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

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your fitness question"):
        if not st.session_state.llm_initialized:
            st.error("Please initialize the chatbot in the sidebar first")
            return

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("Thinking..."):
            try:
                if "tip" in prompt.lower():
                    response = st.session_state.chains["tip"]({"fitness_level": fitness_level})
                elif "workout" in prompt.lower():
                    response = st.session_state.chains["workout"]({
                        "duration": 30,
                        "fitness_level": fitness_level,
                        "workout_focus": "full-body",
                        "equipment": "bodyweight"
                    })
                else:
                    response = st.session_state.chains["general"]({"input": prompt})
                
                if hasattr(response, 'content'):
                    response = response.content
                st.session_state.chains["memory"].save_context({"input": prompt}, {"output": response})

            except Exception as e:
                response = f"Error generating response: {e}"

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()