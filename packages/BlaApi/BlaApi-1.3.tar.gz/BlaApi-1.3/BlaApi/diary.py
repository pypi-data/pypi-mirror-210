import datetime
from BlaApi.client import Client

class Diary:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client(self.username, self.password)
        self.student_ids = self.client.student_ids

    def search_by_student(self, student_number=0, passthru=None):

        diary = self.client.get_diary_list()

        # select the student id on the index: student_number

        student_id = self.student_ids[student_number]
        
        # parse output from diary list function
        # if student id is a match then
        # return the diaries as a list

        # allows passing of already searched list 
        # to perform further sorting

        output = [] # initialize
        if passthru:
            for p in passthru:
                for d in diary:
                    if p == d['id'] and d['studentId'] == student_id:
                        output.append(d['id'])

        if not passthru:
            for d in diary:
                if d['studentId'] == student_id:  
                    output.append(d['id'])
        if output:
            return output
        else:
            raise LookupError('No entries for provided student id.')
        
    def get_current_date(self):
        
        # Retreive current date in a format that the api requires. 
        #! EXAMPLE: "Tue, 9/11/2001"

        # Get current date and day of week
        current_date = datetime.datetime.today()
        day_of_week = current_date.strftime("%A")

        # Format day of week to abbreviated format (e.g. 'Mon')
        abbreviated_day_of_week = day_of_week[:3]

        # Get current day and month
        current_day = str(current_date.day).zfill(2)
        current_month = str(current_date.month).zfill(2)

        # Format date string
        formatted_date = f"{abbreviated_day_of_week}, {current_day}/{current_month}/{current_date.year}"
        
        return formatted_date

    def search_by_date(self, date, passthru= None):

        diary = self.client.get_diary_list()
        # parse output from diary list function
        # if student id is a match then
        # return the diaries as a list

        # allows passing of already searched list 
        # to perform further sorting


        output = [] # initialize

        if passthru:
            for p in passthru:
                for d in diary:
                    if p == d['id'] and d['date'] == date:
                        output.append(d['id'])

        if not passthru:
            for d in diary:
                if d['date'] == date:
                    output.append(d['id'])
        if output:
            return output
        else:
            raise LookupError('No matching entries for the specified date.')


    def search_been_read(self, been_read=True, passthru=None):

        diary = self.client.get_diary_list()

        # parse output from diary list function
        # if diary has been read/unread then
        # return the diaries as a list

        # allows passing of already searched list 
        # to perform further sorting
        # pass in a list of notification ids as passthru arg
         
        
        output = [] # initialize
        
        been_read = str(int(been_read))
        if passthru:
            for p in passthru:
                for d in diary:
                    if p == d['id'] and d['bRead'] == been_read:
                        output.append(d['id'])

        else:
            for d in diary:
                if d['bRead'] == been_read:
                    output.append(d['id'])
        if output:
            return output
        else:
            raise LookupError('No unread/read diaries found.')