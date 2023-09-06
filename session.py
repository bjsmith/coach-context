from deliver_cbt import CBTTherapist, CBTSession, CBTIOInterface

class SessionManager:
    def __init__(self, frontend: CBTIOInterface):
        self.sessions = {}
        #self.IOInterface = IOInterface 
        self.frontend=frontend# the sessionManager can only handle one kind of front-end. I think that's OK for now.
        

    def create_session(self, channel_id, user_id, first_message=None):#, therapist):
        session = CBTSession(channel_id = channel_id, user_id = user_id, frontend=self.frontend, first_message=first_message)#, therapist)
        self.sessions[user_id] = session
        return session

    def get_session(self, user_id):
        return self.sessions.get(user_id)

    def close_session(self, user_id):
        if user_id in self.sessions:
            self.sessions[user_id].end_session()
            del self.sessions[user_id]

    def handle_incoming_message(self, channel_id, user_id, message,ts):
        session = self.get_session(user_id)
        timeout = 8 * 60 * 60  # 8 hours in seconds

        if not session:
            #therapist = CBTTherapist()
            session = self.create_session(channel_id, user_id, first_message=message)
            #response = ""
        else:
            if float(ts) - session.last_message_ts > timeout:
                self.close_session(user_id)
                #try again with a new session
                self.handle_incoming_message(channel_id, user_id, message, ts)
                return()
            response = session.handle_message(message, ts=ts)
        if session.is_ended:
            self.close_session(user_id)
            #return(None)

        return()

#In this design, the `SessionManager` class is responsible for managing sessions, creating new ones, and routing incoming messages to the appropriate session based on the user_id. It also removes sessions that have ended.

