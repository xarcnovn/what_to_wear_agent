# import streamlit as st
# from gemini_self_refine import WeatherData, SelfRefineAgent, SenderClient

# def main():
#     st.set_page_config(page_title="Main App", page_icon="🌐")
#     st.title("I'm 'What to Wear' Agent")
#     st.write(":rainbow[Hi pssst, don't wanna get wet, sun burned or cold? Tell me where you are and I'll tell you what to wear to be nice and comfy!]")
#     st.subheader('How does it work?')
#     st.write("""It's simple - I look at the weather forecast and how people outside are dressed and return an accurate recommendation of clothing for the current weather. I also take into account all the weather changes so you don't have to worry about being caught with unexpected rain or wind.""")

#     with st.form(key='user_input_form'):
#         user_location = st.selectbox("Choose your location", ["Kraków, Poland", "Other locations available soon!"], index=0)
#         user_email = st.text_input("Enter your email")
#         start_date = st.date_input("Hour of daily reminders")
#         submit_button = st.form_submit_button(label='Get current recommendation')
#         submit_button = st.form_submit_button(label='Subscribe to daily recommendations')


#     if submit_button:
#         # Create a placeholder for the loading message
#         # waiting_message = st.empty()
#         # waiting_message.text("Generating recommendation, please wait ~2m...")
#         with st.spinner("Generating recommendation, please wait ~2m..."):

#             # Perform the processing
#             weather_data = WeatherData('274455')  # Hardcoded key for Kraków, because of additional call needed to get a key location so it's redundant for now 
#             self_refine_agent = SelfRefineAgent([weather_data.weather_current, weather_data.weather_future], weather_data.weather_camera_images)
#             sender_client = SenderClient()
#             sender_client.send_email(user_email, self_refine_agent.refined_recommendation, self_refine_agent.visual_recommendation)

#             # Store the results in session_state
#             st.session_state['recommendation'] = self_refine_agent.refined_recommendation
#             st.session_state['visual_recommendation'] = self_refine_agent.visual_recommendation
#             st.session_state['thinking_history'] = f'I returned the final recommendation after {self_refine_agent.refinements} iterations of the Self-Refine algorithm. The thinking history is available here: {self_refine_agent.chat.history}'
#             st.session_state['images'] = weather_data.weather_camera_images
#             st.session_state['camera_links'] = weather_data.nearest_cameras
            
#             # Clear the waiting message and show success message
#             # waiting_message.empty()
#         st.success("Recommendation sent to your email!")

#     # Check if there's a recommendation to display and display it
#     if 'recommendation' in st.session_state:
#         st.markdown(st.session_state['recommendation'], unsafe_allow_html=True)
#         st.balloons()
#     if 'visual_recommendation' in st.session_state:
#         st.image(st.session_state['visual_recommendation'])

# if __name__ == "__main__":
#     main()

import streamlit as st
from gemini_self_refine import WeatherData, SelfRefineAgent, SenderClient

def main():
    st.set_page_config(page_title="Main App", page_icon="🌐")
    st.title("I'm 'What to Wear' Agent")
    st.write(":rainbow: [Hi pssst, don't wanna get wet, sun burned or cold? Tell me where you are and I'll tell you what to wear to be nice and comfy!]")
    st.subheader('How does it work?')
    st.write("It's simple - I look at the weather forecast and how people outside are dressed and return an accurate recommendation of clothing for the current weather. I also take into account all the weather changes so you don't have to worry about being caught with unexpected rain or wind.")

    # Form for instant recommendation
    with st.form(key='instant_recommendation_form'):
        st.write("Get an instant recommendation:")
        user_location_instant = st.selectbox("Choose your location", ["Kraków, Poland", "Other locations available soon!"], index=0)
        submit_instant = st.form_submit_button(label='Get current recommendation')

    st.write("OR")

    # Form for email subscription
    with st.form(key='email_subscription_form'):
        st.write("Subscribe for daily recommendations via email:")
        user_email = st.text_input("Enter your email")
        reminder_time = st.time_input("Time for daily reminders")
        submit_subscribe = st.form_submit_button(label='Subscribe to daily recommendations')

    if submit_instant:
        with st.spinner("Fetching instant recommendation..."):
            weather_data = WeatherData('274455')  # Example location key for Kraków
            self_refine_agent = SelfRefineAgent([weather_data.weather_current, weather_data.weather_future], weather_data.weather_camera_images)
            recommendation = self_refine_agent.refined_recommendation
            
            st.session_state['recommendation'] = recommendation
            st.success("Here is your current weather-based clothing recommendation:")
            st.markdown(recommendation, unsafe_allow_html=True)

    if submit_subscribe:
        with st.spinner("Setting up your daily reminders..."):
            # Assuming sender_client is capable of setting up email reminders
            sender_client = SenderClient()
            sender_client.setup_daily_reminders(user_email, reminder_time)
            st.success(f"Subscribed successfully! Daily recommendations will be sent to {user_email} at {reminder_time.strftime('%H:%M')}.")

if __name__ == "__main__":
    main()

