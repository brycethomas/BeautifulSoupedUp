"""Beautiful Souped Up

Beautiful Souped Up is a GUI utility designed to work with Leonard
Richardson's popular HTML/XML Parser, Beautiful Soup
(http://www.crummy.com/software/BeautifulSoup).  You'll need to have
installed Beautiful Soup before Beautiful Souped Up will work.

Beautiful Souped Up enables you to quickly try out Beautiful Soup style
queries on a piece of markup and see the results within the overall
context of the document. Although you could use the Python interactive
interpreter to quickly try out soup queries on a document, you don't get to
see the results in the context of the entire document.  This is what
Beautiful Souped Up aims to address, by highlighting the matching
pieces of markup within the overall document itself.

Beautiful Soup was designed to allow you to rip out the pieces of
information your after as quickly as possible and then run, run like
the wind.  In the same spirit, Beautiful Souped Up is designed to help
you speed up the process even more by allowing you to quickly identify
when you've written the right query you need to get a grasp on the
segment of information you're after.

And now for some legal stuff:

Copyright (c) 2004-2008, Bryce Thomas

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the the Brycestrosoft House of Software 
    nor the names of its contributors may be
    used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
__author__ = "Bryce Thomas (bthomas@codeemporium.com)"
__version__ = "0.7"
__copyright__ = "Copyright (c) 2009 Bryce Thomas"
__license__ = "New-style BSD"

from BeautifulSoup import BeautifulSoup, Tag,NavigableString,PageElement, ResultSet, isList, isString, DEFAULT_OUTPUT_ENCODING
from Tkinter import *
import tkFont
import traceback

class BeautifulSoupedUp():

  """This class contains all the traversal logic that goes through and
  prints out the markup and highlights any matches.  It works by
  taking the soup (the entire markup) and the results of the user's
  soup query (some subset of the entire markup) and traversing through
  the entire markup tree, checking along the way for matches between any item
  in the soup query results (the subset) and the the current item of
  the entire markup being rendered.
  """

  def __init__(self,soup,matches,textbox):
    self.soup=soup
    self.matches=matches
    self.textbox=textbox
    self.textbox.tag_config("closeTag",foreground="#9D1380")
    self.textbox.tag_config("openTag",foreground="#9D1380")
    self.textbox.tag_config("attrName",foreground="#994500")
    self.textbox.tag_config("attrEquals",foreground="#9D1380")
    self.textbox.tag_config("attrValue",foreground="#1A1AA6")
    self.textbox.tag_config("attrValueQuotes",foreground="#9D1380")
    self.textbox.tag_config("match", background="yellow")
    self.textbox.tag_raise("sel")


  def prettify(self, encoding=DEFAULT_OUTPUT_ENCODING):
    return self.__str__(self.soup,False,encoding,True)


  def noprettify(self,encoding=DEFAULT_OUTPUT_ENCODING):
    return self.__str__(self.soup,False,encoding,False)


  def __str__(self,tag,tagIsMatchChild=False,encoding=DEFAULT_OUTPUT_ENCODING,
              prettyPrint=False,indentLevel=0):
    """Writes the passed in tag and its contents out to the textbox,
    highlighting any matches that it comes across based on the soup
    query."""
    encodedName=tag.toEncoding(tag.name,encoding)
    
    # Checks if the name of the tag itself matches the user's query.
    # NOTE: BeautifulSoup appears to use the same memory location
    # (identity) to store identical tag names.  So for example, a
    # document with two paragraphs (<p>) would return the same memory
    # location for a query of soup('p')[0].name and soup('p')[1].name.
    # In practice what this means is that when a user enters a query
    # like soup('p')[0].name, the logic that does tag name
    # highlighting will register the first paragraph tag name as a
    # match, but also the second paragraph tag name as a match.So all
    # <p> tag names would get highlighted, not just the first, even
    # though the actual return value from BeautifulSoup would just be
    # a single value 'p'.
    tagNameTextboxTag="nomatch"
    tagNameIsMatch=False
    if isinstance(self.matches,unicode):
      if tag.name is self.matches:
        tagNameIsMatch=True
    if tagNameIsMatch:
      tagNameTextboxTag="match"
    
    attrs=[]
    listAttrs=list()
    if tag.attrs:
      for key,val in tag.attrs:
        attrValTag="nomatch"
        # check if the user's soup query returned this attribute value
        # on the current tag
        if isinstance(self.matches,unicode):
          if val is self.matches:
            attrValTag="match"        

        fmt='%s="%s"'
        if isString(val):
          if tag.containsSubstitutions and '%SOUP-ENCODING%' in val:
            val = tag.substituteEncoding(val,encoding)

          if '"' in val:
            fmt="%s='%s'"
            if "'" in val:
              val=val.replace("'","&squot;")

          val=tag.BARE_AMPERSAND_OR_BRACKET.sub(tag._sub_entity, val)

        attrs.append(fmt % (tag.toEncoding(key,encoding),
                            tag.toEncoding(val,encoding)))
        listAttrs.append((tag.toEncoding(key,encoding),tag.toEncoding(val,encoding),attrValTag))
    close=''
    closeTag=''
    if tag.isSelfClosing:
      close=' /'
    else:
      closeTag = '</%s>' % encodedName

    indentTag,indentContents= 0,0
    if prettyPrint:
      indentTag = indentLevel
      space = (' ' * (indentTag-1))
      indentContents=indentTag + 1

    tagIsMatch=False
    textboxTag="nomatch"
    if isinstance(self.matches,NoneType) == False:
      # Handles self.matches being of type Tag, ResultSet, List.  If
      # self.matches is of type unicode, then it shouldn't match any
      # of the conditions and shouldn't break the program with the
      # conditions as they are at present.
      if tag is self.matches or id(tag) in [id(match) for match in self.matches] or tagIsMatchChild:
        tagIsMatch=True
      if tagIsMatch:
        textboxTag="match"  
    
    if tag.hidden:
      contents=self.renderContents(tag, tagIsMatch, encoding, prettyPrint, indentContents)
      s = contents
    else:
      s=[]
      attributeString=''
      if attrs:
        attributeString=' ' + ' '.join(attrs)
      if prettyPrint:
        s.append(space)
        self.textbox.insert(INSERT,space)
      s.append('<%s%s%s>' % (encodedName, attributeString, close))
      self.textbox.insert(INSERT,'<',(textboxTag,"openTag"))
      self.textbox.insert(INSERT,'%s' % (encodedName),(textboxTag,tagNameTextboxTag,"openTag"))
      for listAttr in listAttrs:
        self.textbox.insert(INSERT,' ')
        self.textbox.insert(INSERT,listAttr[0],(textboxTag,"attrName"))
        self.textbox.insert(INSERT,'=',(textboxTag,"attrEquals"))
        self.textbox.insert(INSERT,'"',(textboxTag,"attrValueQuotes"))
        self.textbox.insert(INSERT,listAttr[1],(textboxTag,"attrValue",listAttr[2]))
        self.textbox.insert(INSERT,'"',(textboxTag,"attrValueQuotes"))
      self.textbox.insert(INSERT,close,textboxTag)
      self.textbox.insert(INSERT,'>',(textboxTag,"openTag"))
      if prettyPrint:
        s.append("\n")
        self.textbox.insert(INSERT,"\n")
      contents=self.renderContents(tag,tagIsMatch,encoding,prettyPrint,indentContents)
      s.append(contents)
      if prettyPrint and contents and contents[-1] != "\n":
        s.append("\n")
        self.textbox.insert(INSERT,"\n")
      if prettyPrint and closeTag:
        s.append(space)
        self.textbox.insert(INSERT,space)
      s.append(closeTag)
      self.textbox.insert(INSERT,closeTag,(textboxTag,"closeTag"))
      if prettyPrint and closeTag and tag.nextSibling:
        s.append("\n")
        self.textbox.insert(INSERT,"\n")
      s = ''.join(s)
    return s


  def renderContents(self,tag,contentIsMatchChild=False,encoding=DEFAULT_OUTPUT_ENCODING, prettyPrint=False,indentLevel=0):
    """Renders the content of the passed in tag to the textbox,
    highlighting any matches with the user's query
    """
    s=[]
    for c in tag:
      text = None
      textboxTag = "nomatch"
      navigableStringIsMatch = False
      if isinstance(c, NavigableString):
        text = c.__str__(encoding)
        if isinstance(self.matches,NoneType) == False:
          if isinstance(self.matches,NavigableString): 
            if c is self.matches:
              navigableStringIsMatch = True
          elif c is self.matches or id(c) in [id(match) for match in self.matches]:
            navigableStringIsMatch = True
      elif isinstance(c, Tag):
        s.append(self.__str__(c,contentIsMatchChild,encoding, prettyPrint, indentLevel))
      if text and prettyPrint:
        text = text.strip()
      if text:
        if prettyPrint:
          s.append(" " * (indentLevel-1))
          self.textbox.insert(INSERT," " * (indentLevel-1))
        s.append(text)
        if contentIsMatchChild or navigableStringIsMatch:
          textboxTag="match"
        self.textbox.insert(INSERT,text,textboxTag)
        if prettyPrint:
          s.append("\n")
          self.textbox.insert(INSERT,"\n")
    return ''.join(s)


# Now here's where all the GUI action is at
class App:
  """This class is the GUI for the BeautifulSoupedUp application"""

  def __init__(self,master):
    emphFont=tkFont.Font(font="Helvetica")
    emphFont['weight']='bold'
    emphFont['size']=9

    regFont=tkFont.Font(font="Helvetica")
    regFont['size']=8

    statsBgCol="#BFCDDB"
    queryFrameBgCol="#99A9C2"
    
    soupQueryFrame=Frame(master,bg=queryFrameBgCol)
    soupQueryFrame.grid(row=0,column=0,sticky=W+E)

    self.lblSoupQualifier=Label(soupQueryFrame,text="soup",bg=queryFrameBgCol,font=emphFont)
    self.lblSoupQualifier.grid(row=0,column=0,sticky=W)

    self.soupQuery = Entry(soupQueryFrame,width=63,font=emphFont)
    self.soupQuery.grid(row=0,column=1,sticky=W+E)

    self.btnRunQuery = Button(soupQueryFrame,text="Run query",font=regFont,command=self.runQuery)
    self.btnRunQuery.grid(row=0,column=2)

    self.prettifyText=BooleanVar()
    self.chkPrettify = Checkbutton(soupQueryFrame,text="prettify",bg=queryFrameBgCol,font=emphFont,
                                   variable=self.prettifyText,onvalue=True,offvalue=False)
    self.chkPrettify.select()
    self.chkPrettify.grid(row=0,column=3)

    soupQueryFrame.grid_columnconfigure(1,weight=1)

    soupMatchFrame=Frame(master,bg="green")
    soupMatchFrame.grid(row=1,column=0,sticky=N+S+W+E)

    self.docText = Text(soupMatchFrame,font=regFont,width=100,height=50)
    self.docText.grid(row=0,column=0,sticky=N+S+W+E,pady=3)

    self.scrollbar = Scrollbar(soupMatchFrame, command=self.docText.yview)
    self.scrollbar.grid(row=0,column=1,sticky=N+S)

    self.docText.config(yscrollcommand=self.scrollbar.set)

    soupMatchFrame.grid_columnconfigure(0,weight=1)
    soupMatchFrame.grid_rowconfigure(0,weight=1)

    statsFrame=Frame(master,bg=statsBgCol)
    statsFrame.grid(row=2,column=0,sticky=W+E)

    self.lblNumberOfMatchesValue=Label(statsFrame,text="...",bg=statsBgCol,font=emphFont)
    self.lblNumberOfMatchesValue.grid(row=0,column=0,sticky=W)

    self.lblNumberOfMatches=Label(statsFrame,text="matches",font=regFont,bg=statsBgCol)
    self.lblNumberOfMatches.grid(row=0,column=1,sticky=W)

    self.lblNumMatchesReturnTypeSeparator=Label(statsFrame,text=" |  ",font=regFont,bg=statsBgCol)
    self.lblNumMatchesReturnTypeSeparator.grid(row=0,column=2,sticky=W)

    self.lblReturnTypeValue=Label(statsFrame,text="...",bg=statsBgCol,font=emphFont)
    self.lblReturnTypeValue.grid(row=0,column=3,sticky=W)

    self.lblReturnType=Label(statsFrame,text="return type",font=regFont,bg=statsBgCol)
    self.lblReturnType.grid(row=0,column=4,sticky=W)

    messageFrame=Frame(master)
    messageFrame.grid(row=3,column=0,sticky=W+E+N+S)
    messageFrame.grid_columnconfigure(0,weight=1)
    messageFrame.grid_rowconfigure(0,weight=1)

    self.statusMessage = Text(messageFrame,bg="#E8ECF1",font=regFont,width=100,height=3,
                              state=DISABLED)
    self.statusMessage.grid(row=0,column=0,sticky=W+E+N+S)
    
    self.statusMessageScroll = Scrollbar(messageFrame,command=self.statusMessage.yview)
    self.statusMessageScroll.grid(row=0,column=1,sticky=N+S)
    self.statusMessage.config(yscrollcommand=self.statusMessageScroll.set)

    master.grid_rowconfigure(1,weight=1,minsize=100)
    master.grid_rowconfigure(3,weight=1,minsize=60)
    master.grid_columnconfigure(0,weight=1)

    self.showExample()


  def printStatusMessage(self,msg):
    self.statusMessage.config(state=NORMAL)
    self.statusMessage.insert(INSERT,msg)
    self.statusMessage.config(state=DISABLED)


  def clearStatusMessage(self):
    self.statusMessage.config(state=NORMAL)
    self.statusMessage.delete(1.0,END)
    self.statusMessage.config(state=DISABLED)


  def clearMarkup(self):
    self.docText.delete(1.0,END)


  def showMatches(self,soup,subSoup,outputTarget):
    """Highlights all of the pieces of text in the markup that the user's soup query
    would match"""
    try:
      self.soupPrinter=BeautifulSoupedUp(soup,subSoup,outputTarget)
      if self.prettifyText.get()==True:
        self.soupPrinter.prettify()
      else:
        print self.soupPrinter.noprettify()
    except:
      self.printStatusMessage("Uh-oh... Although your soup query parsed ok, it looks like " \
                              "there was some trouble highlighting any matches.  " \
                              "Here's the error:\n")
      self.printStatusMessage(traceback.format_exc())
      self.clearMarkup()
      self.showMatches(soup,list(),outputTarget)


  def showStats(self,subSoup):
    """Displays statistics about the subSoup results such as 
    the number of matches and return type"""
    if isinstance(subSoup,ResultSet) or isinstance(subSoup,list):
      self.lblNumberOfMatchesValue.config(text=len(subSoup))
    elif isinstance(subSoup,Tag):
      self.lblNumberOfMatchesValue.config(text='1')
    elif isinstance(subSoup,unicode):
      self.lblNumberOfMatchesValue.config(text='1')
    elif isinstance(subSoup,NoneType):
      self.lblNumberOfMatchesValue.config(text='0')
    else:
      self.lblNumberOfMatchesValue.config(text='?')

    self.lblReturnTypeValue.config(text=str(subSoup.__class__))

  
  def runQuery(self):
    """Reparses the soup in order to find matches for the query
    the user has entered and refreshes the results"""
    self.clearStatusMessage()

    # Retrieve the markup from the Text widget and parse it
    markup = self.docText.get('1.0',END) # Row 1, col 0
    self.clearMarkup()
    self.soup=BeautifulSoup(markup)

    # Evaluate the entered soup query.  If what the user has entered
    # can't be evaluated, print an exception message and show the
    # markup with no matches highlighted.
    subSoupEvalString = ['self.soup',self.soupQuery.get()]
    try:
      subSoup=eval(''.join(subSoupEvalString))
    except:
      self.printStatusMessage("Woops!  Looks like your soup query couldn't be parsed." + 
                               "Check that your syntax is valid.  For the inquisitive " +
                               "(or just plain masochistic), here's the error details:\n")
      self.printStatusMessage(traceback.format_exc())
      self.showMatches(self.soup,list(),self.docText)
      return

    self.showStats(subSoup)    
    self.showMatches(self.soup,subSoup,self.docText)
    

  def showExample(self):
    """Presents an example piece of markup with an example query and highlighted
    markup to demonstrate how the utility can be used"""
    
    self.doc=['<html><head><title>Page title</title></head>',
       '<body><p id="firstpara" align="center">This is paragraph <b>one</b>.',
       '<p id="secondpara" align="blah">This is paragraph <b>two</b>.',
       '</html>']
    self.docText.insert(INSERT,''.join(self.doc))
    self.soupQuery.insert(0,"('b')")
    self.runQuery()
    startupMessage = "Yo!  Shown highlighted above is an example of what Beautiful Soup would " \
                     "return if you were to use the query soup('b'), where your soup was the " \
                     "html markup shown above.  Try out soup('p') and see what gets " \
                     "highlighted.  Once you're ready to work with your own markup, " \
                     "delete the markup already shown and type/paste your own markup into " \
                     "the text box instead.  Now when you run another soup query, it'll be " \
                     "run on your own markup."
    self.printStatusMessage(startupMessage)

if __name__ == '__main__':
  root = Tk()
  root.title("Beautiful Souped Up! v " + __version__)

  app = App(root)

root.mainloop()
