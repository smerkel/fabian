#!/usr/bin/env python -w 
"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:erik.knudsen@risoe.dk
"""

import string
import edfimage, tifimage, adscimage, brukerimage, marccdimage,bruker100image,pnmimage
import re,os,os.path,sys,time

class image_file_series:
  def __init__(self,filename=None):
    self.filename=filename
    stem,self.number,self.filetype=deconstruct_filename(filename)
    self.img=None
    self.noread=False
    #setup a few things to start a file series.
    #self.p=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
    #self.m=re.match(self.p,filename)
    
    #store a list of 100 nearby matches
    #this might be a good idea - for now we don't use it
    #g=glob.glob(m.group(1)+'*'+.group(3))
    #for t in g:
    #  self.store[t[len(m.group(1):-len(m.group(3)]=t
    #self.__current=t[len(m.group(1):-len(m.group(3)]
    
  def reset_series(self,filename,number=-1,filetype=None):
    num,ft=deconstruct_filename(filename)
    if filetype==None:
      self.filetype=ft
    else:
      self.filetype=filetype
    if number==-1:
      self.number=number
    else:
      self.number=num
   
  def __openimage(self,filename=None):
    if filename==None:
      filename=self.filename
    self.img=eval( self.filetype+'image.'+self.filetype+'image()')
    try:
      if self.noread:
        if not os.path.exists(filename):
          raise IOError, 'No such file or directory %s' % filename
      else:
	self.img.read(filename)
    except IOError:
      raise
   
  def current(self,toPIL=True):
    if not self.img:
      self.__openimage()
    if toPIL:
      return self.img.toPIL16()
    else:
      return self.img
      
  def next(self,steps=1):
    newnum=self.number+steps
    newfilename=construct_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError,"new filename == old filename"
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError, msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True

  def prev(self,steps=1):
    newnum=self.number-steps
    newfilename=construct_filename(self.filename,newnum)
    if newfilename==self.filename:
      raise ValueError,"new filename == old filename"
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      newfilename=construct_filename(self.filename,newnum,padding=False)
      if newfilename==self.filename:
	raise ValueError,"new filename == old filename"
      try:
	#that didn't work - so try the unpadded version
	self.openimage(newfilename)
      except IOError:
        msg="No such file: %s " %(newfilename)
	raise IOError, msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True
  

  def jump(self,newnum,noconvert=False):
    newfilename=construct_filename(self.filename,newnum)
    try:
      self.__openimage(newfilename)#try to open that file
    except IOError:
      msg="No such file: %s " %(newfilename)
      raise IOError,msg
    #image loaded ok
    self.filename=newfilename
    self.number=newnum
    return True
  
  def loop(self,endnum=999999):
    #a generator for looping through the images in a series with a for loop
    num=self.number
    while num<endnum:
      yield(self.img)
      try:
	self.next()
      except IOError:
	break
      num=num+1
	
#stand-alone functions
def construct_filename(oldfilename,newfilenumber,padding=True,pattern=None):
    #some code to replace the filenumber in oldfilename with newfilenumber
    #by figuring out how the files are named
    if not pattern:
      pattern=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
    m=re.match(pattern,oldfilename)
    if padding==False:
      return m.group(1) + str(newfilenumber) + m.group(3)
    if m.group(2)!='':
      return m.group(1) + string.zfill(newfilenumber,len(m.group(2))) + m.group(3)# +'.' + m.group(4)
    else:
      return oldfilename

def deconstruct_filename(filename, pattern=None):
    if not pattern:
      pattern=re.compile(r"^(.*?)(-?[0-9]{0,4})(\D*)$")
    m=re.match(pattern,filename)
    if m==None or m.group(2)=='':
      number=0;
    else:
      number=int(m.group(2))
    ext=os.path.splitext(filename)
    filetype={'edf': 'edf',
      'gz': 'edf',
      'bz2': 'edf',
      'pnm' : 'pnm',
      'pgm' : 'pnm',
      'pbm' : 'pnm',
      'tif': 'tif',
      'tiff': 'tif',
      'img': 'adsc',
      m.group(2): 'bruker',
      'sfrm': 'bruker100'}[ext[1][1:]]
    return (m.group(1),number,filetype)

def extract_filenumber(filename):
    return deconstruct_filename(filename)[1]

def extract_stem(filename):
    return deconstruct_filename(filename)[0]

def extract_filetype(filename):
    return deconstruct_filename(filename)[2]

if __name__=='__main__':
  import sys,os,time
  b=time.clock()
  fs=file_series_iterator(sys.argv[1])
  print fs.filename,fs.current(toPIL=False)
  while fs.next() and fs.number<20:
    print fs.filename,fs.current(toPIL=False)
  e=time.clock()
  print (e-b)
