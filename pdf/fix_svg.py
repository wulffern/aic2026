#!/usr/bin/env python3

import re
import sys
import os
fname = sys.argv[1]

from sys import platform


def imgConvert(ftype,fotype,path):
    fopath = "media/"+ os.path.basename(path).replace(ftype,fotype)
    if(not os.path.exists(fopath)):
        #- For SVG, prefer rsvg-convert: ImageMagick's own SVG parser fails
        #  on <image> elements with embedded base64 data, which the exported
        #  schematic screenshots use. Those figures then silently miss from
        #  the epub, whose build needs the .png variants made here.
        cmds = []
        if(ftype == ".svg"):
            fmt = fotype.strip(".")
            cmds.append(f"rsvg-convert --format={fmt} --dpi-x=100 --dpi-y=100 -o {fopath} {path}")
        #- exclude-chunks=date,time: ImageMagick otherwise stamps
        #  date:create/date:modify into every PNG, so an unchanged source
        #  converted on two CI runs produced different bytes — which
        #  defeated the standalone PDF cache (py/pdfcache.py).
        magick = "magick" if platform == "darwin" else "convert"
        cmds.append(f"{magick} -density 100 {path} -define png:exclude-chunks=date,time {fopath}")
        for cmd in cmds:
            if(os.system(cmd) == 0 and os.path.exists(fopath)):
                break
            print(f"fix_svg: '{cmd}' failed for {path}")
    return fopath


def toPng(ftype,path):
    return imgConvert(ftype,".png",path)

def toPdf(ftype,path):
    return imgConvert(ftype,".pdf",path)

def getPath(line):

    m = re.findall(r"{([^{}]+)}",line)
    path = m[0]

    return path

tmplt = r"""
{
\centering
\includegraphics[width=\myfigwidth,height=\myfigheight,keepaspectratio]{#path#}
}
"""

#tmplt = r"""
#\pandocbounded{\includegraphics[width=\myfigwidth]{#path#}}
#"""

foname = fname.replace(".latex","_fiximg.tex")
foname_png = fname.replace(".latex","_fiximg_png.tex")
with open(fname) as fi:
    with open(foname,"w") as fo:
        with open(foname_png,"w") as fo_png:
            for line in fi:

                #- Fix titles for kao
                #if(re.search(r"^\s*\\chapter",line)):
                #    nline = """\setchapterstyle{kao}
#\setchapterpreamble[u]{\margintoc}
#""" + line
 #                   fo.write(nline)
 #                   fo_png.write(line)
 #                   continue

                #if(re.search(r"\\begin{longtable}",line)):


                #if(re.search(r"\\end{longtable}",line)):
                #    line = r"\end{tblr}" + "\n"

                #if(re.search(r"\\(toprule|bottomrule|midrule|endhead|endlastfoot)",line)):
                #    line = ""

                #if(re.search(r"\s*>{\\raggedright",line)):
                #    line = ""


                #- Index every section-level heading with a plain-text
                #  title, so the book's index points at real pages.
                #  Filtered: generic structural headings (Summary,
                #  Discussion, ...) and numbered memo items say nothing
                #  as index entries, and headings differing only in
                #  capitalization are merged by sorting on a lowercase
                #  key and displaying in sentence case.
                hm = re.match(r"\\(chapter|section|subsection)\{([^{}\\$]+)\}", line)
                if hm:
                    term = hm.group(2).strip()
                    stop = {"summary", "discussion", "conclusion", "advice", "but",
                            "comparison", "appendix", "demo", "decisions",
                            "choosing", "checklist", "contacts", "career",
                            "documentation", "goal", "goal for today",
                            "my goal", "who", "why", "syllabus", "software",
                            "introduction", "background",
                            "would you like to know more?"}
                    ok = (len(term) > 2
                          and re.match(r"[A-Za-z]", term)
                          and not re.match(r"\d", term)
                          and term.lower() not in stop)
                    if ok:
                        words = term.split()
                        if (len(words) > 1 and
                                all(w[0].isupper() and w[1:].islower()
                                    for w in words if w.isalpha())):
                            #- Sentence-case plain Title Case headings so
                            #  "Band Diagrams" and "Band diagrams" merge;
                            #  terms with acronyms (Bluetooth LE, SAR ADC)
                            #  are left alone
                            term = term[0].upper() + term[1:].lower()
                        line = (line.rstrip("\n") + "\\index{"
                                + term.lower() + "@" + term + "}\n")

                #- Pandoc sometimes uses includesvg instead of includegraphics
                line = line.replace("includesvg","includegraphics")
                if(re.search(r"includegraphics(\[[^\]]+\])?{",line)):
                    path = getPath(line)
                    fopath = path
                    fopath_png = path
                    if(path.endswith(".svg")):
                        fopath = toPdf(".svg",path)
                        fopath_png = toPng(".svg",path)
                        pass
                    elif(path.endswith(".gif")):
                        fopath = toPng(".gif",path)
                        fopath_png = fopath
                        pass
                    elif(path.endswith(".pdf")):
                        fopath_png = toPng(".pdf",path)
                        pass
                    fo.write(tmplt.replace("#path#",fopath))
                    fo_png.write(tmplt.replace("#path#",fopath_png))
                else:
                    fo.write(line)
                    fo_png.write(line)
