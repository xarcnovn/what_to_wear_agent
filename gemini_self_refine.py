import google.generativeai as genai
import textwrap
from IPython.display import Markdown
import requests
import cv2
import time
from dotenv import load_dotenv
import os

load_dotenv()



class WeatherData:

    """
    It fetches and stores weather data and images from public cameras
    """

    def __init__(self, location: str) -> None:
        self.weather_api_key = '5KUGp6jFh5VEK2ywhhCgaAwizCOHYGvV' #os.getenv('ACCUWEATHER_API_KEY') coś tu kurwa nie działa z tym
        self.location = location
        self.nearest_camera = 'https://imageserver.webcamera.pl/rec/krakow-florianska/latest.mp4'
        self.weather_camera_images = ''
        self.weather_current = ''
        self.weather_future = ''


    def get_camera(self, location) -> str:
        # just get a camera from worldcam.eu, waiting for api
        # self.nearest_camera = 'https://imageserver.webcamera.pl/rec/krakow-florianska/latest.mp4'
        pass

    def take_screenshot(self) -> str:
        cap = cv2.VideoCapture(self.nearest_camera)
        success, frame = cap.read()
        if not success:
            print("Failed to capture video frame")
            return None
        screenshot_path = "video_screenshot.png"
        cv2.imwrite(screenshot_path, frame)
        cap.release()
        return screenshot_path
    
    def get_future_weather(self) -> object:
        base_url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{self.location}"
        params = {
            "apikey": self.weather_api_key,
            "details": False,
            'metrics': True
        }
        response = requests.get(base_url, params=params)
        return response.json()

    def get_current_weather(self) -> object:
        base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{self.location}"
        params = {
            "apikey": self.weather_api_key
        }
        response = requests.get(base_url, params=params)
        return response.json()


class SelfRefine:

    """
    It takes weather_data for a given location (current and future) and images from cameras and returns clothing recomendation

    """

    def __init__(self, weather_data, image):
        # self.setup_model()
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        self.chat = self.model.start_chat()
        self.apikey = 'AIzaSyDKtHnN25xQYIODAAZczivqmUS0rFjpUA8'  #coś tu kurwa nie działa genai.configure(os.getenv('GEMINI_API_KEY'))
        self.feedback = ''
        self.refined_recommendation = ''
        self.refinements = 3
        self.images = genai.upload_file(path=image)
        self.weather_data = weather_data
        self.load_few_shot_examples('FEW_SHOTS_EXAMPLES.txt')

    # def setup_model(self):
    #     """
    #     Setup the generative AI model and start a chat session. Includes error handling.
    #     """
    #     try:
    #         self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
    #         self.chat = self.model.start_chat()
    #     except Exception as e:
    #         print(f"Failed to initialize the AI model or start chat: {e}")
    #         raise
    # nie działa

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

    # def upload_photos(self):
    #     try:
    #         self.images = (genai.upload_file(path='video_screenshot.png'))
    #         # self.images = genai.upload_file(path=images)
    #     except Exception as e:
    #         print(f'Error loading photot: {e}')
    #         raise

    def generate_initial_recommendation(self, initial_prompt):
        self.chat.send_message(initial_prompt)

    def generate_feedback(self, feedback_prompt):
        self.feedback = self.chat.send_message(feedback_prompt).candidates[0].content
        time.sleep(10)
    
    def refine_recommendation(self, refinement_prompt):
        self.refined_recommendation = self.chat.send_message(refinement_prompt).candidates[0].content
        time.sleep(10)

    def to_markdown(self, text):
        # text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Below are examples of the reasoning you will follow: {self.few_shots_examples}.

    def run(self):
        initial_prompt = f""" You're an exceptionally well-trained, accurate and friendly robot named "what_to_wear_robot2000". Your goal is to prepare a recommendation of clothing for the weather to assure the user is comfortable and prepared. You're not a fashion critic and avoid fashion-related terms like "it's stylish etc.". 
                            You use a weather forecast {self.weather_data} and photos (that are passed directly to you, if they are not passed you don't make them up) from a given location to make this recommendation. You reason in a following way - first you think what to do, then you make an observation and then you return an actionable and specific list of clothing with a proper, yet concise explanation why you recommend them.
                            Final response template: 
                            - current date and time in the dd/mm/yyyy hh/mm format
                            - Short expalation how you combined data from the camera and forcast to show that you really understand what the weather is and will be and how other people behave during this weather.
                            - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort.
                            Use informative language in a way that user can trust you that you know what you're saying.
                            Format the response in html as a well-formated email message.
                            """     
        feedback_prompt = f"""You have a history of past experiences in which you were asked to recommend a clothing for the given weather based on {self.weather_data} and photos that are directly passed to you. 
                            Your goal is to analyze if your historical recommendation is thorough, complete and in alignement with your current knowledge, data and user's initial prompt. 
                            Analyse your reasoning to find out whether it's correct or there's something to improve. You reason in a following way - first you think what to do, then you make an observation and then you create a detailed plan what is wrong, what is good and what needs to be improved and return specific and actionable feedback that will be used to refine the answer. 
                            If you find the reasoning and recommendation correct and accurate - say it aloud. If not - also. Be critical yet constructive."""
        #the history comes from chat.history attibute in ChatSession
        refinement_prompt = f"""take feedback from previous message and use it to refine the output. Then return only the recommendation for the end user. Be concise yet precise and explain why did you recommend what you recommended. 
                            Final response template: 
                            - Short expalation how you combined data from the camera and forcast to show that you really understand what the weather is and will be and how other people behave during this weather.
                            - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort.
                            Use informative language and always include data like temperature (only in Celcius), wind, sun exposure and perticipation in a way that user can trust you that you know what you're saying.
                            Format the response in html as a well-formated email message.
                            """
        self.generate_initial_recommendation([initial_prompt, self.images])
        for _ in range(self.refinements):
            self.generate_feedback(feedback_prompt)
            self.refine_recommendation(refinement_prompt)
            time.sleep(10) #I kept getting 429 and decided to resolve it this way and it sucks guys


class SenderClient:

    def __init__(self) -> None:
        self.mailgun_api_key = 'aeb104e2e5860e8de96aaa0e85497a78-4c205c86-252461d4'
    def send_email(self, output):
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxaded245994de4fd8b8ff4b90dae5f9d9.mailgun.org/messages",
            auth=("api", self.mailgun_api_key),
            data={"from": "Your App <sandboxaded245994de4fd8b8ff4b90dae5f9d9@mailgun.org>",
                "to": ["charliemirek@gmail.com"],
                "subject": "Your clothing recommendationx§",
                "text": output})

        if response.status_code == 200:
            print("Message sent successfully: 200 OK")
        else:
            print(f"Failed to send message: {response.status_code} {response.reason}")


# app =  SelfRefine()

# app.run()
# print(f'here is a refined recommendation {app.refined_recommendation}')


class WhatToWear:

    """
    The app that based on weather data (forecast and images from public cameras) recommends what to wear to be comfortable outside 
    """

    def __init__(self):
        self.location = '274455' # currently it's only '274455' as it's a key of Krakow and getting the key for other location requires additional call that costs
        self.user = ''

        self.latest_recommendation = ''



    def run(self):
        try:
            weather_data_app = WeatherData('274455')
            weather_data = [weather_data_app.get_future_weather(),weather_data_app.get_current_weather()]
            take_screenshots = weather_data_app.take_screenshot()
            recommendation_app = SelfRefine(weather_data, take_screenshots)
            recommendation_app.run() # add images later
            sender_client = SenderClient()
            self.latest_recommendation = sender_client.send_email(recommendation_app.refined_recommendation)
        except Exception as e:
            f'shit happend: {e}'
            raise
        



# weather_data_app = WeatherData('274455')

# # weather_data.get_current_weather(weather_data.location)
# weather_data = [weather_data_app.get_future_weather(),weather_data_app.get_current_weather()]
# images = weather_data_app.take_screenshot()

# app = SelfRefine(weather_data)
# # print(f'here weather data##################################################### {app.weather_data}')
# app.run()

# print(app.refined_recommendation)
# print(app.chat.history)

app = WhatToWear()
app.run()