"""Concatenate src/*.html into one page.

publish.html  : page content only (the Artifact host wraps it in a document skeleton)
playbook.html : standalone file you can open directly in a browser
"""
import glob
import os

here = os.path.dirname(os.path.abspath(__file__))
parts = sorted(glob.glob(os.path.join(here, "src", "*.html")))
body = "".join(open(p, encoding="utf-8").read() for p in parts)

with open(os.path.join(here, "publish.html"), "w", encoding="utf-8") as f:
    f.write(body)

wrapper = (
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    "<style>:root{color-scheme:light}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}</style>\n"
    "</head>\n<body>\n"
)
with open(os.path.join(here, "playbook.html"), "w", encoding="utf-8") as f:
    f.write(wrapper + body + "\n</body>\n</html>\n")

print("parts:", len(parts))
for name in ("publish.html", "playbook.html"):
    p = os.path.join(here, name)
    print(name, os.path.getsize(p) // 1024, "KB")
