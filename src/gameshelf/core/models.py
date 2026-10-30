class Game:
    def __init__(self, title, command, source="manual", cover=None, hidden=False):
        self.title = title
        self.command = command
        self.source = source
        self.cover = cover
        self.hidden = hidden

    def to_dict(self):
        return {
            "title": self.title,
            "command": self.command,
            "source": self.source,
            "cover": self.cover,
            "hidden": self.hidden,
        }