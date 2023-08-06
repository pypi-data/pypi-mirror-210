import re

def getFileString(filename : str) -> str:
    with open(filename, "r") as f:
        s = f.read()
        return s

def getAngles(filestring : str) -> list:

    index= filestring.find( "\"angleData\": [")
    if index !=-1 :  
        filestring = filestring[index:][:filestring[index:].index("],") + 2]
    else :
        filestring =  ""

    filestring = filestring[14:][:-2].split(", ")
    filestring = [int(i) for i in filestring]

    return filestring

def setAngles(angles : list, filestring : str) -> str:
    
    filestring = re.sub("\"angleData\": \[.*\],", "\"angleData\": [" + ', '.join([str(elem) for elem in angles]) + "],", filestring)
    return filestring

def addEvent(event : str, filestring : str) -> str:
    
    isDecoration = False
    if "AddDecoration" in event:
        isDecoration = True

    if isDecoration:
        filestring = re.sub("\"decorations\":\n\t\[", "\"decorations\":\n\t[" + event, filestring)
    else:
        filestring = re.sub("\"actions\":\n\t\[", "\"actions\":\n\t[" + event, filestring)
    return filestring

def writeToFile(filestring : str, filename : str):
    
    with open(filename, "w") as f:
        f.write(filestring)

def setSpeed(floor : int, speedtype="Bpm", bpm=100, bpmmultiplier=1):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetSpeed\", \"speedType\": \"" + str(speedtype) + "\", \"beatsPerMinute\": " + str(bpm) + ", \"bpmMultiplier\": " + str(bpmmultiplier) + " }"

def twirl(floor : int):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Twirl\" }"

def checkpoint(floor : int, tileoffset=0):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Checkpoint\", \"tileOffset\": " + str(tileoffset) + " }"

def setHitsound(floor : int, gamesound="Hitsound", hitsound="Kick", volume=100):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetHitsound\", \"gameSound\": \"" + gamesound + "\", \"hitsound\": \"" + hitsound + "\", \"hitsoundVolume\": " + str(volume) + " }"

def playSound(floor : int, hitsound="Kick", volume=100, angleoffset=0, eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"PlaySound\", \"hitsound\": \"" + hitsound + "\", \"hitsoundVolume\": " + str(volume) + ", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def setPlanetRotation(floor : int, ease="Linear", easeparts=1, easepartbehavior="Mirror"):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetPlanetRotation\", \"ease\": \"" + ease + "\", \"easeParts\": " + str(easeparts) + ", \"easePartBehavior\": \"" + easepartbehavior + "\" }"

def pause(floor : int, duration=1, countdown=0, anglecorrectiondir=-1):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Pause\", \"duration\": " + str(duration) + ", \"countdownTicks\": " + str(countdown) + ", \"angleCorrectionDir\": " + str(anglecorrectiondir) + " }"

def autoPlayTiles(floor : int, enabled=True, safetytiles=False):
    
    enabled = "Enabled" if enabled == True else "Disabled"
    safetytiles = "Enabled" if safetytiles == True else "Disabled"

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"AutoPlayTiles\", \"enabled\": \"" + enabled + "\", \"safetyTiles\": \"" + safetytiles + "\" }"

def scalePlanets(floor : int, duration=1, targetplanet="FirePlanet", scale=100, angleoffset=0, ease="Linear", eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ScalePlanets\", \"duration\": " + str(duration) + ", \"targetPlanet\": \"" + targetplanet + "\", \"scale\": " + str(scale) + ", \"angleOffset\": " + str(angleoffset) + ", \"ease\": \"" + ease + "\", \"eventTag\": \"" + eventtag + "\" }"

def colorTrack(floor : int, trackcolortype="Single", trackcolor="debb7b", secondarytrackcolor="ffffff", trackcoloranimduration=2, trackcolorpulse="None", trackpulselength=10, trackstyle="Standard", tracktexture="", tracktexturescale=1, trackglowintensity=100):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ColorTrack\", \"trackColorType\": \"" + trackcolortype + "\", \"trackColor\": \"" + trackcolor + "\", \"secondaryTrackColor\": \"" + secondarytrackcolor + "\", \"trackColorAnimDuration\": " + str(trackcoloranimduration) + ", \"trackColorPulse\": \"" + trackcolorpulse + "\", \"trackPulseLength\": " + str(trackpulselength) + ", \"trackStyle\": \"" + trackstyle + "\", \"trackTexture\": \"" + tracktexture + "\", \"trackTextureScale\": " + str(tracktexturescale) + ", \"trackGlowIntensity\": " + str(trackglowintensity) + " }"

def animateTrack(floor : int, trackanimation="None", beatsahead=3, trackdisappearanimation="None", beatsbehind=4):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"AnimateTrack\", \"trackAnimation\": \"" + trackanimation + "\", \"beatsAhead\": " + str(beatsahead) + ", \"trackDisappearAnimation\": \"" + trackdisappearanimation + "\", \"beatsBehind\": " + str(beatsbehind) + " }"

def recolorTrack(floor : int, starttile=0, startrelativeto="ThisTile", endtile=0, endrelativeto="ThisTile", trackcolortype="Single", trackcolor="debb7b", secondarytrackcolor="ffffff", trackcoloranimduration=2, trackcolorpulse="None", trackpulselength=10, trackstyle="Standard", trackglowintensity=100, angleoffset=0, eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"RecolorTrack\", \"startTile\": [" + str(starttile) + ", \"" + startrelativeto + "\"], \"endTile\": [" + str(endtile) + ", \"" + endrelativeto + "\"], \"trackColorType\": \"" + trackcolortype + "\", \"trackColor\": \"" + trackcolor + "\", \"secondaryTrackColor\": \"" + secondarytrackcolor + "\", \"trackColorAnimDuration\": " + str(trackcoloranimduration) + ", \"trackColorPulse\": \"" + trackcolorpulse + "\", \"trackPulseLength\": " + str(trackpulselength) + ", \"trackStyle\": \"" + trackstyle + "\", \"trackGlowIntensity\": " + str(trackglowintensity) + ", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def moveTrack(floor : int, starttile=0, startrelativeto="ThisTile", endtile=0, endrelativeto="ThisTile", gaplength=0, duration=1, posx : int="null", posy : int="null", rotationoffset : int=None, scalex : int=None, scaley : int=None, opacity : int=None, angleoffset=0, ease="Linear", maxvfxonly=False, eventtag=""):
    
    maxvfxonly = "Enabled" if maxvfxonly == True else "Disabled"

    rotstring = ""
    if rotationoffset!=None:
        rotstring = ", \"rotationOffset\": " + str(rotationoffset)
    
    scalexstring = ", \"scale\": [100,"
    if scalex != None:
        scalexstring = ", \"scale\": [" + str(scalex) + ","

    scaleystring = " 100]"
    if scaley != None:
        scaleystring = " " + str(scaley) + "]"

    if scalex == None and scaley == None:
        scalexstring = ""
        scaleystring = ""
    
    opacitystring = ""
    if opacity!=None:
        opacitystring = ", \"opacity\": " + str(opacity)

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"MoveTrack\", \"startTile\": [" + str(starttile) + ", \"" + startrelativeto + "\"], \"endTile\": [" + str(endtile) + ", \"" + endrelativeto + "\"], \"gapLength\": " + str(gaplength) + ", \"duration\": " + str(duration) + ", \"positionOffset\": [" + str(posx) + ", " + str(posy) + "]" + rotstring + scalexstring + scaleystring + opacitystring + ", \"angleOffset\": " + str(angleoffset) + ", \"ease\": \"" + ease + "\", \"maxVfxOnly\": \"" + maxvfxonly + "\", \"eventTag\": \"" + eventtag + "\" }"

def positionTrack(floor : int, posx=0, posy=0, tile=0, relativeto="ThisTile", rotation=0, scale=100, opacity=100, justthistile=False, editoronly=False):
    
    justthistile = "Enabled" if justthistile == True else "Disabled"
    editoronly = "Enabled" if editoronly == True else "Disabled"
    
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"PositionTrack\", \"positionOffset\": [" + str(posx) + ", " + str(posy) + "], \"relativeTo\": [" + str(tile) + ", \"" + relativeto + "\"], \"rotation\": " + str(rotation) + ", \"scale\": " + str(scale) + ", \"opacity\": " + str(opacity) + ", \"justThisTile\": \"" + justthistile + "\", \"editorOnly\": \"" + editoronly + "\" }"

def moveDecorations(floor : int, duration=0, tag="sampleTag", image=None, posx : int="null", posy : int="null", rotationoffset : int=None, scalex : int=None, scaley : int=None, color : str=None, opacity : int=None, depth : int=None, parallaxx : int=None, parallaxy : int=None, angleoffset=0, ease="Linear", eventtag=""):

    imgstring = ""
    if image!=None:
        imgstring = ", \"decorationImage\": \"" + str(image) + "\""
     
    rotstring = ""
    if rotationoffset!=None:
        rotstring = ", \"rotationOffset\": " + str(rotationoffset)

    scalexstring = ", \"scale\": [100,"
    if scalex != None:
        scalexstring = ", \"scale\": [" + str(scalex) + ","

    scaleystring = " 100]"
    if scaley != None:
        scaleystring = " " + str(scaley) + "]"

    if scalex == None and scaley == None:
        scalexstring = ""
        scaleystring = ""

    colstring = ""
    if color!=None:
        colstring = ", \"color\": " + str(color)

    opacitystring = ""
    if opacity!=None:
        opacitystring = ", \"opacity\": " + str(opacity)

    depthstring = ""
    if depth!=None:
        colstring = ", \"depth\": " + str(depth)

    parallaxxstring = ", \"parallax\": [0,"
    if parallaxx != None:
        parallaxxstring = ", \"parallax\": [" + str(parallaxx) + ","

    parallaxystring = " 0]"
    if parallaxy != None:
        parallaxystring = " " + str(parallaxy) + "]"

    if parallaxx == None and parallaxy == None:
        parallaxxstring = ""
        parallaxystring = ""

    return "{ \"floor\": " + str(floor) + ", \"eventType\": \"MoveDecorations\", \"duration\": " + str(duration) + ", \"tag\": \"" + tag + "\"" + imgstring + ", \"positionOffset\": [" + str(posx) + ", " + str(posy) + "]" + rotstring + scalexstring + scaleystring + colstring + opacitystring + depthstring + parallaxxstring + parallaxystring + ", \"angleOffset\": " + str(angleoffset) + ", \"ease\": \"" + ease + "\", \"eventTag\": \"" + str(eventtag) + "\" }"

def setText(floor : int, text="Text", tag="", angleoffset=0, eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetText\", \"decText\": \"" + text + "\", \"tag\": \"" + tag + "\", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"


def customBackground(floor : int, color="000000", bgimage="", imagecolor="ffffff", parallaxx=100, parallaxy=100, bgdisplaymode="FitToScreen", lockrot="Disabled", loopBG="Disabled", unscaledSize=100, angleoffset=0, eventtag=""):
    
    lockrot = "Enabled" if lockrot == True else "Disabled"
    loopBG = "Enabled" if loopBG == True else "Disabled"

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"CustomBackground\", \"color\": \"" + color + "\", \"bgImage\": \"" + bgimage + "\", \"imageColor\": \"" + imagecolor + "\", \"parallax\": [" + str(parallaxx) + ", " + str(parallaxy) + "], \"bgDisplayMode\": \"" + bgdisplaymode + "\", \"lockRot\": \"" + lockrot + "\", \"loopBG\": \"" + loopBG + "\", \"unscaledSize\": " + str(unscaledSize) + ", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def flash(floor : int, duration=1, plane="Background", startcolor="ffffff", startopacity=100, endcolor="ffffff", endopacity=0, angleoffset=0, ease="Linear", eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Flash\", \"duration\": " + str(duration) + ", \"plane\": \"" + plane + "\", \"startColor\": \"" + startcolor + "\", \"startOpacity\": " + str(startopacity) + ", \"endColor\": \"" + endcolor + "\", \"endOpacity\": " + str(endopacity) + ", \"angleOffset\": " + str(angleoffset) + ", \"ease\": \"" + ease + "\", \"eventTag\": \"" + eventtag + "\" }"

def moveCamera(floor : int, duration=1, relativeto : str=None, posx : int="null", posy : int="null", rotation : int=None, zoom : int=None, angleoffset=0, ease="Linear", eventtag=""):
    
    relstring = ""
    if relativeto!=None:
        relstring = ", \"relativeTo\": \"" + relativeto + "\""

    rotstring = ""
    if rotation!=None:
        rotstring = ", \"rotation\": " + str(rotation)

    zoomstring = ""
    if zoom!=None:
        zoomstring = ", \"zoom\": " + str(zoom)

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"MoveCamera\", \"duration\": " + str(duration) + relstring + ", \"position\": [" + str(posx) + ", " + str(posy) + "]" + rotstring + zoomstring + ", \"angleOffset\": " + str(angleoffset) + ", \"ease\": \"" + ease + "\", \"eventTag\": \"" + eventtag + "\" }"

def setFilter(floor : int, filter="Grayscale", enabled=True, intensity=100, duration=0, ease="Linear", disableothers="Disabled", angleoffset=0, eventtag=""):
        
    enabled = "Enabled" if enabled == True else "Disabled"
    disableothers = "Enabled" if disableothers == True else "Disabled"
    
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetFilter\", \"filter\": \"" + filter + "\", \"enabled\": \"" + enabled + "\", \"intensity\": " + str(intensity) + ", \"duration\": " + str(duration) + ", \"ease\": \"" + ease + "\", \"disableOthers\": \"" + disableothers + "\", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def hallOfMirrors(floor : int, enabled=True, angleoffset=0, eventtag=""):
    
    enabled = "Enabled" if enabled == True else "Disabled"
    
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"HallOfMirrors\", \"enabled\": \"" + enabled + "\", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def shakeScreen(floor : int, duration=1, strength=100, intensity=100, fadeOut=True, angleOffset=0, eventtag=""):
    
    fadeOut = "Enabled" if fadeOut == True else "Disabled"

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ShakeScreen\", \"duration\": " + str(duration) + ", \"strength\": " + str(strength) + ", \"intensity\": " + str(intensity) + ", \"fadeOut\": \"" + fadeOut + "\", \"angleOffset\": " + str(angleOffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def bloom(floor : int, enabled=True, threshold=50, intensity=100, color="ffffff", duration=0, ease="Linear", angleoffset=0, eventtag=""):
    
    enabled = "Enabled" if enabled == True else "Disabled"
    
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Bloom\", \"enabled\": \"" + enabled + "\", \"threshold\": " + str(threshold) + ", \"intensity\": " + str(intensity) + ", \"color\": \"" + color + "\", \"duration\": " + str(duration) + ", \"ease\": \"" + ease + "\", \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def screenTile(floor : int, tilex=1, tiley=1, angleoffset=0, eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ScreenTile\", \"tile\": [" + str(tilex) + ", " + str(tiley) + "], \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def screenScroll(floor : int, scrollx=0, scrolly=0, angleoffset=0, eventtag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ScreenScroll\", \"scroll\": [" + str(scrollx) + ", " + str(scrolly) + "], \"angleOffset\": " + str(angleoffset) + ", \"eventTag\": \"" + eventtag + "\" }"

def repeatEvents(floor : int, repititions=1, intreval=1, tag=""):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"RepeatEvents\", \"repetitions\": " + str(repititions) + ", \"interval\": " + str(intreval) + ", \"tag\": \"" + tag + "\" }"

def setConditionalEvents(floor : int, perfecttag="NONE", hittag="NONE", barelytag="NONE", misstag="NONE", losstag="NONE"):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetConditionalEvents\", \"perfectTag\": \"" + perfecttag + "\", \"hitTag\": \"" + hittag + "\", \"barelyTag\": \"" + barelytag + "\", \"missTag\": \"" + misstag + "\", \"lossTag\": \"" + losstag + "\" }"

def setHoldSound(floor : int, holdstartsound="Fuse", holdloopsound="Fuse", holdendsound="Fuse", holdmidsound="Fuse", holdmidsoundtype="Once", holdmidsounddelay=0.5, holdmidsoundtimingrelativeto="End", holdsoundvolume=100):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"SetHoldSound\", \"holdStartSound\": \"" + holdstartsound + "\", \"holdLoopSound\": \"" + holdloopsound + "\", \"holdEndSound\": \"" + holdendsound + "\", \"holdMidSound\": \"" + holdmidsound + "\", \"holdMidSoundType\": \"" + holdmidsoundtype + "\", \"holdMidSoundDelay\": " + str(holdmidsounddelay) + ", \"holdMidSoundTimingRelativeTo\": \"" + holdmidsoundtimingrelativeto + "\", \"holdSoundVolume\": " + str(holdsoundvolume) + " }"

def multiPlanet(floor : int, planets="TwoPlanets"):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"MultiPlanet\", \"planets\": \"" + planets + "\" }"

def hideJudgement(floor : int, hidejudgement=False, hidetileicon=False):
    
    hidejudgement = "Enabled" if hidejudgement == True else "Disabled"
    hidetileicon = "Enabled" if hidetileicon == True else "Disabled"
    
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Hide\", \"hideJudgment\": \"" + hidejudgement + "\", \"hideTileIcon\": \"" + hidetileicon + "\" }"

def scaleMargin(floor : int, scale=100):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ScaleMargin\", \"scale\": " + str(scale) + " }"

def scaleRadius(floor : int, scale=100):
    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"ScaleRadius\", \"scale\": " + str(scale) + " }"

def hold(floor : int, duration = 0, distancemultiplier=100, landinganimation=False):
    
    landinganimation = "Enabled" if landinganimation == True else "Disabled"

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"Hold\", \"duration\": " + str(duration) + ", \"distanceMultiplier\": " + str(distancemultiplier) + ", \"landingAnimation\": \"" + landinganimation + "\" }"

def addDecoration(floor : int, image="", posx=0, posy=0, relativeto="Tile", pivotoffsetx=0, pivotoffsety=0, rotation=0, scalex=100, scaley=100, tilex=1, tiley=1, color="ffffff", opacity=100, depth=-1, parallaxx=0, parallaxy=0, tag="", imagesmoothing=True, failhitbox=False, failhitboxtype="Box", failhitboxscalex=100, failhitboxscaley=100, failhitboxoffsetx=0, failhitboxoffsety=0, failhitboxrotation=0):
    
    imagesmoothing = "Enabled" if imagesmoothing == True else "Disabled"
    failhitbox = "Enabled" if failhitbox == True else "Disabled"

    return "\n\t\t{ \"floor\": " + str(floor) + ", \"eventType\": \"AddDecoration\", \"decorationImage\": \"" + image + "\", \"position\": [" + str(posx) + ", " + str(posy) + "], \"relativeTo\": \"" + relativeto + "\", \"pivotOffset\": [" + str(pivotoffsetx) + ", " + str(pivotoffsety) + "], \"rotation\": " + str(rotation) + ", \"scale\": [" + str(scalex) + ", " + str(scaley) + "], \"tile\": [" + str(tilex) + ", " + str(tiley) + "], \"color\": \"" + color + "\", \"opacity\": " + str(opacity) + ", \"depth\": " + str(depth) + ", \"parallax\": [" + str(parallaxx) + ", " + str(parallaxy) + "], \"tag\": \"" + tag + "\", \"imageSmoothing\": \"" + imagesmoothing + "\", \"failHitbox\": \"" + failhitbox + "\", \"failHitboxType\": \"" + failhitboxtype + "\", \"failHitboxScale\": [" + str(failhitboxscaley) + ", " + str(failhitboxscalex) + "], \"failHitboxOffset\": [" + str(failhitboxoffsetx) + ", " + str(failhitboxoffsety) + "], \"failHitboxRotation\": " + str(failhitboxrotation) + ", \"components\": \"\",  }"
