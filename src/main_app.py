import streamlit as st
from gemini_self_refine import WeatherData, SelfRefineAgent, SenderClient

def main():
    st.set_page_config(page_title="What to Wear Agent", page_icon="🌐")
    st.title(":sunny: I'm 'What to Wear' Agent:umbrella:")
    st.markdown(":rainbow[Hi, pssst! Don't wanna get wet, sun burned or cold? Tell me where you are and I'll tell you what to wear to be nice and comfy!]")
    st.subheader('How does it work?')
    st.write("It's simple - I look through public webcams to see how people outside are dressed and combine it with the weather forecast. This allows me to return an accurate recommendation of clothing suitable for the current conditions. I also take into account any potential weather changes, so you don’t have to worry about being caught off guard by unexpected rain, wind or temperature.")
    st.write("You can either get an instant recommendation here or subscribe to daily email recommendation:blush:")

    with st.form(key='user_input_form'):
        user_location = st.selectbox("Choose your location", ["Kraków, Poland", "Other locations available soon!"], index=0)
        user_email = st.text_input("Enter your email")
        # start_date = st.date_input("Hour of daily reminders")
        submit_button = st.form_submit_button(label='Get current recommendation')
        # submit_button = st.form_submit_button(label='Subscribe to daily recommendations')


    if submit_button:
        # Create a placeholder for the loading message
        # waiting_message = st.empty()
        # waiting_message.text("Generating recommendation, please wait ~2m...")
        with st.spinner("Generating recommendation, please wait ~2m..."):

            # Perform the processing
            weather_data = WeatherData('274455')  # Hardcoded key for Kraków, because of additional call needed to get a key location so it's redundant for now 
            self_refine_agent = SelfRefineAgent([weather_data.weather_current, weather_data.weather_future], weather_data.weather_camera_images)
            sender_client = SenderClient()
            sender_client.send_email(user_email, self_refine_agent.refined_recommendation, self_refine_agent.visual_recommendation)

            # Store the results in session_state
            st.session_state['recommendation'] = self_refine_agent.refined_recommendation
            st.session_state['visual_recommendation'] = self_refine_agent.visual_recommendation
            st.session_state['thinking_history'] = f'I returned the final recommendation after {self_refine_agent.refinements} iterations of the Self-Refine algorithm. The thinking history is available here: {self_refine_agent.chat.history}'
            st.session_state['images'] = weather_data.weather_camera_images
            st.session_state['camera_links'] = weather_data.nearest_cameras
            
            # Clear the waiting message and show success message
            # waiting_message.empty()
        st.success("Recommendation sent to your email!")

    # Check if there's a recommendation to display and display it
    if 'recommendation' in st.session_state:
        st.markdown(st.session_state['recommendation'], unsafe_allow_html=True)
        st.balloons()
    if 'visual_recommendation' in st.session_state:
        st.image(st.session_state['visual_recommendation'])

if __name__ == "__main__":
    main()
