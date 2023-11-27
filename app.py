from flask import Flask, request, render_template
import crawler

app = Flask(__name__)


@app.route("/")
def start():
    crawler.crawl("https://vm009.rz.uos.de/crawl/index.html")
    return render_template("StartView.html")


@app.route("/search")
def searchresults():
    display_corr = False
    prompt = request.args.get('prompt')
    result, corr = crawler.search(prompt)
    if not result:
        display_corr = True
    if not corr:
        display_corr = False
    return render_template("ListView.html",
                           prompt=prompt,
                           result=result,
                           display_corr=display_corr,
                           corr=corr)


if __name__ == "__main__":
    # crawler.crawl("https://vm009.rz.uos.de/crawl/index.html")
    # you have to run it as a regular python file and this starts
    # the app once the crawl is finished
    # Flask had some issues loading modules when started over the
    # command line with 'flask run'
    # also this avoids user inputs before the crawler is done
    app.run()
