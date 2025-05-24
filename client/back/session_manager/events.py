import threading
finish_event = threading.Event()
abort_event = threading.Event()
external_stop_event = threading.Event()