from FlaskSuper.FlaskSuper import FlaskSuper
import sys
import os
def make_app():
    os.mkdir("html")
    with open("html/index.html","w") as Index:
        Index.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>""")
    os.mkdir("static")
    with open("App.py","w") as App:
        App.write("""
from flaskSuper import FlaskSuper

app = FlaskSuper()

@app.route("/")
def index():
    return app.render("index.html")

app.run(debug=True)

""")
    print("Creating an app...")
def main():
    if len(sys.argv) < 2:
        print("Usage: python mytool.py [command]")
        return

    command = sys.argv[1]

    if command == "make":
        make_app()
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
