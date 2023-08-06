from naludaq.backend.managers.base import Manager


class ConfigManager(Manager):
    def __init__(self, board):
        """Utility for higher-level configuration of the backend.

        Args:
            context (Context): context used to communicate with the backend.
        """
        super().__init__(board)

    def configure_packaging(self, events: "bytes | str", answers: "bytes | str"):
        """Sets the stop words used by the backend to separate
        events and answers.

        Args:
            events (bytes | str): stop word for events.
            answers (bytes | str): stop word for answers (register reads).
        """
        if isinstance(events, bytes):
            events = events.hex()
        if isinstance(answers, bytes):
            answers = answers.hex()
        try:
            self.context.client.put(
                "/server/data-format",
                params={
                    "model": self.board.model,
                    "events": events,
                    "answers": answers,
                },
            )
        except ValueError as e:
            raise ValueError("Stop words are invalid") from e
