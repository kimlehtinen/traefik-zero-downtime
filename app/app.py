from time import sleep
from flask import Flask, render_template
from flask import jsonify
import os
import json

app = Flask(__name__)

# Web Pages
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/user/<name>')
def user(name):
	return '<h1>Hello, {0}!</h1>'.format(name)

@app.route("/blog")
def blog():
    dir = blog_tree("blog", None)
    return jsonify(dir)

# Helpers
def blog_tree(path, parent):
    d = {
        'name': os.path.basename(path),
        'path': ''
    }

    if parent is not None:
        d['path'] = os.path.join(parent, d['name'])

    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [blog_tree(os.path.join(path,x), d['path']) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d

# Main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')