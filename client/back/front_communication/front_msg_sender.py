from tech_utils.logger import init_logger
logger = init_logger("Back_Msg2FrontSender")

message_queue = []

def send_message_to_front(message: str):
    global message_queue
    message_queue.append(message)
    return True
    
