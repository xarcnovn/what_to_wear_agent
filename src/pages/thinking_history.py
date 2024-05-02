import streamlit as st

def display_thinking_history():
    st.set_page_config(page_title="Thinking History", page_icon="🤔")
    st.title("Model Thinking History")
    st.write(":rainbow[Here you can take a look at inner workings of the Self-Refine algorithm (https://selfrefine.info/)]")
    if 'thinking_history' in st.session_state:
        formatted_history = st.session_state['thinking_history']
        st.markdown(formatted_history)
    else:
        st.warning("Thinking history is not available until after a recommendation is generated.")

if __name__ == "__main__":
    display_thinking_history()