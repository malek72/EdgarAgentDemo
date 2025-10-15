#import everything from every other file 

#webhooks NAVEEN PLEASE DO THIS.


def get_email():
    return "<EmailLatestMessage>"
def get_twitter():
    return "<TwitterLatestTweet>"
def get_whatsapp():
    return "<WhatsAppLatestMessage>"


#make supabase table to store last "latest" message/tweet id for each platform, so we can fetch only new messages/tweets

def is_new_message(message):
    #check if message is new by comparing with stored message in supabase
    return True

#make function so that we only send new messages/tweets/emails to agent1
def send_new_messages_to_agent1(agent1):
    email = get_email()
    twitter = get_twitter()
    whatsapp = get_whatsapp()
    # Check if the messages are new and send them to agent1
    if is_new_message(email):
        pass
        #call agent1 with email
    if is_new_message(twitter):
        pass
        #call agent1 with twitter   
    if is_new_message(whatsapp):
        pass
        #call agent1 with whatsapp
        #agent1Function(String)
    





