from django.urls import path
from .api import (
    PartyTypeListCreateApi,
    SignListListCreateApi,
    TransitionApiView ,
    ActionListApi,
    DetailsListApiView,
    FlowModelGetApi,
    WorkFlowitemsListApi,
    WorkEventsListApi,
    statesListCreateApi,
    TransitionResetApiview,
    ActionRetrieveUpdateApi,
    FlowModelRetrieveUpdateApi,
    StatesRetrieveUpdateApi,
    PartyTypeRetrieveUpdateApi,
    SignListRetrieveUpdateApi
)


urlpatterns = [
    path('model/',DetailsListApiView.as_view()),
    path('action/',ActionListApi.as_view()),
    path('action/<int:pk>/',ActionRetrieveUpdateApi.as_view()),
    path('flowmodel/',FlowModelGetApi.as_view()),
    path('flowmodel/<int:pk>/',FlowModelRetrieveUpdateApi.as_view()),
    path('workflowitems/<int:pk>/',WorkFlowitemsListApi.as_view()),
    path('workevents/<int:pk>/',WorkEventsListApi.as_view()),
    path('transition/',TransitionApiView.as_view()),
    path('transition/reset/',TransitionResetApiview.as_view()),
    path('states/',statesListCreateApi.as_view()),
    path('states/<int:pk>/',StatesRetrieveUpdateApi.as_view()),
    path('party-type/',PartyTypeListCreateApi.as_view()),
    path('party-type/<int:pk>/',PartyTypeRetrieveUpdateApi.as_view()),
    path('signatures/',SignListListCreateApi.as_view()),
    path('signatures/<int:pk>/',SignListRetrieveUpdateApi.as_view()),
]
