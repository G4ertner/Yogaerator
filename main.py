from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty
import json
from kivy.network.urlrequest import UrlRequest
from creds import openai_key
from kivy.clock import Clock
from functools import partial
import kivy.properties as properties
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.core.window import Window

# Remember to set your OpenAI API key
api_key = openai_key

# setup workout variables
# make response global to be accessible from other functions
global response

######################################
### Setup Screen
#####################################

class SetupScreen(Screen):
    pass

####################################################################
### Workout Overview Screen
####################################################################

class WorkoutOverview(Screen):
    yoga_title = StringProperty("")
    yoga_description = StringProperty("")
    yoga_poses = StringProperty("")
    workout = properties.ListProperty()

    def on_request_success(self, request, result):
        # strip the content from the response
        #res = result['choices'][0]['message']['content'].strip()
        res='''{
    "title": "10-Minute Dog Yoga Sequence",
    "description": "This 10-minute dog yoga sequence is designed to help your furry friend stretch, relax and bond with you. The poses are gentle and easy to follow, and will help your dog release tension and stress.",
    "poses": [
        {
            "pose": "Downward-Facing Dog",
            "breaths": 3,
            "seconds": 30
        },
        {
            "pose": "Upward-Facing Dog",
            "breaths": 3,
            "seconds": 30
        },
        {
            "pose": "Puppy Pose",
            "breaths": 4,
            "seconds": 40
        },
        {
            "pose": "Low Lunge",
            "breaths": 4,
            "seconds": 40
        },
        {
            "pose": "Warrior I",
            "breaths": 3,
            "seconds": 30
        },
        {
            "pose": "Warrior II",
            "breaths": 3,
            "seconds": 30
        },
        {
            "pose": "Triangle Pose",
            "breaths": 3,
            "seconds": 30
        },
        {
            "pose": "Tree Pose",
            "breaths": 4,
            "seconds": 40
        },
        {
            "pose": "Corpse Pose",
            "breaths": 3,
            "seconds": 30
        }
    ]
}'''
        print(res)

        # turn response into json object
        response = json.loads(res)

        # post instructions on overview screen
        self.yoga_title = response['title']
        self.yoga_description = response['description']
        self.yoga_poses = "Poses:\n- " + '\n- '.join([d['pose'] for d in response['poses']])
        self.workout = response['poses']

        self.build_accordion(response['poses'])

    def on_request_failure(self, request, result):
        print("Request failed")

    def get_yoga_workout(self, workout_time, yoga_style):
        self.workout_time = workout_time
        self.yoga_style = yoga_style

        print(f'workout time: {workout_time}. Yoga style: {yoga_style}')
        prompt = f"Yoga style: {yoga_style}; Workout time: {int(workout_time)} minutes."


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

#        request = UrlRequest(
#            url,
#            req_body=json.dumps(data),
#            req_headers=headers,
#            on_success=self.on_request_success,
#            on_failure=self.on_request_failure,
#            on_error=self.on_request_failure,
#            method="POST"
#        )

        self.on_request_success(0,0)

    def build_accordion(self, data):
        #accordion = Accordion()
        accordion = Accordion(orientation='vertical',  size_hint_y=None)

        for item in data:
            accordion_item = AccordionItem(title=item['pose'])
            content_label = Label(
                text=f"Breaths: {item['breaths']}\nSeconds: {item['seconds']}",

            )
            content_label.height = content_label.texture_size[1] + 20
            accordion_item.add_widget(content_label)
            accordion.add_widget(accordion_item)



        # define the size of the accordionItems
        accordion.height = len(accordion.children) * 60  # Set the height

        # Add a dummy AccordionItem at the end to have the visual of a fully closed accordion
        item_dummy = AccordionItem(title='')
        accordion.add_widget(item_dummy)

        overview_screen = self.manager.get_screen('overview')
        overview_screen.ids.container.add_widget(accordion)

        # Set the dummy item as the selected one
        accordion.select(item_dummy)

##########################################
### Workout Screen
##########################################

class Workout(Screen):
    yoga_pose = StringProperty("Downward Dog")
    breath_count = StringProperty("0 breaths")
    gradient = properties.NumericProperty()
    count = 0

    def update_pose(self, poses, pose_index=0, breath_index=None, interval_on=False):
        if pose_index < len(poses):
            pose = poses[pose_index]

            # Update yoga pose if it's the first breath
            if breath_index is None:
                self.yoga_pose = pose['pose']
                breath_index = pose['breaths']

            # Calculate length of breath
            breath_length = int(pose['seconds'] / pose['breaths'])
            breath_middle = breath_length/2
            breath_interval = (breath_length/2) /100
            print(f'breath no: {breath_index}, breath length in seconds: {breath_length}, breath middle: {breath_middle}, breath interval {breath_interval}')

            # Update breaths (counting down)
            self.breath_count = f"{breath_index} breath"
            breath_index -= 1
            self.count = 0
            self.gradient = 0

            # update gradient
            if not interval_on:
                interval_on = True
                Clock.schedule_interval(partial(self.upgrade_gradient, breath_middle), breath_interval)

            # If all breaths are completed for the current pose, move to the next pose
            if breath_index < 0:
                breath_index = None
                pose_index += 1

            # Schedule the update_pose function to be called after a pause
            Clock.schedule_once(lambda dt: self.update_pose(poses, pose_index, breath_index, interval_on), breath_length)

    def upgrade_gradient(self, middle, interval):
        print(f'gradient is {self.gradient}, count is {self.count}. middle is {middle}')
        if self.count <= middle:
            self.gradient += 0.01
        elif self.count > middle:
            self.gradient -= 0.01
        self.count += interval


    def callback(self, dt):
        pass

# TODO: Add Pause button to workout screen
# TODO: on overview, make poses buttons that open pop-up window. In window, explain pose, have 'start from here' button



####################################
### Screen Manager
####################################

class YogaeratorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(WorkoutOverview(name='overview'))
        sm.add_widget(Workout(name='workout'))
        return sm

if __name__ == '__main__':
    YogaeratorApp().run()
