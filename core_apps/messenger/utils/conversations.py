

def get_conversation_id(sender_id, receiver_id):
    ''' 
    Generate a conversation_id based on the sender and receiver ids
    
    Args:
        sender_id (int): The sender user id
        receiver_id (int): The receiver user id
    
    Return:
        str: min(sender_id, receiver_id)_max(sender_id, receiver_id)
    '''
    return f"{min(int(sender_id), int(receiver_id))}_{max(int(sender_id), int(receiver_id))}"