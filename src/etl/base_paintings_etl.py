import logging
import threading
from queue import Queue
from typing import Dict, List


from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class BasePaintingsETL(ABC):
    def __init__(self, batch_size=600, workers=5):
        self.batch_size = batch_size
        self.workers = workers

        # Pipeline Queues
        self.transform_queue = Queue(maxsize=10)
        self.load_queue = Queue(maxsize=10)

    # ========== ETL STAGES - To define in children classes ==========
    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def transform(self):
        pass

    @abstractmethod
    def load(self, batch: List[Dict]) -> None:
        pass

    # ========== WORKERS ==========
    def run_transform_worker(self):
        """
        Worker que:
        1. Retrieves batches from transform_queue
        2. Transforms them
        3. Places them in load_queue
        """

        while True:
            batch = self.transform_queue.get()

            if batch is None:
                self.load_queue.put(None)  # last message
                logger.info("Transform worker received stop signal")
                self.transform_queue.task_done()
                break

            enriched = self.transform(batch)
            self.load_queue.put(enriched)
            self.transform_queue.task_done()

        logger.info("Transform worker stopped")

    def run_load_worker(self):
        """
        Worker that:
        1. Retrieves batches from load_queue
        2. Loads them into the DB
        """
        while True:
            batch = self.load_queue.get()

            if batch is None:
                logger.info("Load worker received stop signal")
                self.load_queue.task_done()
                break

            self.load(batch)
            self.load_queue.task_done()

        logger.info("Load worker stopped")

    # ========== ORCHESTRATOR ==========
    def run(self):
        logger.info("Starting ETL pipeline...")

        # Create threads that execute worker functions
        transform_thread = threading.Thread(
            target=self.run_transform_worker, name="TransformWorker"
        )
        load_thread = threading.Thread(target=self.run_load_worker, name="LoadWorker")

        # Start the workers
        transform_thread.start()
        load_thread.start()

        # Main thread: extract and feed the pipeline
        try:
            for batch in self.extract():
                self.transform_queue.put(batch)
                logger.info("Batch queued for transformation")
        finally:
            self.transform_queue.put(None)
            logger.info("Extraction completed, sent stop signal")

        # Wait until they finish
        transform_thread.join()
        load_thread.join()

        logger.info("ETL pipeline completed!")
