import praw
import config
import datetime
import time

def bot_login():
    print("Logging in....")
    reddit_instance=praw.Reddit(client_id=config.client_id,
                client_secret=config.client_secret,
                user_agent=config.user_agent,
                username=config.username,
                password=config.password)
    print("Logged in.")
    return reddit_instance

def run_bot(reddit_instance):
    print("Searching for new posts")
    subreddit=reddit_instance.subreddit('fmgtestsub')
    for submission in subreddit.stream.submissions():
        if submission.link_flair_text=='help': #removing submissions flaired as help
            submission.reply('removal message')
            submission.remove()
        elif submission.link_flair_text is 'none': #adding submissions not flaired to text file
            add_to_file(submission)
        check_if_flaired() #running method to check if previous posts have been flaired

def add_to_file(submission):
    #with open('submissions.txt', 'a') as f:#
        #f.write(submission)#
        #f.write('\n')#
    with open('submissions.txt', 'r') as f:
        submissions = f.read().splitlines()
    for submission in submissions:
        print('Found new post...')
        add_to_file(submission)
        f.write(submission+'\n')
        #submissions.append(submission)#
        submission.reply("flair post within 15 minutes by replying to this comment with SETFLAIR followed by a space "
                         "and one of the following choices: "+submission.flair.choices)
        print('Added new submission ID to list')
        #print('Submission IDs found: ', submissions)#

def check_if_flaired():
    f=open('submissions.txt','r+')
    f.seek(0) #starting from first submission in the list
    remove_from_list='FALSE' #counter that stores value TRUE when a user flairs a post within 15 minutes
    for line in f:
        submission=line
        if int(time.time())-submission.created>900:
            if submission.link_flair_text is 'none': #deleting post if user does not flair post in time
                submission.reply('removal message')
                submission.remove()
            else:
                all_comments = submission.comments.list() #stores all comments posted on submission in all_comments
                for comment in all_comments:
                    if "SETFLAIR" in comment and comment.is_root is 'False':
                        comment.delete() #if user flairs the post within 15 minutes, bot deletes previous comment
                        comment.parent.delete() #and users flair reply
                submission.select(comment[8:]) #flairs post
                        

        else:
            all_comments=submission.comments.list() #stores all comments posted on submission in all_comments
            for comment in all_comments:
                if "SETFLAIR" in comment and comment.is_root is 'False':
                    submission.select(comment[8:]) #flairs post
                    comment.delete()
                    parent = comment.parent()
                    parent.delete()
                    remove_from_list='TRUE'
                if remove_from_list is 'FALSE':
                    f.write(line+'\n') #writes all submissions back to file (effectively deletes all submissions flaired)

reddit_instance=bot_login()
while True:
    try:
        run_bot(reddit_instance)
    except:
        continue
    time.sleep(15) #makes bot sleep for 15 seconds (can be changed appropriately)
