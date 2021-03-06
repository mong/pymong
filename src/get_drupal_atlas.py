#!/usr/bin/env python

import os
import re
import markdownify
from shutil import copy
import glob

atlas = {1:   ["no/barn", "Barnehelseatlas, 2011–2014", "2015-09-01", "Barnehelseatlas for Norge", "2"],
         39:  ["no/dagkir", "Dagkirurgi,  2011–2013", "2015-01-01", "Dagkirurgi i Norge 2011–2013", "1"],
         49:  ["no/nyfodt", "Nyfødtmedisin, 2009–2014", "2016-12-01", "Norsk nyfødtmedisinsk helseatlas", "3"],
         90:  ["no/eldre", "Eldrehelseatlas, 2013–2015", "2017-06-01", "Eldrehelseatlas for Norge", "4"],
         117: ["en/dagkir", "Day surgery atlas, 2011–2013", "2017-09-01", "Day surgery in Norway 2011 - 2013", "1"],
         118: ["en/barn", "Child Healthcare Atlas, 2011–2014", "2017-09-02", "Child healthcare atlas for Norway", "2"],
         120: ["en/nyfodt", "Neonatal Atlas, 2009–2014", "2017-09-03", "The Norwegian Neonatal Healthcare Atlas, 2009-2014", "3"],
         121: ["en/eldre", "Elderly Healthcare Atlas, 2013–2015", "2017-09-04", "Healthcare Atlas for the Elderly in Norway", "4"],
         123: ["no/kols", "Kols, 2013–2015", "2017-10-01", "Helseatlas kols", "5"],
         131: ["en/kols", "COPD healthcare atlas, 2013–2015", "2018-03-01", "COPD Healthcare Atlas", "5"],
         138: ["no/ortopedi", "Ortopedi, 2012–2016", "2018-12-01", "Helseatlas i ortopedi for Noreg", "7"],
         150: ["no/dagkir2", "Dagkirurgi, 2013–2017", "2018-11-01", "Dagkirurgi i Norge 2013–2017", "6"],
         154: ["en/dagkir2", "Day surgery atlas 2013–2017", "2018-12-01", "Day surgery in Norway 2013–2017", "6"],
         155: ["no/gyn", "Gynekologi, 2015–2017", "2019-01-01", "Helseatlas for gynekologi", "8"],
         157: ["no/fodsel", "Fødselshjelp, 2015–2017", "2019-04-01", "Helseatlas for fødselshjelp", "9"],
         158: ["en/gyn", "Gynaecology, 2015–2017", "2019-05-01", "Gynaecology Healthcare Atlas", "8"],
         178: ["en/fodsel", "Obstetrics 2015–2017", "2019-08-01", "Obstetrics Healthcare Atlas", "9"],
         184: ["en/ortopedi", "Orthopaedic, 2012-2016", "2019-08-01", "Orthopaedic Healthcare Atlas for Norway", "7"],
         259: ["no/psyk", "Psykisk helsevern og TSB, 2014-2018", "2020-06-01", "Helseatlas for psykisk helsevern og rusbehandling", "10"],
         260: ["no/kvalitet", "Kvalitet, 2017–2019", "2021-01-01", "Helseatlas for kvalitet", "11"],
         274: ["en/psyk", "Mental Healthcare 2014-2018", "2021-01-01", "Healthcare Atlas for Mental Healthcare and Substance Abuse Treatment", "10"],
         279: ["en/kvalitet", "Healthcare Quality Atlas", "2021-08-01", "Healthcare Quality Atlas", "11"],
         }

def map_hovedfunn_atlas(file_content):
  for line in file_content:
     if re.search("atlas-button atlas", line):
         # Get <num> out of the following line:
         # <a href="/atlas/<num>/details" class="atlas-button atlas">
         num = re.sub(r"\D", "", line)
         return(num)

def get_hovedfunn_title(file_content):
  for line in file_content:
     if re.search("page-title", line):
         # Get the line with id="page-title"
         return(line.strip())

def get_hovedfunn_content(file_content, img_path):
    # Get the main content from a hovedfunn page
    # Retun a md text string
    html_content = ""
    collecting = False
    mod_img_path = img_path.replace("output/", "/helseatlas/")
    for line in file_content:
        # Start collecting text from line with BEGIN OUTPUT ...
        if re.search("BEGIN OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = True
        # Stop collecting text after line with END OUTPUT ...
        if re.search("END OUTPUT from 'sites/all/themes/custom/helseatlas/templates/ds-1col", line):
            collecting = False
        if collecting:
            if re.search("media-element file-default", line):
                # Replace image line
                filename = line.split()[1].split("/")[-1].replace("\"", "")
                html_content = html_content + "![" + filename.split(".")[-2] + "](" + mod_img_path + "/" + filename + ")"
            elif re.search("element-invisible", line):
                pass
            else:
                # Remove year range in the beginning of each section
                test_string = re.sub("<div class=\"field-item even\">\d*-\d*</div>", "", line)
                test_string = re.sub("<div class=\"field-item even\">\d* - \d*</div>", "", test_string)
                html_content = html_content + test_string
    markdown = markdownify.markdownify(html_content, heading_style = "ATK")

    # clean up file
    markdown = (markdown
                .replace(".png) *", ".png)\n\n*")
                .replace(".png) Figur", ".png)\n\n*Figur")
                .replace("\n## Bakgrunn", "\n### Bakgrunn")
                .replace("\n## Background", "\n### Background")
                .replace("\n## Result", "\n### Result")
                .replace("\n## Kommentar", "\n### Kommentar")
                .replace("\n## Comments", "\n### Comments")
                .replace("  #", "#")
                .replace(".**", ".** ")
                .replace("\n## Utvikling fra", "\n### Utvikling fra")
                .replace("\n## Funn", "\n### Funn")
                .replace(".* Opptaksområdet har færre enn", ". \*Opptaksområdet har færre enn")
                .replace(". * Opptaksområdet har færre enn", ". \*Opptaksområdet har færre enn")
                .replace(". *Opptaksområdet har færre enn", ". \*Opptaksområdet har færre enn")
                .replace(". * opptaksområdet har færre enn", ". \*Opptaksområdet har færre enn")
                .replace(". *Referral area has fewer than", ". \*Referral area has fewer than")
                .replace(".* Referral area has fewer than", ". \*Referral area has fewer than")
                .replace(".*Referral area has fewer than", ". \*Referral area has fewer than")
                .replace("Figur 1: ", "")
                .replace("Figur 2: ", "")
                .replace("**Figur 1.**", "**Figur:**")
                .replace("**Figur 1**.", "**Figur:**")
                .replace("**Figur 2.**", "**Figur:**")
                .replace("**Figur 2**.", "**Figur:**")
                .replace("**Figur 3.**", "**Figur:**")
                .replace("**Figur 3**.", "**Figur:**")
                .replace("\n## \n", "\n")
                )

    return(markdown + "\n\n\n")

def get_figures(file_content, path):
    for line in file_content:
        if re.search("media-element file-default", line):
            filename = line.split()[1].split("//")[-1].replace("\"", "").replace("helseatlas.no/", "")
            copy(filename, path)

def get_file_content(filename):
    file = open(filename, "r")
    file_content = list(file.read().splitlines())
    file.close()
    return(file_content)

def get_hovedfunn_order(file_content):
    hovedfunn = []
    for line in file_content:
        if re.search("<a href=\"/hovedfunn", line):
            hovedfunn.append("hovedfunn/" + (line
            .replace("%C3%B8", "ø")
            .replace("%C3%A6", "æ")
            .replace("%C3%A5", "å")
            .replace("%C2%A0", "")
            .split(">")[4].split("/")[-1]
            .replace("\"", "")))
        if re.search("<a href=\"/en/hovedfunn", line):
            hovedfunn.append("en/hovedfunn/" + (line
            .split(">")[4].split("/")[-1]
            .replace("\"", "")))
    return(hovedfunn)

def get_hovedfunn_start(file_content):
    count = 0
    return_string = ""
    for line in file_content:
        if count == 1:
            return_string = return_string + line + "\n"
            if re.search("</div>", line):
               count = count + 1
        if re.search("<div class=\"pane-content\">", line):
            count = count + 1
    
    return(markdownify.markdownify(return_string.strip(), heading_style = "ATK"))

def create_md_heading(atlas_num, rapport):
    main_title = atlas[atlas_num][3]
    short_title = atlas[atlas_num][1]
    num = atlas[atlas_num][4]
    heading = '''---
num: {0}
mainTitle: {1}
shortTitle: {2}
pdfUrl: {3}
---

## Innhold

'''.format(num, main_title, short_title, rapport)

    return(heading)
    
def get_report(file_content, path):
    if not os.path.exists(path):
        os.makedirs(path)
    for line in file_content:
        if re.search("atlas-button report", line):
            try:
                filename = line.split("\"")[1].replace("https://helseatlas.no/", "")
                copy(filename, path)
            except:
                filename = str(line).split("\"")[11].replace("https://helseatlas.no/", "")
                copy(filename, path)
            only_name = filename.split("/")[-1]
            return(only_name)

def create_local_files(file_content, path = "output/files"):
    new_file_content = ""
    for line in file_content.split("\n"):
        if re.search("\/sites\/default\/files", line):
            try:
                filename = (line
                            .split("](")[1]
                            .replace("https://helseatlas.no/", "")
                            .replace("http://helseatlas.loc/", "")
                            .replace("http://helseatlas.no.loc/", "")
                            .replace("http://helseatlas.no/", "")
                            .replace("/sites/", "sites/")
                            .split(")")[0])
                copy(filename, path)
                only_name = filename.split("/")[-1]
                old_url = line.split("](")[1].split(")")[0]
                new_file_content = new_file_content + (line
                                                      .replace(old_url, "/helseatlas/files/" + only_name)) + "\n"

            except:
                pass
        elif re.search("download\?token", line):
            pass
        else:
            new_file_content = new_file_content + line + "\n"
    return(new_file_content)

if not os.path.exists("output/md/no"):
    os.makedirs("output/md/no")
if not os.path.exists("output/md/en"):
    os.makedirs("output/md/en")

for details in glob.glob("atlas/*/details"):
    atlas_num = int(details.split("/")[1])
    atlas_name = atlas[atlas_num][0]

    img_path = "output/img/" + atlas_name
    md_name = "output/md/" + atlas_name + ".md"
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    detailsfile_content = get_file_content(details)
    entries = get_hovedfunn_order(detailsfile_content)
    hovedfunn_start = get_hovedfunn_start(detailsfile_content)
    hovedfunn_start = create_local_files(hovedfunn_start)

    rapport_name = get_report(detailsfile_content, "output/files")
    md_heading = create_md_heading(atlas_num, "/helseatlas/files/" + rapport_name)

    md_file = open(md_name, "w")
    md_file.write(md_heading + hovedfunn_start)
    md_file.close()

    for entry in entries:
        try:
            file_content = get_file_content(entry)
            title_line = get_hovedfunn_title(file_content)
            hovedfunn = get_hovedfunn_content(file_content, img_path)
            hovedfunn = create_local_files(hovedfunn)

            md_file = open(md_name, "a")
            md_file.write(hovedfunn)
            md_file.close()

            get_figures(file_content, img_path)

        except:
            print("file " + entry + " not found!")
