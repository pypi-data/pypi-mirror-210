import logging.handlers

from notifications import NotificationHandler


class Logger:
    Logger = None
    NotificationHandler = None

    def __init__(
        self,
        logging_service,
        telegram_api_key=None,
        telegram_chat_id=None,
        enable_notifications=True,
        enable_console_log=True,
        enable_file_log=True,
    ):
        if not logging_service:
            raise Exception("logging_service parameter is not specified")

        self.service_name = logging_service
        self.Logger = logging.getLogger(logging_service)
        self.Logger.setLevel(logging.DEBUG)
        self.Logger.propagate = False
        formatter = logging.Formatter(
            "{asctime} [{levelname:7}] {process} {thread} {module} {name}: {message}", style="{"
        )

        if enable_file_log:
            fh = logging.FileHandler(f"logs/{logging_service}.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.Logger.addHandler(fh)

        # logging to console
        if enable_console_log:
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.Logger.addHandler(ch)

        # notification handler
        self.NotificationHandler = NotificationHandler(
            telegram_api_key=telegram_api_key,
            telegram_chat_id=telegram_chat_id,
            enabled=enable_notifications,
        )

        self.info(f"----------------- Starting logger: {logging_service} -----------------")

    def log(self, message, level="info", notify=False):
        if level == "info":
            self.Logger.info(message)
        elif level == "warning":
            self.Logger.warning(message)
        elif level == "error":
            self.Logger.error(message)
        elif level == "debug":
            self.Logger.debug(message)

        if notify and self.NotificationHandler.enabled:
            emoji = ""
            if level == "info":
                emoji = "ℹ️"
            elif level == "warning":
                emoji = "⚠️"
            elif level == "error":
                emoji = "❌"

            self.NotificationHandler.send_notification(f"{emoji} {self.service_name}: {message}")

    def info(self, message, notify=False):
        self.log(message, "info", notify)

    def warning(self, message, notify=False):
        self.log(message, "warning", notify)

    def error(self, message, notify=False):
        self.log(message, "error", notify)

    def debug(self, message, notify=False):
        self.log(message, "debug", notify)
