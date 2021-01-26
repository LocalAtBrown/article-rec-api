from flask import Flask

from db.helpers import get_article_by_external_id

app = Flask(__name__)


@app.route("/")
def hello_world():
    article = get_article_by_external_id(322144)
    return f"Fetched article id {article['id']}: {article['title']}"
