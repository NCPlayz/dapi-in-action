from datetime import datetime
import praw

from .stars import Star
from .executor import run_in_executor


class RedditHandler:
    USER_AGENT = "python:DAPI In Action:v0.1 (by /u/ncplayz)"

    def __init__(self, logger, subreddit: str, client_id: str, client_secret: str, username: str, password: str):
        self.logger = logger

        self.reddit_session = praw.Reddit(client_id=client_id,
                                          client_secret=client_secret,
                                          user_agent=self.USER_AGENT,
                                          username=username,
                                          password=password)
        self.logger.info('Hello Reddit!')
        self.logger.debug('Reddit Logged in at {}'.format(datetime.now()))

        self.subreddit = self.reddit_session.subreddit(subreddit)

    @run_in_executor
    def new_post(self, star: Star):
        title = "{} - New Starboard Message".format(star.author)
        content = "{}\n\n".format(star.content)
        content += star.img_url if star.img_url else ""
        post = self.subreddit.submit(title, content)
        self.logger.debug('Reddit Post on r/{} - "{}" - {}'.format(self.subreddit.display_name, title, post.permalink))
