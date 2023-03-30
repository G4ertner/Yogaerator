from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import json
from kivy.network.urlrequest import UrlRequest
from creds import openai_key

# Remember to set your OpenAI API key
api_key = openai_key

class SetupScreen(Screen):
    pass

class WorkoutScreen(Screen):
    yoga_poses = StringProperty("")

    def on_request_success(self, request, result):
        poses = result['choices'][0]['text'].strip()
        self.yoga_poses = poses

    def on_request_failure(self, request, result):
        print("Request failed")

    def get_yoga_workout(self, workout_time, yoga_style):
        self.workout_time = workout_time
        self.yoga_style = yoga_style

        print(f'workout time: {workout_time}. Yoga style: {yoga_style}')
        prompt = {"workout time in min": int(workout_time), "yoga style": yoga_style}


        # load the prime prompt
        prime_prompt = f'As a knowledgeable yoga instructor, I require you to create a tailored yoga workout based on the given workout time and yoga style. You will provide a well-structured sequence of yoga poses in a bullet point list fitting the workout time. You will ensure that each pose is mentioned by its English name only. There should be no additional information, such as titles, descriptions, explanations, or any extra text before or after the list. The list should consist solely of yoga poses. Now, please create a suitable yoga workout sequence in the style of {yoga_style} for a {workout_time} minute workout.'
        print(f'prompt for GPT: {prime_prompt + str(prompt)}')


        url = "https://api.openai.com/v1/engines/text-davinci-003/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "prompt": prime_prompt + str(prompt),
            "max_tokens": 100,
            "n": 1,
            "stop": None,
            "temperature": 0.5
        }

        request = UrlRequest(
            url,
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=self.on_request_success,
            on_failure=self.on_request_failure,
            on_error=self.on_request_failure,
            method="POST"
        )


class YogaeratorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(WorkoutScreen(name='workout'))
        return sm

if __name__ == '__main__':
    YogaeratorApp().run()
