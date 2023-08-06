# Background To The Site
My goal was to replicate YouTube in 2008. I wanted to allow users to upload videos as well as browse (including viewing) videos uploaded by others. I wanted to give them the ability to subscribe to channels, and view their subscriptions. Discovering new videos is done through the "most viewed" and "most discussed" pages, which present a ranked list videos by their number of views and comments, respectively.

# Distinctiveness and Complexity
I believe this project satifies the Distinctiveness and Complexity requirments, as it is a video based site, that required many additional steps that the previous projects did not. 

For example, by allowing for file uploads, I had to validate them (using PIL and moviepy respectively). This was harder than I thought - I spent a long time trying to debug why I couldn't access the video file. Turns out that I needed to write it to disk and then run the validator afterwards, and if it failed delete the instance.

Additionally I track "views" on every video, which allows me to create a "most viewed" page. There's also a comments (and respectivel "most discussed" page.)

# HTML file descriptions

## discussed.html
The most discussed videos (ranked by number of comments.)
## index.html
The home page. This loads the users "subscriptions" (the channels that the viewer subscribes to.)
## layout.html
The general HTML layout that the rest of the app extends.
## login.html
A page to login for the app.
## register.html
A page to register for the app.

## results.html
The search results page.

## upload.html
A form to allow users to upload videos with associated metadata.

## video-meta.html
A video metadata html template. This is useful so that I can use it on any page that lists videos rather than copy pasting the HTML.

## viewed.html
Shows the most viewed videos.
## watch.html
The watch page. Shows:
1. The video itslef.
2. A link to subscribe or unsubscribe to the channel.
3. The video title and description and channel name.
4. A form to add a commment, followed by a list of comments. Comments show username, timestamp and text.

## your-videos.html
The videos that the current user has uploaded.

# Python files
## views.py
Contains two forms, NewUploadForm, and CommentForm, which store the forms for uploading videos and making a new comment.

### index
The index function gets the list of a users subscriptions. Crutially I need to sort that list by the timestamp (I couldn't figure out how to do that wihtin the django query) so I use a lambda expression.

### videoAPI
This provides information about the video in json format. It was intended to be used for ratings but I couldn't figure out how to aggregate a related object.

### watch 
surfaces the watch page. Looks to see if a user is subscribed (and not themselves) since this affects the subscribe button.

### comment 
Leave a comment on a video and redirect them back to that video.

### unsubscribe / subscribe
Subscribe and unsubscribe to a video. Subscribe creates the Subscribe object in the database, Unsubscribe just deletes it.

### viewed
ranks all videos by most viewed

### discussed
ranks all videos by most discussed

### channel
filters videos by uplaoded on a users channel.

### rating 
submits a new rating object to the database

### upload
allows users to upload a video. Checks it passes the various validators. If not it surfaces an error message.

### login_view / logout view /register
signs users in, out and registers them.

## models.py
This project involes the following models: 
### User
Left at default
### Video
Stores the video itself, a thumbnail image, and title, description and timestamp. It also stores who uploaded the video. Note that this also contains two validation files. The first one is for the images, and uses python image library to ensure that images don't exceed the required dimensions. The second is for the videos, and is more complicated. It ensure that videos are not more than 60 seconds in length. However, since the video must be saved to disk before I can run moviepy, I was required to utilize @receiver(post_save, sender=Video) which runs the validate_video_length after the video object is saved to disk. If it fails the validation the video is deleted from the database.

### Comment
A comment text, user who posted it. 
### Subscribe
A user who subscribed, and who they subscribe to. 
### View
A video and the user who viewed it. I also store the timestamp.
### Rating
A video, a rating (between 1-5) and the user who did it. I also store the timestamp.

# JS files
## watch.js
My javascript is incomplete, but I create span elements with a star. This will be used to create the rating.

# How to run your application.
1. Install required software with requirements.txt
2. python3 manage.py makemigrations vidyo
3. python3 manage.py migrate
4. python3 manage.py runserver


# Future plans for the app
There were several things that I wanted to implement in this project but didn't have time. 
1. Additional verifications during video upload. For example: checking file size, video dimensions.
2. Additional verifications during photo upload. For example: checking image file size (currently I only check dimensions). It would also be cool to intergrate with a machine learning model to check for things like nudity.
3. Processing images. After the image is uploaded, I'd like to compress it to a smaller size. I'd also like to   
4. Javascript - right now the ability to rate the videos is only partially implemented (there's a route but it's not triggered).
Ideally I'd like to have a user tap on a star, and have that send a rating to the database. On the video load, the average rating should show up in the stars (rounded to the nearest star). My issue was that I couldn't figure out how to get model information in the javascript.
5. Search results: this should take you to a search results page, based on a fuzzy match of the title.\
6. The most viewed / most discussed pages should have the ability to limit based on timestamp (eg: showing top videos in the last 24 hours.)

# Any other additional information the staff should know about your project.
N/A
