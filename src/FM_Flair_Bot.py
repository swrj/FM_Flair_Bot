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

def run_bot(reddit_instance, dict):
    print("Searching for new posts")
    subreddit=reddit_instance.subreddit('fmgtestsub')
    for submission in subreddit.stream.submissions():
        if submission.link_flair_text=='help':
            submission.reply('removal message')
            submission.remove()
        elif submission.link_flair_text is 'none':
            add_to_file(submission)

def add_to_file(submission):
    with open('submissions.txt', 'a') as f:
        f.write(submission)
        f.write('\n')
    with open('submissions.txt', 'r') as f:
        submissions = f.read().splitlines()
    for submission in subreddit.stream.submissions():
        if submission in submissions:
            print('Found old post. Skipping...')
        else:
            print('Found new post...')
            add_to_file(submission)
            f.write(submission+'\n')
            submissions.append(submission)
            submission.reply("flair post within 15 minutes by posting SETFLAIR followed by a space and one of the following choices"
                             +submission.flair.choices)
            print('Added new submission ID to list')
            print('Submission IDs found: ', submissions)

def check_if_flaired():
    f=open('submissions.txt','r+')
    f.seek(0)
    for line in f:
        submission=line
        if int(time.time())-submission.created>900:
            if submission.link_flair_text is 'none':
                submission.reply('removal message')
                submission.remove()
            else:
                f.write(line+'\n')

        else:
            all_comments=submission.comments.list()
            for comment in all_comments:
                if "SETFLAIR" in comment:
                    submission.select(comment[8:])



reddit_instance=bot_login()
dict = {}
while True:
    try:
        run_bot(reddit_instance. dict)
    except:
        continue
    time.sleep(15)
