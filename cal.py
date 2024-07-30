import urllib.request
import urllib.error
import tempfile
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from typing import Union

app = FastAPI()
root = "https://edit-calendar.vercel.app/"

def gen_summary(classname: str, classtype: str, classcode: str, form: int) -> str:
    bitform = format(form, "04b")

    new = "SUMMARY:"
    if bitform[0] == "1":
        new += classcode + " "
        if not bitform[1] == "1":
            new += "- "
    if bitform[1] == "1":
        new += classname.title() + " - "
        # if bitform[2] == "1":
        #     new += " - "
    if bitform[2] == "1":
        new += classtype + " "
    if bitform[3] == "1":
        new = new.upper()

    new = new.removesuffix("-").removesuffix("- ")
    new += "\n"
    return new

def rename_events(url, form: int):
    tmp = tempfile.NamedTemporaryFile().name

    try:
        urllib.request.urlretrieve(url, tmp)
    except ValueError:
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

            lines[i] = gen_summary(classname, classtype, classcode, form)

    return "".join(lines)

@app.get("/", response_class=HTMLResponse)
def read_root(url: str = None, ccode: str = None, cname: str = None, ctype: str = None, caps: str = None):
    if ccode is None: ccode = "0"
    if cname is None: cname = "0"
    if ctype is None: ctype = "0"
    if caps is None: caps = "0"

    codechecked = "checked" if ccode == "1" else ""
    namechecked = "checked" if cname == "1" else ""
    typechecked = "checked" if ctype == "1" else ""
    capschecked = "checked" if caps == "1" else ""

    form = int(f"{ccode}{cname}{ctype}{caps}", 2)

    if url is None or url == "None":
        url = ""
        codechecked = "checked"
        namechecked = "checked"
        typechecked = "checked"

    url = url.removeprefix("https://").removeprefix("https:/").removeprefix("http://").removeprefix("http:/")

    if "my-timetable.monash.edu" in url:
        if "my-timetable.monash.edu/even/rest/calendar/ical" in url:
            url = url.removeprefix("my-timetable.monash.edu/even/rest/calendar/ical/")
            footer = f"""
            <p>Example:</p>
            <p>{gen_summary("FUND ALG", "Workshop", "FIT1008", form).removeprefix("SUMMARY:")}</p>
            <p>{root}e?url={url}&f={form}</p>
            """
        else:
            footer = "<p>Please enter the URL given under 'Subscribe to your timetable' on the Allocate+ homepage."
    elif url != "":
        footer = "Please enter a valid URL."
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
            <p>This tool will give you a new URL with correctly formatted class names.</p>
            <p>Simply enter in your Allocate+ calendar URL below, and choose what you want to display.</p>
            <form action="/">
                <label for="url">Enter URL:</label>
                <input type="text" id="url" name="url" value={url}><br>
                <label for="code">Display class code?</label>
                <input type="checkbox" id="ccode" name="ccode" value="1" {codechecked}><br>
                <label for="name">Display class name?</label>
                <input type="checkbox" id="cname" name="cname" value="1" {namechecked}><br>
                <label for="type">Display class type?</label>
                <input type="checkbox" id="ctype" name="ctype" value="1" {typechecked}><br>
                <label for="caps">Capitalise all words?</label>
                <input type="checkbox" id="caps" name="caps" value="1" {capschecked}><br>
                <input type="submit" value="Submit">
            </form>
            {footer}
        </body>
    """

@app.get("/e")
def read_item(url: str = None, f: str = None):
    url = "https://my-timetable.monash.edu/even/rest/calendar/ical/" + url

    f = int(f) if f is not None else 0
    try:
        content = rename_events(url, form=f)
    except Exception as e:
        return Response(content=e, media_type="text/plain")

    if content is None:
        return Response(content="File not found", media_type="text/plain")

    new_filename = "modified.ics"
    response = Response(content=content, media_type="text/calendar")
    response.headers["Content-Disposition"] = f"attachment; filename={new_filename}"
    return response