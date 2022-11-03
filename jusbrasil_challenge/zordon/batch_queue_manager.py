from jusbrasil_challenge.mq.manager import MQManager


class BatchQueueManager(MQManager):
    def send_batch_message(self, message: str, uf: str):
        queue = f"batch_{uf}"
        self.send_message(message, queue)
