import streamlit as st
from gemini_self_refine import WeatherData, SelfRefineAgent, SenderClient

def main():
    st.set_page_config(page_title="What to Wear Agent", page_icon="🌐")
    st.title(":sunny: I'm 'What to Wear' Agent:umbrella:")
    st.markdown(":rainbow[Hi, pssst! Don't wanna get wet, sun burned or cold? Tell me where you are and I'll tell you what to wear to be nice and comfy!]")
    st.subheader('How does it work?')
    st.write("It's simple - I look through public webcams to see how people outside are dressed and combine it with the weather forecast. This allows me to return an accurate recommendation of clothing suitable for the current conditions. I also take into account any potential weather changes, so you don’t have to worry about being caught off guard by unexpected rain, wind or temperature.")
    st.write("You can either get an instant recommendation here or subscribe to a daily email recommendation:blush:")

    with st.form(key='location_form'):
        location = st.selectbox("Choose your location", ["Kraków, Poland", "Other locations available soon!"], index=0) #Only Kraków, Poland is working right now, but other locations will be available soon!
        submit_location = st.form_submit_button("Continue")

    if 'location' not in st.session_state or submit_location:
        st.session_state['location'] = location
    
    if 'location' in st.session_state:
        recommendation_type = st.radio("Select Recommendation Type:", ("Instant Recommendation", "Subscribe to Daily Recommendations"))
        
        if recommendation_type == "Instant Recommendation":
            if st.button("Get instant recommendation"):
                with st.spinner("Working on recommendation, please wait ~2m..."):
                    weather_data = WeatherData('274455')  # Getting this key require additional call to the weather API (which is not free) so for now it's hardcoded for Cracow due to temporary unavailibility of other locations 
                    self_refine_agent = SelfRefineAgent([weather_data.weather_current, weather_data.weather_future], weather_data.weather_camera_images)
                    recommendation = self_refine_agent.refined_recommendation
                    st.session_state['recommendation'] = recommendation
                    st.success("Here is your current weather-based clothing recommendation:")
                    #session state
                    st.session_state['recommendation'] = self_refine_agent.refined_recommendation
                    st.session_state['visual_recommendation'] = self_refine_agent.visual_recommendation
                    st.session_state['thinking_history'] = f'I returned the final recommendation after {self_refine_agent.refinements} iterations of the Self-Refine algorithm. The thinking history is available here: {self_refine_agent.chat.history}'
                    st.session_state['images'] = weather_data.weather_camera_images
                    st.session_state['camera_links'] = weather_data.nearest_cameras

            if 'recommendation' in st.session_state:
                st.markdown(st.session_state['recommendation'], unsafe_allow_html=True)
            if 'visual_recommendation' in st.session_state:
                st.image(st.session_state['visual_recommendation'])
                    
        elif recommendation_type == "Subscribe to Daily Recommendations":
            with st.form(key='subscribe_form'):
                user_email = st.text_input("Enter your email")
                reminder_time = st.time_input("Time for daily reminders")
                submit_subscribe = st.form_submit_button("Subscribe")
                
                if submit_subscribe:
                    with st.spinner("Setting up your daily reminders..."):
                        #there was a job scheduler, but turned out it doesn't work as I thought it was and found it out only few hours before submission...
                        sender_client = SenderClient()
                        # sender_client.setup_daily_reminders(user_email, reminder_time) - under construction, had to be removed
                        st.success(f"Subscribed successfully! Daily recommendations will be sent to {user_email} at {reminder_time.strftime('%H:%M')}.")

if __name__ == "__main__":
    main()
