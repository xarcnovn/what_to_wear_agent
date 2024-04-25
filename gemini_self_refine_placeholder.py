import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import requests
import cv2
import time
from dotenv import load_dotenv

load_dotenv()


class WhatToWear:
    pass


class GetData:
    def __init__(self) -> None:
        self.OWE_api_key

    def take_screenshot(self):
        cap = cv2.VideoCapture(self.nearest_camera)
        success, frame = cap.read()
        if not success:
            print("Failed to capture video frame")
            return None
        screenshot_path = "video_screenshot.png"
        cv2.imwrite(screenshot_path, frame)
        cap.release()
        return screenshot_path
    
    def get_future_weather(self):
        base_url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "q": self.location,
            "key": self.OWE_api_key,
            'hour': 18,
            'days': 1
        }
        response = requests.get(base_url, params=params)
        self.weather_data = response.json()



class SelfRefine:

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.apikey = genai.configure(api_key='AIzaSyDKtHnN25xQYIODAAZczivqmUS0rFjpUA8')
        self.chat = self.model.start_chat()
        self.feedback = ''
        self.refined_recommendation = ''
        self.refinements = 4
        self.images = ''
        self.weather_data = """{{'location': {'name': 'Krakow', 'region': '', 'country': 'Poland', 'lat': 50.08, 'lon': 19.92, 'tz_id': 'Europe/Warsaw', 'localtime_epoch': 1714069607, 'localtime': '2024-04-25 20:26'}, 'current': {'last_updated_epoch': 1714068900, 'last_updated': '2024-04-25 20:15', 'temp_c': 4.7, 'temp_f': 40.5, 'is_day': 0, 'condition': {'text': 'Clear', 'icon': '//cdn.weatherapi.com/weather/64x64/night/113.png', 'code': 1000}, 'wind_mph': 5.6, 'wind_kph': 9.0, 'wind_degree': 220, 'wind_dir': 'SW', 'pressure_mb': 1010.0, 'pressure_in': 29.84, 'precip_mm': 0.0, 'precip_in': 0.0, 'humidity': 74, 'cloud': 9, 'feelslike_c': 2.6, 'feelslike_f': 36.6, 'vis_km': 10.0, 'vis_miles': 6.0, 'uv': 1.0, 'gust_mph': 11.7, 'gust_kph': 18.9}, 'forecast': {'forecastday': [{'date': '2024-04-25', 'date_epoch': 1714003200, 'day': {'maxtemp_c': 11.1, 'maxtemp_f': 52.0, 'mintemp_c': 3.2, 'mintemp_f': 37.8, 'avgtemp_c': 6.6, 'avgtemp_f': 43.9, 'maxwind_mph': 11.4, 'maxwind_kph': 18.4, 'totalprecip_mm': 3.84, 'totalprecip_in': 0.15, 'totalsnow_cm': 0.0, 'avgvis_km': 9.1, 'avgvis_miles': 5.0, 'avghumidity': 74, 'daily_will_it_rain': 1, 'daily_chance_of_rain': 98, 'daily_will_it_snow': 0, 'daily_chance_of_snow': 0, 'condition': {'text': 'Patchy rain nearby', 'icon': '//cdn.weatherapi.com/weather/64x64/day/176.png', 'code': 1063}, 'uv': 4.0}, 'astro': {'sunrise': '05:27 AM', 'sunset': '07:51 PM', 'moonrise': '10:01 PM', 'moonset': '05:42 AM', 'moon_phase': 'Waning Gibbous', 'moon_illumination': 99, 'is_moon_up': 1, 'is_sun_up': 0}, 'hour': [{'time_epoch': 1714060800, 'time': '2024-04-25 18:00', 'temp_c': 8.4, 'temp_f': 47.2, 'is_day': 1, 'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/weather/64x64/day/113.png', 'code': 1000}, 'wind_mph': 6.9, 'wind_kph': 11.2, 'wind_degree': 230, 'wind_dir': 'SW', 'pressure_mb': 1008.0, 'pressure_in': 29.78, 'precip_mm': 0.0, 'precip_in': 0.0, 'snow_cm': 0.0, 'humidity': 67, 'cloud': 11, 'feelslike_c': 6.5, 'feelslike_f': 43.8, 'windchill_c': 6.5, 'windchill_f': 43.8, 'heatindex_c': 8.4, 'heatindex_f': 47.2, 'dewpoint_c': 2.7, 'dewpoint_f': 36.9, 'will_it_rain': 0, 'chance_of_rain': 0, 'will_it_snow': 0, 'chance_of_snow': 0, 'vis_km': 10.0, 'vis_miles': 6.0, 'gust_mph': 11.8, 'gust_kph': 19.0, 'uv': 3.0}]}]}}}"""
        self.load_few_shot_examples('FEW_SHOTS_EXAMPLES.txt')
        self.initial_prompt = f""" You're a trained robot named "what_to_wear_robot2000". Your goal is to prepare a recommendation of clothing for the weather to assure the user is comfortable and prepared. You use a weather forecast {self.weather_data} and photos (that are passed directly to you) from a given location to make this recommendation. You reason in a following way - first you think what to do, then you make an observation and then you return an actionable and specific list of clothing with a proper, yet concise explanation why you recommend them. Response template: 
                                        - List of cloths to wear - from the most outer layer and exclude panties. Pay special attention to all elements that are either warm or cooling.
                                        - Reasoning behind recommendation how you combined data from the camera and forcast. Keep it concise, don't ramble. Tell what is the sky color in the screenshot you see. Also tell what the current temperature in the location. 
                                        Below are examples of the reasoning you will follow: {self.few_shots_examples}"""

    

    def setup_model(self):
        """
        Setup the generative AI model and start a chat session. Includes error handling.
        """
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
            self.chat = self.model.start_chat()
        except Exception as e:
            print(f"Failed to initialize the AI model or start chat: {e}")
            raise

    def load_few_shot_examples(self, file_path):
        """
        Load few shot examples from a text file and assign it to the attribute.
        """
        try:
            with open(file_path, 'r') as file:
                self.few_shots_examples = file.read()
        except Exception as e:
            print(f"Error loading few shot examples from file: {e}")
            raise

    def upload_photos(self):
        try:
            # self.images.image = (genai.upload_file(path='video_screenshot.png'))
            self.images = genai.upload_file(path='video_screenshot.png')
        except Exception as e:
            print(f'Error loading photot: {e}')
            raise


    def generate_initial_recommendation(self, initial_prompt):
        self.chat.send_message(initial_prompt)
        time.sleep(2)

    def generate_feedback(self, feedback_prompt):
        self.feedback = self.chat.send_message(feedback_prompt).candidates[0].content
        time.sleep(2)
    
    def refine_recommendation(self, refinement_prompt):
        self.refined_recommendation = self.chat.send_message(refinement_prompt).candidates[0].content
        time.sleep(2)

    def to_markdown(self, text):
        # text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

        

    def run(self):
        self.generate_initial_recommendation([self.initial_prompt, self.images])
        # feedback_prompt = f"""You will be given the history of a past experience in which you were asked to recommend a clothing for the given weather based on {self.weather_data} and photos that are directly passed to you.
        # The history starts here: {self.chat.history} and ends here.
        # Your goal is to analyze if your recommendation is thorough, complete and in alignement with your current knowledge, data and user's prompt. You reason in a following way - first you think what to do, then you make an observation and then you create a detailed plan what is wrong, what is good and what needs to be improved and return specific and actionable feedback that will be used to refine the answer."""
        # refinement_prompt = f'take {self.feedback} and use it to refine the output'        
        feedback_prompt = f"""You have a history of past experiences in which you were asked to recommend a clothing for the given weather based on {self.weather_data} and photos that are directly passed to you.
        Your goal is to analyze if your recommendation is thorough, complete and in alignement with your current knowledge, data and user's prompt. You reason in a following way - first you think what to do, then you make an observation and then you create a detailed plan what is wrong, what is good and what needs to be improved and return specific and actionable feedback that will be used to refine the answer."""
        refinement_prompt = f'take {self.feedback} and use it to refine the output. Then return only the recommendation for the end user. Be concise yet precise and explain why did you recommend what you recommended.'  
        for _ in range(self.refinements):
            self.generate_feedback(feedback_prompt)
            self.refine_recommendation(refinement_prompt)
            time.sleep(2) #I kept getting 429 and decided to resolve it this way

                    
 

# this one is working for returning formated history
        # for message in self.chat.history:
        #     markdown_obj = self.to_markdown(f'**{message.role}**: {message.parts[0].text}')
        #     print(markdown_obj.data) 
        

app =  SelfRefine()

app.run()
print(f'here is a refined recom {app.refined_recommendation}')
# print(app.chat.history)
