# Changelog:

## BTS630 Conclusion
Deviations from BTS630:

The application only interfaces with the Facebook and Instagram applications at this time.
The user is able to search and browse photos that they appear in, but the application is not equipped to automatically tag users in photos without human interaction.

List of known bugs:

When the server is being accessed via Heroku, and the user attempts to log in to Instagram or Facebook, sometimes they are redirected to the server homepage without being logged in. This can be circumvented by clicking the "Log In" link again.

When an improperly formed array is sent to the /names POST route, it will cause a formatting error in the database. This is due to pymongo reading the improperly formed array as a string.

The tagging system on the front end is very simplistic and may not work as expected with the current implementation. 

Right now there is a input box when uploading an image where the user can explicitly state the name or username of the person in a picture. Only works for photos with one person.

## BTS630 Sprint 4 - Friday April 9

### Ken
#### [Issue #36](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/36)
- Modified the majority of the pipeline. Changed the embedding model to a Torch deep learning model, changed to detection model to a pre-trained Caffe deep learning model.
- Refactored the module.
- Added the extract_embeddings(), train_recognizer(), and the recognize_face() functions.
- Separated training model logic and recognizing image logic so the model can be reused until needing to be retrained.
- Added a confidence filter to improve the recognizer model.
- Added an additional confidence filter when recognizing images. The minimum threshold is 60%, faces falling below will be labeled as "unknown".
- Added the expected directory structure to use the pipeline for furure reference.
- Removed the command argument parser for upcoming integration.

### Ben
#### [Issue #39](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/39) and [Issue #35](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/35)
- Updated the /test_module route, it is now /retrieve_by_user and only takes GET
- Updated the /retrieve_by_user to handle batch querying (i.e. I want pictures only containing "Yumit" and "Kien")
- Exposed the /assign_to_user route to allow the front-end to assign already databased images to a user. Only takes POST
- Exposed the /names route (GET and POST) to retrieve existing faceArr and faceList data by hash, as well as update faceArr and faceList data by hash
- Solved an issue where images with zero faces would not be databased correctly
- Lots of small optimizations and removal of old code, as the facial_detection and load_img_face functions have been modified
- Added functions assign_user_img(userID, hash), update_face_list_data(hash, face_arr, face_list), assign_to_user(), and manage_names()

### Yumit
#### [Issue #34](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/34#issue-836291936)
- Deployed front end to Heroku
- Changes to the code to differentiate between testing phase and deployed phase
- Added more error conditions wheen uploading/retrieving images

Link to application on Heroku: [https://bts630app.herokuapp.com/](https://bts630app.herokuapp.com/)
#### [Issue #38](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/38#issue-842118559)
- Added new library to handle image resizing before being uploaded to a AWS S3 bucket
- New images are cropped to 400x400, not maintaining the original aspect ratio from before

#### [Issue #37](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/37#issue-842099800)
- Added the experimental functionality of tagged photos to the users tagged page

## BTS630 Sprint 3 - Friday March 19

### Kien

#### [Issue #33](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/33)

- Moved the train_face script and recognize_faces_image script to the test_chamber script.
- Added default argument values for the script.

- Added the testing module for the facial recognition pipeline
- Added a directory to store all the testing dataset to test the model against multiple photos.
- Added a function to add and rename new testing photos to the unified testing pool.
- Added logic to extract the photo file names for comparison when predicting faces.
- Added logic to pipe the output of the prediction process to the test_output.csv file.

#### [Issue #28](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/28)

Testing results:
-  With 15 photos per person for the training dataset, the average accuracy of the model reaches 60%.
-  Facebook users from Toronto seems to have around 10-15 public photos with their faces. However, a lot of the photos also includes accessory (sunglasses, hats) or faces at extreme angels.

### Ben
### [Issue 31](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/31) and [Issue 30](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/30)
- Modified the Facebook module to interface with the upload_module route, and POST images to the database as they are retreieved
- Modified the return from the Instagram app to interface with the upload_modle route
- Added FaceList and FaceArr to the img_data table in the db
- FaceList and FaceArr are a 1:1 "facename":"coordinate" structure that allows us to store face locations on an image, as well as that face's name
- Modified the process_image function to assemble the FaceArr as we process the image
- Modified the branching functions from process_image to handle faceArr and faceList 

### Yumit
#### [Issue #32](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/32#issue-835420644)
- Added routes and pages to handle resetting of passwords
- Created a gmail account to handle emailing users the resetting link
- Added relevant success and error messages to inform the user of potential issues
#### [Issue #27](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/27#issue-816724719)
- Added boxes around detected faces based on the coordinates returned by the face detector
- Added links to each box
- Added a new view to handle looking up a user
- Added a page to show searched user information and their uploaded images
#### [Issue #26](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/26#issue-816718160)
- Added the server links for Instagram and Facebook login to the UI
- Added relevant icons for Facebook and Instagram to the file system

*experimented with return values in the server to get album and photo data into the UI but was not succesful in doing so. At this stage the output of these
links is the static HTML pages that are returned from the server.*

#### Other changes
- Added a maximum image size, images are now resized before being sent to server for upload.

*This was due to the coordinate system of the face detector not matching up with the size of the image that is displayed in the UI having the effect of tagging boxes
not lining up with the faces. Limiting the size of the image ensures that the coordinates are accurate throughout processing and display.*

## BTS630 Sprint 2 - Friday February 19

### Kien [Issue #25](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/25)
- Created 2 sample projects using OpenCV and Dlib
#### OpenCV
- Added OpenCV cascade classifier.
- Added code snippets to read the training dataset.
- Trained the classifier on a training dataset of 96 photos of 5 different people (output file is face_trained.yml).
- Added OpenCV LBPHFaceRecognizer model to predict faces of the same 5 people on a different dataset.
#### Dlib
- Added the face_recognition (an extention of Dlib for face detection/face recognition) library.
- Added code snippets to read the training dataset.
- Encoded the faces from the training dataset of 96 photos of 5 different people (output file is encoding.pickle)
- Loaded the encodings to compare and predict faces of the same 5 people on a different dataset.
- Added a 'voting' system to choose out the label with the highest match probability for each face.
#### Test module
- Added a test module to compare the results of the two projects.
- Added the result to the current issue.

### Ben
- Collected requirements for server deployment
- Refactored the main server.py 'server' references to 'app' references (necessary for deployment)
- Slight modification of the instance of OpenCV used, since heroku disallows graphical OpenCV but allows OpenCV-headless
- Deployed to heroku
- Added Kien's routes to the main server.py
- Modified the home page to render Kien's home.html & allow displaying of collected images
- Added Kien's InstagramApp.py
- Added Kien's FacebookApp.py
- Integrated the Facebook and Instagram modules as per Kien's localServer.py
- Slight modification to the serverside app and secret tokens

### Yumit [Issue #23](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/23#issue-801503312)
- Created a class for face normalization
- Faces are now scaled and rotated, relative to eye position, to keep everything as uniform as possible, and saved individually (in this sprint).
- Made the necessary changes to the test server I've been using to return the normalized faces

*The test server and normaliztion class available in the `server_BTS630_sprint2` branch under `testing_server`*
- Adjusted the UI to display the normalized faces for demonstration purposes
#### Small UI related change
- Added a route in the dropdown menu for future Facebook and Instagram integration to the UI

## BTS630 Sprint 1 - Friday January 29

### Kien
 #### Modules changes
 - Added method to disconnect the user accounts from the app.
 - Added methods in both module to exchange the short-lived token for a long-lived token.
 - Added method to refresh the long-lived token for the instagram module.
 - Added a new api call to facebook endpoint to get cover photos for albums.
 #### Test server changes
 - Migrated the http server used for testing the facebook module to the flask instagram test server. All testing will be done on the latter.
 - The server now has separated routes for getting access code and display user information to prevent end user from seeing the access code in the url.
    + Added /InstagramAuth, /InstagramAuth/user, /FacebookAuth, /FacebookAuth/user, /FacebookAuth/user/album/<string:albumid>
 - Added /logout route to delete access tokens.
 - Added new display tags in index.html template to reflect changes in the server.
 

### Ben
 - Created new route /upload_module for images acquired from the facebook/instagram modules
 - Added functionality to upload images to the database without performing processing
 - Modified server route /retrieve to check if an image has been processed when queried
 - Added functionality to perform on-demand processing of images when they are retrieved
 - Added functionality to update existing img_data entries with processed data (faces)
 - Created new route /login_facebook (currently has only partial function)
 - Created new route /login_instagram (currently has only partial function)

### Yumit [Issue #19](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/19#issue-786159816)
 #### Server/face detection changes
 - Found a more accurate [face detector](https://github.com/SenecaCollegeBTSProjects/Group_07/issues/19#issuecomment-769495655)
 - Added the new face detection into existing server code
 - Added additional return elements to the upload route of the server to get image data from the detector for display in the UI
 #### Interface related changes 
 - Renamed files to better reflect their purpose
 - Modified routes to seperate application sections (user related sections and main ui sections)
 - Added a static Javascript file for DOM manipulation instead of having it in a `<script>` tag in the `base.html` file
 - Added the description box to show image data retrieved from the new face detector, for later use this could be for an image description added by the user
 - Added image preview when uploading new images
 - Modified how images are rendered; they now keep their original aspect ratio whereas before they did not and it caused some information loss
 - Images are now ordered from newest to oldest
 - Modified profile picture uploads so that there is no distortion due to resizing
 - Added more descriptive pages for when the user doesn't have pictures uploaded or when a link is not used (ex. Settings link)
 - Improved documentation for clarity and easier future updates
 
 *Created new branch called `interface` where future interface related changes will be pushed to.*
 
 

## Sprint 4 - Wednesday December 9

### Kien:
  - Registered a new application with FaceBook Developer. 
  - Added a basic Flask server with a route to handle redirection from instagram login dialog.
  - Uploaded the server to heroku.
  - Added a test user account and url (to the heroku app) for redirecting.
  - Created a very basic InstaApp class to use Instagram basic api.
  - Created get_access_code() to invoke the login diaglog.
  - Created get_access_token().
  - Created query_user_node() to examinne the token and determine the id of the instagram user who queried that token.
  - Created get_user_media(media_field) for getting all public images from user account.
  - Added proper exception handling for the http requests for instagram api endpoints.
  
### Yumit
  - Create icons for links
  - Remove secondary nav bar from the page
  - Reposition necessary links to the main nav bar
  - Add a menu for user control
  - Rework how face detection works to detect a tilted face
  
  ### Ben
  - Created new database tables for preprocessing, postprocessing, and image data
  - Modified server routes to work with new database infrastructure
  - Modified server response to work with Yumit's client UI
  - Interfaced the server with Yumit's client UI for proof of concept
  - Merged Kien's sprint 3 modules to the main server

  
## Sprint 3 - Wednesday November 4th

### Yumit
  - Upload to the server by Ben from sprint 2
  - Retrieve images processed by the server
  - Display the processed images
  - Improve some UI elements to reduce clutter
  
### Kien:
  - Rewritten the script from sprint 2 into moudle FacebookApp (All functions are 
    now part of the FacebookApp class). The module is ready to be integrated into
    the server.
  - Added proper code documentation.
  - Added a temporary uri for OAuth redirect uri (to be changed later when the website goes online).
  - Added method to invoke facebook login dialog from browser to get access code.
  - Added method to process the access code through an OAuth end point to get access token.
  
### Ben:
  - Rewritten parts of the /upload route to handle new logic:
    - Filename is parsed first
    - Files are now saved exclusively to the processing folder
    - File is hashed before processing begins
    - Function process_image() handles logic for duplicate images
  - Rewritten parts of the /retrieve route to handle database querying:
    - URL image parameter is parsed for a valid filename, then database is queried
    - Result from database is returned as base64 encoded <img> element, no processing is performed
  - Created and configured mongodb cluster
  - Created 'images' collection
  - Created 'users' collection
  - Added function save_img() for inserting a single image (and it's relevant fields) to the images collection in the database
  - Added function load_img_hash() for retrieving a single image from the database via unique hash
  - Added function load_img_name() for retrieving a single image from the database via unique name
  - Added function hash_img() for performing average hashing (grayscale & resize image, compute & return hash)
  - Added function open_pil_image() for opening an image with PIL via a file name
  - Added function remove_local_images() for removing images within the processing folder based on a filename
  - Added function process_image() for handling the logic of database querying and duplicate images
  - Rewritten parts of the facial_detection() function to read/write from the new location, as well as call the save_img() function

## Sprint 2 - Wednesday October 21st

### Ben:
  - Created python server
  - Modified facial detection processing to name files according to date/time
  - Modified facial detection processing to crop images at 128x128 to save processing time
  - Created the /upload route
  - Created the /retrieve route
  - Parse returned images as base64 when returning to the user
  
### Yumit:

  - Home page that shows rows of public images
  - A page where user owned images will be placed
  - A page where tagged images will be placed
  - Profile page where the user can change their profile picture and other settings
  - A Sign up/ Sign in page
  
### Kien:
  - Created initial script for facebook sdk
  - Created placeholder for access token
  - Added get_albums method to call the fb api for a list of user's public album
  - Added get_photos method to call the fb api for the list of user's public photo from an album
  

## Sprint 1 - Wednesday October 7th

### Yumit:

  - Web application using Django and OpenCV libraries
  to demonstrate face detection.
  
  Deliverables:
  - A webpage that shows the raw image file and the modified image files
  showing boxes around the faces that were detected. 
  - Images include
  individuals and groups of people.
