import csv
import xml.dom.minidom
import sys
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

#----- read data from a CSV file
def readCSV(csvReader, Area, Pt, time, X, Y, T, H):
  row0 = csvReader.next()
  csvReader.next()
  for row in csvReader:
    Area.append(row['Area'])
    Pt.append(row['Point'])
    time.append(row['Time'])
    X.append(float(row['Longitude']))
    Y.append(float(row['Latitude']))
    T.append(float(row['Temp']))
    H.append(float(row['Humi']))
  return row0['Area']

#----- define and return a color map
def createColorMap():

  cdict = {'red':   ((0.00, 0, 0),
                     (0.25, 0, 0),
                     (0.50, 0, 0),
                     (0.75, 1, 1),
                     (1.00, 1, 1)),
           'green': ((0.00, 0, 0),
                     (0.25, 1, 1),
                     (0.50, 1, 1),
                     (0.75, 1, 1),
                     (1.00, 0, 0)),
           'blue':  ((0.00, 1, 1),
                     (0.25, 1, 1),
                     (0.50, 0, 0),
                     (0.75, 0, 0),
                     (1.00, 0, 0))}

  return mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)

#----- make a scatter plot
def plotScatter(Area, Pt, X, Y, Z, Zmin, Zmax, coord, 
                sctfile, figfile, numfile,
                cmap, inch=400, radius=40, dpi=200):

  cm = mpl.cm.get_cmap(cmap)
  plt.axes().set_aspect('equal')
  # set figure size in inch
  plt.figure(figsize=(inch*(coord[1]-coord[0]),
                      inch*(coord[3]-coord[2]) ))
  plt.axes().get_yaxis().set_visible(False) 
  plt.axes().get_xaxis().set_visible(False) 
  sc = plt.scatter(X, Y, c=Z, 
                   vmin=Zmin,
                   vmax=Zmax,
                   s=radius, 
                   cmap=cm, 
                   edgecolors='none')

  plt.xlim((coord[0:2]))
  plt.ylim((coord[2:4]))
  plt.savefig(sctfile, 
              format='png',
              bbox_inches="tight",
              dpi=dpi,
              pad_inches=0.0,
              transparent=True)

  #--- plot figures of the variable
  plt.cla()
  for i in range(len(X)):
    plt.text(X[i]+0.00015,Y[i]-0.000075,"%3.1f" % Z[i], 
             size=5, color="white")
  plt.savefig(figfile, 
              format='png',
              bbox_inches="tight",
              dpi=dpi,
              pad_inches=0.0,
              transparent=True)

  #--- plot the numbers of observation points
  plt.cla()
  for i in range(len(Area)):
    plt.text(X[i]-0.000175,Y[i]+0.00015,"%s-%s" % (Area[i], Pt[i]), 
             size=5, color="white")
  plt.savefig(numfile, 
              format='png',
              bbox_inches="tight",
              dpi=dpi,
              pad_inches=0.0,
              transparent=True)

#----- make a colorbar
# ref. http://matplotlib.sourceforge.net/examples/api/colorbar_only.html
def makeColorBar(Zmin, Zmax, coord, cmap, imgfile):
  # Make a figure and axes with dimensions as desired.
  fig = plt.figure(figsize=(8,1))
  ax1 = fig.add_axes([0.05, 1.65, 1., 0.15])
  norm = mpl.colors.Normalize(vmin=Zmin, vmax=Zmax)
  cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                  norm=norm,
                                  orientation='horizontal')
  cb1.set_label('[deg]',position=(0.98,0))
  plt.savefig(imgfile, 
              format='png',
              bbox_inches="tight",
              dpi=120,
              pad_inches=0.1,
              transparent=False)

def createKML(fileName,title,varlist,
              imgfiles,figfile,numfile,cbarfile,
              minmax,url,coord):
  # This constructs the KML document from the CSV file.
  kmlDoc = xml.dom.minidom.Document()
  
  kmlElement = kmlDoc.createElementNS('http://earth.google.com/kml/2.2', 'kml')
  kmlElement.setAttribute('xmlns','http://earth.google.com/kml/2.2')
  kmlElement = kmlDoc.appendChild(kmlElement)
  folderElement = kmlDoc.createElement('Folder')
  folderElement = kmlElement.appendChild(folderElement)
  #--- name
  nameElement = kmlDoc.createElement('name')
  valueText = kmlDoc.createTextNode(title)
  nameElement.appendChild(valueText)
  folderElement.appendChild(nameElement)
  #--- GroundOverlay
  for var in varlist:
    olElement = kmlDoc.createElement('GroundOverlay')
    folderElement.appendChild(olElement)
    #--- name in GroundOverlay
    olnameElement = kmlDoc.createElement('name')
    valueText = kmlDoc.createTextNode("%s %s" % (var,minmax[var]))
    olnameElement.appendChild(valueText)
    olElement.appendChild(olnameElement)
    #--- Icon in GroundOverlay
    iconElement = kmlDoc.createElement('Icon')
    hrefElement = kmlDoc.createElement('href')
    valueText = kmlDoc.createTextNode('%s%s' % (url,imgfiles[var]) )
    hrefElement.appendChild(valueText)
    iconElement.appendChild(hrefElement)
    olElement.appendChild(iconElement)
    #--- Icon in GroundOverlay
    latlonElement = kmlDoc.createElement('LatLonBox')
    # north
    nElement = kmlDoc.createElement('north')
    latlon = kmlDoc.createTextNode(str(coord[3]))
    nElement.appendChild(latlon)
    latlonElement.appendChild(nElement)
    # south
    sElement = kmlDoc.createElement('south')
    latlon = kmlDoc.createTextNode(str(coord[2]))
    sElement.appendChild(latlon)
    latlonElement.appendChild(sElement)
    # east
    eElement = kmlDoc.createElement('east')
    latlon = kmlDoc.createTextNode(str(coord[1]))
    eElement.appendChild(latlon)
    latlonElement.appendChild(eElement)
    # west
    wElement = kmlDoc.createElement('west')
    latlon = kmlDoc.createTextNode(str(coord[0]))
    wElement.appendChild(latlon)
    latlonElement.appendChild(wElement)
    # rotation
    rElement = kmlDoc.createElement('rotation')
    latlon = kmlDoc.createTextNode('0.0')
    rElement.appendChild(latlon)
    latlonElement.appendChild(rElement)

    olElement.appendChild(latlonElement)
    #documentElement = kmlDoc.createElement('Document')
    #documentElement = kmlElement.appendChild(documentElement)

  #--- GroundOverlay
  olElement = kmlDoc.createElement('GroundOverlay')
  folderElement.appendChild(olElement)
  #--- name in GroundOverlay
  olnameElement = kmlDoc.createElement('name')
  valueText = kmlDoc.createTextNode("Temperature figures")
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Visibility in ScreenOverlay
  olnameElement = kmlDoc.createElement('visibility')
  valueText = kmlDoc.createTextNode('0')
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Icon in GroundOverlay
  iconElement = kmlDoc.createElement('Icon')
  hrefElement = kmlDoc.createElement('href')
  valueText = kmlDoc.createTextNode('%s%s' % (url,figfile) )
  hrefElement.appendChild(valueText)
  iconElement.appendChild(hrefElement)
  olElement.appendChild(iconElement)
  #--- Icon in GroundOverlay
  latlonElement = kmlDoc.createElement('LatLonBox')
  # north
  nElement = kmlDoc.createElement('north')
  latlon = kmlDoc.createTextNode(str(coord[3]))
  nElement.appendChild(latlon)
  latlonElement.appendChild(nElement)
  # south
  sElement = kmlDoc.createElement('south')
  latlon = kmlDoc.createTextNode(str(coord[2]))
  sElement.appendChild(latlon)
  latlonElement.appendChild(sElement)
  # east
  eElement = kmlDoc.createElement('east')
  latlon = kmlDoc.createTextNode(str(coord[1]))
  eElement.appendChild(latlon)
  latlonElement.appendChild(eElement)
  # west
  wElement = kmlDoc.createElement('west')
  latlon = kmlDoc.createTextNode(str(coord[0]))
  wElement.appendChild(latlon)
  latlonElement.appendChild(wElement)
  # rotation
  rElement = kmlDoc.createElement('rotation')
  latlon = kmlDoc.createTextNode('0.0')
  rElement.appendChild(latlon)
  latlonElement.appendChild(rElement)
  #
  olElement.appendChild(latlonElement)
  #documentElement = kmlDoc.createElement('Document')
  #documentElement = kmlElement.appendChild(documentElement)

  #--- GroundOverlay
  olElement = kmlDoc.createElement('GroundOverlay')
  folderElement.appendChild(olElement)
  #--- name in GroundOverlay
  olnameElement = kmlDoc.createElement('name')
  valueText = kmlDoc.createTextNode("Area# - Point#")
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Visibility in ScreenOverlay
  olnameElement = kmlDoc.createElement('visibility')
  valueText = kmlDoc.createTextNode('0')
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Icon in GroundOverlay
  iconElement = kmlDoc.createElement('Icon')
  hrefElement = kmlDoc.createElement('href')
  valueText = kmlDoc.createTextNode('%s%s' % (url,numfile) )
  hrefElement.appendChild(valueText)
  iconElement.appendChild(hrefElement)
  olElement.appendChild(iconElement)
  #--- Icon in GroundOverlay
  latlonElement = kmlDoc.createElement('LatLonBox')
  # north
  nElement = kmlDoc.createElement('north')
  latlon = kmlDoc.createTextNode(str(coord[3]))
  nElement.appendChild(latlon)
  latlonElement.appendChild(nElement)
  # south
  sElement = kmlDoc.createElement('south')
  latlon = kmlDoc.createTextNode(str(coord[2]))
  sElement.appendChild(latlon)
  latlonElement.appendChild(sElement)
  # east
  eElement = kmlDoc.createElement('east')
  latlon = kmlDoc.createTextNode(str(coord[1]))
  eElement.appendChild(latlon)
  latlonElement.appendChild(eElement)
  # west
  wElement = kmlDoc.createElement('west')
  latlon = kmlDoc.createTextNode(str(coord[0]))
  wElement.appendChild(latlon)
  latlonElement.appendChild(wElement)
  # rotation
  rElement = kmlDoc.createElement('rotation')
  latlon = kmlDoc.createTextNode('0.0')
  rElement.appendChild(latlon)
  latlonElement.appendChild(rElement)
  #
  olElement.appendChild(latlonElement)
  #documentElement = kmlDoc.createElement('Document')
  #documentElement = kmlElement.appendChild(documentElement)

  #----- GroundOverlay
  olElement = kmlDoc.createElement('ScreenOverlay')
  folderElement.appendChild(olElement)
  #--- name in ScreenOverlay
  olnameElement = kmlDoc.createElement('name')
  valueText = kmlDoc.createTextNode('ColorBar')
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Visibility in ScreenOverlay
  olnameElement = kmlDoc.createElement('visibility')
  valueText = kmlDoc.createTextNode('1')
  olnameElement.appendChild(valueText)
  olElement.appendChild(olnameElement)
  #--- Icon in ScreenOverlay
  iconElement = kmlDoc.createElement('Icon')
  hrefElement = kmlDoc.createElement('href')
  valueText = kmlDoc.createTextNode('%s%s' % (url,cbarfile) )
  hrefElement.appendChild(valueText)
  iconElement.appendChild(hrefElement)
  olElement.appendChild(iconElement)
  #--- overlayXY in ScreenOverlay
  olnameElement = kmlDoc.createElement('overlayXY x="0" y="0" xunits="fraction" yunits="fraction"')
  olElement.appendChild(olnameElement)
  #--- screenXY in ScreenOverlay
  olnameElement = kmlDoc.createElement('screenXY x="0" y="0" xunits="fraction" yunits="fraction"')
  olElement.appendChild(olnameElement)
  #--- rotationXY in ScreenOverlay
  olnameElement = kmlDoc.createElement('rotationXY x="0" y="0" xunits="fraction" yunits="fraction"')
  olElement.appendChild(olnameElement)
  #--- size in ScreenOverlay
  olnameElement = kmlDoc.createElement('size x="0.75" y="0" xunits="fraction" yunits="fraction"')
  olElement.appendChild(olnameElement)

  #for row in csvReader:
  #  placemarkElement = createPlacemark(kmlDoc, row, order)
  #  documentElement.appendChild(placemarkElement)
  kmlFile = open(fileName, 'w')
  kmlFile.write(kmlDoc.toprettyxml('  ', newl = '\n', encoding = 'utf-8'))

def main():
  try:
    csvfile=sys.argv[1]
  except:
    print("[Error] Specify a csv file.")
    sys.exit()

  kmlfile = csvfile
  kmlfile = kmlfile.replace("csv", "kml")

  fi = open(csvfile,"r")
  line = fi.readline() # Skip the first line
  line = fi.readline() # This line contains column titles.
  fi.close()
  order = line.rstrip().split(',')
  #order = ['Area','Point','Time','Latitude','Longitude','Temp','Humi']

  # define arrays
  Area = []
  Pt = []
  time = []
  X = []
  Y = []
  T = []
  H = []

  #--- parameters
  inch   = 400 # inch per latitude
  radius = 40  # radius of a spot [pixel]
  dpi    = 200 # dot per inch
  Tmin   = 30. # minimum range of T
  Tmax   = 33. # maximum range of T
  Tmin   = 23. # minimum range of T
  Tmax   = 27. # maximum range of T
  auto_range = False # set True for automatically adjusting the colormap

  #--- read from CSV file
  csvreader = csv.DictReader(open(csvfile),order)
  title = readCSV(csvreader, Area, Pt, time, X, Y, T, H)
  print(title)
  margin = 0.0005
  coord = (min(X)-margin, max(X)+margin, min(Y)-margin, max(Y)+margin)

  #--- color map
  cmap = createColorMap()

  #--- dump image files
  minmax = {}

  #varlist = ['Temperature','Humidity']
  varlist = ['Temperature']
  imgfiles = {}
  for var in varlist:
    imgfile = csvfile
    imgfile = imgfile.replace("csv", ("%s.png") % var)
    imgfiles[var] = imgfile
  figfile = csvfile
  figfile = figfile.replace("csv", "figures.png")
  numfile = csvfile
  numfile = numfile.replace("csv", "numbers.png")
  # Temperature scatter
  if auto_range:
    Tmin = min(T)
    Tmax = max(T)
  plotScatter(Area, Pt, X, Y, T, Tmin, Tmax, coord, 
              imgfiles['Temperature'], figfile, numfile,
              cmap, inch, radius, dpi)
  minmax['Temperature'] = "(%4.1f-%4.1f deg)" % (min(T),max(T))
  
  #--- make a Colorbar image file
  cbarfile = csvfile
  cbarfile = cbarfile.replace("csv", "colorbar.png")
  makeColorBar(Tmin, Tmax, coord, cmap, cbarfile)

  #--- create KML
  url = 'file:///Users/ogawa/Documents/research/GoogleMapsAPI/'
  url = 'C:\\Documents and Settings\\fluid\heat\\'
  url = os.getcwd()+'\\'
  kml = createKML(kmlfile,title,varlist,
                  imgfiles,figfile,numfile,cbarfile,
                  minmax,url,coord)

  for var in varlist:
    print('%12s : %15s : %s' % (var,minmax[var],imgfiles[var]))
  print('coordinate=',coord)

if __name__ == '__main__':
  main()
