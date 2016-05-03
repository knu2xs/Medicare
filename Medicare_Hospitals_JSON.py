'''
-------------------------------------------------------------------------------
 Name:         Medicare_Hospitals_JSON.py

 Purpose:      Creates a file geodatabase containing a feature class with all
               US hospitals that accept Medicare.

 Author:       Brian Kingery

 Created:      4/29/2016
 Copyright:    (c) bkingery 2016

 Directions:   Ensure JSON file is still operational
               JSON - "https://www.medicare.gov/hospitalservices/Provider.svc/ProviderFinder?loc=ST|" + STATE + "&sort=1|ASC&paging=1|20"
               Example - https://www.medicare.gov/hospitalservices/Provider.svc/ProviderFinder?loc=ST|VA&sort=1|ASC&paging=1|20
 Website:      https://www.medicare.gov/hospitalcompare
-------------------------------------------------------------------------------
'''

import urllib, json, csv, arcpy, datetime
from arcpy import env

def writeCSV(workarea,name,datalist):
    with open(workarea + '/' + name + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for item in datalist:
            try:
                writer.writerow(item)
            except UnicodeEncodeError:
                pass
    csvfile.close()
    print name + '.csv','created'
    
def createFileGeodatabase(workarea,gdbname):
    gdb = workarea + "/" + gdbname + ".gdb"
    if arcpy.Exists(gdb):
        arcpy.Delete_management(gdb)
    arcpy.CreateFileGDB_management(workarea, gdbname)
    print gdbname + '.gdb','created'
    
def createPoints(workarea,gdbname,csvname,fcname,latfield,longfield):
    input_table  = workarea + "/" + csvname + '.csv'
    output_points  = gdbname + ".gdb/" + fcname
    x_field  = longfield
    y_field  = latfield
    input_format = 'DD_2'
    output_format = 'DD_2'
    id_field = ''
    spatial_ref = arcpy.SpatialReference('WGS 1984')
    arcpy.ConvertCoordinateNotation_management(input_table, output_points, x_field, y_field, input_format, output_format, id_field, spatial_ref)
    print 'Point feature class created'

#-------------------------------------------------------------------------------

# let the big dawg eat
ExecutionStartTime = datetime.datetime.now()
print "Started: %s" % ExecutionStartTime.strftime('%A, %B %d, %Y %I:%M:%S %p')
print "Processing\n"

## Target Locations
projectFolder = "R:/Divisions/InfoTech/Private/GIS_Private/Kingery/Development/Web_Scraping/MedicareFacilities/Hospitals"
env.workspace = projectFolder
env.overwriteoutput = True

DATA = []
## Column Headers for CSV file
columnID        = "ID"
columnName      = "Name"
columnAddress   = "Address"
columnCity      = "City"
columnState     = "State"
columnZipcode   = "Zipcode"
columnHType     = "Type"
columnPhone     = "Phone"
columnLat       = "Latitude"
columnLon       = "Longitude"
headers = columnID, columnName, columnAddress, columnCity, columnState, columnZipcode, columnHType, columnPhone, columnLat, columnLon
DATA.append(headers)

stateList = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
stateNum=1
hospitalCount=0
for stateX in stateList:
    
    url = "https://www.medicare.gov/hospitalservices/Provider.svc/ProviderFinder?loc=ST|"+stateX+"&sort=1|ASC&paging=1|9999"
    htmlfile = urllib.urlopen(url)
    data = json.load(htmlfile)

    stateListIndex = str(stateNum)+"/50"
    stateTotal = int(data["recordcount"])
    hospitalCount+=stateTotal
    print "Performing Analysis:",stateX,"-",stateListIndex,"-",stateTotal

    i=0
    while i<stateTotal:
        ID      = data["ProviderFinderResult"][i]["ID"]
        name    = data["ProviderFinderResult"][i]["Name"]
        address = data["ProviderFinderResult"][i]["Adr1"]
        city    = data["ProviderFinderResult"][i]["City"]
        state   = data["ProviderFinderResult"][i]["State"]
        zipcode = data["ProviderFinderResult"][i]["Zip"]   
        htype   = data["ProviderFinderResult"][i]["Supl"][0]["Value"]
        phone   = data["ProviderFinderResult"][i]["Phone"].replace(" ","").replace("(","").replace(")","").replace("-","")
        #phone   = data["ProviderFinderResult"][i]["Phone"]
        lat     = data["ProviderFinderResult"][i]["Lat"]
        lon     = data["ProviderFinderResult"][i]["Long"]

##        print "ID:     ",ID
##        print "Name:   ",name
##        print "Address:",address
##        print "        ",city+",",state,zipcode
##        print "Type:   ",htype
##        print "Phone:  ",phone
##        print "Coords: ",str(lat)+",",str(lon),"\n"

        entry = ID, name, address, city, state, zipcode, htype, phone, lat, lon
        DATA.append(entry)

        i+=1
    stateNum+=1
print "Total Hospital:",hospitalCount    

geodatabaseName = 'Medicare_Facilities'
csvName = 'Medicare_Hospitals'
featureClassName = 'Hospitals'

writeCSV(projectFolder,csvName,DATA)
createFileGeodatabase(projectFolder,geodatabaseName)
createPoints(projectFolder,geodatabaseName,csvName,featureClassName,columnLat,columnLon)

ExecutionEndTime = datetime.datetime.now()
ElapsedTime = ExecutionEndTime - ExecutionStartTime
print "\nEnded: %s" % ExecutionEndTime.strftime('%A, %B %d, %Y %I:%M:%S %p')
print "Elapsed Time: %s" % str(ElapsedTime).split('.')[0]

