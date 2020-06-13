from time import sleep
from flask import Flask, render_template
from flask import jsonify
import os
import json
import markdown2
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

############ Web Pages ############

# index
@app.route("/")
def home():
    posts = get_posts()
    return render_template("home.html", posts=posts)

# about page
@app.route("/about")
def about():
    return render_template("about.html")

# single blog post page
@app.route("/blog/<year>/<month>/<day>/<slug>")
def blogpost(year, month, day, slug):
    file_path = os.path.join('blog', str(year), str(month), str(day), str(slug), "README.md")
    try:
        markdown_html = get_markdown(file_path)
        title = slug

        # get title from markdown html, it will be displayed in breadcrumb
        parsed_html = BeautifulSoup(markdown_html)
        title = parsed_html.find('h1').text
            
        return render_template("post.html", markdown=markdown_html, title=title)
    except Exception as e:
        return str(e)

############ API ############

# GET all blogs
@app.route("/blog")
def blog():
    dir = blog_tree("blog", None)
    return jsonify(dir)

############ Helpers ############

# get all blog posts
def get_posts():
    blogs_dict = blog_tree("blog", None)
    posts = []
    for year_dir in blogs_dict['children']:
        for month_dir in year_dir['children']:
            for day_dir in month_dir['children']:
                date = day_dir['path']
                date_info = date.split('/')
                date = datetime.datetime(int(date_info[0]), int(date_info[1]), int(date_info[2]))
                for blog_post_dir in day_dir['children']:
                    file_path = os.path.join('blog', blog_post_dir['children'][0]['path'])
                    title = ''
                    try:
                        markdown_html = get_markdown(file_path)
                        parsed_html = BeautifulSoup(markdown_html)
                        title = parsed_html.find('h1').text
                    except Exception as e:
                        print(e)
                    blog_post = {
                        'path': blog_post_dir['path'],
                        'date': date.strftime("%B %d, %Y"),
                        'title': title,
                    }
                    posts.append(blog_post)
    
    return list(reversed(posts))

# make a tree out of blog dir
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

# get file markdown
def get_markdown(path):
    try:
        with open(path, "r") as readme_file:
            md_template_string = markdown2.markdown(
                readme_file.read(), extras=['fenced-code-blocks']
            )

            return md_template_string
    except Exception as e:
        return str(e)

############ Main ############
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')