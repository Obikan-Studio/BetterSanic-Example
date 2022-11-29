from sanic import Sanic
import importlib
from sanic_jinja2 import SanicJinja2
from jinja2 import FileSystemLoader

class CogRoute:
    def __init__(self, callback, location, *args, **kwargs):
        self._callback = callback
        self.location = location
        self.cog = None
        self.args = args
        self.kwargs = kwargs
    
    async def callback(self, request, *args, **kwargs):
        return await self._callback(self.cog, request, *args, **kwargs)
       
    async def __call__(self, request, *args, **kwargs):
        return await self.callback(request, *args, **kwargs)

class CogException:
    def __init__(self, callback, *exceptions, route_names=None):
        self._callback = callback
        self.cog = None
        self.route_names = route_names
        self.exceptions = exceptions
    
    async def callback(self, request, exception, *args, **kwargs):
        return await self._callback(self.cog, request, exception, *args, **kwargs)
        
    async def __call__(self, request, exception, *args, **kwargs):
        return await self.callback(request, exception, *args, **kwargs)


class Cog:
    def __new__(cls, *args, **kwargs):
        new_cls = super().__new__(cls)
        new_cls.routes = [route for route in [getattr(cls, k) for k in dir(cls)] if isinstance(route, CogRoute)]
        new_cls.exceptions = [exception for exception in [getattr(cls, k) for k in dir(cls)] if isinstance(exception, CogException)]
        for route in new_cls.routes: route.cog = new_cls
        for exception in new_cls.exceptions: exception.cog = new_cls
        return new_cls

class BetterSanic(Sanic):
    def __init__(self, *args, enable_jinja2_async=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx.jinja = SanicJinja2(self, enable_async=enable_jinja2_async, loader=FileSystemLoader("templates"))
        self.ctx.cogs = []
    
    @property
    def jinja(self):
        return self.ctx.jinja

    def add_cog(self, cog):
        self.ctx.cogs.append(cog)
        for route in cog.routes:
            self.add_route(route.callback, route.location, *route.args, **route.kwargs)
        for exception in cog.exceptions:
            for exception_type in exception.exceptions:
                self.error_handler.add(exception_type, exception.callback, route_names=exception.route_names)
    
    def load_extension(self, name):
        spec = importlib.util.find_spec(name)
        extension = importlib.util.module_from_spec(spec)
        name = importlib.util.resolve_name(name, None)
        spec.loader.exec_module(extension)
        extension.setup(self)

def route(location, *args, **kwargs):
    def decorator(func):
        return CogRoute(func, location, *args, **kwargs)
    return decorator
    
def exception(*exceptions, route_names=None):
    def decorator(func):
        return CogException(func, *exceptions, route_names)
    return decorator
