# FM_Flair_Bot


***About***  
This reddit bot was created with [/u/John_Yuki](reddit.com/user/john_yuki) to implement flairs and time specific submission removals for the ~36k subscriber strong community at [/r/FootballManagerGames](https://www.reddit.com/r/footballmanagergames). Submissions to a subreddit are usually flaired with a text tag that helps categorize submissions. Flaired submissions give an idea about the post without users having to open it while also helping users sort submissions by a specified category. However, many users simply forget to flair a post or are unable to flair a post while viewing Reddit on a mobile device. This bot helps moderators of a subreddit implement flairs by providing both a reminder for users to flair their submissions as well as an easy system for users to set a flair on mobile.  

This bot is written in Python and makes use of [PRAW](https://praw.readthedocs.io/en/latest/) as well as [SQLITE](https://www.sqlite.org/).

***What does this bot do?***
* The bot scans submissions made to a specified subreddit. 
* When a submission is made without a flair, it comments on the submission, reminding the poster to flair the post within a specified amount of time as well as giving the user instructions on how to easily flair a post by replying to the comment with a comman. 
* The submission ID is then added to a database, which is constantly checked to see if the submisssion gets flaired within the specified time limit. 
* If the user manually sets the flair or gives out a command to set a flair, then the flair for the submission is set and the comments instructing the user to flair the post and the comment which instructs the bot to flair the post are removed and the post is approved to the subreddit. 
* *However,* if the user fails to change the flair him/herself or fails to instruct the bot to set a flair (implemented by the user replying to the bots comment with the words "SETFLAIR" followed by the flair text) then the post is removed and the bot posts a comment informing the user about the removal. 
* The bot also checks if a post has been flaired incorrectly and automatically removes such posts. (for example, the post is flaired as HELP when there is a specific thread that exists already for asking help)

***How can I use this for my own specific subreddit?***
* Install Python if you haven't already from [here](https://www.python.org/downloads/)
* Clone this repository by typing `git clone https://www.github.com/swrj/FM_Flair_Bot`
* Open FM_Flair_Bot.py in a text editor and change all the variables in upper case to the specifications of your bot.
* Open Config.py and add the username and password of your bot. Go to https://www.reddit.com/prefs/apps while logged in to your bot account and click on the "Create an app" button. Name your bot, choose the script option and change the redirect uri to http://localhost:8080 and create the app. On the next page you will see the values for client_id and client_secret. Add these to the config file. Add a description for your user agent. This should be descriptive and should adhere to the official Reddit API rules found [**here**](https://github.com/reddit/reddit/wiki/API).
* Run your script! 
If you are on Windows, open command prompt and run the script like this:  
`C:\Python27\python.exe C:\Users\Username\Downloads\FM_Flair_Bot\src\FM_Flair_Bot.py`  
If you are on MacOS or a Linux distro then run the script like this:   
`cd \home\user\FM_Flair_Bot\src\`  
`python FM_Flair_Bot.py`  
Remember, your bot account ***needs*** to be a moderator to flair/remove submissions.
