import logging
import threading
from queue import Queue
from config import collection

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Queue for asynchronous logging
log_queue = Queue()

def db_logger():
    """Background thread to process and insert events from the log queue."""
    while True:
        try:
            event = log_queue.get(timeout=1)  # Wait for an event for up to 1 second
            if event is None:  # Shutdown signal
                break
            try:
                collection.insert_one(event)
                logging.info(f"Logged event: {event}")
            except Exception as e:
                logging.error(f"Database insertion error: {e}")
        except Exception:
            continue

# Start the logging thread
db_thread = threading.Thread(target=db_logger, daemon=True)
db_thread.start()

def log_event(event_data):
    """Add an event to the logging queue."""
    log_queue.put(event_data)
