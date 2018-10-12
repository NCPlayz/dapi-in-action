class Star:
    """
    Represents a Starred message
    """

    def __init__(self, message_id, author, content, img_url=None):
        self.message_id = message_id
        self.author = str(author)
        self.content = content
        self.img_url = img_url


class StarQueue:
    """
    A FIFO queue of stars
    """
    
    def __init__(self):
        self.__queue = []
        
    @property
    def queue(self):
        return self.__queue

    def append(self, star):
        self.__queue.append(star)

    def pop(self):
        return self.__queue.pop(0)
