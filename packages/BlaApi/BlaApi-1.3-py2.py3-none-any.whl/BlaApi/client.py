import json
import httpx
from fake_useragent import UserAgent as ua

class Client:
    client = httpx.Client() # instanciate 
    #! BLA credentials must be passed in as string
    def __init__(self, username: str, password: str):
        # Random UserAgent
        self.headers = {'UserAgent': str(ua().chrome)}
        self.username = username
        self.password = password
        self.token = self.login().get('token')
        self.student_ids = self.login().get('student_ids')
        self.student_names = self.login().get('student_names')
        
    def login(self):
        # Construct API endpoint URL
        endpoint = "login"
        api_url = f"https://beaconlightacademy.edu.pk/app/restapi.php?endpoint={endpoint}&rnd=1667581678739&username={self.username}&password={self.password}"
        
        # Send POST request to API endpoint with headers
        response = self.client.post(api_url, headers=self.headers)
        
        #! Raise an error if POST fails
        response.raise_for_status()
        
        # error handling
        if json.loads(response.content).get('success') == False:
            raise ValueError(json.loads(response.content).get('error'))
        
        data = json.loads(response.content)['data']
        # Retrieve access token & student info from JSON response
        token = data.get('accessToken')
        student_info = data.get('students')

        # Return student ids and student names as lists
        student_ids = [] #Initialize
        student_names = [] #Initialize

        for s in student_info:
            # Return student ids as list
            id = s.get('id')
            student_ids.append(id)

            # Return student name as list
            name = s.get('studentName')
            student_names.append(name)


        # Return retrieved data as dictionary
        output = {
            'token': token,
            'student_ids': student_ids,
            'student_names': student_names

        }
        return output

    def get_diary_list(self):
        # Construct API endpoint URL
        endpoint = "diaryList"
        api_url = f"https://beaconlightacademy.edu.pk/app/restapi.php?endpoint={endpoint}&accessToken={self.token}&year=1"
        
        # Send POST request to API endpoint with headers
        response = self.client.post(api_url, headers=self.headers)
        
        # error handling
        if json.loads(response.content).get('success') == False:
            raise ValueError(json.loads(response.content).get('error'))
        
        #! Raise an error if POST fails
        response.raise_for_status()
        
        # Retreive diary list from JSON response
        data = json.loads(response.content)['data']
        
        return data

    def get_diary_data(self, notification_ids: list):
        
        output = [] # initialize

        if not isinstance(notification_ids, list): # error check
            raise ValueError("Notification IDs must be passed as a list")
        
        for notification_id in notification_ids:
            # Construct API endpoint URL
            endpoint = "diaryDetails"
            api_url = f"https://beaconlightacademy.edu.pk/app/restapi.php?endpoint={endpoint}&accessToken={self.token}&appUserNotificationId={notification_id}"
            
            # Send POST request to API endpoint with headers
            response = self.client.post(api_url, headers=self.headers)
            
            #! Raise an error if POST fails
            response.raise_for_status()
            
            
            # error handling
            if json.loads(response.content).get('success') == False:
                raise ValueError(json.loads(response.content).get('error'))
            
            # Retrieve diary data from JSON response
            data = json.loads(response.content)['data']
            output.append(data)

        return output