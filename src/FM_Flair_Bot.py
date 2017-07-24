import praw
import Config_1
import time
import os
import pickle
import six

def load_dict(path_file):
    if os.path.isfile(path_file):
        with open(path_file, 'rb') as f:
            return pickle.load(f)
    else:
        return {}

def save_dict(data, path_file):
    with open(path_file, 'ab') as f:
        pickle.dump(data, f)

print("Logging in....")
reddit_instance=praw.Reddit(client_id=Config_1.client_id,
                            client_secret=Config_1.client_secret,
                            user_agent=Config_1.user_agent,
                            username=Config_1.username,
                            password=Config_1.password)
print("Logged in.")
dict_history=load_dict('submissions.txt')

while True:
    print("Searching for new posts")
    subreddit=reddit_instance.subreddit('fmgtestsub')
    for submission in subreddit.new(limit=10):
        print "new iteration"
        if submission.link_flair_text=='Help': #removing submissions flaired as help
            submission.reply('removal message')
            submission.remove()
        elif submission.id not in dict_history:
            dict_history[submission.id] = submission.link_flair_css_class
            submission.reply("flair post").mod.distinguish()
        save_dict(dict_history, 'submissions.txt')
        print "entered check if flaired"
        dict_keys = list(dict_history)
        for key in dict_keys:
            print key
            submission = reddit_instance.submission(key)
            if time.time() - submission.created_utc > 30.0:
                print "time more than 30"
                all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
                for comment in all_comments:
                    if "SETFLAIR" in comment.body:
                        flair = comment.body[9:]
                        submission.mod.flair(text=flair, css_class="Link")
                        comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                        comment.parent.mod.remove()  # and users flair reply
                        del dict_history[key]
                        break
                if submission.link_flair_css_class is not 'Link' and submission.link_flair_text is None:  # deleting post if user does not flair post in time
                    submission.reply('removal message').mod.distinguish()
                    submission.mod.remove()
                    print "deleted post"
                    del dict_history[key]
            else:
                print "time less than 30"
                if submission.link_flair_css_class is not 'Link' and submission.link_flair_text is None:
                    print "Not flaired"
                    all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
                    for comment in all_comments:
                        if "SETFLAIR" in comment.body and comment.is_root is 'False':
                            flair = comment.body[9:]
                            submission.mod.flair(text=flair, css_class="Link")
                            comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                            comment.parent.mod.remove()  # and users flair reply
                            del dict_history[key]
                            break
                else:
                    print "Flaired"
                    all_comments = submission.comments.list()  # stores all comments posted on submission in all_comments
                    for comment in all_comments:
                        if "flair post" in comment.body and comment.is_root is 'True':
                            comment.mod.remove()  # if user flairs the post within 15 minutes, bot deletes previous comment
                            del dict_history[key]
            print "passed all conditions"
            save_dict(dict_history, 'submissions.txt')
