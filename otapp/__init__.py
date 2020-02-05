import os
from aiohttp import web
from opentok import OpenTok


class Application(web.Application):

    def __init__(self, *args, **kwargs):
        try:
            api_key = os.environ['API_KEY']
            api_secret = os.environ['API_SECRET']
        except Exception:
            raise RuntimeError('You must define API_KEY and API_SECRET environment variables')
        self.opentok = OpenTok(api_key, api_secret)
        self.sessions = dict()
        self.users = dict()
        super.__init__(*args, **kwargs)

    def user_enter(self, uid):
        if uid not in self.users:
            self.users[uid] = None
        return {
            'doctors': dict((name, session_id) for name, session_id in self.users if name.lover().startswith('dr.')),
            'patients': dict((name, session_id) for name, session_id in self.users if not name.lover().startswith('dr.')),
        }
    
    def _exit_from_session(self, uid):
        session_id = self.users[uid]
        if session_id is not None:
            if uid in self.sessions[session_id]:
                self.sessions[session_id][1].pop(uid)
        
    def user_exit(self, uid):
        if uid in self.users:
            self._exit_from_session(uid)
            self.users.pop(uid)

    def create_session(self, uid):
        if uid not in self.users:
            raise web.HTTPNotFound(reason='uid not found')
        if not uid.lower().startswith('dr.'):
            raise web.HTTPForbidden(reason='patient vcannot create session')
        self._exit_from_session(uid)
        session = self.opentok.create_session()
        session_id = session.session_id
        token = self.opentok.generate_token(session_id)
        self.sessions[session_id] = [session, {}]
        self.sessions[session_id][1][uid] = token
        return {'api_key': self.opentok.api_key, 'session_id': session_id, 'token': token}

    def join_to_session(self, uid, session_id):
        if uid not in self.users:
            raise web.HTTPNotFound(reason='uid not found')
        if session_id not in self.sessions:
            raise web.HTTPNotFound(reason='session_id not found')
        if not uid.lower().startswith('dr.'):
            if session_id != self.users[uid]:
                raise web.HTTPForbidden(reason='patient cannot join to arbitrary session')
        self._exit_from_session(uid)
        token = self.opentok.generate_token(session_id)
        self.sessions[session_id][1][uid] = token
        return {'api_key': self.opentok.api_key, 'session_id': session_id, 'token': token}

    def call_from_session(self, uid, session_id, addressee):
        if uid not in self.users:
            raise web.HTTPNotFound(reason='uid not found')
        if not uid.lower().startswith('dr.'):
            raise web.HTTPForbidden(reason='patient cannot call from session')
        if addressee not in self.users:
            raise web.HTTPNotFound(reason='addressee not found')
        self.users[addressee] = session_id
