# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Mash.
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# =============================================================================
# Imports ----------------------------------------------------------------------
#--Standard
import re
import os
import sys

# ------------------------------------------------------------------------------
class Callables:
    """A singleton set of objects (typically functions or class instances) that
    can be called as functions from the command line.

    Functions are called with their arguments, while object instances are called
    with their method and then their functions. E.g.:
    * bish afunction arg1 arg2 arg3
    * bish anInstance.aMethod arg1 arg2 arg3"""

    # --Ctor
    def __init__(self):
        """Initialization."""
        self.callObjs = {}

    # --Add a callable
    def add(self, callObj, callKey=None):
        """Add a callable object.

        callObj:
            A function or class instance.
        callKey:
            Name by which the object will be accessed from the command line.
            If callKey is not defined, then callObj.__name__ is used."""
        callKey = callKey or callObj.__name__
        self.callObjs[callKey] = callObj

    # --Help
    def printHelp(self, callKey):
        """Print help for specified callKey."""
        print(help(self.callObjs[callKey]))

    # --Main
    def main(self):
        callObjs = self.callObjs
        # --Call key, tail
        # This makes no sense since if there was a dot it would be in the filename
        # callParts = string.split(sys.argv[1], '.', 1)
        callKey = sys.argv[1]
        # This makes no sense because it doesn't seem to capture what is after genHtml
        # The intent here is to use callObj.__name__ but there isn't a tail
        # callTail = (len(callParts) > 1 and callParts[1])
        # --Help request?
        if callKey == '-h':
            self.printHelp(self)
            return
        # --Not have key?
        if callKey not in callObjs:
            print("Unknown function/object: {}".format(callKey))
            return
        # --Callable
        callObj = callObjs[callKey]
        if isinstance(callObj, str):
            callObj = eval(callObj)
        # The intent here is to use callObj.__name__ but there isn't a tail
        # if callTail:
        #    callObj = eval('callObj.' + callTail)
        # --Args
        args = sys.argv[2:]
        # --Keywords?
        keywords = {}
        argDex = 0
        reKeyArg = re.compile(r'^\-(\D\w+)')
        reKeyBool = re.compile(r'^\+(\D\w+)')
        while argDex < len(args):
            arg = args[argDex]
            if reKeyArg.match(arg):
                keyword = reKeyArg.match(arg).group(1)
                value = args[argDex + 1]
                keywords[keyword] = value
                del args[argDex:argDex + 2]
            elif reKeyBool.match(arg):
                keyword = reKeyBool.match(arg).group(1)
                keywords[keyword] = 1
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        callObj(*args, **keywords)


# --Callables Singleton
callables = Callables()


def mainFunction(func):
    """A function for adding functions to callables."""
    callables.add(func)
    return func


# Wrye Text ===================================================================
"""This section of the module provides a single function for converting
wtxt text files to html files.

Headings:
= XXXX >> H1 "XXX"
== XXXX >> H2 "XXX"
=== XXXX >> H3 "XXX"
==== XXXX >> H4 "XXX"
Notes:
* These must start at first character of line.
* The XXX text is compressed to form an anchor. E.g == Foo Bar gets anchored as" FooBar".
* If the line has trailing ='s, they are discarded. This is useful for making
  text version of level 1 and 2 headings more readable.

Bullet Lists:
* Level 1
  * Level 2
    * Level 3
Notes:
* These must start at first character of line.
* Recognized bullet characters are: - ! ? . + * o The dot (.) produces an invisible
  bullet, and the * produces a bullet character.

Styles:
  __Text__
  ~~Italic~~
  **BoldItalic**
Notes:
* These can be anywhere on line, and effects can continue across lines.

Links:
 [[file]] produces <a href=file>file</a>
 [[file|text]] produces <a href=file>text</a>

Contents
{{CONTENTS=NN}} Where NN is the desired depth of contents (1 for single level,
2 for two levels, etc.).
"""

htmlHead = """
<!DOCTYPE html>
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=iso-8859-1">
<TITLE>%s</TITLE>
<STYLE>%s</STYLE>
</HEAD>
<BODY>
    <section class="page-header">
      <h1 class="project-name">%s</h1>
      <h2 class="project-tagline">Collection of Wrye Bash history and information</h2>
    </section>
<SECTION  class="main-content">
<DIV>
"""
defaultCss = """
:root {
  --cayman-header-heading: rgb(255, 255, 255);
  --cayman-header-background: rgb(21, 153, 87);
  --cayman-header-background-secondary: rgb(21, 87, 153);
  --cayman-section-headings: rgb(21, 153, 87);
  --cayman-body-text: rgb(96, 108, 113);
  --cayman-body-href: rgb(30, 107, 184);
  --cayman-blockquote-text: rgb(129, 145, 152);
  --cayman-code-background: rgb(243, 246, 250);
  --cayman-code-text: rgb(86, 116, 130);
  --cayman-border: rgb(220, 230, 240);
  --cayman-table-border-color: rgb(233, 235, 236);
  --cayman-hr-border: rgb(239, 240, 241);
  --body-text: rgb(149, 157, 165);
  --body-background: rgb(36, 41, 46);
  --code-background: rgb(29, 33, 37);
  --header1-text: rgb(225, 228, 232);
  --header2-text: rgb(223, 226, 229);
  --header3-text: rgb(216, 220, 225);
  --header4-text: rgb(209, 213, 218);
  --header5-text: rgb(202, 207, 211);
  --header6-text: rgb(174, 182, 190);
  --header-border: rgb(100, 109, 119);
  --header1-background: rgb(79, 90, 100);
  --header2-background: rgb(81, 88, 97);
  --header3-background: rgb(61, 69, 77);
  --header4-background: rgb(58, 67, 75);
  --header5-background: rgb(47, 54, 60);
  --header6-background: rgb(40, 46, 52);
  --toc-header-text: var(--cayman-header-background);
  --blockquote-grey: rgb(33, 33, 33);
  --black-text: rgb(0, 0, 0);
  --blue-text: rgb(33, 136, 255);
  --brown-text: rgb(152, 112, 16);
  --cyan-text: rgb(41, 208, 208);
  --ltgray-text: rgb(209, 210, 212);
  --gray-text: rgb(181, 181, 181);
  --dkgray-text: rgb(87, 87, 87);
  --green-text: rgb(21, 153, 87);
  --ltblue-text: rgb(157, 175, 255);
  --ltgreen-text: rgb(129, 197, 122);
  --orange-text: rgb(218, 119, 62);
  --pink-text: rgb(255, 205, 243);
  --purple-text: rgb(209, 188, 249);
  --red-text: rgb(207, 52, 50);
  --tan-text: rgb(233, 222, 187);
  --white-text: rgb(255, 255, 255);
  --yellow-text: rgb(244, 203, 53);
  --old-red-text: rgb(224, 88, 88);
  --darkred-text: rgb(214, 24, 0);
  --ltred-text: rgb(211, 47, 47);
}

.page-header {
  color: var(--white-text);
  text-align: center;
  background-color: var(--cayman-header-background);
  background-image: linear-gradient(120deg, var(--cayman-header-background-secondary), var(--cayman-header-background));
  padding: 3rem 4rem;
}

.gridhead1 { grid-area: padding1; }
.gridhead2 { grid-area: image; }
.gridhead3 { grid-area: header; }
.gridhead4 { grid-area: padding2; }
.gridhead5 { grid-area: buttons; }
.toc1 { grid-area: lefttoc; }
.toc2 { grid-area: righttoc; }
.grid-header { display: grid; color: var(--cayman-header-heading); background-color: var(--cayman-header-background); background-image: linear-gradient(120deg, var(--cayman-header-background-secondary), var(--cayman-header-background)); }
.grid-header div.gridhead2 { text-align: right; }
.grid-header div.gridhead3 { text-align: left; }
.grid-header div.gridhead5 { text-align: center; }
@media screen and (min-width: 1900px) { .grid-header { grid-template-areas: 'padding1 image header padding2' 'buttons buttons buttons buttons'; } }
@media screen and (min-width: 1580px) and (max-width: 1900px) { .grid-header { grid-template-areas: 'padding1 image header padding2' 'buttons buttons buttons buttons'; } }
@media screen and (min-width: 1260px) and (max-width: 1580px) { .grid-header { grid-template-areas: 'padding1 image header padding2' 'buttons buttons buttons buttons'; } }
@media screen and (min-width: 780px) and (max-width: 1260px) { .grid-header { grid-template-areas: 'padding1 image header padding2' 'buttons buttons buttons buttons'; } }
@media screen and (max-width: 780px) { .grid-header { grid-template-areas: 'padding1' 'image' 'header' 'padding2' 'buttons'; }
  .grid-header div.gridhead2 { text-align: center; }
  .grid-header div.gridhead3 { text-align: center; }
  .grid-header div.gridhead5 { text-align: center; } }
.grid-toc { display: grid; }
@media screen and (min-width: 1900px) { .grid-toc { grid-template-areas: 'lefttoc righttoc'; } }
@media screen and (min-width: 1580px) and (max-width: 1900px) { .grid-toc { grid-template-areas: 'lefttoc righttoc'; } }
@media screen and (min-width: 1260px) and (max-width: 1580px) { .grid-toc { grid-template-areas: 'lefttoc righttoc'; } }
@media screen and (min-width: 780px) and (max-width: 1260px) { .grid-toc { grid-template-areas: 'lefttoc righttoc'; } }
@media screen and (max-width: 780px) { .grid-toc { grid-template-areas: 'lefttoc' 'righttoc'; } }
.grid-toc div { background: var(--body-background); }

.project-tagline { margin-bottom: 2rem; font-weight: normal; opacity: 0.7; }
.project-name { margin-top: 0; margin-bottom: 0.1rem; }
html * { -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; }
tr:nth-child(odd) { background: var(--header1-background); }
tr:nth-child(even) { background: var(--header2-background); }
tr:hover { background-color: var(--code-background); }

* { box-sizing: border-box; }
body { margin: 0; }
body { padding: 0; font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; line-height: 1.5; color: var(--body-text); background: var(--body-background); }

h1 { font-size: 2.0rem; margin: 1em 0; }
h2 { font-size: 1.75rem; margin: 1em 0; }
h3 { font-size: 1.5rem; margin: 1em 0; }
h4 { font-size: 1.25rem; margin: 1em 0; }
h5 { font-size: 1.0rem; margin: 1em 0; }
h6 { font-size: 0.75rem; margin: 1em 0; }

.main-content { word-wrap: break-word; }
.main-content :first-child { margin-top: 0; }

.main-content code { padding: 0.13rem 0.25rem; font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 0.9rem; color: var(--purple-text); background-color: var(--code-background); border-radius: 0.3rem; }
.main-content pre { padding: 0.8rem; margin: 0.25rem 0.75rem 0.25rem 0.75rem; font: 1rem Consolas, "Liberation Mono", Menlo, Courier, monospace; color: var(--purple-text); word-wrap: normal; background-color: var(--code-background); border: solid 1px var(--cayman-border); border-radius: 0.3rem; }
.main-content pre > code { padding: 0; margin: 0; font-size: 0.9rem; color: var(--purple-text); word-break: normal; white-space: pre; background: transparent; border: 0; }
.main-content .highlight { margin-bottom: 0.75rem; }
.main-content .highlight pre { margin-bottom: 0; word-break: normal; }
.main-content .highlight pre, .main-content pre { padding: 0.75rem; overflow: auto; font-size: 0.9rem; line-height: 1.45; border-radius: 0.3rem; -webkit-overflow-scrolling: touch; }
.main-content pre code, .main-content pre tt { display: inline; max-width: initial; padding: 0; margin: 0; overflow: initial; line-height: inherit; word-wrap: normal; background-color: transparent; border: 0; }
.main-content pre code:before, .main-content pre code:after, .main-content pre tt:before, .main-content pre tt:after { content: normal; }
.main-content ul, .main-content ol { margin-top: 0; }

.main-content table { display: block; width: 100%; overflow: auto; word-break: normal; word-break: keep-all; -webkit-overflow-scrolling: touch; }
.main-content table th { font-weight: bold; background-color: var(--header1-border); }
.main-content table th, .main-content table td { padding: 0.25rem 0.75rem; border: 1px solid var(--header1-border); }

.main-content table { display: block; width: 100%; overflow: auto; word-break: normal; word-break: keep-all; -webkit-overflow-scrolling: touch; }
.main-content table th { font-weight: bold; background-color: var(--header1-border); }
.main-content table th, .main-content table td { padding: 0.5rem 1rem; border: 1px solid var(--header1-border); }

.main-content dl { padding: 0; }
.main-content dl dt { padding: 0; margin-top: 0.75rem; font-size: 1rem; font-weight: bold; }
.main-content dl dd { padding: 0; margin-bottom: 0.75rem; }

.main-content hr { height: 0.13; padding: 0; margin: 0.75rem 0; background-color: var(--cayman-hr-border); border: 0; }

.main-content h1, .main-content h2, .main-content h3, .main-content h4, .main-content h5, .main-content h6 { margin: 0.75rem; padding-left: 0.24rem; font-weight: normal; color: var(--toc-header-text); }
.main-content h1.grhead1 { font-size: 1.40rem; margin: 0.13rem 0 0.13rem 0.9rem; color: var(--toc-header-text); padding: 0px 0px 0px 0px; line-height: 24px; }
.main-content h2.grhead2 { font-size: 1.30rem; margin: 0.13rem 0 0.13rem 1.50rem; color: var(--toc-header-text); padding: 0px 0px 0px 0px; line-height: 24px; }
.main-content h3.grhead3 { font-size: 1.20rem; margin: 0.13rem 0 0.13rem 2.10rem; color: var(--toc-header-text); padding: 0px 0px 0px 0px; line-height: 24px; }
.main-content h4.grhead4 { font-size: 1.10rem; margin: 0.13rem 0 0.13rem 2.75rem; color: var(--toc-header-text); padding: 0px 0px 0px 0px; line-height: 24px; }
.main-content h1.header1 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header1-text); background: var(--header1-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }
.main-content h2.header2 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header2-text); background: var(--header2-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }
.main-content h3.header3 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header3-text); background: var(--header3-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }
.main-content h4.header4 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header4-text); background: var(--header4-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }
.main-content h5.header5 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header5-text); background: var(--header5-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }
.main-content h6.header6 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header6-text); background: var(--header6-background); border-color: var(--header-border); display: block; padding-left: 0.5rem; }

a { color: var(--blue-text); text-decoration: none; }
a:hover { text-decoration: underline; }
font.black, a.black { color: var(--black-text); }
font.blue, a.blue { color: var(--blue-text); }
font.brown, a.brown { color: var(--brown-text); }
font.cyan, a.cyan { color: var(--cyan-text); }
font.dkgray, a.dkgray { color: var(--dkgray-text); }
font.gray, a.gray { color: var(--gray-text); }
font.green, a.green { color: var(--green-text); }
font.ltblue, a.ltblue { color: var(--ltblue-text); }
font.ltgray, a.ltgray { color: var(--ltgray-text); }
font.ltgreen, a.ltgreen { color: var(--ltgreen-text); }
font.orange, a.orange { color: var(--orange-text); }
font.pink, a.pink { color: var(--pink-text); }
font.purple, a.purple { color: var(--purple-text); }
font.red, a.red { color: var(--red-text); }
font.tan, a.tan { color: var(--tan-text); }
font.white, a.white { color: var(--white-text); }
font.yellow, a.yellow { color: var(--yellow-text); }

input[id^="spoiler"] { display: none; }
input[id^="spoiler"] + label { display: inline; margin: 0.25rem; padding: 0.25rem; color: white; background-color: rgba(23, 130, 130, 0.9); border-color: rgba(23, 130, 130, 0.2); text-align: center; font-size: 1.25rem; border-radius: 0.5rem; cursor: pointer; transition: all .6s; }
input[id^="spoiler"]:checked + label { color: var(--purple-text); background-color: var(--code-background); outline-style: hidden; }
input[id^="spoiler"] ~ .spoiler { width: auto; height: 0; overflow: hidden; opacity: 0; margin: 0.25rem; padding: 0.25rem; color: var(--purple-text); background-color: var(--code-background); border: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0.8); border-radius: 8px; transition: all .6s; }
input[id^="spoiler"] ~ .spoiler p { color: inherit; }
input[id^="spoiler"]:checked + label + .spoiler { height: auto; opacity: 1; padding: 10px; }

.main-content p { margin: 0 0 0 0.75rem; color: var(--body-text); }
.main-content p.empty { margin-top: 0.1rem; margin-bottom: 0.1rem; }
.main-content p.list-1 { margin-left: 0.9rem; }
.main-content p.list-2 { margin-left: 1.50rem; }
.main-content p.list-3 { margin-left: 2.10rem; }
.main-content p.list-4 { margin-left: 2.75rem; }
.main-content p.list-5 { margin-left: 3.4rem; }
.main-content p.list-6 { margin-left: 4rem; }

section.quote { display: block; justify-content: center; align-items: center; margin: 0.5rem 1rem 0.5rem 1rem; color: rgba(150, 150, 150, 0.8); background-color: rgba(150, 150, 150, 0.08); border-color: rgba(150, 150, 150, 0.2); border-style: solid; border-width: 3px; border-radius: 0.3rem; transition: color 0.2s, background-color 0.2s, border-color 0.2s; box-shadow: 5px 3px 30px black; }
section.quote p { margin: 0; padding: 0; line-height: 24px; }
section.quote p.empty { margin: 0; padding: 0; line-height: 24px; }
section.quote .attr { margin: 0; padding: 0 0 0.1rem 0.5rem; font: normal 400 1.5em/1.5em 'Montserrat', sans-serif; background-color: rgba(150, 150, 150, 0.2); letter-spacing: 0.04em; text-align: left; }
section.quote .attr:before { content: " - "; }
section.quote .attr:after { content: " - "; }

.drkbtn {  padding: 0.9rem; font-size: 1.2rem; display: inline-block; margin-bottom: 0.5rem; margin-left: 0.90rem; /* Preserve these colors the look goof on the header background */ color: white; background-color: rgba(23, 130, 130, 0.9); border-color: rgba(23, 130, 130, 0.2); border-style: solid; border-width: 1px; border-radius: 0.3rem; transition: color 0.2s, background-color 0.2s, border-color 0.2s; }
.drkbtn:hover { text-decoration: none; color: rgba(255, 255, 255, 0.8); background-color: rgba(34, 195, 195, 0.7); border-color: rgba(255, 255, 255, 0.3); }
.drkbtn + .drkbtn { margin-left: 0.50rem; }
.drkbtn + .drkbtn { margin-top: 0.5rem; margin-left: 0; } }
"""

# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None):
    """Generates an html file from a wtxt file. CssDir specifies a directory to search for css files."""
    if not outFile:
        outFile = os.path.splitext(srcFile)[0] + '.html'
    if srcFile:
        if srcFile == 'index.txt':
            page_number = 1
        else:
            if '-' in srcFile:
                page_number = int(srcFile.split('-', 1)[0])
            else:
                page_number = 0
    # RegEx Independent Routines ------------------------------------
    def anchorReplace(maObject):
        temp = maObject.group(1)
        anchor = reWd.sub('', temp)
        return '<div id="{}"></div>'.format(anchor)

    def boldReplace(maObject):
        state = states['bold'] = not states['bold']
        return ('</B>', '<B>')[state]

    def italicReplace(maObject):
        state = states['italic'] = not states['italic']
        return ('</I>', '<I>')[state]

    def boldItalicReplace(maObject):
        state = states['boldItalic'] = not states['boldItalic']
        return ('</I></B>', '<B><I>')[state]

    def strip_color(text):
        if reTextColor.search(text):
            temp = reTextColor.search(text)
            text_clolor = temp.group(1)
            strip_color = temp.group(0)
            fontClass = 'class="{}"'.format(text_clolor)
            out_text = re.sub(strip_color, '', text)
        else:
            fontClass = ''
            out_text = text
        return fontClass, out_text

    # RegEx ---------------------------------------------------------
    # --Headers
    reHead = re.compile(r'(=+) *(.+)')
    reHeadGreen = re.compile(r'(#+) *(.+)')
    headFormat = '<h{} class="header{}" id="{}">{}</h{}>\n'
    headFormatGreen = '<h{} id="{}">{}</h{}>\n'
    reHeaderText = re.compile(r'(<h\d {1,3}.+?>)(.*)(<\/h\d>)')
    reHeaderID = re.compile(r'(id="(.+?)")')
    # --List
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    # --Misc. text
    reHRule = re.compile(r'^\s*-{4,}\s*$')
    reEmpty = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    rePreBegin = re.compile('<pre>', re.I)
    rePreEnd = re.compile('</pre>', re.I)
    reParagraph = re.compile('<p\s+|<p>', re.I)
    reCloseParagraph = re.compile('</p>', re.I)
    # --Bold, Italic, BoldItalic
    reBold = re.compile(r'__')
    reItalic = re.compile(r'~~')
    reBoldItalic = re.compile(r'\*\*')
    states = {'bold': False, 'italic': False, 'boldItalic': False}
    # --Links
    reLink = re.compile(r'\[\[(.+?)\]\]')
    reHttp = re.compile(r' (http:\/\/[\?=_~a-zA-Z0-9\.\/%-]+)')
    reWww = re.compile(r' (www\.[\?=_~a-zA-Z0-9\./%-]+)')
    reWd = re.compile(r'(<[^>]+>|\[[^\]]+\]|\W+)')
    rePar = re.compile(r'^([a-zA-Z\d]|\*\*|~~|__|^\.{1,}|^\*{1,}|^\"{1,})')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z0-9]{2,4}$)')
    # --TextColors
    reTextColor = re.compile(r'{{a:(.+?)}}')
    # --Tags
    reAnchorTag = re.compile('{{nav:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    reTitleTag = re.compile(r'^{{PAGETITLE="(.+?)"}}')
    reNoteTag = re.compile(r'^{{note:(.+?)}}')
    reComment = re.compile(r'^\/\*.+\*\/')
    reCTypeBegin = re.compile(r'^\/\*')
    reCTypeEnd = re.compile('\*\/$')
    reSpoilerBegin = re.compile(r'\[\[sb:(.*?)\]\]')
    reSpoilerEnd = re.compile(r'\[\[se:\]\]')
    reBlockquoteBegin = re.compile(r'\[\[bb:(.*?)\]\]')
    reBlockquoteBEnd = re.compile(r'\[\[be:\]\]')
    reHtmlBegin = re.compile(r'(^\<font.+?\>)|(^\<code.+?\>)|(^\<a\s{1,3}href.+?\>)|(^\<a\s{1,3}(class=".+?)?href.+?\>)|(^\<img\s{1,3}src.+?\>)|^\u00A9|^\<strong|^\<[bB]\>')
    reNavigationButtonBegin = re.compile(r'{{nbb}}')
    reNavigationButtonEnd = re.compile(r'{{nbe}}')
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --Images
    reImageInline = re.compile(r'{{inline:(.+?)}}')
    reImageOnly = re.compile(r'{{image:(.+?)}}')
    reImageCaption = re.compile(r'{{image-caption:(.+?)}}')
    reImageCaptionUrl = re.compile(r'{{image-cap-url:(.+?)}}')

    def imageInline(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (max_width, file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '<img src="img\{}" style="max-width: {};" alt="{}"/>'.format(file_name, max_width, alt_text)

    def imageInclude(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text) = [chunk.strip() for chunk in image_line.split('|', 1)]
        return '<figure class="image-caption">\n<img src="img\{}" alt="{}"/>\n</figure>'.format(
            file_name, alt_text)

    def imageCaption(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption) = [chunk.strip() for chunk in image_line.split('|', 2)]
        return '<figure class="image-caption">\n<img src="img\{}" alt="{}"/>\n<figcaption>{}</figcaption>\n</figure>\n'.format(
            file_name, alt_text, caption)

    def imageCaptionUrl(maObject):
        image_line = maObject.group(1).strip()
        if '|' in image_line:
            (file_name, alt_text, caption, url, urlname) = [chunk.strip() for chunk in image_line.split('|', 4)]
        return '<figure class="image-caption">\n<img src="img\{}" alt="{}"/>\n<figcaption>{}</figcaption>\n<a href="{}">{}</a>\n</figure>\n'.format(
            file_name, alt_text, caption, url, urlname)

    def spoilerTag(line):
        spoilerID = ''
        spoilerText = ''
        if '|' in line:
            (spoilerID, spoilerText) = [chunk.strip() for chunk in line.split('|', 1)]
        spoilerID = spoilerID.lower()
        return (spoilerID, spoilerText)

    def httpReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reHttp.sub(r' <a href="\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reHttp.sub(r' <a href="\1">\1</a>', temp_text)
        return temp_line

    def wwwReplace(line):
        temp_text = line
        if inNavigationButtons:
            temp_line = reWww.sub(r' <a href="http://\1" class="drkbtn">\1</a>', temp_text)
        else:
            temp_line = reWww.sub(r' <a href="http://\1">\1</a>', temp_text)
        return temp_line

    def linkReplace(maObject):
        link_object = maObject.group(1)
        if '|' in link_object:
            (address, text) = [chunk.strip() for chunk in link_object.split('|', 1)]
        else:
            address = text = link_object
        fontClass, text = strip_color(text)
        if len(address) == 1 and address == '#':
            address += reWd.sub('', text)
        reInternalLink = re.compile(r'^#(.*)')
        anchor_compile = reInternalLink.match(address)
        if anchor_compile:
            anchor_result = anchor_compile.group(1)
            anchor_out = reWd.sub('', anchor_result)
            address = '#{}'.format(anchor_out)
        if inNavigationButtons:
            return '<a {} href="{}" class="drkbtn">{}</a>'.format(fontClass, address, text)
        else:
            return '<a {} href="{}">{}</a>'.format(fontClass, address, text)

    # --Defaults ----------------------------------------------------------
    level = 1
    spaces = ''
    cssFile = None
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --Init
    outLines = []
    contents = [] # The list variable for the Table of Contents
    header_match = [] # A duplicate list of the Table of Contents with numbers
    addContents = 0 # When set to 0 headers are not added to the TOC
    inPre = False
    inComment = False
    htmlIDSet = list()
    dupeEntryCount = 1
    blockAuthor = "Unknown"
    inNavigationButtons = False
    pageTitle = 'Your Content'
    # --Read source file --------------------------------------------------
    ins = open(srcFile, 'r')
    for line in ins:
        # --Liquid ------------------------------------
        line = re.sub(r'\{% raw %\}', '', line)
        line = re.sub(r'\{% endraw %\}', '', line)
        # --Preformatted? -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if (inPre and not maPreEnd) or maPreBegin:
            inPre = True
            outLines.append(line)
            continue
        if maPreEnd:
            inPre = False
            outLines.append(line)
            continue
        maTitleTag = reTitleTag.match(line)
        maCTypeBegin = reCTypeBegin.match(line)
        maCTypeEnd = reCTypeEnd.search(line)
        maComment = reComment.match(line)
        if maComment:
            continue
        if inComment or maCTypeBegin or maCTypeEnd or maComment:
            inComment = maCTypeBegin or (inComment and not maCTypeEnd)
            continue
        if maTitleTag:
            pageTitle = re.sub(r'({{PAGETITLE=")(.*)("}})(\n)?', r'\2', line)
            line = '= ' + pageTitle
        # --Re Matches -------------------------------
        maContents = reContentsTag.match(line)
        maCss = reCssTag.match(line)
        maHead = reHead.match(line)
        maHeadgreen = reHeadGreen.match(line)
        maList = reList.match(line)
        maPar = rePar.match(line)
        maHRule = reHRule.match(line)
        maEmpty = reEmpty.match(line)
        maSpoilerBegin = reSpoilerBegin.match(line)
        maSpoilerEnd = reSpoilerEnd.match(line)
        maBlockquoteBegin = reBlockquoteBegin.match(line)
        maBlockquoteEnd = reBlockquoteBEnd.match(line)
        maNavigationButtonBegin = reNavigationButtonBegin.match(line)
        maNavigationButtonEnd = reNavigationButtonEnd.match(line)
        # --Navigation Buttons ----------------------------------
        if maNavigationButtonBegin:
            line = '<div>\n'
            inNavigationButtons = True
        if maNavigationButtonEnd:
            line = '</div>\n'
            inNavigationButtons = False
        # --Contents ----------------------------------
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
        # --CSS
        elif maCss:
            cssFile = maCss.group(1).strip()
            continue
        # --Headers
        elif maHead:
            lead, text = maHead.group(1, 2)
            text = re.sub(' *=*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormat.format(level, level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --Green Header
        elif maHeadgreen:
            lead, text = maHeadgreen.group(1, 2)
            text = re.sub(' *\#*$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormatGreen.format(level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --List item
        elif maList:
            spaces = maList.group(1)
            bullet = maList.group(2)
            text = maList.group(3)
            if bullet == '.':
                bullet = '&nbsp;'
            elif bullet == '*':
                bullet = '&bull;'
            level = int(len(spaces) / 2 + 1)
            line = '{}<p class="list-{}">{}&nbsp; '.format(spaces, level, bullet)
            line = '{}{}</p>\n'.format(line, text)
        # --HRule
        elif maHRule:
            line = '<hr>\n'
        # --Paragraph
        elif maPar:
            line = '<p>' + line.rstrip() + '</p>\n'
        # --Empty line
        elif maEmpty:
            line = spaces + '<p class="empty">&nbsp;</p>\n'
        # --Spoiler Tag ---------------------------
        elif maSpoilerBegin:
            spoilerline = maSpoilerBegin.group(1)
            spoilerID, spoilerName = spoilerTag(spoilerline)
            firstLine = '<input type="checkbox" id="{}" />\n'.format(spoilerID)
            outLines.append(firstLine)
            secondLine = '<label for="{}">{}</label>\n'.format(spoilerID, spoilerName)
            outLines.append(secondLine)
            thirdLine = '<div class="spoiler">\n'
            outLines.append(thirdLine)
            continue
        elif maSpoilerEnd:
            line = '</div>\n'
        # --Blockquote ---------------------------
        elif maBlockquoteBegin:
            firstLine = '<section class="quote">\n'
            outLines.append(firstLine)
            author = maBlockquoteBegin.group(1)
            if len(author) < 1:
                author = blockAuthor
            authorLine = '<p class="attr">{}</p>\n'.format(author)
            outLines.append(authorLine)
            continue
        elif maBlockquoteEnd:
            line = '</section>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --Bold/Italic subs
        line = reBold.sub(boldReplace, line)
        line = reItalic.sub(italicReplace, line)
        line = reBoldItalic.sub(boldItalicReplace, line)
        # --Wtxt Tags
        line = reAnchorTag.sub(anchorReplace, line)
        # --Images
        line = reImageInline.sub(imageInline, line)
        line = reImageOnly.sub(imageInclude, line)
        line = reImageCaption.sub(imageCaption, line)
        line = reImageCaptionUrl.sub(imageCaptionUrl, line)
        # --Hyperlinks
        line = reLink.sub(linkReplace, line)
        line = httpReplace(line)
        line = wwwReplace(line)
        # --Re Note -------------------------------
        maNoteTag = reNoteTag.match(line)
        if maNoteTag:
            note_text = maNoteTag.group(1)
            line_out = '<p class="note">{}</p>\n'.format(note_text)
            outLines.append(line_out)
            continue
        # --HTML Font or Code tag first of Line ------------------
        maHtmlBegin = reHtmlBegin.match(line)
        if maHtmlBegin:
            maParagraph = reParagraph.match(line)
            maCloseParagraph = reCloseParagraph.search(line)
            if not maParagraph:
                line = '<p>' + line
            if not maCloseParagraph:
                line = re.sub(r'(\n)?$', '', line)
                line = line + '</p>\n'
        # --Save line ------------------
        outLines.append(line)
    ins.close()
    # --Get Css -----------------------------------------------------------
    css = defaultCss
    # --Write Output ------------------------------------------------------
    out = open(outFile, 'w')
    out.write(htmlHead % (pageTitle, css, pageTitle))
    didContents = False
    countlist = [page_number, 0, 0, 0, 0, 0, 0]
    for line in outLines:
        if reContentsTag.match(line):
            if not didContents:
                if len(contents) > 0:
                    baseLevel = min([level for (level, name, text) in contents])
                else:
                    baseLevel = 1
                previousLevel = baseLevel
                for heading in contents:
                    number = ''
                    level = heading[0] - baseLevel + 1
                    if heading[0] > previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] < previousLevel:
                        # Zero out everything not a duplicate
                        for i in range(level+1, 7):
                            countlist[i] = 0
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] == previousLevel:
                        countlist[level] += 1
                        for i in range(level+1):
                            if i == 0:
                                number += str(countlist[i])
                            else:
                                number += '.' + str(countlist[i])
                    if heading[0] <= addContents:
                        out.write('<p class="list-{}">&bull;&nbsp; <a href="#{}">{} {}</a></p>\n'.format(level, heading[1], number, heading[2]))
                        header_match.append((heading[1], number))
                    previousLevel = heading[0]
                didContents = True
        else:
            maIsHeader = re.search(r'<\/h\d>$', line)
            if maIsHeader:
                header_id_object = reHeaderID.search(line)
                header_id_result = header_id_object.group(2)
                for header_to_match in header_match:
                    if header_to_match[0] == header_id_result:
                        split_line = reHeaderText.split(line)
                        text_replace = '{} - {}'.format(header_to_match[1], split_line[2])
                        line = '{}{}{}\n'.format(split_line[1], text_replace, split_line[3])
                        break
            out.write(line)
    out.write('</div>\n</section>\n</BODY>\n</HTML>\n')
    out.close()
	

@mainFunction
def genHtml(fileName, outFile=None):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.txt':
        wtxtToHtml(fileName, outFile=None)
        # docsDir = r'c:\program files\bethesda softworks\morrowind\data files\docs'
        # wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext

if __name__ == '__main__':
        callables.main()
