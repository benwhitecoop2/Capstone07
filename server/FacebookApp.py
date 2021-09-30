import os
import requests
import json
import webbrowser
from datetime import datetime

"""
TODO: Store access token and user ID in session variables
      Store the facebook api version separately from the urls
Note: the server would need the urlparse lib to integrate this module
"""


class FacebookApp:
    # fb_api_url and fb_url are 2 separate urls as requested by the facebook api and cannot swap
    # places to each other. They are both use at different locations in this module.
    # Refers to the https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
    # for more details.
    fb_api_url = "https://graph.facebook.com/v8.0/"
    fb_url = "https://www.facebook.com/v8.0/"
    my_fb_api_url = fb_api_url + "me/"
    # TODO: find a better way to store app_id and app_secret (server-side only)
    #old info
    #app_id = 781954879264516
    #app_secret = "d6c542122a028a444a5d37feb17039b3"
    #new info
    app_id = 119932499999110
    app_secret = "439dcdf5c971f094a3d5cc3fbd2aa4c0"
    # default redirect url, to be changed and processed according to the server
    redirect_url = "https://www.facebook.com/connect/login_success.html"
    # placeholder for the user access token

    def __init__(self):
        super().__init__()

    # This method invokes the login dialog from facebook and will append the access token code to
    # the redirect_url. The server is required to catch and process the get request to extract
    # the access token.
    # The url needs to be added to the Valid OAuth Redirect URIs section in the facebook app
    # located at https://developers.facebook.com/apps/781954879264516/fb-login/settings/ (admin).
    # This method does not return anything
    def login(self, redirect_url):
        app_id_str = "client_id=" + str(self.app_id)
        redirect_uri_str = "redirect_uri=" + redirect_url
        state_str = "state=" + "{st=state123abc,ds=123456789}"  # -> TODO: store states in separate variables
        scope_str = "scope=" + "public_profile" + "&" + "user_photos"
        response_type_str = "response_type=code"  # -> the code for token processing to be returned in url parameters
        login_dialog_url = self.fb_url + "dialog/oauth?" + app_id_str + "&" + redirect_uri_str + "&"
        login_dialog_url = login_dialog_url + state_str + "&" + scope_str + "&" + response_type_str
        return login_dialog_url

    # This method needs to be called in the server route responsible for handing the redirect_url
    # from the login method. The handler will extract the token code from the incoming get request
    # and parse it to this method which in turn will send a get request to a  OAuth endpoint
    # to extract the token_code from its parameters.
    # This method returns an access token
    def get_token(self, redirect_url, token_code):
        app_id_str = "client_id=" + str(self.app_id)
        redirect_uri_str = "redirect_uri=" + redirect_url
        client_secret_str = "&client_secret=" + self.app_secret
        token_code_str = "code=" + token_code
        oauth_endpoint_url = self.fb_api_url + "oauth/access_token?"
        oauth_endpoint_url = oauth_endpoint_url + app_id_str + "&" + redirect_uri_str + "&" + client_secret_str + "&" + token_code_str
        try:
            response = requests.get(oauth_endpoint_url)
        except requests.exceptions.Timeout as e:
            print(e)
        else:
            r_data = json.loads(response.text)
            print(r_data)
            return r_data["access_token"]

    def get_long_lived_token(self, token):
        graph_url = "https://graph.facebook.com/v9.0/oauth/access_token?grant_type=fb_exchange_token"
        app_id_url = "&client_id="+str(self.app_id)
        app_secret_url = "&client_secret="+self.app_secret
        token_url = "&fb_exchange_token="+token
        get_url = graph_url+app_id_url+app_secret_url+token_url
        r_long_lived_token = ""
        try:
            print(get_url)
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

    # This method retrieves all public photos from the album passed to its parameter.
    # If mode = 1(url), this method will return a dict of urls to the photos
    # If mode = 2(download photos), this method will return an empty dict
    def get_images_from_album(self, album_id, token, mode):
        dict_img = {}
        result = {}
        if token != "placeholder":
            post_url = "https://bts630test.herokuapp.com/upload_module" #POST route for uploading
            album_url = self.fb_api_url + album_id + "?fields=photos%7Bimages%7D&" + "access_token=" + token
            try:
                response = requests.get(album_url)
            except requests.exceptions.Timeout as e:
                print(e)
            else:
                r_data = json.loads(response.text)
                r_images = r_data['photos']['data']
                if mode == 1:
                    i = 0
                    for images in r_images:
                        image_url = images['images'][0]['source']
                        dict_img[i] = image_url
                        
                        #POST image to upload_module to enter into database
                        dt_string = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        
                        img_data = requests.get(image_url).content
                        with open(dt_string + ".jpg", 'wb') as handler:
                            handler.write(img_data)
                            
                        files = {"file": ( dt_string + ".jpg", open(dt_string + ".jpg", 'rb'), 'multipart/form-data', {'Expires':'0'}) }
                        
                        with requests.Session() as s:
                            r = s.post(post_url, files=files)
                            print(r.status_code)
                        
                        #remove the temp file after we're done
                        os.remove(dt_string + ".jpg")
                        
                        i = i + 1
                    result = dict_img
                elif mode == 2:
                    i = 0
                    for images in r_images:
                        image_url = images['images'][0]['source']
                        dict_img[image_url] = i
                        i = i + 1
                        img_data = requests.get(image_url).content
                        f = open(album_id + str(dict_img[image_url]) + ".jpg", 'wb')
                        f.write(img_data)
                        print(image_url)
        else:
            print("Access token is: " + token)
        return result

    # This method retrieves all public albums from the user's facebook account.
    # This method returns a dictionary in form of "album_name": album_id
    def get_all_albums(self, token):
        # This dictionary contains the list of albums belonging to the user
        # The key is the name of the album and the value is its id
        albums_dict = {}
        if token != "":
            albums_url = self.my_fb_api_url + "albums?" + "access_token=" + token
            try:
                response = requests.get(albums_url)
            except requests.exceptions.Timeout as e:
                print(e)
            else:
                r_data = json.loads(response.text)
                r_albums = r_data['data']
                for album in r_albums:
                    url = "https://graph.facebook.com/v9.0/"+album['id']+"?fields=cover_photo%2Cpicture%7Burl%7D&access_token="+token
                    try:
                        response = requests.get(url)
                    except requests.exceptions.Timeout as e:
                        print(e)
                    else:
                        r_data = json.loads(response.text)
                        cover_url = r_data['picture']['data']['url']
                        albums_dict[album['name']] = {'cover_url': cover_url, 'id': album['id']}
        else:
            print("Access token is: " + token)
        return albums_dict

    # Test method (server-side) for the class
    def get_album(self, token):
        albums_dict = self.get_all_albums(token)
        for album in albums_dict:
            print(album)

        alb = "July 22"
        return self.get_images_from_album(albums_dict[alb], token, 1)