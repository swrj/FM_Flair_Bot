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

subreddit = reddit.subreddit('fmgtestsub')

conn = sqlite3.connect('id_list.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS Submissions_Commented_On(Submission_ID)')
conn.commit()
c.execute('CREATE TABLE IF NOT EXISTS Submissions_To_Ignore(Submission_ID)')
conn.commit()

print('Opened database successfully.')
print('Logged in as:', Config_1.username)


def send_flair_reminder():
    c.execute('INSERT INTO Submissions_Commented_On VALUES (?)', (submission.id,))
    conn.commit()
    submission.reply('Please remember to flair your post.').mod.distinguish()
    print('Sent flair reminder.')


def help_post():
    submission.reply('''This post has been removed for help flair.''').mod.distinguish()
    submission.mod.remove()
    print('Removed a help post.')


def remove_comment():
    for comment in submission.comments:
        try:
            if comment.author.name == reddit.user.me():
                c.execute('INSERT INTO Submissions_To_Ignore VALUES (?)', (submission.id,))
                conn.commit()
                comment.delete()
                print('Removed my flair reminder.')
        except PrawcoreException:
            pass


def check_age():
    print('Checking Age...')
    removal_msg = '''Post removed for being too old.'''
    if time.time() - submission.created_utc > 120:
        submission.reply(removal_msg).mod.distinguish()
        submission.mod.remove()
        print('Removed an old post.')


def check_flair():
    print('Checking Flair...')
    flair_template = subreddit.flair.link_templates
    flair_list = [flair['text'] for flair in flair_template]
    if submission.link_flair_text == 'Help':
        help_post()
    elif submission.link_flair_text in flair_list:
        remove_comment()
    elif submission.link_flair_text not in flair_list:
        all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
        for comment in all_comments:
            if "SETFLAIR" in comment.body and comment.author is submission.author:
                flair = comment.body[9:]
                submission.mod.flair(text=flair, css_class='')
                comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                parent=comment.parent()
                parent.mod.remove()  # and users flair reply
        check_age()


while True:
    time.sleep(2)
    print('Searching...')
    for submission in subreddit.new(limit=10):
        print(submission.comments.list())
        c.execute('SELECT Submission_ID FROM Submissions_Commented_On')
        submissions_commented_on = set()
        for row in c.fetchall():
            submissions_commented_on.add(row[0])
        c.execute('SELECT Submission_ID FROM Submissions_To_Ignore')
        submissions_to_ignore = set()
        for row in c.fetchall():
            submissions_to_ignore.add(row[0])
        if submission.id not in submissions_commented_on:
            send_flair_reminder()
        if submission.id in submissions_commented_on and submission.id not in submissions_to_ignore:
            check_flair()
