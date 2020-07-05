from requests_oauthlib import OAuth2Session
from django.utils import timezone
from . import views
import json
import dateutil.parser
from _datetime import datetime
from bs4 import BeautifulSoup

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
        '$select': 'subject,organizer,start,end,attendees,body',
        '$orderby': 'createdDateTime DESC',
        '$top': '10',
    }
    events = graph_client.get('{0}/me/calendar/events'.format(graph_url), params=query_params)
    # events = graph_client.get('{0}/me/events'.format(graph_url))
    # Return the JSON result
    return events.json()


def schedule_meeting(token):
    graph_client = OAuth2Session(token=token)
    subject = 'hellowing with teams final'
    start_time = "2020-06-28T23:50:02.096Z"
    end_time = "2020-06-29T21:30:02.096Z"
    meeting = graph_client.post('{0}/me/events'.format(graph_url), json={'subject': subject,
                                                                         'start': {
                                                                             'dateTime': start_time,
                                                                             "timezone": "UTC"},
                                                                         'end': {
                                                                             'dateTime': end_time,
                                                                             'timezone': 'UTC'
                                                                         },
                                                                         "attendees": [
                                                                             {
                                                                                 "emailAddress": {
                                                                                     "address": "sidharth.kaushik@atos.net",
                                                                                     "name": "Sidharth Kaushik"
                                                                                 },
                                                                                 "type": "required"
                                                                             }
                                                                         ],
                                                                         "onlineMeetingProvider": "teamsForBusiness",
                                                                         "isOnlineMeeting": True,
                                                                         })
    return meeting.json()
    print(meeting.json())
    # Return the JSON result


def migrateNow(token):
    graph_client = OAuth2Session(token=token)
    events = get_calendar_events(token)
    user = get_user(token)
    mail = user.get('mail')
    if events:
        for event in events['value']:
            organizer = event.get('organizer')
            organizer = organizer.get('emailAddress')
            organizer = organizer.get('address')
            if mail == organizer:
                start_key = event.get('start')
                start_key = start_key.get('dateTime')
                date_fixed = start_key.split('T')[0]
                date_fixed = str(datetime.strptime(date_fixed, '%Y-%m-%d'))
                date_fixed = date_fixed.split(" ")[0]
                todays_date = str(datetime.today())
                todays_date = todays_date.split(" ")[0]
                if date_fixed > todays_date:
                    event_info = json.dumps(event, indent=4, sort_keys=True, default=str)
                    json_info = json.loads(event_info)
                    attendees = json_info['attendees']
                    html = json_info['body']
                    soup = BeautifulSoup(html['content'], "html.parser")
                    [s.extract() for s in soup(['head', 'title'])]
                    visible_text = soup.getText()
                    if 'Skype' in visible_text:
                        visible_body_finalized = visible_text.replace('Skype', 'Microsoft Teams')
                        visible_body_finalized = str(visible_body_finalized + 'New Migrated Meeting')
                        subject = json_info['subject']
                        start_time = json_info['start']['dateTime']
                        start_time = start_time.replace(" ", "T")
                        start_time = str(start_time + 'Z')
                        end_time = json_info['end']['dateTime']
                        end_time = end_time.replace(" ", "T")
                        end_time = str(end_time + 'Z')
                        meeting = graph_client.post('{0}/me/events'.format(graph_url), json={
                            "subject": subject,
                            "body": {
                                "contentType": "HTML",
                                "content": visible_body_finalized
                            },
                            "start": {
                                "dateTime": start_time,
                                "timeZone": "UTC"
                            },
                            "end": {
                                "dateTime": end_time,
                                "timeZone": "UTC"
                            },
                            "attendees": attendees,
                            "allowNewTimeProposals": True,
                            "isOnlineMeeting": True,
                            "onlineMeetingProvider": "teamsForBusiness",
                        })
                        print(meeting.json())
                        print('\n\n\t' + 'Next loop' + '\n\n')
                        return meeting.json()
