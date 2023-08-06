import asyncio


class smiley:

    def __init__(self, id):
        self.id = id
        self.status = 500
        self.status_message = 'unknown status message'
        self.response = None
        self.thread_force_stop = False

    def get_id(self):
        return self.id

    def set_status(self, st, msg):
        self.status = st
        self.status_message = msg

    def get_status(self):
        return (self.status, self.status_message)

    def set_response(self, response):
        self.response = response

    def get_response(self):
        return (self.response)

    def get_thread_force_stop(self):
        return (self.thread_force_stop)

    def set_thread_force_stop(self, thread_force_stop):
        self.thread_force_stop = thread_force_stop


class smiley_collection:

    def __init__(self):
        self.smiley_dict = {}

    def add(self, smiley):
        self.smiley_dict[smiley.id] = smiley

    def get(self):
        return self.smiley_dict

    def remove(self):
        self.smiley_dict = {}

    def remove_by_id(self, id):
        del self.smiley_dict[id]


def start_loop(loop):
    asyncio.set_event_loop(loop)
    try:
        loop.run_forever()
    finally:
        print('end loop')
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
