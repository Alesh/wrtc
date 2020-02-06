import os
from aiohttp import web
from opentok import OpenTok


class Application(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            api_key = os.environ['API_KEY']
            api_secret = os.environ['API_SECRET']
        except Exception:
            raise RuntimeError('You must define API_KEY and API_SECRET environment variables')
        self.opentok = OpenTok(api_key, api_secret)
        self.sessions = dict()
        self.users = dict()

    def user_enter(self, user_id):
        if user_id not in self.users:
            self.users[user_id] = None
        rv = {'state': self.users[user_id]}

        if user_id.lower().startswith('dr.'):
            rv['patients'] = dict((user_id, session_id)
                                  for user_id, session_id in self.users.items()
                                  if not user_id.lower().startswith('dr.'))
        return rv

    def _exit_from_session(self, user_id):
        session_id = self.users[user_id]
        if session_id is not None:
            if user_id in self.sessions[session_id]:
                self.sessions[session_id][1].pop(user_id)

    def user_exit(self, user_id):
        if user_id in self.users:
            self._exit_from_session(user_id)
            self.users.pop(user_id)

    def create_session(self, user_id):
        if user_id not in self.users:
            raise web.HTTPNotFound(reason='user_id not found')
        if not user_id.lower().startswith('dr.'):
            raise web.HTTPForbidden(reason='patient vcannot create session')
        self._exit_from_session(user_id)
        session = self.opentok.create_session()
        session_id = session.session_id
        token = self.opentok.generate_token(session_id)
        self.sessions[session_id] = [session, {}]
        self.sessions[session_id][1][user_id] = token
        return {'api_key': self.opentok.api_key, 'session_id': session_id, 'token': token}

    def join_to_session(self, user_id, session_id):
        if user_id not in self.users:
            raise web.HTTPNotFound(reason='user_id not found')
        if session_id not in self.sessions:
            raise web.HTTPNotFound(reason='session_id not found')
        if not user_id.lower().startswith('dr.'):
            if session_id != self.users[user_id]:
                raise web.HTTPForbidden(reason='patient cannot join to arbitrary session')
        self._exit_from_session(user_id)
        token = self.opentok.generate_token(session_id)
        self.sessions[session_id][1][user_id] = token
        return {'api_key': self.opentok.api_key, 'session_id': session_id, 'token': token}

    def call_from_session(self, user_id, session_id, addressee):
        if user_id not in self.users:
            raise web.HTTPNotFound(reason='user_id not found')
        if not user_id.lower().startswith('dr.'):
            raise web.HTTPForbidden(reason='patient cannot call from session')
        if addressee not in self.users:
            raise web.HTTPNotFound(reason='addressee not found')
        self.users[addressee] = session_id
