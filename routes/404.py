import bettersanic as bs
from sanic.response import text
from sanic.exceptions import NotFound


class NotFoundPage(bs.Cog):
    def __init__(self, app):
        self.app = app
    
    @bs.exception(NotFound)
    async def notfound(self, request, exception):
        return text("page not found", status=404)

def setup(app):
    app.add_cog(NotFoundPage(app))
