import google.generativeai as genai
import requests
import cv2
import time
from dotenv import load_dotenv
import os

load_dotenv()



class WeatherData:
    """
    It fetches and stores weather data and images from public cameras based on 
    """

    def __init__(self, location: str) -> None:
        self.weather_api_key = '5KUGp6jFh5VEK2ywhhCgaAwizCOHYGvV'
        self.location = location
        self.nearest_cameras = [
            'https://imageserver.webcamera.pl/rec/krakow-florianska/latest.mp4',
            'https://imageserver.webcamera.pl/rec/krakow-synagoga-stara/latest.mp4',
            'https://imageserver.webcamera.pl/rec/krakow-wentzl/latest.mp4'
        ]
        self.screenshot_index = 0 
        self.weather_camera_images = [self.take_screenshot(camera) for camera in self.nearest_cameras]
        self.weather_future = ''
        self.weather_current = ''

    def take_screenshot(self, camera) -> str:
        cap = cv2.VideoCapture(camera)
        success, frame = cap.read()
        if not success:
            print("Failed to capture video frame")
            return None
        self.screenshot_index += 1
        screenshot_path = f"video_screenshot{self.screenshot_index}.png"
        cv2.imwrite(screenshot_path, frame)
        cap.release()
        return screenshot_path

    def get_future_weather(self) -> object:
        base_url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{self.location}"
        params = {
            "apikey": self.weather_api_key,
            'language': 'en-us',
            "details": True,
            'metrics': True
        }
        response = requests.get(base_url, params=params)
        self.weather_future = f'This is the 12-hours forecast:{response.json()}'

    def get_current_weather(self) -> object:
        base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{self.location}"
        params = {
            "apikey": self.weather_api_key,
            'language': 'en-us',
            "details": True,
        }
        response = requests.get(base_url, params=params)
        self.weather_current = f'This is the current weather:{response.json()}'


class SelfRefineAgent:

    """
    It takes weather_data for a given location (current and future) and images from cameras and returns clothing recomendation

    """

    def __init__(self, weather_data, images):
        # self.setup_model()
        self.generation_config = {
                                    "temperature": 1,
                                    "top_p": 0.95,
                                    "top_k": 0,
                                    "max_output_tokens": 8192,
                                    "stop_sequences": [
                                        "NO IMPROVEMENT NEEDED",
                                    ],
                                    }
        self.model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest',generation_config=self.generation_config)
        self.chat = self.model.start_chat()
        self.apikey = 'AIzaSyDKtHnN25xQYIODAAZczivqmUS0rFjpUA8'  #coś tu kurwa nie działa genai.configure(os.getenv('GEMINI_API_KEY'))
        self.refinements = 2
        self.images = [genai.upload_file(path=image) for image in images]
        self.weather_data = weather_data
        self.refined_recommendation = ''

    def generate_initial_recommendation(self, initial_prompt):
        self.chat.send_message(initial_prompt)

    def generate_feedback(self, feedback_prompt):
        self.feedback = self.chat.send_message(feedback_prompt).text
        time.sleep(7)
    
    def refine_recommendation(self, refinement_prompt):
        self.refined_recommendation = self.chat.send_message(refinement_prompt).text
        time.sleep(7)


# Below are examples of the reasoning you will follow: {self.few_shots_examples}.

#     def run(self):
#         initial_prompt = f""" You're an exceptionally well-trained, accurate and friendly robot named "what_to_wear_robot2000". Your goal is to prepare a recommendation of clothing for the weather to assure the user is comfortable and prepared. You will avoid fashion-related tips like "it's stylish etc.". 
#                             You use a weather forecast {self.weather_data} and uploaded photos (that are passed directly to you, you, will receive them firstif they are not passed you don't make them up) from a given location to make this recommendation. You reason in a following way - first you think what to do, then you make an observation and then you return an actionable and specific list of clothing with a proper, yet concise explanation why you recommend them. Also don't overrecommend - if you don't know something, admit it. If you don't see any people on the pictures - admit it. If there's no chance for precipitation don't recommend an umbrella. You must rely only on information from the weather forecast and pictures analysis.
#                             To analyze the photos: You need to analyse in a step by step way uploaded photos to discover what people wear in the pictures. Answer in detail what cloths they wear, what is a general clothing rule amongst them, how does it relate to your knowledge about proper clothing for the weather, what is the quality of the photo especially how many people there is and how good or bad you can recognise their cloths and what are the current weather conditions. Then return the observation.
#                             To analyze the forecast: You need to analyse in a step by step way data from the weather forecast to discover what is the weather in a given location to discover what would be a suitable clothing for these conditions. Answer in detail what current and future weather conditions are in a given location, especially what’s temperature, any kind of participation, wind, sun exposure, UV and other relevant factors. You’re oriented on a potential change of the weather conditions and how it will impact the clothing. Also, you’re aware of the location’s climate and time of the year and day. Then return the observation.
#                             To return the final recommendation: You need to think in a step by step way about the recommendation to be sure that the user will wear proper clothing for the weather. You will take into account factors like temperature regulation, moisture control, protection, mobility, comfort and materials. You analyse observations from the previous steps and looking for similarities and contradictions between photos, their descriptions and the weather forecast. You focus on finding the most critical and less important clothing and the weather details to provide the best recommendation.
#                             Final response template: 
#                             - Expalation how you combined data from the cameras and forcast to show that you really understand what the weather is and will be and how other people behave during this weather.
#                             - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort.
#                             Use informative language in a way that user can trust you that you know what you're saying. Format the response in html as a well-formated email message like this:
# <html><body><h2>Recommendation title</h2><h3>Explanation</h3><ul><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li></ul></body></html>                            """     
#                             #the history comes from chat.history attibute in ChatSession
#         feedback_prompt = f"""You have a history of past experiences in which you were asked to recommend a clothing for the given weather based on {self.weather_data} and photos that are directly passed to you. 
#                             Your goal is to analyze if your historical recommendations are thorough, complete and in alignement with the data and user's initial prompt. Everything to ensure that the user will receive reliable recommendation. Also, care about the proper html formatting. If you need to you can run the photos and forecast analysis once again.
#                             Analyse your reasoning to find out whether it's correct or there's something to improve. You reason in a following way - first you think what to do, then you make an observation and then you create a detailed plan what is wrong, what is good and what needs to be improved and return specific and actionable feedback that will be used to refine the answer. 
#                             If you find the reasoning and recommendation correct and accurate - say these exact words "NO IMPROVEMENT NEEDED". If it's not correct and accurate say "FEEDBACK MUST BE IMPLEMENTED". Always be critical yet constructive."""
        
#         refinement_prompt = f"""Take feedback from the previous message and use it to refine the output. Make sure you're correct with your understanding of the feedback. Then return only the relevant recommendation for the end user. Be concise yet precise and explain why did you recommend what you recommended. Also don't overrecommend - if you don't know something, admit it. If you don't see any people on the pictures - admit it. If there's no chance for precipitation don't recommend an umbrella. You must rely only on information from the weather forecast and pictures analysis.
#                             Final response template: 
#                             - Expalation how you combined data from the camera and forcast to show that you really understand what the weather is and will be and how other people behave during this weather.
#                             - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort.
#                             Use informative language and always include data like temperature (only in Celcius), wind, sun exposure and perticipation chance (in %) in a way that user can trust you that you know what you're saying.
#                             Format the response in html as a well-formated email message like this:
# <html><body><h2>Recommendation title</h2><h3>Explanation</h3><ul><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li></ul></body></html>
# """
#         self.generate_initial_recommendation(['first image to analyze', self.images[0], 'second image to analyze', self.images[1], 'third image to analyze', self.images[2], initial_prompt])
#         for _ in range(self.refinements):
#             self.generate_feedback(feedback_prompt)
#             self.refine_recommendation(refinement_prompt)
#             time.sleep(10) #I keep getting 429 and decided to resolve it this way and it sucks guys

    def run(self):
        initial_prompt = f""" You're an exceptionally well-trained, accurate and friendly robot named "what_to_wear_robot2000". Your goal is to prepare a recommendation of clothing for the weather to assure the user is comfortable and prepared. You will avoid fashion-related tips like "it's stylish etc.". You use a weather forecast {self.weather_data} and uploaded photos (that are passed directly to you, you, will receive them firstif they are not passed you don't make them up) from a given location to make this recommendation. You reason in a following way - first you think what to do, then you make an observation and then you return an actionable and specific list of clothing with a proper, yet concise explanation why you recommend them. Also don't overrecommend - if you don't know something, admit it. If you don't see any people on the pictures - admit it. If there's no chance for precipitation don't recommend an umbrella. You must rely only on information from the weather forecast and pictures analysis. To analyze the photos: You need to analyse in a step by step way uploaded photos to discover what people wear in the pictures. Answer in detail what cloths they wear, what is a general clothing rule amongst them, how does it relate to your knowledge about proper clothing for the weather, what is the quality of the photo especially how many people there is and how good or bad you can recognise their cloths and what are the current weather conditions. Analyse each photo in the same detailed and thorough way. Then return the observation. To analyze the forecast: You need to analyse in a step by step way data from the weather forecast to discover what is the weather in a given location to discover what would be a suitable clothing for these conditions. Answer in detail what current and future weather conditions are in a given location, especially what’s temperature, any kind of participation, wind, sun exposure, UV and other relevant factors. You’re oriented on a potential change of the weather conditions and how it will impact the clothing. Display temperature only in Celcius degrees Also, you’re aware of the location’s climate and time of the year and day. Then return the observation. To return the final recommendation: You need to think in a step by step way about the recommendation to be sure that the user will wear proper clothing for the weather. You will take into account factors like temperature regulation, moisture control, protection, mobility, comfort and materials. You analyse observations from the previous steps and looking for similarities and contradictions between photos, their descriptions and the weather forecast. You focus on finding the most critical and less important clothing and the weather details to provide the best recommendation. Final response template: - Expalation how you combined data from the cameras and forcast to show that you really understand what the weather is and will be and how other people behave during this weather. - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort. Use informative language in a way that user can trust you that you know what you're saying. Format the response in html as a well-formated email message like this: <html><body><h2>Recommendation title</h2><h3>Explanation</h3><ul><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li></ul></body></html>"""     
                            #the history comes from chat.history attibute in ChatSession
        feedback_prompt = f"""You have a history of past experiences in which you were asked to recommend a clothing for the given weather based on {self.weather_data} and images that are directly passed to you. Your goal is to analyze if your historical recommendations are thorough, complete and in alignement with the data from the forecast and from the images and the user's initial prompt. Everything to ensure that the user will receive reliable recommendation. Also, care about the proper html formatting. If you need to you can run the images and forecast analyzis once again. Analyze your reasoning to find out whether it's correct or there's something to improve. You reason in a following way - first you think what to do, then you make an observation and then you create a detailed plan what is good and what needs to be improved and return specific and actionable feedback that will be used to refine the answer. If you find the reasoning and recommendation correct and accurate - say these exact words "NO IMPROVEMENT NEEDED". If it's not correct and accurate say "FEEDBACK MUST BE IMPLEMENTED". Always be critical yet constructive."""
        
        refinement_prompt = f"""Take feedback from the previous message and use it to refine the output. Make sure you're correct with your understanding of the feedback. Then return only the relevant recommendation for the end user. Be concise, but explain why did you recommend what you recommended. Also don't overrecommend - if you don't know something, admit it. If you don't see any people on the pictures - admit it. If there's no chance for precipitation don't recommend an umbrella. You must rely only on information from the weather forecast and pictures analysis. Final response template: - Expalation how you combined data from the camera and forcast to show that you really understand what the weather is and will be and how other people behave during this weather. - List of cloths to wear - It has to be easy to understand and actionable. Pay special attention to all elements that are either warm or cooling or providing additonal comfort. Use informative language and always include data like temperature (display temperature only in Celcius degrees), wind, sun exposure and perticipation chance (in %) in a way that user can trust you that you know what you're saying. Format the response in html as a well-formated email message like this: <html><body><h2>Recommendation title</h2><h3>Explanation</h3><ul><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li><li><b>some clothing</b></li></ul></body></html>
"""
        self.generate_initial_recommendation(['first image', self.images[0], 'second image', self.images[1], 'third image', self.images[2], initial_prompt])
        for _ in range(self.refinements):
            self.generate_feedback(feedback_prompt)
            self.refine_recommendation(refinement_prompt)
            time.sleep(7) #I keep getting 429 and decided to resolve it this way and it sucks guys


class SenderClient:


    def __init__(self) -> None:
        self.mailgun_api_key = 'aeb104e2e5860e8de96aaa0e85497a78-4c205c86-252461d4'
    def send_email(self, message):
        response = requests.post(
            "https://api.mailgun.net/v3/sandboxaded245994de4fd8b8ff4b90dae5f9d9.mailgun.org/messages",
            auth=("api", self.mailgun_api_key),
            data={"from": "Your App <sandboxaded245994de4fd8b8ff4b90dae5f9d9@mailgun.org>",
                "to": ["charliemirek@gmail.com"],
                "subject": "Your clothing recommendation for today!",
                "html": message})

        if response.status_code == 200:
            print("Message sent successfully: 200 OK")
        else:
            print(f"Failed to send message: {response.status_code} {response.reason}")


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
            weather_data_app.get_future_weather()
            weather_data_app.get_current_weather()
            weather_data = [weather_data_app.weather_current, weather_data_app.weather_future]
            take_screenshots = weather_data_app.weather_camera_images
            recommendation_app = SelfRefineAgent(weather_data, take_screenshots)
            recommendation_app.run()
            sender_client = SenderClient()
            self.latest_recommendation = sender_client.send_email(recommendation_app.refined_recommendation)
            print(f'tutaj ta jebana historia pierdolona kurwa mac:###############{recommendation_app.chat.history}#######################')
        except Exception as e:
            f'shit happend: {e}'
            raise
        
app = WhatToWear()
app.run()