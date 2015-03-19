from django.shortcuts import render
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session
import logging
import os
import sys
from urllib import parse
import webbrowser
#import http.server

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json

# Create your views here.
def index(request):
    return HttpResponse("welcome to the uaconnect module")

def selfview(request):
    logging.basicConfig(level=logging.DEBUG)

    # Store your client ID and secret in your OS's environment using these keys, or
    # redefine these values here.
    CLIENT_ID = os.environ.get('UA_KEY')
    CLIENT_SECRET = os.environ.get('UA_SECRET')
    #print 'client:' , CLIENT_ID
    #print 'secret:' , CLIENT_SECRET

    if CLIENT_ID is None or CLIENT_SECRET is None:
        print('Please ensure $MMF_CLIENT_ID and $MMF_CLIENT_SECRET environment ' \
              'variables are set.')
        sys.exit(1)

    # As a convenience, localhost.mapmyapi.com redirects to localhost.
    redirect_uri = 'http://localhost.mapmyapi.com:12345/callback'   
    authorize_url = 'https://www.mapmyfitness.com/v7.0/oauth2/authorize/?' \
                'client_id={0}&response_type=code&redirect_uri={1}'.format(CLIENT_ID, redirect_uri)


    # Set up a basic handler for the redirect issued by the MapMyFitness 
    # authorize page. For any GET request, it simply returns a 200.
    # When run interactively, the request's URL will be printed out.
    class AuthorizationHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.server.path = self.path

    
    parsed_redirect_uri = parse.urlparse(redirect_uri)
    server_address = parsed_redirect_uri.hostname, parsed_redirect_uri.port
    
    print('server_address:', server_address)
    
    # NOTE: Don't go to the web browser just yet...
    webbrowser.open(authorize_url)
    
    # Start our web server. handle_request() will block until a request comes in.
    httpd = HTTPServer(server_address, AuthorizationHandler)
    print ('Now waiting for the user to authorize the application...')
    httpd.handle_request()
    
    # At this point a request has been handled. Let's parse its URL.
    httpd.server_close()
    callback_url = parse.urlparse(httpd.path)
    authorize_code = parse.parse_qs(callback_url.query)['code'][0]
    
    print('Got an authorize code:', authorize_code)
    
    access_token_url = 'https://api.mapmyfitness.com/v7.0/oauth2/access_token/'
    access_token_data = {'grant_type': 'authorization_code',
                         'client_id': CLIENT_ID,
                         'client_secret': CLIENT_SECRET,
                         'code': authorize_code}
    
    response = requests.post(url=access_token_url,
                             data=access_token_data,
                             headers={'Api-Key': CLIENT_ID})
    
    print ('Request details:')
    print ('Content-Type:', response.request.headers['Content-Type'])
    print ('Request body:', response.request.body)
    
    # retrieve the access_token from the response
    try:
        access_token = response.json()
        print ('Got an access token:', access_token)
    except:
        print ('Did not get JSON. Here is the response and content:')
        print (response)
        print (response.content)
    
    # Use the access token to request a resource on behalf of the user
    activity_type_url = 'https://oauth2-api.mapmyapi.com/v7.0/activity_type/'
    response = requests.get(url=activity_type_url, verify=False,
                            headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})
    
    # Refresh a client's credentials to prevent expiration
    refresh_token_url = 'https://oauth2-api.mapmyapi.com/v7.0/oauth2/access_token/'
    refresh_token_data = {'grant_type': 'refresh_token',
                          'client_id': CLIENT_ID,
                          'client_secret': CLIENT_SECRET,
                          'refresh_token': access_token['refresh_token']}
    
    response = requests.post(url=refresh_token_url, data=refresh_token_data,
                             headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})
    
    print ('Request details:')
    print ('Content-Type:', response.request.headers['Content-Type'])
    print ('Request body:', response.request.body)
    
    try:
        access_token = response.json()
        print ('Got an access token:', access_token)
    except:
        print ('Did not get JSON. Here is the response and content:')
        print (response)
        print (response.content)
    
    # Attempt another request on the user's behalf using the token
    refresh_token = response.json()
    #response = requests.get(url=activity_type_url, verify=False,
    #                        headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})
    workouts_url = 'https://oauth2-api.mapmyapi.com/v7.0/workout/?user=27173534'
    user_url = 'https://oauth2-api.mapmyapi.com/v7.1/user/self/'
    #response = requests.get(url=workouts_url, verify=False,
    #                        headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})
    #workouts_url = 'https://oauth2-api.mapmyapi.com/v7.1/workout/273123402/'
    response = requests.get(url=user_url, verify=False,
                            headers={'api-key': CLIENT_ID, 'authorization': 'Bearer %s' % access_token['access_token']})
    
    data = response.json()
    print("Name:",data["display_name"])
    #print (json.dumps(data,sort_keys=True,indent=2))
    #print data[1]["name"]
    #print data[2]["name"]
    return HttpResponse("self view page")
