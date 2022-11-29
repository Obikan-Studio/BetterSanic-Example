from utils.bettersanic import BetterSanic
import os



app = BetterSanic("BetterSanic-Demo", enable_jinja2_async=True)
app.static('/static', './static')

for route in os.listdir("./routes"):
    if os.path.splitext(route)[1] == ".py":
        app.load_extension(f"routes.{os.path.splitext(route)[0]}")

app.run(host="0.0.0.0", port=8010)
