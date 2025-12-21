
import datetime as dt
import numpy as np
import os
from agi.stk12.stkdesktop import STKDesktop
from agi.stk12.stkobjects import *
from agi.stk12.stkutil import *
from agi.stk12.stkx import *
from agi.stk12.utilities.colors import Color
from agi.stk12.stkdesktop import STKDesktop
from agi.stk12.stkobjects import *


uiApp = STKDesktop.StartApplication(visible=True)
uiApp.Visible = True
uiApp.UserControl = True
stkRoot = uiApp.Root
type(stkRoot)


stkRoot.NewScenario("ConstellationAccessAnalysis")
scenario = stkRoot.CurrentScenario
type(scenario)
dir(scenario)

scenario.StartTime = "1 Jun 2022 15:00:00.000"
scenario.StopTime = "2 Jun 2022 15:00:00.000"
stkRoot.Rewind() 

with open(r"C:\Users\meesa\Downloads\IntegrationCert_Python\IntegrationCert_Python\Facilities.txt", "r") as facilityFile:

    for line in facilityFile:
        facilityData = line.strip().split(",")
        
        insertNewFacCmd = f"New / */Facility {facilityData[0]}"
        stkRoot.ExecuteCommand(insertNewFacCmd)
        

        setPositionCmd = (
    f"SetPosition */Facility/{facilityData[0]} "
    f"Geodetic {facilityData[1]} {facilityData[2]} {facilityData[3]} m")
        stkRoot.ExecuteCommand(setPositionCmd)

        

        setColorCmd = f"Graphics */Facility/{facilityData[0]} SetColor Cyan"
        stkRoot.ExecuteCommand(setColorCmd)
        
facilityFile.close()
print("Facilities created successfully.")

satellite = AgSatellite(scenario.Children.New(AgESTKObjectType.eSatellite, "TestSatellite"))
satelliteBasicGfxAttributes =  satellite.Graphics.Attributes
satelliteBasicGfxAttributes.Color = Color.FromRGB(255,255,0) 
satelliteBasicGfxAttributes.Line.Width = AgELineWidth.e2 
satelliteBasicGfxAttributes.Inherit = False
satelliteBasicGfxAttributes.IsGroundTrackVisible = False

satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
twoBodyPropagator = satellite.Propagator


keplerian = twoBodyPropagator.InitialState.Representation.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)                                                                                  
keplerian.SizeShapeType = AgEClassicalSizeShape.eSizeShapeSemimajorAxis

keplerian.SizeShape.SemiMajorAxis = 7159
keplerian.SizeShape.Eccentricity = 0
keplerian.Orientation.Inclination = 86.4
keplerian.Orientation.ArgOfPerigee = 0
keplerian.Orientation.AscNode.Value = 45
keplerian.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
keplerian.Location.Value = 45

twoBodyPropagator.InitialState.Representation.Assign(keplerian)
twoBodyPropagator.Propagate()

satellite.Unload()

numOrbitPlanes = 4
numSatsPerPlane = 8

for orbitPlaneNum, RAAN in enumerate(range(0,180,180//numOrbitPlanes),1): 

    for satNum, trueAnomaly in enumerate(range(0,360,360//numSatsPerPlane), 1): 
       
        satellite = AgSatellite(scenario.Children.New(AgESTKObjectType.eSatellite, f"Sat{orbitPlaneNum}{satNum}"))
       
        satelliteBasicGfxAttributes =  satellite.Graphics.Attributes
        satelliteBasicGfxAttributes.Color = Color.FromRGB(255,255,0) 
        satelliteBasicGfxAttributes.Line.Width = 2     
        satelliteBasicGfxAttributes.Inherit = False
        satelliteBasicGfxAttributes.IsGroundTrackVisible = False
                
        satellite.SetPropagatorType(AgEVePropagatorType.ePropagatorTwoBody)
        
        twoBodyPropagator = satellite.Propagator
        keplerian = twoBodyPropagator.InitialState.Representation.ConvertTo(AgEOrbitStateType.eOrbitStateClassical)

        keplerian.SizeShapeType = AgEClassicalSizeShape.eSizeShapeSemimajorAxis
        keplerian.SizeShape.SemiMajorAxis = 7159 
        keplerian.SizeShape.Eccentricity = 0

        keplerian.Orientation.Inclination = 86.4 
        keplerian.Orientation.ArgOfPerigee = 0 
        keplerian.Orientation.AscNodeType = AgEOrientationAscNode.eAscNodeRAAN
        keplerian.Orientation.AscNode.Value = RAAN  
        
        keplerian.LocationType = AgEClassicalLocation.eLocationTrueAnomaly
        keplerian.Location.Value = trueAnomaly + (360//numSatsPerPlane/2)*(orbitPlaneNum%2)  
              
        satellite.Propagator.InitialState.Representation.Assign(keplerian)
        satellite.Propagator.Propagate()
 
sensorConstellation = AgConstellation(scenario.Children.New(AgESTKObjectType.eConstellation,"SensorConstellation"))

for satellite in scenario.Children.GetElements(AgESTKObjectType.eSatellite): 
    sensor = AgSensor(satellite.Children.New(
        AgESTKObjectType.eSensor, f"Sensor{satellite.InstanceName[3:]}"))
    sensor.CommonTasks.SetPatternSimpleConic(62.5, 2)
    sensor.VO.PercentTranslucency = 75
    sensor.Graphics.LineStyle = AgELineWidth.e2 
    sensor.Graphics.LineStyle = AgELineStyle.eDotted 
    sensorConstellation.Objects.Add(sensor.Path)
facilityConstellation = AgConstellation(scenario.Children.New(
    AgESTKObjectType.eConstellation, "FacilityConstellation"))


for facility in scenario.Children.GetElements(AgESTKObjectType.eFacility):
    facilityConstellation.Objects.Add(facility.Path)

chain = AgChain(scenario.Children.New(AgESTKObjectType.eChain, "FacsToSensors"))

chain.Graphics.Animation.Color = Color.FromRGB(0,255,0) 
chain.Graphics.Animation.LineWidth = AgELineWidth.e3
chain.Graphics.Animation.IsHighlightVisible = False

stkVersion = stkRoot.ExecuteCommand("GetSTKVersion /")
if ('13' in stkVersion.Item(0)):
    chain.StartObject = facilityConstellation
    chain.EndObject   = sensorConstellation
    chain.Connections.Add(facilityConstellation,sensorConstellation,1,1)
else:
    chain.Objects.Add(facilityConstellation.Path)
    chain.Objects.Add(sensorConstellation.Path)

chain.ComputeAccess()
facilityAccess = chain.DataProviders.Item('Object Access').Exec(scenario.StartTime, scenario.StopTime)
                                                               
help(facilityAccess)

print(facilityAccess.Intervals.Count)  
print(facilityAccess.Intervals.Item(0).DataSets.GetRow(0))
print(facilityAccess.Intervals.Item(1).DataSets.GetRow(0))


facilityCount = scenario.Children.GetElements(AgESTKObjectType.eFacility).Count

facilityNum = 0
for accessNum in range(facilityAccess.Intervals.Count):
    if 'Fac' in facilityAccess.Intervals.Item(accessNum).DataSets.Item(0).GetValues()[0]:
        facilityNum+=1
        facilityDataSet = facilityAccess.Intervals.Item(accessNum).DataSets
        el = facilityDataSet.ElementNames

        facilityDataSet = facilityAccess.Intervals.Item(accessNum).DataSets  
        dataSet = facilityDataSet.GetDataSetByName("Duration")
        values = dataSet.GetValues()
        numRows = len(values)
        with open(f"Fac{facilityNum:02}Access.txt", "w") as dataFile:
            dataFile.write(f"{el[0]},{el[2]},{el[3]},{el[4]}\n")
            for row in range(numRows):
                rowData = facilityDataSet.GetRow(row)
                dataFile.write(f"{rowData[0]},{rowData[2]},{rowData[3]},{rowData[4]}\n")        
        dataFile.close()
        if facilityNum == 1:
            if os.path.exists("MaxOutageData.txt"):
                open('MaxOutageData.txt', 'w').close()
        
        maxOutage=None
        with open("MaxOutageData.txt", "a") as outageFile:
            if numRows == 1:
                outageFile.write(f"Fac{facilityNum:02},NA,NA,NA\n")
                print(f"Fac{facilityNum:02}: No Outage")
            
            else:
               
                startTimes = list(
                    facilityDataSet.GetDataSetByName("Start Time").GetValues())
                stopTimes = list(
                    facilityDataSet.GetDataSetByName("Stop Time").GetValues())
                
                startDatetimes = np.array(
                    [dt.datetime.strptime(startTime[:-3], "%d %b %Y %H:%M:%S.%f") 
                     for startTime in startTimes])
                stopDatetimes = np.array(
                    [dt.datetime.strptime(stopTime[:-3], "%d %b %Y %H:%M:%S.%f") 
                     for stopTime in stopTimes])
                
                outages = startDatetimes[1:] - stopDatetimes[:-1]
                
                maxOutage = np.amax(outages).total_seconds()
                start = stopTimes[np.argmax(outages)]
                stop = startTimes[np.argmax(outages)+1]

                outageFile.write(f"Fac{facilityNum:02},{maxOutage},{start},{stop}\n")
                print(f"Fac{facilityNum:02}: {maxOutage} seconds from {start} until {stop}")
        
        outageFile.close()

print("ANALYSIS RESULTS - FACILITY DATA")

print("\n Question 1: Facilities with Continuous Access (No Outage) ")
continuous_facilities = []

with open("MaxOutageData.txt", "r") as f:
    for line in f:
        data = line.strip().split(",")
        facility = data[0]
        max_outage = data[1]
        
        if max_outage == "NA":
            continuous_facilities.append(facility)
            print(f"{facility}: Continuous access - NO OUTAGE")

if len(continuous_facilities) == 0:
    print("ANSWER: D. None")
else:
    print(f"ANSWER: Facilities with continuous access: {', '.join(continuous_facilities)}")

print("\n--- Question 2: Viable Facilities (Max Outage ≤ 5 minutes) ---")
viable_count = 0
viable_facilities = []

with open("MaxOutageData.txt", "r") as f:
    for line in f:
        data = line.strip().split(",")
        facility = data[0]
        max_outage = data[1]
        
        if max_outage == "NA":
            print(f"{facility}: No outage - VIABLE")
            viable_count += 1
            viable_facilities.append(facility)
        elif float(max_outage) <= 300:
            print(f"{facility}: Max outage {max_outage}s ({float(max_outage)/60:.2f} min) - VIABLE")
            viable_count += 1
            viable_facilities.append(facility)
        else:
            print(f"{facility}: Max outage {max_outage}s ({float(max_outage)/60:.2f} min) - NOT VIABLE")

print(f"\nANSWER: {viable_count} viable facilities")
print(f"Viable facilities: {', '.join(viable_facilities)}")

print("\n--- Question 3: Facility with Longest Break in Access ---")
max_outage_value = -1
max_outage_facility = None
max_outage_start = None
max_outage_stop = None

with open("MaxOutageData.txt", "r") as f:
    for line in f:
        data = line.strip().split(",")
        facility = data[0]
        max_outage = data[1]
        
        if max_outage != "NA":
            outage_seconds = float(max_outage)
            if outage_seconds > max_outage_value:
                max_outage_value = outage_seconds
                max_outage_facility = facility
                max_outage_start = data[2]
                max_outage_stop = data[3]

if max_outage_facility:
    print(f"ANSWER: {max_outage_facility}")
    print(f"Longest outage: {max_outage_value} seconds ({max_outage_value/60:.2f} minutes)")
    print(f"From: {max_outage_start}")
    print(f"To: {max_outage_stop}")



facTwo = scenario.Children.Item("Fac02")

facTwoConstraints = facTwo.AccessConstraints
facTwoAzConstraint = facTwoConstraints.AddConstraint(AgEAccessConstraints.eCstrAzimuthAngle)
facTwoAzConstraint.EnableMin = True
facTwoAzConstraint.EnableMax = True
facTwoAzConstraint.Min = 45 
facTwoAzConstraint.Max = 315 

access = facTwo.GetAccess("Satellite/Sat11")
access.ComputeAccess()

accessDataPrv = access.DataProviders.Item(
    "Access Data").Exec(scenario.StartTime, scenario.StopTime)

accessStartTimes = accessDataPrv.DataSets.GetDataSetByName(
    "Start Time").GetValues()
print(accessStartTimes[0])

aircraft = AgAircraft(scenario.Children.New(AgESTKObjectType.eAircraft,"Indian_aircraft"))

dir(aircraft)

attitude = aircraft.Attitude
attitude.Basic.SetProfileType(AgEVeProfile.eCoordinatedTurn)

convertUtil = stkRoot.ConversionUtility
aircraftStartTime = convertUtil.NewDate("UTCG",accessStartTimes[0])
aircraftStartTime = aircraftStartTime.Add("min", 30)
print(aircraftStartTime.Format("UTCG"))

waypoints = np.genfromtxt(
    r"d:\STK\IntegrationCert_Python\IntegrationCert_Python\FlightPlan.txt",
    skip_header=1,
    delimiter=","
)
                        
print(waypoints)

aircraft.SetRouteType(AgEVePropagatorType.ePropagatorGreatArc)
route = aircraft.Route

startEp = aircraft.Route.EphemerisInterval.GetStartEpoch()
startEp.SetExplicitTime(aircraftStartTime.Format("UTCG"))
aircraft.Route.EphemerisInterval.SetStartEpoch(startEp)
aircraft.Route.Method = AgEVeWayPtCompMethod.eDetermineTimeAccFromVel
aircraft.Route.SetAltitudeRefType(AgEVeAltitudeRef.eWayPtAltRefMSL)
stkRoot.UnitPreferences.SetCurrentUnit("DistanceUnit","nm")
stkRoot.UnitPreferences.SetCurrentUnit("TimeUnit","hr")

for waypoint in waypoints:
    newWaypoint = route.Waypoints.Add()
    newWaypoint.Latitude = float(waypoint[0]) 
    newWaypoint.Longitude = float(waypoint[1]) 
    newWaypoint.Altitude = convertUtil.ConvertQuantity(
        "DistanceUnit","ft","nm", waypoint[2])
    newWaypoint.Speed = waypoint[3] 
    newWaypoint.TurnRadius = 1.8 

route.Propagate()
stkRoot.UnitPreferences.ResetUnits()


aircraftBasicGfxAttributes = aircraft.Graphics.Attributes
aircraftBasicGfxAttributes.Color = Color.FromRGB(255,14,246) 
aircraftBasicGfxAttributes.Line.Width = AgELineWidth.e3
modelFile = aircraft.VO.Model.ModelData
modelFile.Filename = os.path.abspath(
    uiApp.Path[:-3] + "STKData\\VO\\Models\\Air\\c-130_hercules.glb")

aircraftConstraints = aircraft.AccessConstraints

elConstraint = aircraftConstraints.AddConstraint(AgEAccessConstraints.eCstrElevationAngle)
elConstraint.EnableMin = True
elConstraint.Min = 10    

degradeSensorConstellation = sensorConstellation.CopyObject("DegradedSensorConstellation")
degradeSensorConstellation.Objects.RemoveName("Satellite/Sat11/Sensor/Sensor11")
aircraftChain = scenario.Children.New(AgESTKObjectType.eChain, "AcftToSensors")
aircraftChain.Graphics.Animation.Color = Color.FromRGB(0,255,0) 
aircraftChain.Graphics.Animation.LineWidth = AgELineWidth.e3
aircraftChain.Graphics.Animation.IsHighlightVisible = False

if ('13' in stkVersion.Item(0)):
    aircraftChain.StartObject = aircraft
    aircraftChain.EndObject   = degradeSensorConstellation
    aircraftChain.Connections.Add(aircraft,degradeSensorConstellation,1,1)
else:
    aircraftChain.Objects.Add(aircraft.Path)
    aircraftChain.Objects.Add(degradeSensorConstellation.Path)

aircraftChain.ComputeAccess()
aircraftAccess = aircraftChain.DataProviders.Item("Complete Access").Exec(scenario.StartTime,scenario.StopTime)

el = aircraftAccess.DataSets.ElementNames
numRows = aircraftAccess.DataSets.RowCount

with open("AircraftAccess.txt", "w") as dataFile:
    dataFile.write(f"{el[0]},{el[1]},{el[2]},{el[3]}\n")
    print(f"{el[0]},{el[1]},{el[2]},{el[3]}")
    
    for row in range(numRows):
        rowData = aircraftAccess.DataSets.GetRow(row)
        dataFile.write(f"{rowData[0]},{rowData[1]},{rowData[2]},{rowData[3]}\n")
        print(f"{rowData[0]},{rowData[1]},{rowData[2]},{rowData[3]}")
        
if numRows == 1:
    print(f"No Outage")

else:
   
    startTimes = list(aircraftAccess.DataSets.GetDataSetByName("Start Time").GetValues())
    stopTimes = list(aircraftAccess.DataSets.GetDataSetByName("Stop Time").GetValues())
    
    startDatetimes = np.array(
        [dt.datetime.strptime(startTime[:-3], "%d %b %Y %H:%M:%S.%f") 
         for startTime in startTimes])
    stopDatetimes = np.array(
        [dt.datetime.strptime(stopTime[:-3], "%d %b %Y %H:%M:%S.%f") 
         for stopTime in stopTimes])
    
    outages = startDatetimes[1:] - stopDatetimes[:-1]
    maxOutage = np.amax(outages).total_seconds()
    start = stopTimes[np.argmax(outages)]
    stop = startTimes[np.argmax(outages)+1]
    
    print(f"\nAC Max Outage: {maxOutage} seconds from {start} until {stop}")
    print("AIRCRAFT BREAK ANALYSIS")
    print(f"\n--- Question 4: Time of Largest Aircraft Break ---")
    print(f"ANSWER: {start}")
    print(f"Outage duration: {maxOutage} seconds ({maxOutage/60:.2f} minutes)")
    print(f"\n--- Question 5: Aircraft Position at Start of Largest Break ---")

    try:
        aircraftPosAtBreak = aircraft.DataProviders.Item("LLA State").Group.Item("Fixed")
        posData = aircraftPosAtBreak.ExecSingle(start)
        lat = posData.DataSets.GetDataSetByName("Lat").GetValues()[0]
        lon = posData.DataSets.GetDataSetByName("Lon").GetValues()[0]
        
        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")
        print(f"ANSWER: Approximately {float(lat):.3f}, {float(lon):.3f}")
    except Exception as e:
        print(f"Could not retrieve aircraft position: {e}")
    


aircraftLLA = aircraft.DataProviders.Item("LLA State")   

aircraftLLAFixed = aircraftLLA.Group.Item("Fixed").Exec(
    scenario.StartTime, scenario.StopTime, 600)

stkRoot.UnitPreferences.SetCurrentUnit("DistanceUnit","ft")
el = aircraftLLAFixed.DataSets.ElementNames
aircraftLLAFixedRes = np.array(aircraftLLAFixed.DataSets.ToArray())

print(f"{el[0]:30} {el[1]:20} {el[2]:28} {el[11]:15}")
for lla in aircraftLLAFixedRes:
    print(f"{lla[0]:30} {lla[1]:20} {lla[2]:20} {round(float(lla[11])):15}")

stkRoot.UnitPreferences.ResetUnits()   

facTwoPosData = facTwo.DataProviders.Item("All Position").Exec()
els = facTwoPosData.DataSets.ElementNames
data = facTwoPosData.DataSets.ToArray()[0]
for idx, el in enumerate(els):
    print(f"{el}: {data[idx]}")


status = "Script completed successfully."
print(status)