## Local photo finding tool (Done by Kien)

### Actor (User)
Online user with a valid account in the system.

### Pre-conditions
User is logged into the system. 

### Main Flow
1. The user clicks on the **Upload album** button on the main website.
2. The system prompts the user to select a folder from their computer.
3. The user selects the folder where the album resided.
4. The system prompts the user to upload a picture from their computer with the face they want to search for.
5. The user selects a picture with a person's face in it.
6. The system returns a list of photos from the uploaded album with the person's face in it.

### Alternate Flows
- If the folder the user has selected has no suitable files to be used:
	1. After step 3, the system will let the user know that there was no suitable files to be used in the folder. Return to step 2.
- If the picture the user has selected is not suitable to be used:
	1. After step 4, the system will let the user know that the file is not suitable. Return to step 3.
- If the result of the comparisions is 0:
	1. After step 6, the system will let the user know that no picture has been found and the user can go back to step 5.

### Postconditions
After the user has uploaded their album, it will be stored in the database under the user's account. The album can then be accessed and managed through the **My albums** tab. The photo with a person's face is deleted from the database after a session is over.

---

## Online photo finding tool (Done by Kien)

### Actor (User)
Online user with a valid account in the system.

### Pre-conditions
User is logged into the system. User account must be linked to at least 1 online social account (like Facebook).

### Main Flow
1. The user clicks on the **Search online** button on the main website.
2. The user selects which social media website they wish to get a photo album from through a list of associated accounts.
3. The system promts the user to select an album from the list of albums found with that account.
4. The user selects 1 album.
5. The system prompts the user to upload a picture from their computer with the face they want to search for.
6. The user selects a picture with a person's face in it.
7. The system returns a list of photos from the album with the person's face in it.

### Alternate Flows
- If no albums are found with the associated account:
	1. After step 2, the system will let the user know that no album is found and the user can go back to step 2.
- If the picture the user has selected is not suitable to be used:
	1. After step 5, the system will let the user know that the file is not suitable. Return to step 3.
- If the result of the comparisions is 0:
	1. After step 6, the system will let the user know that no picture has been found and the user can go back to step 6.

### Postconditions
The photo with a person's face is deleted from the database after a session is over.

---

## Authentication (Done by Yumit)

### Actor (User)

### Pre-conditions

No pre-conditions for this use case.

### Main Flow

1. User enters username/email and password.
2. The system checks the database for the credentials.
3. The system allows the user to enter if the credentials are correct.

### Alternate Flows

- If the credentials entered are incorrect:
	1. An error message is shown to the user alerting them that the username/email or password are incorrect and to try again.
- If no account is found with the username/email that is entered:
	1. An error message is shown to the user telling them that there is no such account, redirecting the user to create an account if they choose to.

### Postconditions

After the user has logged in to their account without any errors they can then use the application however they choose such as
uploading images.

---

## Automatic Tagging (Done by Yumit)

### Actor (User)

A user with a valid account.

### Pre-conditions

The user must allow the usage of facial recognition and must have already submitted pictures of themselves for the system to 
analyze their facial features.

### Main Flow

1. An image is uploaded by a user.
2. The system analyzes the image for any faces.
3. Once faces are recognized, the system searches the database for any known people in the image.
4. If known people are found, the system appends a link to the profile with the name of the person found to the image.
5. All found people get a notification about the image.
6. The image appears in the tab for external user images for all found users.

### Alternate Flows

- If no faces are detected:
	1. The system performs no operations on the image.
	
- If there are faces detected and there are unknown people in the image:
	1. The system shows a message to the user that has uploaded the image that the image has a person that was not found in the database. The user has the option of manually tagging the unknown people in the image. 


### Postconditions

The user can view images of themselves uploaded by someone else automatically.