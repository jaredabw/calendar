import urllib.request
import tempfile

url = "https://my-timetable.monash.edu/even/rest/calendar/ical/50f96f6b-7019-45ab-accc-1d81eb2814b9"

output = "output.ics"

def rename_events(url):
    tmp = tempfile.NamedTemporaryFile().name
    urllib.request.urlretrieve(url, tmp)
    with open(tmp, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("SUMMARY:"):
            classname, classtype = line.split("\\, ")
            classtype = classtype.rstrip().removesuffix("-JTU") + "\n"
            classname = classname.rstrip().removeprefix("SUMMARY:") + "\n"

            classcode = lines[i+2].removeprefix("DESCRIPTION:").split("_")[0]
            lines[i] = f"SUMMARY:{classcode} - {classtype}"

    with open(output, "w") as f:
        f.writelines(lines)

rename_events(url)