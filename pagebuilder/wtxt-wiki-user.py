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


# ETXT =========================================================================
"""This section of the module provides a single function for converting
wtxt text files to html files."""
etxtHeader = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=iso-8859-1">
<TITLE>%s</TITLE>
<STYLE>
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H5 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
.date0 { background-color: #FFAAAA }
.date1 { background-color: #ffc0b3 }
.date2 { background-color: #ffd5bb }
.date3 { background-color: #ffeac4 }
</STYLE>
</HEAD>
<BODY BGCOLOR='#ffffcc'>
"""


@mainFunction
def etxtToHtml(inFileName):
    import time
    """Generates an html file from an etxt file."""
    # --Re's
    reHead2 = re.compile(r'## *([^=]*) ?=*')
    reHead3 = re.compile(r'# *([^=]*) ?=*')
    reHead4 = re.compile(r'@ *(.*)\s+')
    reHead5 = re.compile(r'% *(.*)\s+')
    reList = re.compile(r'( *)([-!?\.\+\*o]) (.*)')
    reBlank = re.compile(r'\s+$')
    reMDash = re.compile(r'--')
    reBoldEsc = re.compile(r'\_')
    reBoldOpen = re.compile(r' _')
    reBoldClose = re.compile(r'(?<!\\)_( |$)')
    reItalicOpen = re.compile(r' ~')
    reItalicClose = re.compile(r'~( |$)')
    reBoldicOpen = re.compile(r' \*')
    reBoldicClose = re.compile(r'\*( |$)')
    reBold = re.compile(r'\*\*([^\*]+)\*\*')
    reItalic = re.compile(r'\*([^\*]+)\*')
    reLink = re.compile(r'\[\[(.*?)\]\]')
    reHttp = re.compile(r' (http://[_~a-zA-Z0-9\./%-]+)')
    reWww = re.compile(r' (www\.[_~a-zA-Z0-9\./%-]+)')
    reDate = re.compile(r'\[([0-9]+/[0-9]+/[0-9]+)\]')
    reContents = re.compile(r'\[CONTENTS=?(\d+)\]\s*$')
    reWd = re.compile(r'\W\d*')
    rePar = re.compile(r'\^(.*)')
    reFullLink = re.compile(r'(:|#|\.[a-zA-Z]{3,4}$)')
    # --Date styling (Replacement function used with reDate.)
    dateNow = time.time()

    def dateReplace(maDate):
        date = time.mktime(
            time.strptime(maDate.group(1), '%m/%d/%Y'))  # [1/25/2005]
        age = int((dateNow - date) / (7 * 24 * 3600))
        if age < 0: age = 0
        if age > 3: age = 3
        return '<span class=date%d>%s</span>' % (age, maDate.group(1))

    def linkReplace(maLink):
        address = text = maLink.group(1).strip()
        if '|' in text:
            (address, text) = [chunk.strip() for chunk in text.split('|', 1)]
        if not reFullLink.search(address):
            address = address + '.html'
        return '<a href="%s">%s</a>' % (address, text)

    # --Defaults
    title = ''
    level = 1
    spaces = ''
    headForm = "<h%d><a name='%s'>%s</a></h%d>\n"
    # --Open files
    inFileRoot = re.sub('\.[a-zA-Z]+$', '', inFileName)
    inFile = open(inFileName)
    # --Init
    outLines = []
    contents = []
    addContents = 0
    # --Read through inFile
    for line in inFile.readlines():
        maHead2 = reHead2.match(line)
        maHead3 = reHead3.match(line)
        maHead4 = reHead4.match(line)
        maHead5 = reHead5.match(line)
        maPar = rePar.match(line)
        maList = reList.match(line)
        maBlank = reBlank.match(line)
        maContents = reContents.match(line)
        # --Contents
        if maContents:
            if maContents.group(1):
                addContents = int(maContents.group(1))
            else:
                addContents = 100
        # --Header 2?
        if maHead2:
            text = maHead2.group(1)
            name = reWd.sub('', text)
            line = headForm % (2, name, text, 3)
            if addContents: contents.append((2, name, text))
            # --Title?
            if not title: title = text
        # --Header 3?
        elif maHead3:
            text = maHead3.group(1)
            name = reWd.sub('', text)
            line = headForm % (3, name, text, 3)
            if addContents: contents.append((3, name, text))
            # --Title?
            if not title: title = text
        # --Header 4?
        elif maHead4:
            text = maHead4.group(1)
            name = reWd.sub('', text)
            line = headForm % (4, name, text, 4)
            if addContents: contents.append((4, name, text))
        # --Header 5?
        elif maHead5:
            text = maHead5.group(1)
            name = reWd.sub('', text)
            line = headForm % (5, name, text, 5)
            if addContents: contents.append((5, name, text))
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
            line = spaces + '<p class=list-' + `level` + '>' + bullet + '&nbsp; '
            line = line + text + '\n'
        # --Paragraph
        elif maPar:
            line = '<p>' + maPar.group(1)
        # --Blank line
        elif maBlank:
            line = spaces + '<p class=list' + `level` + '>&nbsp;</p>'
        # --Misc. Text changes
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --New bold/italic subs
        line = reBoldOpen.sub(' <B>', line)
        line = reItalicOpen.sub(' <I>', line)
        line = reBoldicOpen.sub(' <I><B>', line)
        line = reBoldClose.sub('</B> ', line)
        line = reBoldEsc.sub('_', line)
        line = reItalicClose.sub('</I> ', line)
        line = reBoldicClose.sub('</B></I> ', line)
        # --Old style bold/italic subs
        line = reBold.sub(r'<B><I>\1</I></B>', line)
        line = reItalic.sub(r'<I>\1</I>', line)
        # --Date
        line = reDate.sub(dateReplace, line)
        # --Local links
        line = reLink.sub(linkReplace, line)
        # --Hyperlink
        line = reHttp.sub(r' <a href="\1">\1</a>', line)
        line = reWww.sub(r' <a href="http://\1">\1</a>', line)
        # --Write it
        # print line
        outLines.append(line)
    inFile.close()
    # --Output file
    outFile = open(inFileRoot + '.html', 'w')
    outFile.write(etxtHeader % (title,))
    didContents = False
    for line in outLines:
        if reContents.match(line):
            if not didContents:
                baseLevel = min([level for (level, name, text) in contents])
                for (level, name, text) in contents:
                    level = level - baseLevel + 1
                    if level <= addContents:
                        outFile.write(
                            '<p class=list-%d>&bull;&nbsp; <a href="#%s">%s</a></p>\n' % (
                            level, name, text))
                didContents = True
        else:
            outFile.write(line)
    outFile.write('</body>\n</html>\n')
    outFile.close()
    # --Done

@mainFunction
def etxtToWtxt(fileName=None):
    """TextMunch: Converts etxt files to wtxt formatting."""
    if fileName:
        ins = open(fileName)
    else:
        import sys
        ins = sys.stdin
    for line in ins:
        line = re.sub(r'^\^ ?', '', line)
        line = re.sub(r'^## ([^=]+) =', r'= \1 ==', line)
        line = re.sub(r'^# ([^=]+) =', r'== \1 ', line)
        line = re.sub(r'^@ ', r'=== ', line)
        line = re.sub(r'^% ', r'==== ', line)
        line = re.sub(r'\[CONTENTS=(\d+)\]', r'{{CONTENTS=\1}}', line)
        line = re.sub(r'~([^ ].+?)~', r'~~\1~~', line)
        line = re.sub(r'_([^ ].+?)_', r'__\1__', line)
        line = re.sub(r'\*([^ ].+?)\*', r'**\1**', line)
        print line,


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
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=iso-8859-1">
<TITLE>%s</TITLE>
<STYLE>%s</STYLE>
</HEAD>
<BODY>
"""
defaultCss = """
H1 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.empty {}
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
PRE { border: 1px solid; background: #FDF5E6; padding: 0.5em; margin-top: 0in; margin-bottom: 0in; margin-left: 0.25in}
CODE { background-color: #FDF5E6;}
BODY { background-color: #ffffcc; }
"""

# Conversion ------------------------------------------------------------------
@mainFunction
def wtxtToHtml(srcFile, outFile=None, cssDir=''):
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

    def linkReplace(maObject):
        address = text = maObject.group(1).strip()
        if '|' in text:
            (address, text) = [chunk.strip() for chunk in text.split('|', 1)]
            if address == '#': address += reWd.sub('', text)
        if not reFullLink.search(address):
            address = address + '.html'
        return '<a href="%s">%s</a>' % (address, text)

    # --Tags
    reAnchorTag = re.compile('{{A:(.+?)}}')
    reContentsTag = re.compile(r'\s*{{CONTENTS=?(\d+)}}\s*$')
    reCssTag = re.compile('\s*{{CSS:(.+?)}}\s*$')
    # --Defaults ----------------------------------------------------------
    title = ''
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
    isInParagraph = False
    htmlIDSet = list()
    dupeEntryCount = 1
    # --Read source file --------------------------------------------------
    ins = file(srcFile)
    for line in ins:
        isInParagraph, wasInParagraph = False, isInParagraph
        # --Preformatted? -----------------------------
        maPreBegin = rePreBegin.search(line)
        maPreEnd = rePreEnd.search(line)
        if inPre or maPreBegin or maPreEnd:
            inPre = maPreBegin or (inPre and not maPreEnd)
            outLines.append(line)
            continue
        # --Re Matches -------------------------------
        maContents = reContentsTag.match(line)
        maCss = reCssTag.match(line)
        maHead = reHead.match(line)
        maHeadgreen = reHeadGreen.match(line)
        maList = reList.match(line)
        maPar = rePar.match(line)
        maHRule = reHRule.match(line)
        maEmpty = reEmpty.match(line)
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
            if not title and level <= 2: title = text
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
            if not title and level <= 2: title = text
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
            line = spaces + '<p class=empty>&nbsp;</p>\n'
        # --Misc. Text changes --------------------
        line = reMDash.sub('&#150', line)
        line = reMDash.sub('&#150', line)
        # --Bold/Italic subs
        line = reBold.sub(boldReplace, line)
        line = reItalic.sub(italicReplace, line)
        line = reBoldItalic.sub(boldItalicReplace, line)
        # --Wtxt Tags
        line = reAnchorTag.sub(anchorReplace, line)
        # --Hyperlinks
        line = reLink.sub(linkReplace, line)
        line = reHttp.sub(r' <a href="\1">\1</a>', line)
        line = reWww.sub(r' <a href="http://\1">\1</a>', line)
        # --Save line ------------------
        # print line,
        outLines.append(line)
    ins.close()
    # --Get Css -----------------------------------------------------------
    if not cssFile:
        css = defaultCss
    else:
        cssBaseName = os.path.basename(cssFile)  # --Dir spec not allowed.
        cssSrcFile = os.path.join(os.path.dirname(srcFile), cssBaseName)
        cssDirFile = os.path.join(cssDir, cssBaseName)
        if os.path.splitext(cssBaseName)[-1].lower() != '.css':
            raise "Invalid Css file: " + cssFile
        elif os.path.exists(cssSrcFile):
            cssFile = cssSrcFile
        elif os.path.exists(cssDirFile):
            cssFile = cssDirFile
        else:
            raise 'Css file not found: ' + cssFile
        css = ''.join(open(cssFile).readlines())
        if '<' in css:
            raise "Non css tag in css file: " + cssFile
    # --Write Output ------------------------------------------------------
    out = file(outFile, 'w')
    out.write(htmlHead % (title, css))
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
    out.write('</div>\n</section>\n')
    out.close()
	

@mainFunction
def genHtml(fileName, outFile=None, cssDir=''):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.etxt':
        etxtToHtml(fileName)
    elif ext == '.txt':
        wtxtToHtml(fileName, outFile=None, cssDir='')
        # docsDir = r'c:\program files\bethesda softworks\morrowind\data files\docs'
        # wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext

if __name__ == '__main__':
        callables.main()
