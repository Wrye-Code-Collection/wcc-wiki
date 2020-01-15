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
import string
import sys
import types
import os

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
        print help(self.callObjs[callKey])

    # --Main
    def main(self):
        callObjs = self.callObjs
        # --Call key, tail
        callParts = string.split(sys.argv[1], '.', 1)
        callKey = callParts[0]
        callTail = (len(callParts) > 1 and callParts[1])
        # --Help request?
        if callKey == '-h':
            self.printHelp(self)
            return
        # --Not have key?
        if callKey not in callObjs:
            print "Unknown function/object:", callKey
            return
        # --Callable
        callObj = callObjs[callKey]
        if type(callObj) == types.StringType:
            callObj = eval(callObj)
        if callTail:
            callObj = eval('callObj.' + callTail)
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
        apply(callObj, args, keywords)


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
      <h1 class="project-name">Wrye-Code-Collection Wiki</h1>
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
html {
    font-size: 16px;
  -webkit-box-sizing: border-box;
  -moz-box-sizing: border-box;
  box-sizing: border-box;
}

* {
  box-sizing: border-box;
}

body { padding: 0; margin: 0; font-family: "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif; line-height: 1.5; color: var(--body-text); background: var(--body-background); }

.page-header {
  color: var(--white-text);
  text-align: center;
  background-color: var(--cayman-header-background);
  background-image: linear-gradient(120deg, var(--cayman-header-background-secondary), var(--cayman-header-background));
  padding: 3rem 4rem;
}
h1 { font-size: 2.0rem; margin: 1em 0; }
h2 { font-size: 1.75rem; margin: 1em 0; }
h3 { font-size: 1.5rem; margin: 1em 0; }
h4 { font-size: 1.25rem; margin: 1em 0; }
h5 { font-size: 1.0rem; margin: 1em 0; }
h6 { font-size: 0.75rem; margin: 1em 0; }

.main-content { word-wrap: break-word; }
.main-content :first-child { margin-top: 0; }

.main-content code { padding: 2px 4px; font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 0.9rem; color: var(--purple-text); background-color: var(--code-background); border-radius: 0.3rem; }
.main-content pre { padding: 0.8rem; margin-top: 0; margin-bottom: 1rem; font: 1rem Consolas, "Liberation Mono", Menlo, Courier, monospace; color: var(--purple-text); word-wrap: normal; background-color: var(--code-background); border: solid 1px var(--cayman-border); border-radius: 0.3rem; }
.main-content pre > code { padding: 0; margin: 0; font-size: 0.9rem; color: var(--purple-text); word-break: normal; white-space: pre; background: transparent; border: 0; }
.main-content .highlight { margin-bottom: 1rem; }
.main-content .highlight pre { margin-bottom: 0; word-break: normal; }
.main-content .highlight pre, .main-content pre { padding: 0.8rem; overflow: auto; font-size: 0.9rem; line-height: 1.45; border-radius: 0.3rem; -webkit-overflow-scrolling: touch; }
.main-content pre code, .main-content pre tt { display: inline; max-width: initial; padding: 0; margin: 0; overflow: initial; line-height: inherit; word-wrap: normal; background-color: transparent; border: 0; }
.main-content pre code:before, .main-content pre code:after, .main-content pre tt:before, .main-content pre tt:after { content: normal; }
.main-content ul, .main-content ol { margin-top: 0; }

.main-content blockquote { padding: 0 1rem; margin-left: 0; color: var(--purple-text); background: var(--header3-background); border-left: 0.3rem solid var(--ltgray-text); }
.main-content blockquote > :first-child { margin-top: 0; }
.main-content blockquote > :last-child { margin-bottom: 0; }

.main-content table { display: block; width: 100%; overflow: auto; word-break: normal; word-break: keep-all; -webkit-overflow-scrolling: touch; }
.main-content table th { font-weight: bold; background-color: var(--header1-border); }
.main-content table th, .main-content table td { padding: 0.5rem 1rem; border: 1px solid var(--header1-border); }

.main-content dl { padding: 0; }
.main-content dl dt { padding: 0; margin-top: 1rem; font-size: 1rem; font-weight: bold; }
.main-content dl dd { padding: 0; margin-bottom: 1rem; }

.main-content hr { height: 2px; padding: 0; margin: 1rem 0; background-color: var(--white-text); border: 0; }

.main-content h1, .main-content h2, .main-content h3, .main-content h4, .main-content h5, .main-content h6 { margin-top: 2rem; margin-bottom: 1rem; font-weight: normal; color: var(--toc-header-text); }
.main-content h1.header1 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header1-text); background: var(--header1-background); border-color: var(--header-border); display: block; }
.main-content h2.header2 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header2-text); background: var(--header2-background); border-color: var(--header-border); display: block; }
.main-content h3.header3 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header3-text); background: var(--header3-background); border-color: var(--header-border); display: block; }
.main-content h4.header4 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header4-text); background: var(--header4-background); border-color: var(--header-border); display: block; }
.main-content h5.header5 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header5-text); background: var(--header5-background); border-color: var(--header-border); display: block; }
.main-content h6.header6 { border-top: 2px solid; border-bottom: 2px solid; color: var(--header6-text); background: var(--header6-background); border-color: var(--header-border); display: block; }

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
input[id^="spoiler"] + label { display: inline; margin: 10px 0px; padding: 2px 20px; color: white; background-color: rgba(23, 130, 130, 0.9); border-color: rgba(23, 130, 130, 0.2); text-align: center; font-size: 24px; border-radius: 8px; cursor: pointer; transition: all .6s; }
input[id^="spoiler"]:checked + label { color: rgba(255, 255, 255, 0.7); background-color: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.2); }
input[id^="spoiler"] ~ .spoiler { width: auto; height: 0; overflow: hidden; opacity: 0; margin: 0; padding: 10px; color: var(--purple-text); background-color: var(--code-background); border: 1px solid white; border-radius: 8px; transition: all .6s; }
input[id^="spoiler"] ~ .spoiler p { color: inherit; }
input[id^="spoiler"]:checked + label + .spoiler { height: auto; opacity: 1; padding: 10px; }

.main-content p { margin-top: 0.1rem; margin-bottom: 0.1rem; color: var(--body-text); }
.main-content p.empty { margin-top: 0.1rem; margin-bottom: 0.1rem; }
.main-content p.list-1 { margin-left: 0.15in; text-indent: -0.15in; }
.main-content p.list-2 { margin-left: 0.3in; text-indent: -0.15in; }
.main-content p.list-3 { margin-left: 0.45in; text-indent: -0.15in; }
.main-content p.list-4 { margin-left: 0.6in; text-indent: -0.15in; }
.main-content p.list-5 { margin-left: 0.75in; text-indent: -0.15in; }
.main-content p.list-6 { margin-left: 1.00in; text-indent: -0.15in; }

section.quote { display: block; justify-content: center; align-items: center; margin: 0.5rem 1rem 0.5rem 1rem; color: rgba(150, 150, 150, 0.8); background-color: rgba(150, 150, 150, 0.08); border-color: rgba(150, 150, 150, 0.2); border-style: solid; border-width: 3px; border-radius: 0.3rem; transition: color 0.2s, background-color 0.2s, border-color 0.2s; box-shadow: 5px 3px 30px black; }
section.quote p { margin: 0; padding: 0; line-height: 24px; }
section.quote p.empty { margin: 0; padding: 0; line-height: 24px; }
section.quote .attr { margin: 0; padding: 0 0 0.1rem 0.5rem; font: normal 400 1.5em/1.5em 'Montserrat', sans-serif; background-color: rgba(150, 150, 150, 0.2); letter-spacing: 0.04em; text-align: left; }
section.quote .attr:before { content: " - "; }
section.quote .attr:after { content: " - "; }
"""

# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None):
    """Generates an html file from a wtxt file. CssDir specifies a directory to search for css files."""
    if not outFile:
        import os
        outFile = os.path.splitext(srcFile)[0] + '.html'
    # Setup ---------------------------------------------------------
    # --Headers
    reHead = re.compile(r'(=+) *(.+)')
    reHeadGreen = re.compile(r'(#+) *(.+)')
    headFormat = '<h%d class="header%d" id="%s">%s</h%d>\n'
    headFormatGreen = '<h%d id="%s">%s</h%d>\n'
    # --List
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    # --Misc. text
    reHRule = re.compile(r'^\s*-{4,}\s*$')
    reEmpty = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    rePreBegin = re.compile('<pre>', re.I)
    rePreEnd = re.compile('</pre>', re.I)
    reParagraph = re.compile('<pre>', re.I)
    reCloseParagraph = re.compile('</pre>', re.I)

    def anchorReplace(maObject):
        text = maObject.group(1)
        anchor = reWd.sub('', text)
        return "<a name='%s'>%s</a>" % (anchor, text)

    # --Bold, Italic, BoldItalic
    reBold = re.compile(r'__')
    reItalic = re.compile(r'~~')
    reBoldItalic = re.compile(r'\*\*')
    states = {'bold': False, 'italic': False, 'boldItalic': False}

    def boldReplace(maObject):
        state = states['bold'] = not states['bold']
        return ('</B>', '<B>')[state]

    def italicReplace(maObject):
        state = states['italic'] = not states['italic']
        return ('</I>', '<I>')[state]

    def boldItalicReplace(maObject):
        state = states['boldItalic'] = not states['boldItalic']
        return ('</I></B>', '<B><I>')[state]

    # --Links
    reLink = re.compile(r'\[\[(.*?)\]\]')
    reHttp = re.compile(r' (http://[_~a-zA-Z0-9\./%-]+)')
    reWww = re.compile(r' (www\.[_~a-zA-Z0-9\./%-]+)')
    reWd = re.compile(r'(<[^>]+>|\[[^\]]+\]|\W+)')
    rePar = re.compile(r'^([a-zA-Z]|\*\*|~~|__)')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z0-9]{2,4}$)')

    def check_color(text):
        fontClass = ''
        if '{{a:black}}' in text:
            fontClass = 'class="black"'
        if '{{a:blue}}' in text:
            fontClass = 'class="blue"'
        if '{{a:brown}}' in text:
            fontClass = 'class="brown"'
        if '{{a:cyan}}' in text:
            fontClass = 'class="cyan"'
        if '{{a:dkgray}}' in text:
            fontClass = 'class="dkgray"'
        if '{{a:gray}}' in text:
            fontClass = 'class="gray"'
        if '{{a:green}}' in text:
            fontClass = 'class="green"'
        if '{{a:ltblue}}' in text:
            fontClass = 'class="ltblue"'
        if '{{a:ltgray}}' in text:
            fontClass = 'class="ltgray"'
        if '{{a:ltgreen}}' in text:
            fontClass = 'class="ltgreen"'
        if '{{a:orange}}' in text:
            fontClass = 'class="orange"'
        if '{{a:pink}}' in text:
            fontClass = 'class="pink"'
        if '{{a:purple}}' in text:
            fontClass = 'class="purple"'
        if '{{a:red}}' in text:
            fontClass = 'class="red"'
        if '{{a:tan}}' in text:
            fontClass = 'class="tan"'
        if '{{a:white}}' in text:
            fontClass = 'class="white"'
        if '{{a:yellow}}' in text:
            fontClass = 'class="yellow"'
        return fontClass

    def strip_color(text):
        temp = text
        if '{{a:black}}' in text:
            temp = re.sub('{{a:black}}', '', text)
        if '{{a:blue}}' in text:
            temp = re.sub('{{a:blue}}', '', text)
        if '{{a:brown}}' in text:
            temp = re.sub('{{a:brown}}', '', text)
        if '{{a:cyan}}' in text:
            temp = re.sub('{{a:cyan}}', '', text)
        if '{{a:dkgray}}' in text:
            temp = re.sub('{{a:dkgray}}', '', text)
        if '{{a:gray}}' in text:
            temp = re.sub('{{a:gray}}', '', text)
        if '{{a:green}}' in text:
            temp = re.sub('{{a:green}}', '', text)
        if '{{a:ltblue}}' in text:
            temp = re.sub('{{a:ltblue}}', '', text)
        if '{{a:ltgray}}' in text:
            temp = re.sub('{{a:ltgray}}', '', text)
        if '{{a:ltgreen}}' in text:
            temp = re.sub('{{a:ltgreen}}', '', text)
        if '{{a:orange}}' in text:
            temp = re.sub('{{a:orange}}', '', text)
        if '{{a:pink}}' in text:
            temp = re.sub('{{a:pink}}', '', text)
        if '{{a:purple}}' in text:
            temp = re.sub('{{a:purple}}', '', text)
        if '{{a:red}}' in text:
            temp = re.sub('{{a:red}}', '', text)
        if '{{a:tan}}' in text:
            temp = re.sub('{{a:tan}}', '', text)
        if '{{a:white}}' in text:
            temp = re.sub('{{a:white}}', '', text)
        if '{{a:yellow}}' in text:
            temp = re.sub('{{a:yellow}}', '', text)
        return temp

    def spoilerTag(line):
        spoilerID = ''
        spoilerText = ''
        if '|' in line:
            (spoilerID, spoilerText) = [chunk.strip() for chunk in line.split('|', 1)]
        spoilerID = re.sub('\[\[', '', spoilerID)
        spoilerText = re.sub('\]\]', '', spoilerText)
        return (spoilerID, spoilerText)

    def linkReplace(maObject):
        address = text = maObject.group(1).strip()
        skipStrip = False
        if '|' in text:
            (address, text) = [chunk.strip() for chunk in text.split('|', 1)]
            if address == '#':
                fontClass = check_color(text)
                text = strip_color(text)
                address += reWd.sub('', text)
                skipStrip = True
        if not reFullLink.search(address):
            address = address + '.html'
        if not skipStrip:
            fontClass = check_color(text)
            text = strip_color(text)
        return '<a {} href="{}">{}</a>'.format(fontClass, address, text)

    # --Tags
    pageTitle = 'Your Content'
    # reAnchorTag = re.compile('{{A:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    reTitleTag = re.compile(r'({{PAGETITLE=")(.*)("}})$')
    reComment = re.compile(r'^\/\*.+\*\/')
    reCTypeBegin = re.compile(r'^\/\*')
    reCTypeEnd = re.compile('\*\/$')
    reSpoilerBegin = re.compile(r'\[\[sb:(.*?)\]\]')
    reSpoilerEnd = re.compile(r'\[\[se:\]\]')
    reBlockquoteBegin = re.compile(r'\[\[bb:(.*?)\]\]')
    reBlockquoteBEnd = re.compile(r'\[\[be:\]\]')
    reHtmlBegin = re.compile(r'(^\<font.+?\>)|(^\<code.+?\>)')
    # --Defaults ----------------------------------------------------------
    level = 1
    spaces = ''
    cssFile = None
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', srcFile)
    # --Init
    outLines = []
    contents = [] # The list variable for the Table of Contents
    addContents = 0 # When set to 0 headers are not added to the TOC
    inPre = False
    inComment = False
    isInParagraph = False
    htmlIDSet = list()
    dupeEntryCount = 1
    # --Read source file --------------------------------------------------
    ins = file(srcFile)
    blockAuthor = "Unknown"
    for line in ins:
        isInParagraph, wasInParagraph = False, isInParagraph
        # --Liquid ------------------------------------
        line = re.sub(r'\{% raw %\}', '', line)
        line = re.sub(r'\{% endraw %\}', '', line)
        # --Preformatted? -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if inPre or maPreBegin or maPreEnd:
            inPre = maPreBegin or (inPre and not maPreEnd)
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
        # --Contents ----------------------------------
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
            inPar = False
        # --CSS
        elif maCss:
            cssFile = maCss.group(1).strip()
            continue
        # --Headers
        elif maHead:
            lead, text = maHead.group(1, 2)
            text = re.sub(' *=*#?$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormat % (level, level, anchor, text, level)
            if addContents:
                contents.append((level, anchor, text))
            # --Title?
        # --Green Header
        elif maHeadgreen:
            lead, text = maHeadgreen.group(1, 2)
            text = re.sub(' *\#*#?$', '', text.strip())
            anchor = reWd.sub('', text)
            level = len(lead)
            if not htmlIDSet.count(anchor):
                htmlIDSet.append(anchor)
            else:
                anchor += str(dupeEntryCount)
                htmlIDSet.append(anchor)
                dupeEntryCount += 1
            line = headFormatGreen % (level, anchor, text, level)
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
            level = len(spaces) / 2 + 1
            line = spaces + '<p class="list-' + `level` + '">' + bullet + '&nbsp; '
            line = line + text + '</p>\n'
        # --HRule
        elif maHRule:
            line = '<hr>\n'
        # --Paragraph
        elif maPar:
            if not wasInParagraph: line = '<p>' + line.rstrip() + '</p>\n'
            isInParagraph = True
        # --Empty line
        elif maEmpty:
            line = spaces + '<p class="empty">&nbsp;</p>\n'
        # --Spoiler Tag ---------------------------
        elif maSpoilerBegin:
            line = re.sub('sb:', '', line)
            spoilerID, spoilerName = spoilerTag(line)
            spoilerID = spoilerID.lower()
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
            author = re.sub(r'\[\[bb:(.*?)\]\]\n', r'\1', line)
            if len(author) < 1:
                author = blockAuthor
            authorLine = '<p class="attr">{}</p>\n'.format(author)
            outLines.append(authorLine)
            # secondLine = '<div class="quote">\n'
            # outLines.append(secondLine)
            # openQuote = '<p class="quotetext">\n'
            # outLines.append(openQuote)
            continue
        elif maBlockquoteEnd:
            # closingQuote = '</p>\n'
            # outLines.append(closingQuote)
            # closingDiv = '</div>\n'
            # outLines.append(closingDiv)
            line = '</section>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --Bold/Italic subs
        line = reBold.sub(boldReplace, line)
        line = reItalic.sub(italicReplace, line)
        line = reBoldItalic.sub(boldItalicReplace, line)
        # --Wtxt Tags
        # line = reAnchorTag.sub(anchorReplace, line)
        # --Hyperlinks
        line = reLink.sub(linkReplace, line)
        line = reHttp.sub(r' <a href="\1">\1</a>', line)
        line = reWww.sub(r' <a href="http://\1">\1</a>', line)
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
        # print line,
        outLines.append(line)
    ins.close()
    # --Get Css -----------------------------------------------------------
    css = defaultCss
    # --Write Output ------------------------------------------------------
    out = file(outFile, 'w')
    out.write(htmlHead % (pageTitle, css))
    didContents = False
    for line in outLines:
        if reContentsTag.match(line):
            if not didContents:
                baseLevel = min([level for (level, name, text) in contents])
                for (level, name, text) in contents:
                    level = level - baseLevel + 1
                    if level <= addContents:
                        out.write(
                            '<p class="list-%d">&bull;&nbsp; <a href="#%s">%s</a></p>\n' % (
                            level, name, text))
                didContents = True
        else:
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
