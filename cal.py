import urllib.request
import tempfile
from fastapi import FastAPI, Response

app = FastAPI()

def rename_events(url):
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
            lines[i] = f"SUMMARY:{classcode} - {classtype}"

    return "".join(lines)

@app.get("/")
def read_root():
    return {"message": "Hello World!"}

@app.get("/{init_url:path}")
def read_item(init_url = None):
    content = rename_events(init_url)
    if content is None:
        return Response(content="File not found", media_type="text/plain")

    new_filename = "modified.ics"
    response = Response(content=content, media_type="text/calendar")
    response.headers["Content-Disposition"] = f"attachment; filename={new_filename}"
    return response