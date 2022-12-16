import bettersanic as bs
from sanic.response import text

class Index(bs.Cog):
    def __init__(self, app):
        self.app = app
    
    @bs.route("/")
    async def index(self, request):
        return text("Hello World")

def setup(app):
    app.add_cog(Index(app))
