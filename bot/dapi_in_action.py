#!/usr/bin/python3

import os
from datetime import datetime
import yaml
import asyncio
import discord
from discord.ext import commands
import logging

from bot.handlers.stars import StarQueue, Star
from .handlers import reddit


class DIA(commands.Bot):

    def __init__(self, prefixes: str="DIA-"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.debug("Started process")

        self.prefixes = prefixes
        self.tokens = self.find_tokens()
        self.owner = []

        if 'starboard_whitelist' not in self.tokens:
            self.logger.error("'starboard_whitelist' could not be found in tokens.yaml! Exiting...")
            exit(1)
        else:
            self.starboard_whitelist = self.tokens['starboard_whitelist']

        self.stars = StarQueue()
        # Queue of stars that the bot can append new stars onto
        # and the Reddit posting module can pull stars from
        # Both can work independently and simultaneously
        # self.stars.append(Star(...)) - Add a star to be posted
        # self.stars.pop() - Get next star to post to Reddit

        self.presence = discord.Game(name=f'dapi-in-action | DIA-')

        super().__init__(self.prefixes, activity=self.presence)

        self.r_session = self.setup_reddit()

        startup_extensions = []

        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                startup_extensions.append(file.replace('.py', ''))

        for extension in startup_extensions:
            try:
                self.load_extension(f'cogs.{extension}')
                self.logger.debug(f'Loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__}: {e}'
                self.logger.error(f'Failed to load extension {error}')

        self.r_submit_task = self.loop.create_task(self.reddit_submit())

    def find_tokens(self):
        try:
            with open("tokens.yaml", 'r') as stream:
                self.logger.debug("Loaded token file")
                tokens = yaml.load(stream)
                return tokens
        except FileNotFoundError:
            self.logger.error("token.yaml not found! Exiting...")
            exit(1)

    def run(self):
        try:
            super().run(self.tokens['discord_token'])
        except discord.LoginFailure:
            self.logger.error("Improper token has been passed! Exiting...")
            exit(1)

        if hasattr(self.tokens, 'owners'):
            self.owner = self.tokens['owners']
        else:
            self.owner = [self.application_info().owner]

    def setup_reddit(self):
        cred_missing = False
        reddits = self.tokens['reddit']
        args = []

        for key in reddits:
            if reddits[key] is None:
                self.logger.error('Your Reddit {} is missing!'.format(key.replace('_', '')))
                cred_missing = True
            else:
                args.append(reddits[key])

        if cred_missing:
            self.logger.error('Please fix your Reddit key(s)! Exiting...')
            exit(1)
        else:
            return reddit.RedditHandler(self.logger, *args)

    async def on_ready(self):
        self.logger.info("Hello Discord!")
        self.logger.debug("Discord Logged in at {}".format(datetime.now()))

    async def on_message(self, message):
        """
        Dispatches the messages to the correct places
        """
        # TODO: Do the above
        # When appending stars to the queue, use the Star class, so that the data is in a consistent format for
        # the reddit module
        #
        if message.channel.id in self.starboard_whitelist:
            self.dispatch('star_message', message)

    def add_star(self, star: Star):
        return self.stars.append(star)

    async def reddit_submit(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(60)
            self.logger.debug("=== Reddit Stars - {} - Background Task Initiated ===".format(datetime.now()))
            if len(self.stars.queue) > 0:
                self.logger.debug("Star found.")
                await self.r_session.new_post(self.stars.queue[0])
                self.stars.pop()
            else:
                self.logger.debug("No stars found.")
            self.logger.debug("=== Reddit Stars - {} - Background Task Finished  ===".format(datetime.now()))


