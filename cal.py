import urllib.request
import urllib.error
import tempfile
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from typing import Union

app = FastAPI()

def rename_events(url):
    tmp = tempfile.NamedTemporaryFile().name

    url = f"https://{url}"

    try:
        urllib.request.urlretrieve(url, tmp)
    except ValueError:
        print("Invalid URL")
        return None

    with open(tmp, "r") as f:
        lines = f.readlines()

    if len(lines) == 0:
        return None

    for i, line in enumerate(lines):
        if i == 1 and "Allocate" not in line:
            return None

        if line.startswith("SUMMARY:"):
            classname, classtype = line.split("\\, ")
            classtype = classtype.rstrip().removesuffix("-JTU")
            classname = classname.rstrip().removeprefix("SUMMARY:")

            classcode = lines[i+2].removeprefix("DESCRIPTION:").split("_")[0]
            lines[i] = f"SUMMARY:{classcode} - {classtype}\n"

    return "".join(lines)

@app.get("/", response_class=HTMLResponse)
def read_root(url: str = None, ccode: str = None, cname: str = None, ctype: str = None, caps: str = None):
    if ccode is None: ccode = "0"
    if cname is None: cname = "0"
    if ctype is None: ctype = "0"
    if caps is None: caps = "0"
    if url is not None:
        footer = f"<p>edit-calendar.vercel.app/e?url={url}&f={ccode}&c={caps}</p>"
    else:
        footer = ""
    return f"""
    <html>
        <head>
            <title>Allocate+ Calendar Renamer</title>
        </head>
        <body>
            <h1>Allocate+ Calendar Renamer</h1>
            <p>Have you ever wanted to add your Allocate+ classes to your Google Calendar, but been annoyed by the weird names of the classes?</p>
            <form action="/">
                <label for="url">Enter URL:</label>
                <input type="text" id="url" name="url"><br>
                <label for="code">Display class code?</label>
                <input type="checkbox" id="ccode" name="ccode" value="1"><br>
                <label for="name">Display class name?</label>
                <input type="checkbox" id="cname" name="cname" value="1"><br>
                <label for="type">Display class type?</label>
                <input type="checkbox" id="ctype" name="ctype" value="1"><br>
                <label for="caps">Capitalise all words?</label>
                <input type="checkbox" id="caps" name="caps" value="1"><br>
                <input type="submit" value="Submit">
            </form>
            {footer}
        </body>
    """ # checkboxes for formats: course code, name and type, capitalised or not, order?

@app.get("/e")
def read_item(url: str = None, format: str = None):
    url = url.removeprefix("https://").removeprefix("https:/").removeprefix("http://").removeprefix("http:/")
    content = rename_events(url)
    if content is None:
        return Response(content="File not found", media_type="text/plain")

    new_filename = "modified.ics"
    response = Response(content=content, media_type="text/calendar")
    response.headers["Content-Disposition"] = f"attachment; filename={new_filename}"
    return response