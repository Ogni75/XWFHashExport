#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
X-Ways Extension
Only runnable with X-Ways 32-bit and python x-tension
Export a hashlist with several hashvalues per file
Hashlist contains md4, ed2k, md5, sha1 and sha256

Ingo Braun
Osnabrück
Germany

Questions:  xtension@ilmirmal.de

I know, I'm not the best programmer so the code is need to be improved.
If you take changes or improvements, it would be nice to see it. Please send it to me...


    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
    der GNU General Public License, wie von der Free Software Foundation,
    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
    veröffentlichten Version, weiterverbreiten und/oder modifizieren.

    Dieses Programm wird in der Hoffnung, dass es nützlich sein wird, aber
    OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
    Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
    Siehe die GNU General Public License für weitere Details.

    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
    Programm erhalten haben. Wenn nicht, siehe <http://www.gnu.org/licenses/>.

'''

import XWF

import hashlib
import os
from Tkinter import *
from tkFileDialog import *
from time import *
#import multiprocessing

# import re
# import zlib
# import sqlite3
# import sys
# import codecs

VERSION = "0.19"
home = os.path.expanduser("~") + "\\Desktop\\"

### changable variables

XWReportTable = "HashSetExport"  # Reporttable text
hfilepre = "HashExport_"  # Hashfileprefix
hfilesuf = ".txt"  # Hashfilesuffix
header = "**XWaysHASHExport**\n"  # Header of Hashfile
exportPath = home  # standard path to save Hashfile (userhome)
evidencename_regex = r"^[0-9]{4}_[0-9]{4,5}"  # descripes the evidence naming convention
casenamelength = 12  # maximal casename length
vbs = "201700000000"  # standard casename
casenameregex = r"^[0-9]"  # allowed characters
placeholder = "*-*"  # hash placeholder, if no hash calculated
seperator = ";"  # seperator tsv=\t, csv=;
title = True  # title line after header line
titletext = "Filename" + seperator + \
            "Filesize" + seperator + \
            "MD4" + seperator + \
            "ED2K" + seperator + \
            "MD5" + seperator + \
            "SHA1" + seperator + \
            "SHA256" + seperator + \
            "Evidence" + seperator + \
            "Date\n"

STATISTIK = True  # write statistik file
STATISITIKFILE = "./statistik.log"  # path to statistikfile

###  debugging options ###
### real much data to write; follow up every file ###
DEBUG = False
DEBUGLOG = True
DEBUGFILE = "./debug.log"  # path to debugfile

### textfields to localisation

txt_about = "Hashwertexport fuer PIOS DB"
txt_unknownevidence = "unbekanntes Asservat"
txt_lastevidence = "vorheriges Asservat"
txt_actualevidence = "Export aus Asservat"
txt_evidencefinished = "Asservat abgeschlossen"
txt_saveto = "Speicherpfad"
txt_casenameshort = "Nivadisnummer zu kurz"
txt_casenamelong = "Nivadisnummer zu lang"
txt_casenamewrongchar = "Fehlerhafte Zeichen"
txt_casenamenoentry = "Eingabe erforderlich"
txt_caseentrylabel = "Hashwertexport fuer die KiPo DB der PIOS"
txt_casenameentry = "Nivadisnummer"
txt_seconds = "Sekunden"
txt_minutes = "Minuten"
txt_hours = "Stunden"
txt_exportfinished = "HashExport abgeschlossen"
txt_exportedhashes = "exportierte (neue) Hashsets"
txt_ignoredfiles = "ignorierte Dateien"
txt_errorfiles = "fehlerhafte Dateien"
txt_scriptruntime = "Laufzeit"
txt_calculatedbytes = "Datendurchsatz"
txt_writtenstatistik = "Statistikdaten geschrieben"
txt_nowrittenstatistik = "keine Statistikdaten geschrieben"

XTINITIALIZE = False  # first run; var to restrain output

### some counter
minfilesize = 1  # minimal file size
maxfilesize = 2147483648  # maximal file size
fileCounter = 0  # processed files in round
fileIgnored = 0  # ignored file (marked as saved, to small/big to hash)
writeCounter = 0  # count every round to write; write every 1000 hashes in db/textfile, count +1
fileError = 0  # error during calculation
calculatedbytes = 0  # bytecounter
numbercpu = 1  # numbers of cpu

### empty some vars
old_evidence = ""
act_evidence = ""
hashString = ""

### XwaysReport Table Association

XWnoExportbig = "no " + XWReportTable + "(to big)"
XWnoExportsmall = "no " + XWReportTable + "(to small)"
XWnoExporterror = "no " + XWReportTable + "(error)"

lt = localtime()

savedate = strftime("%d.%m.%Y", lt)


# This class provided by X-Ways OutputRedirector sample script; I included it in this script to prevent needing two files
class redirector:
    def write(self, text):
        # flag=1: Python calls print a second time to print the line feed
        # so we don't need to do this here
        XWF.OutputMessage(text, 1)
        return


# The first function that is called when a Python X-Tension is called
def XT_Init(nVersion, nFlags, hMainWnd, lpReserved):
    sys.stderr = sys.stdout = redirector()  # instantiates redirector class object provided by X-Ways (so print statements output to messages window)

    global XTINITIALIZE
    global HFILE
    global vbs
    global scriptstarttime

    if XTINITIALIZE:
        print('X-Tension initialization')
        return

    if not XTINITIALIZE:

        vbsEingabe()

        if DEBUG:
            print ('__________________________')
            print ('DEBUG Modus')
            print (HFILE)
            print ('__________________________')

        HFILE = exportPath + hfilepre + vbs + hfilesuf

        if not os.path.isfile(HFILE):
            hashfileheader = header
            if title:
                hashfileheader += titletext

            write_hashfile(hashfileheader)

        scriptstarttime = clock()
        if DEBUGLOG:
            starttime = "start" + str(scriptstarttime) + "\n"
            write_debugfile(starttime)

    return


# Describes X-Tension, required function
def XT_About(hParentWnd, lpReserved):
    global XTINITIALIZE
    XTINITIALIZE = True
    print('\n' + txt_about + ' (Version: ' + VERSION + ')')
    print ('__________________________________________')

    return


# Called before items or search hits are processed individually, required function
def XT_Prepare(hVolume, hEvidence, nOpType, lpReserved):
    global act_evidence
    global old_evidence
    global XTINITIALIZE

    if not XTINITIALIZE:

        numbercpu = multiprocessing.cpu_count()

        if DEBUG:
            print ('Found processors :' + str(numbercpu))
        if DEBUGLOG:
            debugInformation = "Number of processors: " + str(numbercpu) + "\n"
            write_debugfile(debugInformation)

        volname = XWF.GetVolumeName(hVolume, 2)
        assname = volname.split(',')

        if not (re.search(evidencename_regex, assname[0])):
            act_evidence = txt_unknownevidence
        else:
            act_evidence = assname[0]

        # volItemCount=XWF.GetItemCount(hVolume) #ist nur gesamtliste nicht nur markierter teil! **TEST**

        if DEBUG:
            print(txt_lastevidence + ': ' + old_evidence)
            print(txt_actualevidence + ': ' + act_evidence)
            print ('__________________________')
        if old_evidence != act_evidence:
            print (txt_evidencefinished + ": " + act_evidence)

        old_evidence = act_evidence

    return


# Use for search X-Tensions (loaded from search dialog within X-Ways), required function
def XT_ProcessSearchHit(iSize, nItemID, nRelOfs, nAbsOfs, lpOptionalHitPtr, lpSearchTermID, nLength, nCodePage, nFlags):
    return


# Implement and export this function if you merely need to retrieve information about the file but don't need to read its contents (performance benefit)
def XT_ProcessItem(nItem, reserved):
    return


def vbsEingabe():
    global XTINITIALIZE

    statusmessage = txt_saveto + ": " + exportPath

    #
    def center_window(width=230, height=90):
        # get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # calculate position x and y coordinates
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def senden(event=None):
        global vbs
        vbs = eingabe.get()
        if len(vbs) < casenamelength:
            statusbar = Label(root, text=txt_casenameshort, bd=1, relief=SUNKEN, anchor=W, fg="red")
            statusbar.grid(row=4, columnspan=4, sticky=NSEW)
            statusbar.bind("<Button-1>", changePath)

        if len(vbs) > casenamelength:
            statusbar = Label(root, text=txt_casenamelong, bd=1, relief=SUNKEN, anchor=W, fg="red")
            statusbar.grid(row=4, columnspan=4, sticky=NSEW)
            statusbar.bind("<Button-1>", changePath)

        if not re.search(casenameregex, vbs):
            statusbar = Label(root, text=txt_casenamewrongchar, bd=1, relief=SUNKEN, anchor=W, fg="red")
            statusbar.grid(row=4, columnspan=4, sticky=NSEW)
            statusbar.bind("<Button-1>", changePath)

        if len(vbs) == 0:
            statusbar = Label(root, text=txt_casenamenoentry, bd=1, relief=SUNKEN, anchor=W, fg="red")
            statusbar.grid(row=4, columnspan=4, sticky=NSEW)
            statusbar.bind("<Button-1>", changePath)

        if len(vbs) == 12:
            root.destroy()

    def cancel(event=None):
        vbs = ""
        XTINITIALIZE = True
        root.destroy()

    def changePath(event):

        dirname = askdirectory()

    root = Tk(baseName='vbsEingabe')

    root.title("Hashexport")
    center_window()

    lab1 = Label(root, text=txt_caseentrylabel, anchor=E).grid(row=1, columnspan=2)

    lab = Label(root, text=txt_casenameentry + ": ", anchor=W).grid(row=2, column=0)

    eingabe = Entry(root, text=vbs)
    eingabe.grid(row=2, column=1)

    but = Button(root, text="OK", command=senden, anchor=E).grid(row=3, column=0, sticky=E, pady=2)

    but = Button(root, text="Cancel", command=cancel, anchor=E).grid(row=3, column=1, sticky=W, pady=2)

    statusbar = Label(root, text=statusmessage, bd=1, relief=SUNKEN, anchor=W)
    statusbar.grid(row=4, columnspan=4, sticky=NSEW)
    statusbar.bind("<Button-1>", changePath)

    root.bind('<Return>', senden)

    root.mainloop()


def hashfile(fileContent, algorithm):
    algorithm.update(fileContent)

    return algorithm.hexdigest()


def pdnaanalysis(fileContent):
    return placeholder


def read_unicode(text, charset='utf-8'):
    if isinstance(text, basestring):
        if not isinstance(text, unicode):
            text = unicode(obj, charset)
    return text


def ed2k(fileContent):
    md4 = hashlib.new('md4').copy

    def splitup(content):
        startdata = 0
        enddata = 0
        buffersize = 9728000

        while True:

            enddata += buffersize
            x = f[startdata:enddata]

            startdata += buffersize

            if x:
                yield x
            else:
                return

    def md4_hash(data):
        m = md4()
        m.update(data)
        return m

    filechunk = splitup(filecontent)
    hashes = [md4_hash(data).digest() for data in filechunk]
    if len(hashes) == 1:
        return hashes[0].encode("hex")
    else:
        return md4_hash(reduce(lambda filechunk, d: filechunk + d, hashes, "")).hexdigest()


def write_debugfile(debugInformation):
    try:
        with open(DEBUGFILE, 'a') as file:
            file.write(debugInformation.encode('utf8'))
    except:
        print ('Error writing debug values')
    return


def write_hashfile(hashString):
    try:
        with open(HFILE, 'a') as hashfile:
            hashfile.write(hashString.encode('utf8'))
    except:
        print ('Error writing hash values')
    return


# Implement and export this function if you need to read the item's contents, which you can do using the hItem parameter (file handle)
def XT_ProcessItemEx(nItem, hItem, reserved):
    global XTINITIALIZE

    global fileCounter
    global fileIgnored
    global writeCounter
    global fileError
    global hashString
    global hashset
    global act_evidence
    global calculatedbytes

    offset = 0
    maxsize = 2199023255552
    hashset = []

    md4Hash = placeholder
    ed2kHash = placeholder
    md5Hash = placeholder
    sha1Hash = placeholder
    sha256Hash = placeholder
    pdna = placeholder

    if not XTINITIALIZE:
        filesize = XWF.GetItemSize(nItem)
        # filename = XWF.GetItemName(nItem).encode('utf8', 'replace')

        filename = XWF.GetItemName(nItem)  # .decode(encoding='utf8')
        filename = read_unicode(filename)
        if DEBUGLOG:
            debugInformation = filename + seperator + str(filesize) + seperator + str(nItem) + "\n"
            write_debugfile(debugInformation)

        # volname = XWF.GetItemInformation(hItem, 1)                                    **TEST**
        # print ('volname: ' + volname)                     ##Ausgabe kompletter Pfad **TEST**


        reportTable = XWF.GetReportTableAssocs(nItem)
        if (re.search(XWReportTable, reportTable)):
            fileIgnored += 1
            return

        fileCounter += 1

        if fileCounter == 1000:
            if DEBUG:
                print ("write round:" + str(writeCounter))

            write_hashfile(hashString)

            hashString = ""
            writeCounter += 1
            fileCounter = 0

        if DEBUG:
            print ('processing ' + filename)
            print ('__________________________')

        if (offset < filesize) and (filesize < maxfilesize):

            try:

                fileContent = XWF.Read(hItem, offset, filesize)

                md4Hash = hashfile(fileContent, hashlib.new('md4'))

                if filesize < 9728001:
                    ed2kHash = md4Hash
                else:
                    ed2kHash = ed2k(fileContent)

                md5Hash = hashfile(fileContent, hashlib.md5())

                sha1Hash = hashfile(fileContent, hashlib.sha1())

                sha256Hash = hashfile(fileContent, hashlib.sha256())

                # pdna = pdnaanalysis(fileContent) ###not implemented

                calculatedbytes += filesize

                if DEBUG:
                    print ('Only debug Information:')
                    print ('ItemID:' + str(nItem))
                    print ('Size: ' + str(filesize))
                    print ('MD4: ' + md4Hash)
                    print ('ED2K: ' + ed2kHash)
                    print ('MD5: ' + md5Hash)
                    print ('sha1: ' + sha1Hash)
                    print ('sha256: ' + sha256Hash)
                    print ('========================')
                    print ('__________________________')
                #
                filevalue = {}
                filevalue['exportdate'] = savedate
                filevalue['evidence'] = act_evidence
                filevalue['name'] = filename
                filevalue['size'] = filesize
                filevalue['MD4'] = md4Hash
                filevalue['ED2K'] = ed2kHash
                filevalue['MD5'] = md5Hash
                filevalue['SHA1'] = sha1Hash
                filevalue['SHA256'] = sha256Hash
                # filevalue['PDNA'] = pdna      ###not implemented

                hashset.append(filevalue)

                hashString += filename + seperator + str(
                    filesize) + seperator + md4Hash + seperator + ed2kHash + seperator + md5Hash + \
                              seperator + sha1Hash + seperator + sha256Hash + seperator + act_evidence + seperator + savedate + "\n"

                XWF.AddToReportTable(nItem, XWReportTable, 1)

            except:

                XWF.AddToReportTable(nItem, XWnoExporterror, 1)
                fileError += 1
                fileCounter -= 1


        else:

            fileIgnored += 1
            fileCounter -= 1
            if offset >= filesize:
                XWF.AddToReportTable(nItem, XWnoExportsmall, 1)
            else:
                XWF.AddToReportTable(nItem, XWnoExportbig, 1)
            if DEBUG:
                print ('File too small; no Hash calculated')
        # XWF.ShowProgress()

        XWF.ProcessMessages()

    return


# Called when other operations have completed, required function
def XT_Finalize(hVolume, hEvidence, nOpType, lpReserved):
    return


# Called just before the DLL is unloaded to give you a chance to dispose any allocated memory, save certain data permanently etc., required function
def XT_Done(lpReserved):
    # if not initalize:

    if not XTINITIALIZE:

        if fileCounter > 0:
            write_hashfile(hashString)

        hashExported = writeCounter * 1000 + fileCounter

        scriptendtime = clock()

        scriptruntime = scriptendtime - scriptstarttime

        if (scriptruntime < 60):
            scriptrun = "%1.2f " % scriptruntime + txt_seconds
        if (scriptruntime > 60) and (scriptruntime < 3600):
            scriptrun = "%1.2f " % (scriptruntime / 60) + txt_minutes
        if (scriptruntime > 3600):
            scriptrun = "%1.2f " % (scriptruntime / 3600) + txt_hours

        print('\n' + txt_exportfinished)

        if hashExported > 0:
            print(txt_exportedhashes + ':\t' + str(hashExported))
        if fileIgnored > 0:
            print(txt_ignoredfiles + ':\t' + str(fileIgnored))
        if fileError > 0:
            print(txt_errorfiles + ':\t' + str(fileError))
        print(txt_scriptruntime + ': ' + scriptrun)
        print(txt_calculatedbytes + ': \t' + str(calculatedbytes) + ' Bytes ')

        if STATISTIK:
            print ('__________________________')
            try:
                with open(STATISITIKFILE, 'a') as file:
                    statistikstring = str(hashExported) + seperator + str(fileIgnored) + seperator + str(
                        fileError) + seperator + str(
                        scriptrun) + seperator + str(calculatedbytes) + "\n"
                    file.write(statistikstring)
                print(txt_writtenstatistik)
            except:
                print(txt_nowrittenstatistik)
        if DEBUGLOG:
            endtime = "end:" + str(scriptendtime) + "\n"
            write_debugfile(endtime)

        print ('__________________________')
        print('Have a nice day')
        print ('__________________________')

    return


if __name__ == "__main__":
    print ('\nScript not executeable!\n')
    print ('Only usable as X-Ways X-tension (32-bit)')
    quit()
