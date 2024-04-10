import os
import cv2
import requests
import base64

# export OAI_api_key=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
# export OWE_api_key=e87699dec87db9816c4d72e92d5d875e
# export G_api_key=AIzaSyDKtHnN25xQYIODAAZczivqmUS0rFjpUA8


class WeatherApp:
    def __init__(self, location):
        self.location = location
        self.current_weather = None
        self.future_weather = None
        self.recommendation = None
        self.user_clothing = ['jacket.png','gloves.png','coat.png']
        self.nearest_camera = 'https://imageserver.webcamera.pl/rec/krakow-florianska/latest.mp4'
        self.OAI_api_key = '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'
        self.OWE_api_key = 'e87699dec87db9816c4d72e92d5d875e'
        self.Mailgun_api_key = 'aeb104e2e5860e8de96aaa0e85497a78-4c205c86-252461d4'
    
    def get_camera():
        # just get a camera from worldcam.eu, waiting for api
        pass

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

    def get_current_weather(self):
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.location,
            "appid": self.OWE_api_key,
            "units": "metric"
        }
        response = requests.get(base_url, params=params)
        self.current_weather = response.json()
    
    def get_future_weather(self):
        base_url = "https://pro.openweathermap.org/data/2.5/forecast/hourly"
        params = {
            "q": self.location,
            "appid": self.OWE_api_key,
            "units": "metric"
        }
        response = requests.get(base_url, params=params)
        self.future_weather = response.json()


    def get_recommendation(self):
        if not self.current_weather:
            print("Weather data not available.")
            return
        
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        image_path = "video_screenshot.png"
        base64_image = encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.OAI_api_key}"
        }
        
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You're a trained robot that recognizes what clothing people wear outside on pictures from street cameras. 
                                        Your goal is to reason in a step by step manner what should a person wear to be prepared for a given weather conditions as the people in the picture are prepared. 
                                        Combine this knowledge with data from {self.current_weather}, forecast from {self.future_weather} and with users clothing (one of the images attached) and return a short recommendation including if any of his/her clothing suits the weather. Don't ramble. Avoid very obvious recommendations. Also explain why do you recommend what you recommend.
                                        Response template: 
                                        - List of cloths to wear - from the most outer layer and exclude panties. Pay special attention to all elements that are either warm or cooling.
                                        - Reasoning behind recommendation how you combined data from the camera and forcast. Keep it concise, don't ramble. Tell what is the sky color in the screenshot you see.
                                        """
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                                                {
                            "type": "image_url",
                            "image_url": {
                                "url": 'https://8a.pl/media/catalog/product/_/T/_The_North_Face_Recycled_Mcmurdo___brandy_brown_196573647046a_2b68.webp'
                            }
                        }
                        
                         
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        self.recommendation = data['choices'][0]['message']['content']
        
        #return print(data['choices'][0]['message']['content'])
    
    # def send_email(self, output):
    #     response = requests.post(
    #         "https://api.mailgun.net/v3/sandboxaded245994de4fd8b8ff4b90dae5f9d9.mailgun.org/messages",
    #         auth=("api", self.Mailgun_api_key),
    #         data={"from": "Your App <sandboxaded245994de4fd8b8ff4b90dae5f9d9@mailgun.org>",
    #             "to": ["charliemirek@gmail.com"],
    #             "subject": "Hello",
    #             "text": output})

    #     if response.status_code == 200:
    #         print("Message sent successfully: 200 OK")
    #     else:
    #         print(f"Failed to send message: {response.status_code} {response.reason}")

    def run(self):
        self.get_current_weather()
        self.get_future_weather()
        print(self.current_weather)
        print(self.future_weather)
        screenshot_path = self.take_screenshot()
        if screenshot_path:
            print(f"Screenshot saved to {screenshot_path}")
        else:
            print("Could not take a screenshot of the video.")
        self.get_recommendation()
        # self.send_email(self.recommendation)
        print(self.recommendation)


if __name__ == "__main__":
    app = WeatherApp('Krakow, PL')
    app.run()

