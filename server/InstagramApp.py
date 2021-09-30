# This module uses the instagram basic api to retrieve access code, access token,
# and all the posts from a test user account (ane more). Note that this module only works for
# test user account that has been registered with the app. Because instagram basic
# api does not addresses authentication but rather facebook api, there needs to be
# another module to take care of authentication.

# The test user for this module is a mock instagram account (a.tester.01) that will have
# some stock photos to represent a generic instagram social account.

# This module serves as source code for the GetPhotoInsg app registered with FaceBook.
# More information can be found on the https://developers.facebook.com/ page.

# -----------------------------------------------------------------------------------------
# V1.0:
#   -Created a very basic InstaApp class to use Instagram basic api.
#   -get_user_media() currently only runs with media_url as media field (for the purpose of
#    the app). Method needs to be expanded as needed to handle other fields argument.
#   -oauth redirect uri and url needs to be changed. GitHub Pages doesn't support server-side
#    language so as of now cannot handle http requests. The uri and url needs to be a secured
#    http (as requested by facebook policy).
#   -added proper error handling for http requests to instagram endpoints in get_access_token(),
#    get_user_media(), and query_user_node() methods.
import os
import requests
import json
import webbrowser
from datetime import datetime


class InstaApp:
    instagram_graph_url = "https://graph.instagram.com/"
    instagram_oauth_url = "https://api.instagram.com/oauth/"

    # Registered uris and url with the app for redirection. There should be dedicated and unique links
    # for each of the following categories.
    oauth_redirect_uri = "https://bts630test.herokuapp.com/InstagramAuth/"
    # oauth_redirect_uri = "https://akitak1290.github.io/probable-winner/"
    deauthorize_callback_url = "https://akitak1290.github.io/probable-winner/"
    deletion_request_url = "https://akitak1290.github.io/probable-winner/"

    # Registered app with facebook
    #old info
    #get_photo_insg_app_id = "1350390948638049"
    #get_photo_insg_app_secret = "8de99ace038097799deeb4f377b7c8d8"
    #new info
    get_photo_insg_app_id = "469220600777355"
    get_photo_insg_app_secret = "7664aabe45aab2270fa528a83084acb4"

    # Arrays to store response media from instagram endpoints
    image_urls = {}

    def __init__(self):
        super().__init__()

    # This method makes a get request to the oauth authorize end point to get
    # an access code (that will be used to get an access token)
    def get_access_code(self):
        url = self.instagram_oauth_url+"authorize?"
        client_para = "client_id="+self.get_photo_insg_app_id
        redirect_pare = "redirect_uri="+self.oauth_redirect_uri
        scope = ["user_profile", "user_media"]
        scope_para = "scope="+scope[0]+","+scope[1]
        res_type = ["code", "token"]
        res_type_para = "response_type="+res_type[0]
        auth_url = url+client_para+"&"+redirect_pare+"&"+scope_para+"&"+res_type_para
        # Open authentication dialog in user web browser as a new tab
        # webbrowser.open_new_tab(auth_url)
        return auth_url

    # This method makes a post request with a 1 time use access token as parameter to
    # get a token for the test user account. This method will propel the exception
    # (if any) as ValueError to the caller.
    # This method returns a string
    def get_access_token(self, access_code):
        url = self.instagram_oauth_url+"access_token"
        return_str = ""
        payload = {
            'client_id': self.get_photo_insg_app_id,
            'client_secret': self.get_photo_insg_app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': self.oauth_redirect_uri,
            'code': access_code
        }
        try:
            r = requests.post(url, data=payload)
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
        else:
            # Parse the response as json
            r_data = json.loads(r.text)
            r_key_1 = (list(r_data.keys()))[0]
            # Raise an exception if the call was unsuccessful
            if r_key_1 == "error_type":
                r_error_information = list(r_data.values())
                raise ValueError(r_error_information[0]+",code:"+str(r_error_information[1])+":"+r_error_information[2])
            elif r_key_1 == "access_token":
                return_str = r_data["access_token"]
        return return_str

    def get_long_lived_token(self, token):
        graph_url = "https://graph.instagram.com/access_token?grant_type=ig_exchange_token"
        app_url = "&client_secret="+self.get_photo_insg_app_secret
        token_url = "&access_token="+token
        get_url = graph_url+app_url+token_url
        r_long_lived_token = ""
        try:
            r = requests.get(get_url)
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
        else:
            r_data = json.loads(r.text)
            r_key_1 = (list(r_data.keys()))[0]
            # Raise an exception if the call was unsuccessful
            if r_key_1 == "error":
                r_error = (list(r_data.values()))[0]["message"]
                raise ValueError(r_error)
            elif r_key_1 == "access_token":
                r_long_lived_token = r_data["access_token"]
        return r_long_lived_token

    def refresh_long_lived_token(self, long_lived_token):
        graph_url = "https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token"
        long_lived_token_url = "&access_token="+long_lived_token
        get_url = graph_url+long_lived_token_url
        try:
            r = requests.get(get_url)
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
        else:
            r_data = json.loads(r.text)
            r_key_1 = (list(r_data.keys()))[0]
            # Raise an exception if the call was unsuccessful
            if r_key_1 == "error":
                r_error = (list(r_data.values()))[0]["message"]
                raise ValueError(r_error)
            elif r_key_1 == "access_token":
                r_long_lived_token = r_data["access_token"]
        return r_long_lived_token

    # This method will examine the token, determine the id of the instagram user
    # who queried what token, and query that user. This function will propel the
    # exception (if any) as ValueError to the caller.
    # This method returns a dictionary containing the id of the user and their
    # username
    def query_user_node(self, access_token):
        rtn_dict = {}
        fields = ["id", "username"]
        fields_para = "fields="+fields[0]+","+fields[1]
        url = self.instagram_graph_url+"me?"+fields_para+"&"+access_token
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
        else:
            # Parse the response as json
            r_data = json.loads(r.text)
            r_key_1 = (list(r_data.keys()))[0]
            # Raise an exception if the call was unsuccessful
            if r_key_1 == "error":
                r_error = (list(r_data.values()))[0]["message"]
                raise ValueError(r_error)
            elif r_key_1 == "id":
                r_values = list(r_data.values())
                rtn_dict["id"] = r_values[0]
                rtn_dict["username"] = r_values[1]
        return rtn_dict

    # This function makes a get request to the me/media end point to get media from the
    # user account. The list of media fields include the following:
    #       ---------------------------------------------------------------------------------
    #       |FIELD NAME     |DESCRIPTION                                                    |
    #       ---------------------------------------------------------------------------------
    #       |caption        |The Media's caption text. Not returnable for Media in albums.  |
    #       |id             |The Media's ID.                                                |
    #       |media_type     |The Media's type. Can be IMAGE, VIDEO, or CAROUSEL_ALBUM.      |
    #       |media_url      |The Media's URL.                                               |
    #       |permalink      |The Media's permanent URL.                                     |
    #       |thumbnail_url  |The Media's thumbnail image URL. Only available on VIDEO Media.|
    #       |timestamp      |The Media's publish date in ISO 8601 format.                   |
    #       |username       |The Media owner's username.                                    |
    #       ---------------------------------------------------------------------------------
    # If media_field is empty, the call to the endpoint (if valid) will only returns the media
    # ids.
    # This function will propel the exception (if any) as ValueError to the caller.
    # This method returns a dict. -> Need to address this later, return might varies depends on the media field
    def get_user_media(self, access_token, media_field):
        media_arr = {}
        media_field_para = "fields="+media_field
        access_token_para = "access_token="+access_token
        url = self.instagram_graph_url + "me/media?"+media_field_para+"&"+access_token_para
        post_url = "https://bts630test.herokuapp.com/upload_module" #POST route for uploading
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            raise ValueError(e)
        else:
            r_data = json.loads(r.text)
            r_key_1 = (list(r_data.keys()))[0]
            # Raise an exception if the call was unsuccessful
            if r_key_1 == "error":
                r_error = (list(r_data.values()))[0]["message"]
                raise ValueError(r_error)
            elif r_key_1 == "data":
                media_urls_list = r_data["data"]
                if media_field == "media_url":
                    if self.extract_image_urls(media_urls_list):
                        media_arr = self.image_urls
                        
        return media_arr

    # This method extracts the urls from an array of dictionaries.
    # The urls are the first keys in each dictionaries. The second keys
    # are the ids of each post. The urls are store in a class dict.
    # This method returns true if the urls exist, false otherwise
    def extract_image_urls(self, media_list):
        media_found = False
        i = 0
        for m in media_list:
            self.image_urls[i] = m["media_url"]
            i = i + 1
        if len(self.image_urls) != 0:
            media_found = True
        return media_found

def main():
    try:
        # app = InstaApp()
        # app.get_access_code()
        code = "AQBGb5imrqhtJMVTiSZJ9aU8N5bBHHvbXMvU6XTr0t5Jrgkuept0luAhIY_0wQZ6tdxHp-_w50dPb_xLEsryCn_cH-Ruu5z8Q9" \
               "VYYnieNpk50AtG4HBhe_XZytmy3yep769v3iZi32A_qsen4nwTrL4HxjVl_nmV__0dpa-_cwwEdI90XBwnDB7MbNJ5u5vOvdl-7" \
               "pNnw9g_Si3ojvKApzWDADkXWSWmZUvHcoj7ODTj0g"
        #try:
        #    print(app.get_access_token(code))
        #    # print(app.get_user_media(token, "media_url"))
        #    # app.query_user_node(token)
        #except ValueError as err:
        #    print(err)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()