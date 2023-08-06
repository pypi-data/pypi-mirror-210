import queue
import threading

import apprise


class NotificationHandler:
    def __init__(self, telegram_chat_id, telegram_api_key, enabled=True):
        if enabled and telegram_chat_id and telegram_api_key:
            self.apobj = apprise.Apprise()
            self.apobj.add(f"tgram://{telegram_api_key}/{telegram_chat_id}")
            self.queue = queue.Queue()
            self.start_worker()
            self.enabled = True
        else:
            self.enabled = False

    def start_worker(self):
        threading.Thread(target=self.process_queue, daemon=True).start()

    def process_queue(self):
        while True:
            message, attachments = self.queue.get()

            if attachments:
                self.apobj.notify(body=message, attach=attachments)
            else:
                self.apobj.notify(body=message)
            self.queue.task_done()

    def send_notification(self, message, attachments=None):
        if self.enabled:
            self.queue.put((message, attachments or []))
