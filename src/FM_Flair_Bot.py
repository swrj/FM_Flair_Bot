import praw
import Config_1
from datetime import datetime
import time
import os
import six.moves.cPickle
import six

def load_dict(path_file):
    if os.path.isfile(path_file):
        with open(path_file, 'rb') as f:
            return six.moves.cPickle.load(f)
    else:
        return {}

def save_dict(data, path_file):
    with open(path_file, 'wb') as f:
        six.moves.cPickle.dump(data, f)

print("Logging in....")
reddit_instance=praw.Reddit(client_id=Config_1.client_id,
                            client_secret=Config_1.client_secret,
                            user_agent=Config_1.user_agent,
                            username=Config_1.username,
                            password=Config_1.password)
print("Logged in.")
dict_history=load_dict('submissions.p')

while True:
    print("Searching for new posts")
    subreddit=reddit_instance.subreddit('fmgtestsub')
    for submission in subreddit.stream.submissions():
        if submission.link_flair_text=='Help': #removing submissions flaired as help
            submission.reply('removal message')
            submission.remove()
        elif submission.id not in dict_history and submission.link_flair_text is None:
            dict_history['id'] = submission.id
        print "entered check if flaired"
        submission.reply("flair post").mod.distinguish()
        temp_dict_history = dict_history
        for submission_ in six.iteritems(dict_history):
            submission = reddit_instance.submission(int(submission_['id']))
            if datetime.utcnow() > submission_['time_created'] + 30:
                if submission.link_flair_text is None:  # deleting post if user does not flair post in time
                    submission.reply('removal message').mod.distinguish()
                    reddit_instance.submission.mod.remove()
                    del temp_dict_history[submission_]
                else:
                    all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
                    for comment in all_comments:
                        if "SETFLAIR" in comment.body and comment.is_root is 'False':
                            flair = comment.body[9:]
                            submission.mod.flair(text=flair, css_class="")
                            comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                            comment.parent.mod.remove()  # and users flair reply
                            del temp_dict_history[submission_]

            else:
                all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
                for comment in all_comments:
                    if "SETFLAIR" in comment and comment.is_root is 'False':
                        flair = comment.body[9:]
                        submission.mod.flair(text=flair, css_class="")
                        comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                        comment.parent.mod.remove()  # and users flair reply
                        del temp_dict_history[submission_]
            dict_history = temp_dict_history
            save_dict(dict_history, 'submissions.p')
