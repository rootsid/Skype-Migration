from requests_oauthlib import OAuth2Session
from django.utils import timezone

graph_url = 'https://graph.microsoft.com/v1.0'


def get_user(token):
    graph_client = OAuth2Session(token=token)
    # Send GET to /me
    user = graph_client.get('{0}/me'.format(graph_url))
    # Return the JSON result
    return user.json()


def get_calendar_events(token):
    graph_client = OAuth2Session(token=token)
    # Configure query parameters to
    # modify the results
    # query_params = {
    #     '$select': 'subject,organizer,start,end',
    #     '$orderby': 'createdDateTime DESC'
    # }
    # Send GET to /me/events
    # events = graph_client.get('{0}/me/calendar'.format(graph_url), params=query_params)
    # '$select': 'subject,body,attendees,organizer,start,end,location'
    query_params = {
        '$select': 'subject,organizer,start,end',
        '$orderby': 'createdDateTime DESC',
        '$top': '5000',
    }
    events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
    # events = graph_client.get('{0}/me/events'.format(graph_url))
    # Return the JSON result
    return events.json()

def schedule_meeting(token):
    graph_client = OAuth2Session(token=token)
    # Send POST to /me/events
    meeting = graph_client.post('{0}/me/events'.format(graph_url), json={'subject': 'testing123',
                                                                         'start': {
                                                                             'dateTime': "2020-06-13T21:30:02.096Z",
                                                                             "timezone": "UTC"},
                                                                         'end': {
                                                                             'dateTime': "2020-06-20T21:30:02.096Z",
                                                                             'timezone': 'UTC'
                                                                         }
                                                                         })
    return meeting.json()
    print(meeting.json())
    # Return the JSON result
