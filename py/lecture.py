#!/usr/bin/env python3

import re
import os
import click
from sys import platform
import shutil
import urllib.parse
import hashlib

aic_version = "aicXX"

with open("version") as fi:
    aic_version = fi.read().strip()

year = aic_version.replace("aic","")

class Bibtex(dict):

    def __init__(self,filename):
        self.filename = filename

        self.counter = list()
        self.counter.append(0)
        self.referenced = dict()
        self._read()


    def _parse(self,buffer):

        buffer = buffer.strip("}").strip()
        key = ""
        ignore = False
        collect = False
        token = ""
        name = ""
        for c in buffer:
            #if(c == '}' and not ignore):
            #    collect = False
            if(collect):
                if(c == "=" and not ignore):
                    key = token.strip()
                    token = ""
                    continue
                elif(c == "\"" or c == "{" or c == "}"):
                    ignore = not ignore
                elif(c == "," and not ignore):
                    if(key == ""):
                        name = token.strip()
                        self[name] = dict()
                    else:
                        self[name][key] = token.replace("\"","").replace("{","").replace("}","").strip()
                        pass
                    token = ""
                    key = ""
                    continue

            if(re.search(r'^\s*\@[^{]+{',token) and not ignore):
                collect = True
                token = ""
                name = ""
                key = ""

            token += c



        if(name == ""):
            print(buffer)
        else:
            self[name][key] = token.replace("\"","").replace("{","").replace("}","").strip()

        #print("\ndata = ",name, data, "\n\n")



    def _read(self):

        with open(self.filename) as fi:
            item = False
            buffer = ""
            for line in fi:

                #if(re.search(r"^\@",line)):
                #    item = True
                #if(item):
                #    line = re.sub(r"\s+"," ",line)
                #    buffer += line.strip() + " "

                #if(re.search(r"}\s*;?\s*$",line)):

                if(re.search(r"^\@[^\s]+\{",line)):
                    item = True
                    self._parse(buffer)
                    buffer = ""
                if(item):
                    line = re.sub(r"\s+"," ",line)
                    buffer += line.strip() + " "
            self._parse(buffer)

    def addFootNote(self,nr):
        self.counter.append(int(nr))

    def sort(self):
        self.counter = sorted(self.counter)

    def toMarkdownCite(self,key):


        if("cite_nr" not in self[key]):
            self[key]["cite_nr"] = int(self.counter[-1]) + 1
            self.counter.append(self[key]["cite_nr"])


        nr = self[key]["cite_nr"]

        if(key not in self.referenced):
            self.referenced[key] = 0

        self.referenced[key] += 1


        return f"[^{nr}]"


    def toMarkdownRef(self):

        ss = ""
        for key in self.referenced:
            item = self[key]

            ss += "[^" + str(item["cite_nr"]) + "]: "

            if("author" in item):
                ss += item["author"] + ","
            if("title" in item):
                ss += " _" + item["title"] + "_ "
            if("year" in item):
                ss += " " + item["year"] + " "
            if("url" in item):
                ss += "<" + item["url"] + ">"
            if("doi" in item):
                ss += "<https://doi.org/" + item["doi"] + ">"

            ss += "\n"

        return ss



class Image():

    def __init__(self,imgsrc,options):
        self.src = imgsrc
        self.orgsrc = imgsrc
        self.options = options
        self.directory = options["dir"]
        self.skip = False
        self.isUrl = False
        self.abstmp = os.path.abspath(os.path.normpath(options["dir"] +  "/../pdf/media")) + "/"

        if(not os.path.exists(self.abstmp)):
            os.makedirs(self.abstmp)


        if("/ip/" in self.src and "allowIP" not in self.options):
            self.skip = True

        if(re.search(r"\s*https?://",self.src)):
            self.isUrl = True


        if(not self.skip and ".pdf" in self.src and "latex" not in self.options):
            #- I've changed to svg, hopefully better images
            svg = self.src.replace(".pdf",".svg")
            if(not os.path.exists(os.path.join(self.directory,svg))):
                cmd = f"cd {self.directory}; pdftocairo -svg {self.src} {svg}"
                os.system(cmd)
            self.src = svg

        if(self.isUrl and "downloadImage" in self.options):
#            print(self.src)
            url = self.src
            arr = url.split("?")
            end = arr[0].split(".")[-1]
            #print(self.src)
            self.src = self.abstmp +  hashlib.sha256(os.path.basename(self.src).encode()).hexdigest() + "." + end
            #print(self.src)
            if(not os.path.exists(self.src)):
                os.system(f"cd {self.abstmp}; wget {url} -O {self.src}")


        self.filesrc = os.path.basename(self.src)
        self.dirsrc  = os.path.dirname(self.src)


    def copy(self):

        if(self.isUrl and not ("downloadImage" in self.options) ):
            return
            
        if(self.skip):
            return

        if("jekyll" in self.options):
            shutil.copyfile(os.path.join(self.options["dir"],self.src), "docs/assets/media/" + self.filesrc)
        elif("latex" in self.options):
            os.makedirs(self.options["latex"] + "media/",exist_ok=True)
            try:
                #print(self.src)
                if(self.src.startswith("../")):
                    shutil.copyfile(os.path.join(self.options["dir"],self.src),  self.options["latex"] + "media/" + self.filesrc)
                    if("pdf" in self.src):
                        shutil.copyfile(os.path.join(self.options["dir"],self.src.replace(".pdf",".svg")),  self.options["latex"] + "media/" + self.filesrc.replace(".pdf",".svg") )
                    if("svg" in self.src):
                         shutil.copyfile(os.path.join(self.options["dir"],self.src.replace(".svg",".pdf")),  self.options["latex"] + "media/" + self.filesrc.replace(".svg",".pdf") )
            except Exception as e:
                print("Image.copy: ",e)
    def __str__(self):

        if(self.skip):
            return f"> image {self.src} removed"

        if("jekyll" in self.options):
            path = self.options["jekyll"] + "assets/media/" + self.filesrc

            return f"![]({path})" + "{: width=\"700\" }\n"
        elif("latex" in self.options):

            if(self.dirsrc == self.abstmp):
                path = self.abstmp + self.filesrc
            else:
                path = "media/" + self.filesrc
            #print(path)

            return f"<!-- {self.orgsrc} -->\n\n![]({path})\n\n"

        return self.src

class Lecture():
    
    def __init__(self,filename,options):
        self.filename = filename
        self.title = ""
        self.options = options
        self.date = None
        self.images = list()

        self.filters = {
            r"^\s*---\s*$" : "",
            r"\[.column\]" : "",
            r"\[\.background.*\]" : "",
            r"\[\.text.*\]" : "",
            r"\[\.table  *\]" : "",
            r"\#\s*\[\s*fit\s*\]" : "# ",
            r"\*\*Q:\*\*" : "",
            r"^[.table.*]$": "",
            r"#(.*) Thanks!" : ""
        }

        self.bibtex = Bibtex("pdf/aic.bib")

        self._read()
        if("Latex" not in str(self.__class__)):
            self._replaceCites()

    def copyAssets(self, images_file="images.txt"):
        with open(images_file,"a") as fo:
            for image in self.images:
                if(not image.skip and not image.isUrl):
                    fo.write(image.orgsrc + "\n")
                    fo.write(image.src +"\n")
                image.copy()

    def _replaceCites(self):

        for line in self.buffer:
            m = re.search(r"\s+\[\^(\d+)\]",line)
            if(m):
                nr = m.groups()[0]
                mr = self.bibtex.addFootNote(nr)

        #- Sort so the last footnote is correct
        self.bibtex.sort()

        for i in range(0,len(self.buffer)):
            line = self.buffer[i]
            #- Find references
            m = re.search(r"\s+\[\@([^\]]+)\]\s+",line)
            if(m):
                for key in m.groups():
                    md = self.bibtex.toMarkdownCite(key)
                    self.buffer[i] = line.replace(f"[@{key}]",md)

        self.buffer.append(self.bibtex.toMarkdownRef())

    def _read(self):

        self.buffer = list()
        first = True
        self.output = False
        self.skipslide = False
        self.removeComment = False

        with open(self.filename) as fi:
            for line in fi:

                if(first and "date:" in line):
                    (k,v) = line.split(" ")
                    self.date = v.strip()

                if(first and re.search(r"^\s*$",line)):
                    first = False
                    self.output = True


                line = self._readPan(line)

                if(line):
                    line = self._filterLine(line)
                    line = self._convertImage(line)


                if(line is not None and self.output):
                    self.buffer.append(line)



    def _readPan(self,line):

        #- Check pan tags
        m = re.search(r"<!--pan_([^:]+):(.*)$",line)
        if(m):
            key = m.groups()[0]
            val = m.groups()[1]


            if(key == "title"):
                self.title = val.replace("-->","")

            elif(key == "skip"):
                self.skipslide = True
                self.output = False

            elif(key == "doc"):
                 # Start statemachine
                # 1. Skip this line, it should be <!--pan_doc:
                # 2. Enable removing -->
                # 3. When -->, assume that's the end of the pan_doc, and go back to normal
                self.removeComment = True
            else:
                print(f"Unknown key {key}")

            return None

        #- Go back to normal mode
        if(self.removeComment and re.search(r"-->",line)):
            self.removeComment = False
            return None

        if(self.skipslide and re.search(r"^\s*---\s*$",line)):
            self.output = True
        return line

    def _convertImage(self,line):
        if(re.search("^<!--",line)):
            return line

        m = re.search(r"\!\[([^\]]*)\]\(([^\)]+)\)",line)

        if(m):
            imgsrc = m.groups()[1]

            if(not "downloadImage" in self.options):
                if(re.search(r"\s*https://",imgsrc)):
                    return f"![]({imgsrc})"

            i = Image(imgsrc,self.options)
            self.images.append(i)
            line = str(i)
        return line


    def _filterLine(self,line):
        for r,s in self.filters.items():
            line = re.sub(r,s,line)
        return line

    def __str__(self):

        ss = ""

        if("jekyll" in self.options):

            furl = f"https://github.com/wulffern/{aic_version}/tree/main/" + self.filename
            slides = ""
            if("lectures" in self.filename ):
                #slides = "[Slides](" +  self.options["jekyll"] + self.filename.replace("lectures","assets/slides").replace(".md",".pdf") +")"
                slides = " [PDF](" +  self.options["jekyll"] + self.filename.replace("lectures","assets/").replace(".md",".pdf") +")"

            ss += f"""---
layout: post
title: {self.title}
math: true
permalink: {self.title.strip().lower().replace(" ","_")}
---

> If you find an error in what I've made, then [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo), fix [{self.filename}]({furl}), [commit](https://git-scm.com/docs/git-commit), [push](https://git-scm.com/docs/git-push) and [create a pull request](https://docs.github.com/en/desktop/contributing-and-collaborating-using-github-desktop/working-with-your-remote-repository-on-github-or-github-enterprise/creating-an-issue-or-pull-request). That way, we use the global brain power most efficiently, and avoid multiple humans spending time on discovering the same error.

{slides}


""" + """



* TOC
{:toc }

"""

        for l in self.buffer:
            ss += l
        return ss

class Presentation(Lecture):

    def __init__(self,filename,options):
        self.filename = filename
        self.title = filename.replace(".md","")
        self.options = options

        self.images = list()

        self.filters = {
            r"\[\.background.*\]" : "",
            r"\[\.text.*\]" : "",
            r"\[\.table  *\]" : "",
            r"\#\s*\[\s*fit\s*\]" : "## ",
            r"^[.table.*]$": "",
            r"\!\[[^\]]+\]" : "![]",
            r"^# ":"## ",
            r"\[.column\]" : "",
            #"^---":"#",

        }

        self._read()

    def _read(self):

        self.buffer = list()
        first = True
        self.output = False
        self.skipslide = False
        self.removeComment = False

        with open(self.filename) as fi:
            for line in fi:

                if(first and re.search(r"^\s*$",line)):
                    first = False
                    self.output = True

                key = ""
                val = ""
                m = re.search(r"<!--pan_([^:]+):(.*)$",line)
                if(m):
                    key = m.groups()[0]
                    val = m.groups()[1]


                if(key == "title"):
                    self.title = val.replace("-->","")

                if(re.search(r"^<!--",line)):
                    self.output = False

                line = self._filterLine(line)
                line = self._convertImage(line)

                if(line is not None and self.output):
                    self.buffer.append(line)

                if(re.search(r"-->",line)):
                    self.output = True

    def __str__(self):

        ss = ""

        ss += f"""---
title: {self.title}
output:
  slidy_presentation:
    footer: "Copyright (c) {year}, Carsten Wulff"
    fig_width: 800
---

""" + """




"""
        for l in self.buffer:
            ss += l
        return ss

class Latex(Lecture):

    def __init__(self,filename,options):
        self.filename = filename
        self.title = filename.replace(".md","")
        self.options = options

        self.images = list()

        self.filters = {
             r"^\s*---\s*$" : "",
            r"\[.column\]" : "",
            r"\[\.background.*\]" : "",
            r"\[\.text.*\]" : "",
            r"\[\.table  *\]" : "",
            r"\#\s*\[\s*fit\s*\]" : "# ",
            r"\#\#\s*\[\s*fit\s*\]" : "## ",
            #"^## \*\*Q:\*\*.*$" : "",
            r"^[.table.*]$": "",
            r"^\* TOC":"",
            r"^{:toc }":"",
            r"\*\*Q:\*\*" : "",
            r"#(.*) Thanks!" : "",
            r"<sub>" :"<small><sub>_",
            r"</sub>" :"_</sub></small>"
            #"^---":"#",
        }

        self._read()



    def __str__(self):

        ss = ""

        ss += f"""

""" + """




"""
        for l in self.buffer:
            ss += l
        return ss


    

@click.group()
def cli():
    """
    Convert a lecture to something
    """
    pass

@cli.command()
@click.argument("filename")
@click.option("--root",default=f"/{aic_version}/",help="Root of jekyll site")
@click.option("--date",default=None,help="Date to use")
@click.option("--images-file",default="images.txt",help="File to write image list to")
def post(filename,root,date,images_file):
    options = dict()
    options["jekyll"] = root
    options["dir"] = os.path.dirname(filename)

    os.makedirs("docs/assets/media/", exist_ok=True)
    os.makedirs("docs/_posts", exist_ok=True)

    print(f"Info: {filename}")
    #- Post
    l = Lecture(filename,options=options)

    if(date is None and l.date is not None):
        date = l.date
    else:
        raise Exception(f"I need a date, either in the frontmatter, or the option for {filename}")

    l.copyAssets(images_file=images_file)
    fname = "docs/_posts/" + date +"-"+ l.title.strip().replace(" ","-") + ".markdown"

    with open(fname,"w") as fo:
        fo.write(str(l))



    


@cli.command()
@click.argument("filename")
@click.option("--root",default="pdf/",help="output root")
@click.option("--no-append",is_flag=True,default=False,help="Skip appending to shared files (for parallel builds)")
def latex(filename,root,no_append):
    options = dict()
    options["latex"] = root
    options["downloadImage"] = True
    options["allowIP"] = True
    options["dir"] = os.path.dirname(filename)

    basename = os.path.basename(filename).replace(".md","")

    p = Latex(filename,options)
    p.copyAssets()


    fname = root + os.path.sep + p.title.strip().replace(" ","_").lower() + ".md"
    with open(fname,"w") as fo:
        fo.write(str(p))

    foname_fixed = p.title.strip().replace(" ","_").lower()+"_fiximg.tex"
    foname = os.path.basename(filename).replace(".md",".tex")

    title = p.title.strip()
    title = re.sub(r"Lecture\s+[\d|X]*\s+-\s+","",title)

    chapter_text = (r"\setchapterstyle{kao}" + "\n"
        + r"\setchapterpreamble[u]{\margintoc}" + "\n"
        + r"\chapter{" + title + "}" + "\n"
        + r"\input{" + foname_fixed + "}" + "\n\n")

    download_text = f"- [{title}](/{aic_version}/assets/{basename}.pdf)\n"

    with open(f"pdf/{basename}_chapter.inc","w") as fo:
        fo.write(chapter_text)
    with open(f"pdf/{basename}_download.inc","w") as fo:
        fo.write(download_text)

    if not no_append:
        with open("pdf/chapters.tex","a") as fo:
            fo.write(chapter_text)
        with open("docs/downloads.md","a") as fo:
            fo.write(download_text)

    with open("pdf/version_short.tex") as fi:
        version = fi.read()

    with open("pdf/short_tmplt.tex") as fi:
        buff = fi.read()
        with open("pdf/" + foname,"w") as fo:
            fo.write(buff.replace("__title__",title).replace("__file__",foname_fixed).replace("__version__",version))

    flatex = fname.replace(".md",".latex")
    cmd = f"pandoc --citeproc --bibliography=pdf/aic.bib --csl=pdf/ieee-with-url.csl  -o {flatex} {fname}  "
    os.system(cmd)
    #cmd = f"pandoc -s --citeproc --bibliography=pdf/aic.bib --csl=pdf/ieee-with-url.csl  -o {flatex}_standalone.tex {fname}  "
    #os.system(cmd)




if __name__ == "__main__":
    cli()
