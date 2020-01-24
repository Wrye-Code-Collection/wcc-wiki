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
from bs4 import BeautifulSoup

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


@mainFunction
def getPosts(srcFile, outFile=None, outtext=None):
    """TextMunch: Converts html files to wtxt formatting."""
    if not outFile:
        import os
        outFile = 'out-' + os.path.splitext(srcFile)[0] + '.html'
    if not outtext:
        import os
        outtext = os.path.splitext(srcFile)[0] + '.txt'
    post_list = []
    soup = BeautifulSoup(open(srcFile), features="html5lib")
    all_posts = soup.find("div", id="ips_Posts")
    for div in all_posts.find_all('div'):
        if div.get('id'):
            post_list.append(div.get('id'))
    #print(post_list)
    outPosts = []
    outText = []
    for post in post_list:
        found = soup.find("div", id=post)
        post_wrap = found.div
        post_body = post_wrap.find("div", class_="post_body")
        post_wrap.find("div", class_="post_body")
        content = post_body.find("div")
        text = content.text + '\n'
        outText.append(text)
        outPosts.append(content.prettify(formatter="html"))
    #print(outPosts)
    out = file(outFile, 'w')
    for post in outPosts:
        out.write(post.encode('utf8'))
    out.close()
    out = file(outtext, 'w')
    for post in outText:
        out.write(post.encode('utf8'))
    out.close()


@mainFunction
def htmlToWtxt(srcFile, outFile=None):
    """TextMunch: Converts html files to wtxt formatting."""

    # --- Functions
    def flipBool(bool):
        return not bool

    def writeOut(bool1, bool2):
        if  not bool1 and not bool2:
            return True
        else: return False

    def wasInBlock(isBool, wasBool):
        if not isBool and wasBool:
            return False, False
        return isBool, wasBool

    # --- Begining of Code
    if not outFile:
        import os
        outFile = os.path.splitext(srcFile)[0] + '.txt'
    outLines = []
    writeToFile = True
    isInFrontmatter = False
    wasInFrontmatter = False
    isStyleBlock = False
    wasStyleBlock = False
    # --Read source file --------------------------------------------------
    ins = file(srcFile)
    reFrontMatter = re.compile('---', re.I)
    reStyleBlock = re.compile('(<STYLE>|<\/STYLE>)')
    for line in ins:
        soup = BeautifulSoup(line, features="html5lib")
        text = soup.prettify().encode('ascii')
        print(text)

        #line = re.sub(r'&bull;&nbsp;', '', line)
        #maFrontMatter = reFrontMatter.match(line)
        #maStyleBlock = reStyleBlock.search(line)
        #if maFrontMatter:
        #    isInFrontmatter, wasInFrontmatter = flipBool(isInFrontmatter), True
        #if maStyleBlock:
        #    isStyleBlock, wasStyleBlock = flipBool(isStyleBlock), True
        # line = re.sub(r'^## ([^=]+) =', r'= \1 ==', line)
        # line = re.sub(r'^# ([^=]+) =', r'== \1 ', line)
        # line = re.sub(r'^@ ', r'=== ', line)
        # line = re.sub(r'^% ', r'==== ', line)
        # line = re.sub(r'\[CONTENTS=(\d+)\]', r'{{CONTENTS=\1}}', line)
        # line = re.sub(r'~([^ ].+?)~', r'~~\1~~', line)
        # line = re.sub(r'_([^ ].+?)_', r'__\1__', line)
        # line = re.sub(r'\*([^ ].+?)\*', r'**\1**', line)
        # writeToFile = writeOut(isInFrontmatter, wasInFrontmatter)
        # writeToFile = writeOut(isStyleBlock, wasStyleBlock)
        #if writeToFile:
        #    outLines.append(line)
        #isInFrontmatter, wasInFrontmatter = wasInBlock(isInFrontmatter, wasInFrontmatter)
        #isStyleBlock, wasStyleBlock = wasInBlock(isStyleBlock, wasStyleBlock)
    ins.close()
    #out = file(outFile, 'w')
    #for line in outLines:
    #    out.write(line)
    #out.close()

#--- things to strip
# 1---
# <br \/> and <br \/>\n
# (<em.*>)(.*)(<\/em>) and <br \/>\n
# (<a href=')(http:.*)('\sclass='.*')(\stitle='.*')(\srel='.*')?(\srel='.*')?(>)(.*)()(<\/a>) and [[\2 \| \8]]<br \/>\n
# (<a href=')(http:.*)('\sclass='.*')(\stitle='.*')?(\srel='.*')?(>)(.*)(<\/a>) and [[\2 \| \7]]<br \/>\n
# (<a href=')(http:.*)('\sclass='.*')(\stitle='.*')(\srel='.*')(>)(<span.*'>)?(.*)<\/span>?(<\/a>) and [[\2 \| \7]]<br \/>\n
# (<a href=')(http:.*)('\sclass='.*')(\stitle='.*')(\srel='.*')?(\srel='.*')?(>)(.*)(<\/a>) and [[\2 \| \9]]<br \/>\n

@mainFunction
def genHtml(fileName, outFile=None, outtext=None):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == '.html' or ext == '.htm':
        getPosts(fileName, outFile, outtext)
    else:
        raise "Unrecognized file type: " + ext

if __name__ == '__main__':
        callables.main()
