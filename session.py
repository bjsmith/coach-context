from chat import ChatConfig
from deliver_help import Therapist, CoachingSession, CoachingIOInterface, AsyncCoachingIOInterface
from storage_management import S3BucketManagement, LocalStorageManagement


class BaseSessionManager:

    def __init__(self, frontend: CoachingIOInterface):
                
        config_settings = ChatConfig.get_config()
        if ChatConfig.get_config()['IS_HEROKU']=='True':
            self.storage_manager = S3BucketManagement(
                config_settings['AWS_ACCESS_KEY_ID'],
                config_settings['AWS_SECRET_ACCESS_KEY'],
                config_settings['S3_BUCKET']
            )
        else:
            self.storage_manager = LocalStorageManagement('user_data/')


        self.storage_manager = S3BucketManagement(
                config_settings['AWS_ACCESS_KEY_ID'],
                config_settings['AWS_SECRET_ACCESS_KEY'],
                config_settings['S3_BUCKET']
            )

class SessionManager(BaseSessionManager):
    def __init__(self, frontend: CoachingIOInterface):#,async_mode=False):
        self.sessions = {}
        #self.IOInterface = IOInterface 
        self.frontend=frontend# the sessionManager can only handle one kind of front-end. I think that's OK for now.
        #self.async_mode = async_mode

        super().__init__(frontend)
        

    def create_session(self, channel_id, user_id, first_message=None):#, therapist):
        session = CoachingSession(channel_id = channel_id, user_id = user_id, frontend=self.frontend, first_message=first_message,
                                  storage_manager=self.storage_manager)#, therapist)
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

class AsyncSessionManager(BaseSessionManager):
    def __init__(self, frontend: AsyncCoachingIOInterface):
        self.sessions = {}
        #self.IOInterface = IOInterface 
        self.frontend=frontend# the sessionManager can only handle one kind of front-end. I think that's OK for now.

        super().__init__(frontend)

        

    async def create_session(self, channel_id, user_id, first_message=None):#, therapist):
        session = CoachingSession(
            channel_id = channel_id, user_id = user_id, frontend=self.frontend, first_message=first_message, is_async=True,
            file_storage_manager=self.storage_manager
            )#, therapist)
        #for the async version, we need to do a distinct to send out the introductory message
        self.sessions[user_id] = session
        await session.respond_to_session_opening_async()
        
        return session

    def get_session(self, user_id):
        return self.sessions.get(user_id)

    def close_session(self, user_id):
        if user_id in self.sessions:
            self.sessions[user_id].end_session()
            del self.sessions[user_id]

    async def handle_incoming_message(self, channel_id, user_id, message,ts):
        session = self.get_session(user_id)
        timeout = 8 * 60 * 60  # 8 hours in seconds

        if not session:
            #therapist = CBTTherapist()
            session = await self.create_session(channel_id, user_id, first_message=message)
            #response = ""
            
             
        else:
            if float(ts) - session.last_message_ts > timeout:
                self.close_session(user_id)
                #try again with a new session
                await self.handle_incoming_message(channel_id, user_id, message, ts)
                return()

            await session.handle_message_async(message, ts=ts)
            
        if session.is_ended:
            self.close_session(user_id)
            #return(None)

        return()

#In this design, the `SessionManager` class is responsible for managing sessions, creating new ones, and routing incoming messages to the appropriate session based on the user_id. It also removes sessions that have ended.

