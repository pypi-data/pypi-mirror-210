# BLA-API-Wrapper.

## Description

##### A light weight python library to interact with [Beacon Light Academy's Homework App.](https://beaconlightacademy.edu.pk/app/)

### Table of Contents

- [Installation](#Installation)



- [Quick-Start](#Quick-Start)



- [Documentation](#Documentation)



- [Examples](https://github.com/Omer-Farooqui/BLA-Api-Wrapper/tree/master/examples)


- Useful Links:
  
  - [PyPI](https://pypi.org/project/BlaApi/)
  
  - [Github Repo](https://github.com/Omer-Farooqui/BLA-Api-Wrapper)

## Installation

The library is available on [PyPI](https://pypi.org/project/BlaApi/), install using pip.

```shell
pip install BlaApi
```

Or update it.

```shell
pip install BlaApi --upgrade
```

## Quick Start

The code below returns a list of **'notification_ids'** The date needs to be in the format; **'Abbreviated_Day, DD/MM/YYYY'**

```python
from BlaApi.diary import Diary
username = # Bla username
password = # Bla password

d = Diary(username=username, password=password)
notification_ids = d.search_by_date("Thu, 13/04/2023")
print(notification_ids)
```

###### Output:

```shell
['3049357', '3049213', '3038795', '3038038', '3036497', '3036305']
```

We can use **'notification ids'** to make api calls and retrieve useful information.

```python
#from BlaApi.client import Client
#c = Client(username, password)
c = d.client
diary_data = c.get_diary_data(notification_ids)
print(diary_data)
```

The output consists of a list of dictionaries which contain details for the corresponding notification id.

###### Output:

```python
[{
        "studentId": "8326",
        "id": "3049213",
        "appDiaryId": "64980",
        "title": "Class work - 13th April",
        "details": "<p><strong>Book: TBS</strong></p><p><strong>Unit 06: Setting up a company</strong></p><p><strong>Chapter 01: Gathering information</strong></p><p>Chapter completed; discussed all activities. 'Sharpen your skills' also covered. </p><p><br></p>",
        "bRead": "1",
        "created": "2023-04-13 10:05:25",
        "diaryType": "cw",
        "dateDue": None,
        "attachment": None,
        "attachment2": None,
        "dateSubmitted": None,
        "subject": "ENGLISH LANGUAGE",
        "currentTimestamp": "2023-04-15 15:25:21",
        "assignmentId": "64980",
        "gr_no": "12266",
        "comments": [],
},
]
```

*Currently, there is no built-in way to parse this output, but I might add it in the future if needed. Check out some [examples](https://github.com/Omer-Farooqui/BLA-Api-Wrapper/tree/master/examples) or read the [documentation.](#Documentation)*

## Documentation

This is some boilerplate code you should be familiar with.

```python
from BlaApi.client import Client
from BlaApi.diary import Diary
username = #bla username
password = #bla password

c = Client(username, password)
d = Diary(username, password)
```

> Whenever I mention **'Client'**, or **'Diary'**, it means that i'm talking about the files [client.py](https://github.com/Omer-Farooqui/BLA-Api-Wrapper/blob/master/BlaApi/client.py), and [diary.py](https://github.com/Omer-Farooqui/BLA-Api-Wrapper/blob/master/BlaApi/diary.py). Also keep in mind that In the api, the 'notificationId' and 'id' variables are used interchangeably.

The **'login()'** method from **'Client'** allows you to retrieve information such as: auth token, student names, student ids .

The **'get_diary_list()'** method from **'Client'**  will return a list of all the diaries available in the app's database, which allows you to retrieve information such as: date posted, subject name, assignment id, notification id (id), title, description, diary type (cw/hw), if the diary has been read (bRead) and the student id which the diary corresponds to.

The **'get_diary_data()'** method from **'Client'** allows you to get the content of the diary itself, by passing a list of notification ids. it has options such as: student id, app diary id (assignment id), attachment id, comments and the rest is the same as **get_diary_list()**

The **'Diary'** class contains many methods to parse and sort through the diary list, and return notification ids for the entries. The methods inside it also allow you to also pass in a list of notification ids as a second argument using its **'passthru'** variable.

The **'get_current_date()'** method from **'Diary'** returns today's date in a format that the api needs to function. (Abbreviated_Day, DD/MM/YYYY)

The **'search_by_student'** method from **'Diary'** returns the notification_ids for one of the students registered on your account. By default it sets student_number = 0, meaning it will return diaries for the first student by default.

The other methods from **'Diary'** are: **'search_by_date(date)'**, and **'search_been_read(True/False)'**. They are self explanatory.

## To-Do

- [ ] Add some way to parse the diary data
  
  - [ ] Comments
  
  - [ ] Description
  
  - [ ] Attachments

- [ ] Make better doccumentation

### My motivation to create this

Simply put, I found my school's app to be subpar, so I'm attempting to create a better one. *(It's also an excuse to learn new skills)*




Feel free to open an [issue](https://github.com/Omer-Farooqui/BLA-Api-Wrapper/issues) if you want to send hate comments, and star my [repo](https://github.com/Omer-Farooqui/BLA-Api-Wrapper) if you don't 👉👈.
