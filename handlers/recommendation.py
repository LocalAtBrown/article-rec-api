from handlers.base import APIHandler


class RecHandler(APIHandler):
    async def get(self):
        self.finish("Hello")
