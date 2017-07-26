import praw
import time
import sqlite3
import Config_1
from prawcore.exceptions import PrawcoreException

reddit = praw.Reddit(
    client_id=Config_1.client_id,
    client_secret=Config_1.client_secret,
    user_agent=Config_1.user_agent,
    username=Config_1.username,
    password=Config_1.password)

LIMIT = 10  # Number of posts to iterate through in subreddit/new. The more frequent the submissions are in your
# subreddit, the higher the number should be. 10 is more than enough for subreddits under ~50k

TIME_LIMIT = 120  # Number of seconds after which post should be removed if not flaired.

SUBREDDIT = reddit.subreddit('fmgtestsub')  # Enter subreddit here.

COMMENT_FOOTNOTE = '''\n\n---^^I ^^am ^^a ^^bot. ^^I ^^was ^^created ^^by 
[^^John_Yuki](https://www.reddit.com/user/John_Yuki/) ^^and [^^Swaraj](https://github.com/swrj)^^. ^^If ^^you ^^have 
^^any ^^questions ^^or ^^need ^^to ^^report ^^a ^^bug/problem, ^^please ^^message ^^John_Yuki ^^on ^^Reddit. '''
# Footnote to add to comments stored in variable.

COMMENT_TEXT = '''Please flair your post. You may also reply to this comment with SETFLAIR followed by a space and one 
of the following flair options and I will flair it for you:  \n\n'''  # First line of comment
for template in SUBREDDIT.flair.link_templates:
    COMMENT_TEXT += '* ' + str(template['text']) + '  \n\n'  # Adds all the flairs in the subreddit to comment in a list
COMMENT_TEXT += '***You have 15 minutes to reply to this comment with SETFLAIR followed by one of the above options ' \
                'before your post is automatically removed. Example - SETFLAIR GUIDE***'  # Text in comment after flairs
COMMENT_TEXT += COMMENT_FOOTNOTE  # Adds footnote right at the end of the comment

REMOVAL_MESSAGE = '''This post has been removed as it was not flaired in time. Posts must be flaired within 15 minutes 
of creation.'''  # Removal message to be posted when time limit expires

HELP_REMOVAL_MESSAGE = '''This post has been removed as it was flaired as "HELP". All advice/help posts must go in the 
daily thread that is stickied at the top of the subreddit.'''  # Message to post before removal when flaired 'HELP'

flair_template = SUBREDDIT.flair.link_templates  # returns link templates on specified subreddit
flair_list = [flair['text'] for flair in flair_template]

conn = sqlite3.connect('id_list.db')  # Creates a connection object that represents id_list.db
c = conn.cursor()  # Creates a cursor object to perform SQL commands
c.execute('CREATE TABLE IF NOT EXISTS Submissions_Commented_On(Submission_ID)')  # DB to store unresolved submissions
conn.commit()
c.execute('CREATE TABLE IF NOT EXISTS Submissions_To_Ignore(Submission_ID)')  # DB to store resolved submissions
conn.commit()  # Saves changes to database

print('Opened database successfully.')
print('Logged in as:', Config_1.username)


def check_comments():
    print ("Checking comments...")
    all_comments = submission.comments.list()
    for comment in all_comments:  # Checks to see if user comments to flair a post by replying to comment with a flair
        if "SETFLAIR" in comment.body.upper() and comment.author == submission.author:
            index = comment.body.find("SETFLAIR")  # finds index of SETFLAIR in OP's comment
            for flairs in flair_list:
                if flairs.upper() in comment.body.upper():
                    flair = flairs.upper()
            print (flair)
            if flair.upper() in flair_list:
                submission.mod.flair(text=flair.upper(), css_class='')  # Flairs the post with the text
                c.execute('INSERT INTO Submissions_To_Ignore VALUES (?)', (submission.id,))
                conn.commit()
                comment.mod.remove()
                parent=comment.parent()
                parent.mod.remove()
                print('Set flair and removed comments.')


def send_flair_reminder():
    c.execute('INSERT INTO Submissions_Commented_On VALUES (?)', (submission.id,))
    conn.commit()
    submission.reply(COMMENT_TEXT).mod.distinguish()  # Reminds user to flair within time limit
    print('Sent flair reminder.')


def help_post():
    submission.reply(HELP_REMOVAL_MESSAGE + COMMENT_FOOTNOTE).mod.distinguish()  # Adds footnote to removal message
    submission.mod.remove()  # Removes submission for being flaired as 'HELP'
    print('Removed a help post.')


def remove_comment():
    for comment in submission.comments:
        try:
            if comment.author.name == reddit.user.me():  # Deletes comment instructing to flair post
                c.execute('INSERT INTO Submissions_To_Ignore VALUES (?)', (submission.id,))
                conn.commit()
                comment.delete()
        except PrawcoreException:  # Handles exception
            pass


def check_age():
    print('Checking Age...')
    removal_text = REMOVAL_MESSAGE
    removal_text += COMMENT_FOOTNOTE  # Adds footnote to removal message
    if time.time() - submission.created_utc > TIME_LIMIT:  # checks if time limit has passed
        for comment in submission.comments:
            try:
                if comment.author.name == reddit.user.me():
                    c.execute('INSERT INTO Submissions_To_Ignore VALUES (?)', (submission.id,))
                    conn.commit()
                    comment.delete()
            except PrawcoreException:
                pass
        submission.reply(removal_text).mod.distinguish()
        submission.mod.remove()
        print('Removed an old post.')


def check_flair():
    print('Checking Flair...')
    if submission.link_flair_text == 'Help':
        help_post()  # redirects to help_post if post is flaired as "Help". Automatic removal.
    elif submission.link_flair_text in flair_list:
        remove_comment()  # removes previous comment made by bot
    elif submission.link_flair_text not in flair_list:
        check_age()  # checks if post has crossed time limit
        check_comments()  # checks if OP has manually set flair
        time.sleep(5)


while True:
    time.sleep(2)
    print('Searching...')
    for submission in SUBREDDIT.new(limit=LIMIT):  # enter number of submissions to iterate through
                                                # 10-15 is fine for submissions with a couple of posts every hour
                                                # ~50 for large subreddits (>100k subscribers)
        c.execute('SELECT Submission_ID FROM Submissions_Commented_On')  # returns submission ID's of posts commented on
        submissions_commented_on = set()
        for row in c.fetchall():
            submissions_commented_on.add(row[0])
        c.execute('SELECT Submission_ID FROM Submissions_To_Ignore')
        submissions_to_ignore = set()  # stores all resolved submissions in a set
        for row in c.fetchall():
            submissions_to_ignore.add(row[0])
        if submission.id not in submissions_commented_on:
            send_flair_reminder()  # sends flair reminder if new submission
        if submission.id in submissions_commented_on and submission.id not in submissions_to_ignore:
            check_flair()  # checks if flair is resolved if old unresolved submission
