from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import json
from kivy.network.urlrequest import UrlRequest
from creds import openai_key

# Remember to set your OpenAI API key
api_key = openai_key

# setup workout variables
title = ''
description = ''
workout = {}
workout_poses = ''

class SetupScreen(Screen):
    pass

class WorkoutOverview(Screen):
    yoga_title = StringProperty("")
    yoga_description = StringProperty("")
    yoga_poses = StringProperty("")



    def on_request_success(self, request, result):
        res = result['choices'][0]['message']['content'].strip()
        print(res)
        response = json.loads(res)
        self.yoga_title = response['title']
        self.yoga_description = response['description']
        self.yoga_poses = "Poses:\n- " + '\n- '.join([d['pose'] for d in response['poses']])


    def on_request_failure(self, request, result):
        print("Request failed")

    def get_yoga_workout(self, workout_time, yoga_style):
        self.workout_time = workout_time
        self.yoga_style = yoga_style

        print(f'workout time: {workout_time}. Yoga style: {yoga_style}')
        prompt = f"Yoga style: {yoga_style}; Workout time: {int(workout_time)}"


        # load the prompts
        system_prompt = f'''
        As a knowledgeable yoga instructor, will you create a tailored yoga workout based on the given workout time and yoga style provided to you by the user.
        You will provide a well-structured sequence of yoga poses fitting the workout time. You will ensure that each pose is mentioned by its English name only (no Sanskrit names, not even in brackets or parentheses).
        You will provide your answer in a JSON format containing the following: First, a title for the workout, then a short description/introduction of the workout (2-3 sentences), and then for each pose the pose name, amounts of breaths in this pose, and seconds on how long this pose lasts.
        '''
        first_user_prompt = '''
        Yoga style: Relaxation; Workout time: 14 minutes
        '''
        first_assistant_prompt = '''
        {
        "title": "15-Minute Relaxation Yoga Sequence",
        "description": "This 15-minute relaxation yoga sequence is designed to help you release tension and restore a sense of calmness in both your body and mind. The gentle, slow-paced poses will encourage deep relaxation and help you feel refreshed after completing the practice.",
        "poses": [
        {
        "pose": "Child's Pose",
        "breaths": 6,
        "seconds": 60
        },
        {
        "pose": "Cat-Cow",
        "breaths": 8,
        "seconds": 80
        },
        {
        "pose": "Seated Forward Bend",
        "breaths": 6,
        "seconds": 60
        },
        {
        "pose": "Butterfly Pose",
        "breaths": 5,
        "seconds": 50
        },
        {
        "pose": "Supported Fish Pose",
        "breaths": 6,
        "seconds": 60
        },
        {
        "pose": "Happy Baby Pose",
        "breaths": 6,
        "seconds": 60
        },
        {
        "pose": "Reclined Spinal Twist",
        "breaths": 6,
        "seconds": 60
        },
        {
        "pose": "Legs Up the Wall",
        "breaths": 10,
        "seconds": 100
        },
        {
        "pose": "Corpse Pose",
        "breaths": 12,
        "seconds": 120
        }
        ]
        }
        '''


        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": first_user_prompt},
                {"role": "user", "content": first_assistant_prompt},
                {"role": "user", "content": prompt}],
            "max_tokens": 2048,
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
        sm.add_widget(WorkoutOverview(name='workout'))
        return sm

if __name__ == '__main__':
    YogaeratorApp().run()
