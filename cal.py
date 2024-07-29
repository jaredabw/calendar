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
def read_root(url: str = None, format: str = None):
    if url is not None:
        footer = f"""<p>edit-calendar.vercel.app/e?url={url}&format={format}</p>"""
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
            <p>To receive a link with renamed clases, you can simply add "edit-calendar.vercel.app/" in front of the URL.</p>
            <form action="/">
                <label for="url">Enter URL:</label>
                <input type="text" id="url" name="url">
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