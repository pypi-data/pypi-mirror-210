# SCF_FSM_PACKAGE

![Logo](https://finflo-test.netlify.app/static/media/finfloLogo.52c3039f.svg)

A resuable python django package that can handle state transition and workflow's in your django application .

## Description
- The finflo package is designed to handle the workflow management cycle .
- Your state transition's are made easy with finflo
- customizable Actions and states with on_flow interchangable
- Pre installed signature levels for each action

## TECHNOLOGY STACK
[![https://www.python.org/](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DJANGO](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)

## IMPORTANT LINKS 

1. [Documentation](https://documenter.getpostman.com/view/11858287/2s8YmUJyvy)
2. [Postman collection](https://api.postman.com/collections/11858287-f9ff5270-991d-4782-9fab-c034597f3f43?access_key=PMAT-01GJCW5ZKHZM68NWKCNW7KDJP2)



## Authors

- [@anandrajB](https://github.com/anandrajB)


## Prerequisite
- python
- Django
- Django-rest-framework

## 1. Installation 

### 1.1 Initial setup

- Install finflo using [pip](https://pypi.org/project/finflo/)

```bash
pip install finflo
```

- In your django application , browse to installed_apps section in settings.py and add this ,

```bash
INSTALLED_APPS = [
    'finflo',
    'rest_framework'
]
```
- Add this in your settings.py 

```bash
FINFLO = {
    'WORK_MODEL' : ['MyApp.Model','MyApp2.Model2'],
    'PARTY_TYPE' : [] #optional
}
```
- The PARTY_TYPE is optional , if it is not needed you can leave it as blank like this []

- Navigate to the middleware section in your settings.py and add the finflo middleware

```
MIDDLEWARE = [
    'finflo.middleware.TransitionUserMiddleware',
]
```

- Now add this peice of code in your urls.py

```
urlpatterns = [
    path('', include('finflo.urls'))
]
```
### 1.2 Migrations

- once all the steps done from the above section 1.1 .
- now we can apply the migrations for the database using ,
```
- python manage.py makemigrations
```
```
- python manage.py migrate 
```

### 1.3 Re-migrate
- ***scenario 1*** : if any new values is added to the **WORK_MODEL**
- ***example for scenario 1 :***
```
# see 1.1 

FINFLO = {
    'WORK_MODEL' : ['MyApp.Model','MyApp2.Model2','MyApp3.Model3'],
    'PARTY_MODEL' : ['MyApp1.Model1'] 
}

```
- In the above 1.1 , you can see *MyApp3.Model3* is newly addded 
- Now you can remigrate the database without droping it simply by the below command .

```
- python manage.py migrate --fake finflo 0001
- python manage.py migrate finflo 0002
```

## Usage

1. Once your setup is completed , whenever the objects in **WORK_MODEL** is created , the finflo automatically creates :
    
    - Transition manager
    - workflowitems 
    - workevents

2. The transition for each model can be carried out with 2 methods:
    
    1. Navigate to the url : *localhost/transition/*
        - in the content section use the format as below and POST 
        - {"type" : "MyApp.Model" , "action" : "MyAction" , "t_id" : "1"}
    
    2. In Postman , pass the following key in body as follows 

        - t_id (transition_id)
        - type (model_type)
        - action 
        - Example <br /> ![Screenshot](finflo_postman.PNG)


3.  Some important information for transition are as follows :
    
    |  Arguments   | Data_Type  |
    | ------------- | ------------- |
    | type   | str  |
    | action  | str  |
    | t_id | int  | 
    | source  | str  | 
    | interim  | str  | 
    | target  | str  | 
    | from_party  | str  | 
    | to_party  | str  | 




## API URLS

1. List of all Url's

| Api URL's  | METHOD | FORM DATA | QUERY_PARAMS |
| ------------- | ------------- | ------------- | ------------- |
| *localhost/model/* | GET  | NONE | *?type=Model&t_id=1* ***or*** <br/> ***or*** *t_id=1* |
| *localhost/*transition*/* | POST | action , type , t_id , <br /> ***optional :*** from_party , to_party , <br /> source , interim , target| NONE |
| *localhost/*transition*/reset/* | POST | type , t_id | NONE |
| *localhost/*action*/* | GET , POST | description , model , <br/> from_state ,to_state ,<br /> from_party , to_party , stage_required | *?action=MYACTION* ***or*** <br/> *?action=MYACTION&?model=Model*| 
| *localhost/*signatures*/* | GET , POST | name , sub_action_name | NONE |
| *localhost/*party-type*/* | GET , POST | description | NONE |
| *localhost/*states*/* | GET , POST | description | NONE |
| *localhost/*workflowitems*/* | GET | NONE | NONE |
| *localhost/workevents/* | GET | NONE | NONE |




## Support

For support, contact

1. support@venzo.com 
2. anandrajb@venzotechnologies.com