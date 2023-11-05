from flask import Flask, request, render_template
import crawler

app = Flask(__name__)

@app.route("/")
def start():
    return render_template("StartView.html")


@app.route("/search")
def searchresults():
    prompt = request.args.get('prompt')
    result = crawler.search(prompt)
    return render_template("ListView.html", prompt=prompt, result=result)

if __name__ == "__main__":
    crawler.crawl("https://vm009.rz.uos.de/crawl/index.html")
    # you have to run it as a regular python file and this starts the app once the crawl is finished
    # Flask had some issues loading modules when started over the command line with 'flask run'
    # also this avoids user inputs before the crawler is done
    app.run()