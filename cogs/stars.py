from bot.handlers import stars


class Stars:
    def __init__(self, bot):
        self.bot = bot

    async def on_star_message(self, message):
        if message.embeds:
            s = message.embeds[0]
            star = stars.Star(message.id, s.title, s.description)
        else:
            star = stars.Star(message.id, message.author, message.content)
        self.bot.add_star(star)


def setup(bot):
    bot.add_cog(Stars(bot))
