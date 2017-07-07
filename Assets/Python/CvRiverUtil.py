#!/usr/bin/python
# -*- coding: utf-8 -*-

import CvUtil
from CvPythonExtensions import *
import CvEventInterface

# globals
gc = CyGlobalContext()

CHAR_TO_CARDINAL = {"n": 1, "e": 2, "s": 4, "w": 8}
COORD_TO_CARDINAL = {(-1, 0): 8, (0, -1): 4,
                     (0, 1): 1, (1, 0): 2}
# INVERT_CARDINAL = {"n": "s", "e": "w", "s": "n", "w": "e", None: None}
INVERT_CARDINAL = {1: 4, 4: 1, 2: 8, 8: 2, None: None}

# Texturen einer Gruppe sollten auf die gleichen Modelle passen
RiverTextureGroups = [
    ["TEXTURE_DESERT1", "TEXTURE_GREEN1", "TEXTURE_TRANSPARENT"],  # Gruppe 0
    ["TEXTURE_DESERT2", "TEXTURE_GREEN2", "TEXTURE_TRANSPARENT"],  # Gruppe 1
    ["TEXTURE_DESERT3", "TEXTURE_GREEN3", "TEXTURE_TRANSPARENT"],  # Gruppe 2
]

RiverTextureKeymap = [
    "TXT_KEY_RIVER_DESERT_TEXTURE",
    "TXT_KEY_RIVER_GREEN_TEXTURE",
    "TXT_KEY_RIVER_TRANSPARENT_TEXTURE",
    ]

# Mappt Gruppe auf Variante mit dem passenden Untermodell
""" Variety  - Beschreibung
    0          leeres Modell (empty.nif)
    1          Quellen, Mündungen und Verbindungen
    2          Verzweigungen
"""
RiverVarieties = {"DEST": 1, "SOURCE": 1, "RIVER": 1, "BRANCH": 2}

# Strukturierte Erfassung aller Flussvarianten
# Aufbau:
# Gruppe=>Ausrichtung=>Variante=>(Flussseite, Texturgruppe)
# Beispiel:
# DEST    W            1 (int)   (w         , 1)
RiverTypes = {
    "DEST": {"N": {1: [("w1", 1), ("e1", 1)]},
             "S": {1: [("w1", 1), ("e1", 1)]},
             "W": {1: [("n1", 1), ("s1", 1)]},
             "E": {1: [("n1", 1), ("s1", 1)]},
             },
    "SOURCE": {"N": {1: [("1", 1)]},
               "S": {1: [("1", 1)]},
               "W": {1: [("1", 1)]},
               "E": {1: [("1", 1)]},
               },
    "RIVER": {"NS": {1: [("w1", 0), ("e1", 0)], 2: [("w2", 0), ("e2", 0)]},
              "WE": {1: [("n1", 0), ("s1", 0)], 2: [("n2", 0), ("s2", 0)]},
              "NW": {1: [("n1", 0), ("s1", 0)]},
              "NE": {1: [("n1", 0), ("s1", 0)]},
              "SW": {1: [("n1", 0), ("s1", 0)]},
              "SE": {1: [("n1", 0), ("s1", 0)]},
              },
    "BRANCH": {"N": {1: [("n1", 2), ("s1", 2)], 2: [("n2", 2), ("s2", 2)],
                     3: [("n3", 2), ("s3", 2)]},
               "W": {1: [("w1", 2), ("e1", 2)], 2: [("w2", 2), ("e2", 2)],
                     3: [("w3", 2), ("e3", 2)]},
               "S": {1: [("s1", 2), ("n1", 2)], 2: [("s2", 2), ("n2", 2)],
                     3: [("s3", 2), ("n3", 2)]},
               "E": {1: [("e1", 2), ("w1", 2)], 2: [("e2", 2), ("w2", 2)],
                     3: [("e3", 2), ("w3", 2)]},
               },
}

# Schlüssel wird aus den äußeren Keys der obigen Struktur abgeleitet.
RiverKeymap = {
    "EMPTY": "TXT_KEY_RIVER_EMPTY",
    "DEST_N": "TXT_KEY_RIVER_DEST_N",
    "DEST_W": "TXT_KEY_RIVER_DEST_W",
    "DEST_S": "TXT_KEY_RIVER_DEST_S",
    "DEST_E": "TXT_KEY_RIVER_DEST_E",
    "SOURCE_N": "TXT_KEY_RIVER_SOURCE_N",
    "SOURCE_W": "TXT_KEY_RIVER_SOURCE_W",
    "SOURCE_S": "TXT_KEY_RIVER_SOURCE_S",
    "SOURCE_E": "TXT_KEY_RIVER_SOURCE_E",
    "RIVER_NS": "TXT_KEY_RIVER_NS",
    "RIVER_WE": "TXT_KEY_RIVER_WE",
    "RIVER_NW": "TXT_KEY_RIVER_NW",
    "RIVER_NE": "TXT_KEY_RIVER_NE",
    "RIVER_SW": "TXT_KEY_RIVER_SW",
    "RIVER_SE": "TXT_KEY_RIVER_SE",
    "BRANCH_N": "TXT_KEY_RIVER_BRANCH_N",
    "BRANCH_W": "TXT_KEY_RIVER_BRANCH_W",
    "BRANCH_S": "TXT_KEY_RIVER_BRANCH_S",
    "BRANCH_E": "TXT_KEY_RIVER_BRANCH_E",
    "DECORATION": "TXT_KEY_RIVER_DECORATION",
    "DECO_EVERGREEN": "TXT_KEY_DECO_EVERGREEN",
    "DECO_SAVANNA": "TXT_KEY_DECO_SAVANNA",
    "DECO_SNOWY": "TXT_KEY_DECO_SNOWY",
}

DecoTypes = {
    "DECO_EVERGREEN": ["E1", "N1", "S1", "W1"],
    "DECO_SAVANNA": ["E1", "N1", "S1", "W1"],
    "DECO_SNOWY": ["E1", "N1", "S1", "W1"],
    }

# Liste der Wasserfarben
WaterTexturePrefix = "TEXTURE_WATER_"
WaterTypes = [
    ("TXT_KEY_CULTURELEVEL_NONE", []),  # Index 0 is transparent
    ("TXT_KEY_RIVER_BLUE", ["BLUE_FULL", "BLUE_HALVE"]),
    ("TXT_KEY_RIVER_GREEN", ["GREEN_FULL", "GREEN_HALVE"]),
    ("TXT_KEY_RIVER_YELLOW", ["YELLOW_FULL", "YELLOW_HALVE"]),
    ("TXT_KEY_RIVER_WHITE", ["WHITE_FULL", "WHITE_HALVE"]),
    ("TXT_KEY_RIVER_BROWN", ["BROWN_FULL", "BROWN_HALVE"]),
]
WaterNodes = [
    "NODE_WATER_0",
    "NODE_WATER_90",
    "NODE_WATER_180",
    "NODE_WATER_270"]

# Liste der "Stromschnellen"
# Von RiverTypes abgeleiteter Key: (Gruppe)+"_"+(Ausrichtung)(Variante)
# Die Bewegungsrichtung ist mit ccw (counter clockwise) oder cw gekennzeichnet.
# Die Bedeutungen der der Akürzungen sind überladen.
# ccw entspricht: nach oben, nach links, gegen den Uhrzeigersinn
# cw jeweils invertiert.
# Zweite Liste im Tupel gibt die möglichen Ausrichtungen der Wassertexturen an.
# [] : None
# -1 : All
#  0 : Full,
#  1 : Halve, North
#  2 : Halve, East
#  3 : Halve, South
#  4 : Halve, West
RapidModelPrefix = "MODEL_RAPID_"
# Nodes of layers with different z value (omit flickering).
RapidNodePrefixes = ["NODE_RAPID", "NODE_RAPID2"]
RapidTypes = {
    "RIVER_NS1": ([("rNS1cw",), ("rNS1ccw",)], [0, 1, 3]),
    "RIVER_NS2": ([("rNS2cw",), ("rNS2ccw",)], [0, 1, 3]),
    "RIVER_WE1": ([("rWE1cw",), ("rWE1ccw",)], [0, 2, 4]),
    "RIVER_WE2": ([("rWE2cw",), ("rWE2ccw",)], [0, 2, 4]),
    "RIVER_NW1": ([("rNWcw",), ("rNWccw",)], [-1]),
    "RIVER_NE1": ([("rNEcw",), ("rNEccw",)], [-1]),
    "RIVER_SW1": ([("rSWcw",), ("rSWccw",)], [-1]),
    "RIVER_SE1": ([("rSEcw",), ("rSEccw",)], [-1]),
    "DEST_N1": ([("dNtoward",), ("dNalong",)], [0, 1]),
    "DEST_W1": ([("dWtoward",), ("dWalong",)], [0, 2]),
    "DEST_S1": ([("dStoward",), ("dSalong",)], [0, 3]),
    "DEST_E1": ([("dEtoward",), ("dEalong",)], [0, 4]),
    "SOURCE_N1": ([("sNalong",), ("sNtoward",)], [0, 1]),
    "SOURCE_W1": ([("sWalong",), ("sWtoward",)], [0, 2]),
    "SOURCE_S1": ([("sSalong",), ("sStoward",)], [0, 3]),
    "SOURCE_E1": ([("sEalong",), ("sEtoward",)], [0, 4]),
    "BRANCH_N1": ([("tN1ab", "tN1ac"), ("tN1ba", "tN1bc"), ("tN1ca", "tN1cb"),
                   ("tN1ba", "tN1ca"), ("tN1ab", "tN1cb"), ("tN1ac", "tN1bc"),
                   ], [-1]),
    "BRANCH_N2": ([("tN2ab", "tN2ac"), ("tN2ba", "tN2bc"), ("tN2ca", "tN2cb"),
                   ("tN2ba", "tN2ca"), ("tN2ab", "tN2cb"), ("tN2ac", "tN2bc"),
                   ], [-1]),
    "BRANCH_N3": ([("tN3ab", "tN3ac"), ("tN3ba", "tN3bc"), ("tN3ca", "tN3cb"),
                   ("tN3ba", "tN3ca"), ("tN3ab", "tN3cb"), ("tN3ac", "tN3bc"),
                   ], [-1]),
    "BRANCH_W1": ([("tW1ab", "tW1ac"), ("tW1ba", "tW1bc"), ("tW1ca", "tW1cb"),
                   ("tW1ba", "tW1ca"), ("tW1ab", "tW1cb"), ("tW1ac", "tW1bc"),
                   ], [-1]),
    "BRANCH_W2": ([("tW2ab", "tW2ac"), ("tW2ba", "tW2bc"), ("tW2ca", "tW2cb"),
                   ("tW2ba", "tW2ca"), ("tW2ab", "tW2cb"), ("tW2ac", "tW2bc"),
                   ], [-1]),
    "BRANCH_W3": ([("tW3ab", "tW3ac"), ("tW3ba", "tW3bc"), ("tW3ca", "tW3cb"),
                   ("tW3ba", "tW3ca"), ("tW3ab", "tW3cb"), ("tW3ac", "tW3bc"),
                   ], [-1]),
    "BRANCH_S1": ([("tS1ab", "tS1ac"), ("tS1ba", "tS1bc"), ("tS1ca", "tS1cb"),
                   ("tS1ba", "tS1ca"), ("tS1ab", "tS1cb"), ("tS1ac", "tS1bc"),
                   ], [-1]),
    "BRANCH_S2": ([("tS2ab", "tS2ac"), ("tS2ba", "tS2bc"), ("tS2ca", "tS2cb"),
                   ("tS2ba", "tS2ca"), ("tS2ab", "tS2cb"), ("tS2ac", "tS2bc"),
                   ], [-1]),
    "BRANCH_S3": ([("tS3ab", "tS3ac"), ("tS3ba", "tS3bc"), ("tS3ca", "tS3cb"),
                   ("tS3ba", "tS3ca"), ("tS3ab", "tS3cb"), ("tS3ac", "tS3bc"),
                   ], [-1]),
    "BRANCH_E1": ([("tE1ab", "tE1ac"), ("tE1ba", "tE1bc"), ("tE1ca", "tE1cb"),
                   ("tE1ba", "tE1ca"), ("tE1ab", "tE1cb"), ("tE1ac", "tE1bc"),
                   ], [-1]),
    "BRANCH_E2": ([("tE2ab", "tE2ac"), ("tE2ba", "tE2bc"), ("tE2ca", "tE2cb"),
                   ("tE2ba", "tE2ca"), ("tE2ab", "tE2cb"), ("tE2ac", "tE2bc"),
                   ], [-1]),
    "BRANCH_E3": ([("tE3ab", "tE3ac"), ("tE3ba", "tE3bc"), ("tE3ca", "tE3cb"),
                   ("tE3ba", "tE3ca"), ("tE3ab", "tE3cb"), ("tE3ac", "tE3bc"),
                   ], [-1]),
    }

RapidTransitions = {

}

# [((Input cardinals, Output cardinals)), ...flipped versions...]
RiverOrientations = {
    "RIVER_NS": [(("n",), ("s",))],
    "RIVER_WE": [(("w",), ("e",))],
    "RIVER_NW": [(("w",), ("n",))],
    "RIVER_NE": [(("n",), ("e",))],
    "RIVER_SE": [(("e",), ("s",))],
    "RIVER_SW": [(("s",), ("w",))],
    "SOURCE_N": [((), ("n",))],
    "SOURCE_W": [((), ("w",))],
    "SOURCE_S": [((), ("s",))],
    "SOURCE_E": [((), ("e",))],
    "DEST_N": [(("n",), ())],
    "DEST_W": [(("w",), ())],
    "DEST_S": [(("s",), ())],
    "DEST_E": [(("e",), ())],
    "BRANCH_N": [(("e",), ("s", "w"))],
    "BRANCH_W": [(("n",), ("e", "s"))],
    "BRANCH_S": [(("w",), ("n", "e"))],
    "BRANCH_E": [(("s",), ("w", "n"))],
}


def _flipGroup1(keys):
    # Flip input and output. Order releates to RapidTypes
    for k in keys:
        (i, o) = RiverOrientations[k][0]
        RiverOrientations[k].append((o, i))


def _flipGroup2(keys):
    # Order of entries is releating to RapidTypes.
    for k in keys:
        (i, o) = RiverOrientations[k][0]
        RiverOrientations[k].append(((o[0],), (o[1], i[0])))
        RiverOrientations[k].append(((o[1],), (i[0], o[0])))
        RiverOrientations[k].append(((o[0], o[1]), (i[0],)))
        RiverOrientations[k].append(((o[1], i[0]), (o[0],)))
        RiverOrientations[k].append(((i[0], o[0]), (o[1],)))

# Add flipped versions
_flipGroup1(["RIVER_NS", "RIVER_WE", "RIVER_NW",
             "RIVER_NE", "RIVER_SW", "RIVER_SE"])
_flipGroup1(["DEST_N", "DEST_W", "DEST_S", "DEST_E",
             "SOURCE_N", "SOURCE_W", "SOURCE_S", "SOURCE_E"])
_flipGroup2(["BRANCH_N", "BRANCH_W", "BRANCH_S", "BRANCH_E"])


# Unrolling struct for linear map.
def _unroll():
    dl = []
    for k, v in DecoTypes.iteritems():
        for o in v:
            dl.append(k+"_"+o)

    wl = []
    for wt in WaterTypes:
        wl.extend(wt[1])

    return (dl, wl)

(DecoList, WaterList) = _unroll()


# Dicts stores list of terrain and feature ids
# which are releated to the river feature.
# Allows easy lookup if a feature should be handled as
# river.
# Note: Initialisize them after XML loading!
RIVER_TERRAINS = []
RIVER_FEATURES = []


class RiverDesc:

    def __init__(self, scriptDataDict=None):
        self.rtype = None
        self.align = None
        self.variant = 1  # Keys beginning with 1 to omit lists with 0...
        self.textures = [0, 0]  # tid for each (side,id)-Tuple
        self.decorations = []
        self.rapids = 0
        self.waterColor = 0
        self.waterRotation = 0
        if scriptDataDict is not None:
            self.loadScriptDict(scriptDataDict)

    # read short description
    def loadScriptDict(self, scriptDataDict):
        rid = scriptDataDict["i"]
        irtype = int(rid/100)
        ialign = int(rid % 100)/10
        ivariant = int(rid % 10)
        self.rtype = RiverTypes.keys()[irtype]
        self.align = RiverTypes[self.rtype].keys()[ialign]
        self.variant = ivariant
        self.textures = scriptDataDict.get("t", [])
        self.decorations = scriptDataDict.get("d", [])
        # Water color and Rapid id
        wid = scriptDataDict.get("w", 0)
        self.waterColor = int(wid / 100)
        self.waterRotation = int(wid % 100)/10
        self.rapids = int(wid % 10)

    # parse into short script for script field
    def dumpScriptDict(self):
        irtype = RiverTypes.keys().index(self.rtype)
        ialign = RiverTypes[self.rtype].keys().index(self.align)
        sd = {"t": self.textures,
              "i": (100*irtype + 10*ialign + self.variant),
              }
        if self.decorations != []:
            sd["d"] = self.decorations
        iTmp = 100*self.waterColor + 10*self.waterRotation + self.rapids
        if 0 != iTmp:
            sd["w"] = iTmp
        return sd

    # matching id for FeatureVariety
    def getVariety(self):
        if self.rtype is not None:
            return RiverVarieties[self.rtype]
        return 0

    # matching node name in Model file
    def getVariantSides(self):
        if self.rtype is not None and self.align is not None:
            return RiverTypes[self.rtype][self.align][self.variant]
        return {}

    # Position of input and output sides as (inputs, outputs) tuple.
    def getOrientation(self):
        if self.rtype is None or self.align is None:
            return ((), ())
        idx = max(0, self.rapids-1)
        return RiverOrientations[self.getKey()][idx]

    # Key for RiverKeymap
    def getKey(self):
        if self.rtype is None or self.align is None:
            return "EMPTY"
        else:
            return "_".join([self.rtype, self.align])

    def draw(self, pPlot):
        if self.rtype is None or self.align is None:
            return

        try:
            lSides = self.getVariantSides()
            for i in xrange(len(lSides)):
                name = "".join(["NODE_", self.rtype,
                                "_", self.align,
                                lSides[i][0]])
                # model = "".join(["MODEL_", self.rtype,
                #                "_", self.align,
                #                lSides[i][0]])
                texture = RiverTextureGroups[lSides[i][1]][self.textures[i]]
                # Variante ohne Dummy-Nodes
                pPlot.setFeatureDummyVisibility(name, True)
                pPlot.setFeatureDummyTexture(name, texture)

                """
                # Elegante, aber fehlerhafte Variante mit Dummy-Nodes,
                # Hier schlaegt leider contourgeometry fehl!?
                # Achtung, es sind nur Namen aus dem Wurzelnif erlaubt
                pPlot.addFeatureDummyModel("NODE_RIGHT_0", model)
                #pPlot.setFeatureDummyTexture("NODE_RIGHT_0", texture)
                """

            # Deco
            for deco in self.decorations:
                # deco_type = DecoTypes.keys[int(deco%10)]
                # deco_direction = DecoTypes[deco_type][int(deco/10)]
                # node = "_".join(["NODE",deco_type,deco_direction])
                node = "NODE_" + DecoList[deco]
                pPlot.setFeatureDummyVisibility(node, True)

        except:
            _riverErrorMsg("RiverDesc draw failed.")

        # Extra, water colors
        self.drawWaterColor(pPlot)
        # Extra, add rapids
        self.drawRapids(pPlot)

    def drawWaterColor(self, pPlot):
        if self.waterColor > 0:
            if self.waterRotation > 0:
                node = WaterNodes[self.waterRotation-1]
                texture = WaterTexturePrefix+WaterList[self.waterColor-1]
            else:
                # No rotation for full texture
                node = WaterNodes[0]
                texture = WaterTexturePrefix+WaterList[self.waterColor-1]

            try:
                pPlot.setFeatureDummyTexture(node, texture)
                pPlot.setFeatureDummyVisibility(node, True)
            except:
                _riverErrorMsg(
                    "RiverDesc water color failed. " +
                    node +
                    ", " +
                    texture)

    def drawRapids(self, pPlot):
        if self.rapids > 0:
            rapid_key = "".join(
                [self.rtype, "_", self.align, str(self.variant)])
            if(rapid_key in RapidTypes and
               self.rapids-1 < len(RapidTypes[rapid_key][0])):
                rapidList = RapidTypes[rapid_key][0][self.rapids-1]
                # for r in rapidList:
                for iR in xrange(len(rapidList)):
                    r = rapidList[iR]
                    rapid_node_name = RapidNodePrefixes[iR]
                    rapid_model_name = RapidModelPrefix + r
                    try:
                        pPlot.addFeatureDummyModel(
                            rapid_node_name,
                            rapid_model_name)
                    except:
                        _riverErrorMsg("RiverDesc draw failed." +
                                       rapid_key + ", " + r +
                                       ", " + rapid_model_name)


def _riverErrorMsg(msg, argTuple=()):
    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5,
                             CyTranslator().getText(msg, argTuple),
                             None, 2, None, ColorTypes(14), 0, 0,
                             False, False)


def getRiverScriptData(pPlot):
    """ Convert script data into river tile description object."""
    riverDesc = RiverDesc()
    if pPlot is not None:
        scriptDict = CvUtil.getScriptData(pPlot, ["r"], None)
        if scriptDict is not None:
            riverDesc.loadScriptDict(scriptDict)
    return riverDesc

# Returns True if plot contain feater
# of the river feature list.


def hasRiverFeature(pPlot):
    return pPlot.getFeatureType() in RIVER_FEATURES


def isRiverFeature(iFeature):
    return iFeature in RIVER_FEATURES


def addRiverFeature(pPlot, riverDesc=RiverDesc(), bSetTerrain=True):
    iTerrainRiver = CvUtil.findInfoTypeNum(
        gc.getFeatureInfo,
        gc.getNumFeatureInfos(),
        'TERRAIN_RIVER')
    iFeatureRiver = CvUtil.findInfoTypeNum(
        gc.getFeatureInfo,
        gc.getNumFeatureInfos(),
        'FEATURE_RIVER')
    if bSetTerrain:
        pPlot.setTerrainType(iTerrainRiver, True, True)

    iVariety = riverDesc.getVariety()
    # Variant 0 is empty.nif,
    pPlot.setFeatureType(-1, 0)
    pPlot.setFeatureType(iFeatureRiver, iVariety)
    updateRiverFeature(pPlot, riverDesc, False)


def _resetRiverFeature(pPlot):
    iVariety = pPlot.getFeatureVariety()
    for rtype, aligns in RiverTypes.iteritems():
        if RiverVarieties[rtype] is not iVariety:
            continue
        for align, versions in aligns.iteritems():
            for version, sides in versions.iteritems():
                for side in sides:
                    node = "NODE_"+rtype+"_"+align+side[0]
                    #  models = "MODEL_"+rtype+"_"+align+side[0]
                    pPlot.setFeatureDummyVisibility(node, False)

    for dtype, ords in DecoTypes.iteritems():
        for o in ords:
            node = "NODE_"+dtype+"_"+o
            pPlot.setFeatureDummyVisibility(node, False)

    for wnode in WaterNodes:
        pPlot.setFeatureDummyVisibility(wnode, False)


def updateRiverFeature(pPlot, riverDesc, bSave=False):
    """Reset plot, apply new river tile description and
    redraw. Optionally, invoke save of new values in
    script field."""
    pPlot.resetFeatureModel()
    iVariety = pPlot.getFeatureVariety()

    # Aktualisiere Variety, falls erforderlich.
    if riverDesc.getVariety() is not iVariety:
        iFeature = pPlot.getFeatureType()
        iVariety = riverDesc.getVariety()
        pPlot.setFeatureType(-1, 0)
        pPlot.setFeatureType(iFeature, iVariety)

    # Verstecken aller Unterknoten
    _resetRiverFeature(pPlot)

    # Anzeigen des passenden Unterknoten und Anpassung der Textur(en)
    bShowRiverFeatures = not CyUserProfile().getPlayerOption(
        PlayerOptionTypes.PLAYEROPTION_MODDER_1)
    if bShowRiverFeatures:
        riverDesc.draw(pPlot)

    if riverDesc.rtype is None or riverDesc.align is None:
        return

    # Speichern der neuen Werte
    if bSave:
        CvUtil.addScriptData(pPlot, "r", riverDesc.dumpScriptDict())


def initRiverTiles(bAddFeatures=False):
    """ Loop throgh whole map and initialise all river tiles."""
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    global RIVER_TERRAINS
    global RIVER_FEATURES
    RIVER_TERRAINS = [
        gc.getInfoTypeForString("TERRAIN_RIVER"),
        gc.getInfoTypeForString("TERRAIN_RIVER_FORD")]
    RIVER_FEATURES = [
        gc.getInfoTypeForString("FEATURE_RIVER"),
        gc.getInfoTypeForString("FEATURE_RIVER_FORD")]
    for x in range(iMapW):
        for y in range(iMapH):
            loopPlot = gc.getMap().plot(x, y)
            """
            if loopPlot.getTerrainType() in RIVER_TERRAINS:
                iFeatureRiver = loopPlot.getFeatureType()
                if bAddFeatures and iFeatureRiver not in RIVER_FEATURES:
                    iFeatureRiver = RIVER_FEATURES[0]
                    loopPlot.setFeatureType(iFeatureRiver, 0)
                if iFeatureRiver not in RIVER_FEATURES:
                    continue
            """
            if loopPlot.getFeatureType() in RIVER_FEATURES:
                iTerrainRiver = loopPlot.getTerrainType()
                if bAddFeatures and iTerrainRiver not in RIVER_TERRAINS:
                    iTerrainRiver = RIVER_TERRAINS[0]
                    loopPlot.setTerrainType(iTerrainRiver, True, True)

                iVariety = loopPlot.getFeatureVariety()
                if iVariety == 0:
                    continue
                riverDesc = getRiverScriptData(loopPlot)
                updateRiverFeature(loopPlot, riverDesc)


def addGoldNearbyRiverTiles():
    """Increase extra gold value of plot if zero.
    Well, this algorithm is not correct for all cases...
    """
    iMapW = gc.getMap().getGridWidth()
    iMapH = gc.getMap().getGridHeight()
    global RIVER_TERRAINS
    RIVER_TERRAINS = [
        gc.getInfoTypeForString("TERRAIN_RIVER"),
        gc.getInfoTypeForString("TERRAIN_RIVER_FORD")]
    neighbours_indizies = [
        (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    goldYield = 2
    for x in range(iMapW):
        for y in range(iMapH):
            loopPlot = gc.getMap().plot(x, y)
            if(loopPlot.isRiver() or
               loopPlot.getPlotType() is not PlotTypes.PLOT_LAND):
                continue
            neighbours = [gc.getMap().plot(x + n[0], y + n[1])
                          for n in neighbours_indizies]
            for nPlot in neighbours:
                if nPlot is None:
                    continue
                if nPlot.getTerrainType() in RIVER_TERRAINS:
                    iYield = loopPlot.getYield(YieldTypes(goldYield))
                    iImprovement = loopPlot.getImprovementType()
                    if iImprovement > -1:
                        iYield -= loopPlot.calculateImprovementYieldChange(iImprovement, YieldTypes(goldYield), loopPlot.getOwner(), False)
                    if iYield == 0:
                        # Achtung, Methode wirkt eher wie eine Change-Routine?!
                        CyGame().setPlotExtraYield(loopPlot.getX(), loopPlot.getY(), goldYield, iYield + 1)
                        break


def addRiverFeatureSimple(pPlot, iFeature, iVariety):
    """Helper function to setup one river version for each variant.
    This can be used in WBPlotScreen to setup this feature correctly
    without knowing of the internals.
    """
    riverDesc = RiverDesc()
    # iVariety 0 is empty.nif,
    if iVariety == 1:
        riverDesc.rtype = "DEST"
        riverDesc.align = "N"
    if iVariety == 2:
        riverDesc.rtype = "BRANCH"
        riverDesc.align = "N"
    pPlot.setFeatureType(-1, 0)
    pPlot.setFeatureType(iFeature, iVariety)
    updateRiverFeature(pPlot, riverDesc, True)

"""
 Try to determine good matching variant in relation
 to neigbour fields.
 Assumes that the field has already the correct
 terrain and feature type.
 (TERRAIN_RIVER, TERRAIN_RIVER_FORD, FEATURE_RIVER, FEATURE_RIVER_FORD)
"""


# TODO
"""
def findGoodRiverVariant(pPlot):
    riverDesc = RiverDesc()
    iFeature = pPlot.getFeatureType()
    iVariety = pPlot.getFeatureVariety()
    WATER_TERRAINS = [
        gc.getInfoTypeForString("TERRAIN_RIVER"),
        gc.getInfoTypeForString("TERRAIN_RIVER_FORD"),
        gc.getInfoTypeForString("TERRAIN_OCEAN"),
        gc.getInfoTypeForString("TERRAIN_COAST"),
        ]
    RIVER_FEATURES = [
        gc.getInfoTypeForString("FEATURE_RIVER"),
        gc.getInfoTypeForString("FEATURE_RIVER_FORD")]
"""


def getAdjacentTiles(pPlot, bBranchOnly):
    """ Search connected river plots """
    # iMapW = gc.getMap().getGridWidth()
    # iMapH = gc.getMap().getGridHeight()
    dPlotCache = {}
    # Second argument marks 'source direction during this search'.
    lPlotTodo = [(pPlot, pPlot)]
    # Third component indicates positioning
    neighbours_indizies = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    lPlotReturn = []

    while lPlotTodo:
        (curPlot, prevPlot) = lPlotTodo.pop()
        curCoord = (curPlot.getX(), curPlot.getY())
        if curCoord in dPlotCache:
            continue

        dPlotCache[curCoord] = True
        neighbours = [(gc.getMap().plot(curCoord[0] + n[0],
                                        curCoord[1] + n[1]),
                       COORD_TO_CARDINAL[n])
                      for n in neighbours_indizies]
        neighboursRiver = filter(
            lambda x_p: x_p[0] is not None and x_p[0].getFeatureType()
            in RIVER_FEATURES, neighbours)

        if len(neighboursRiver) > 2:
            lPlotReturn.append(
                (curPlot, prevPlot, sum([p for(n, p) in neighboursRiver])))
            if not bBranchOnly:
                for (n, p) in neighboursRiver:
                    if (n.getX(), n.getY()) in dPlotCache:
                        continue
                    lPlotTodo.append((n, curPlot))
        elif len(neighboursRiver) > 0:
            lPlotReturn.append(
                (curPlot, prevPlot, sum([p for(n, p) in neighboursRiver])))
            for (n, p) in neighboursRiver:
                if (n.getX(), n.getY()) in dPlotCache:
                    continue
                lPlotTodo.append((n, curPlot))

    return lPlotReturn


def _isSourceOrDest(p1, p2, idx):
    """ Gibt wieder ob p1 in Richtung einer Quell-/Senkseite von p2 liegt.
    Rückgabe ist die entsprechende Richtung in Bezug zu p2.
    """
    descP2 = getRiverScriptData(p2)
    relCoords = (p1.getX()-p2.getX(), p1.getY()-p2.getY())
    if relCoords not in COORD_TO_CARDINAL:
        return None
    plotDir = COORD_TO_CARDINAL[relCoords]
    p2Dirs = [CHAR_TO_CARDINAL[s] for s in descP2.getOrientation()[idx]]
    if plotDir in p2Dirs:
        return plotDir
    else:
        return None


def _sourcePlot(cur, source):
    """ Seite von cur in die etwas fließt."""
    return INVERT_CARDINAL[_isSourceOrDest(cur, source, 1)]


def _destPlot(cur, dest):
    """ Seite von cur aus der etwas fließt."""
    return INVERT_CARDINAL[_isSourceOrDest(cur, dest, 0)]


def _setSourceDirection(plot, sDir):
    desc = getRiverScriptData(plot)
    ori = desc.getOrientation()
    sDirs = [CHAR_TO_CARDINAL[s] for s in ori[0]]
    dDirs = [CHAR_TO_CARDINAL[s] for s in ori[1]]
    _debugMsg("sDir... "+str(sDir)+", "+str(sDirs))
    if sDir in sDirs:
        return
    tileType = len(sDirs) + len(dDirs)
    _debugMsg("tileType: "+str(tileType))
    oris = RiverOrientations[desc.getKey()]
    idx = 0
    if tileType == 1 or tileType == 2:
        for (i, o) in oris:
            if sDir in [CHAR_TO_CARDINAL[s] for s in i]:
                _debugMsg("sfound: "+str(i))
                break
            idx += 1
    elif tileType == 3:
        if len(sDirs) == 1:
            # Two sources, one dest. Flip one of the branches.
            for (i, o) in oris:
                sDirs2 = [CHAR_TO_CARDINAL[s] for s in i]
                if sDir in sDirs2 and sDirs[0] in sDirs2:
                    _debugMsg("sfound: "+str(i))
                    break
                idx += 1
        else:
            # Three sources... Flip both branches
            for (i, o) in oris:
                if [sDir] == [CHAR_TO_CARDINAL[s] for s in i]:
                    _debugMsg("sfound: "+str(i))
                    break
                idx += 1

    if idx < len(oris):
        desc.rapids = idx + 1
        _debugMsg("new rapid: " + str(desc.rapids))
        updateRiverFeature(plot, desc, True)


def _setDestDirection(plot, dDir):
    desc = getRiverScriptData(plot)
    ori = desc.getOrientation()
    sDirs = [CHAR_TO_CARDINAL[s] for s in ori[0]]
    dDirs = [CHAR_TO_CARDINAL[s] for s in ori[1]]
    _debugMsg("dDir... "+str(dDir)+", "+str(dDirs))
    if dDir in dDirs:
        return
    tileType = len(sDirs) + len(dDirs)
    _debugMsg("tileType: "+str(tileType))
    oris = RiverOrientations[desc.getKey()]
    idx = 0
    if tileType == 1 or tileType == 2:
        for (i, o) in oris:
            if dDir in [CHAR_TO_CARDINAL[d] for d in o]:
                _debugMsg("dfound: "+str(o))
                break
            idx += 1
    elif tileType == 3:
        if len(dDirs) == 1:
            # one source, two dest. Flip one of the branches.
            for (i, o) in oris:
                dDirs2 = [CHAR_TO_CARDINAL[d] for d in o]
                if dDir in dDirs2 and dDirs[0] in dDirs2:
                    _debugMsg("dfound: "+str(o))
                    break
                idx += 1
        else:
            # Three sources... Flip both branches
            for (i, o) in oris:
                if [dDir] == [CHAR_TO_CARDINAL[d] for d in o]:
                    _debugMsg("dfound: "+str(o))
                    break
                idx += 1

    if idx < len(oris):
        desc.rapids = idx + 1
        _debugMsg("new rapid: " + str(desc.rapids))
        updateRiverFeature(plot, desc, True)


def setRapidDirection(nearbyPlots):
    """ Use direction of first entry of nearbyPlots and sets recursivly
    all rapids directions of the rest.
    - Use return value of getAdjacentTiles as input!
    - The result for branch tiles could be wrong because the correct value
    is not well-defined.
    """

    # Handing of simplest case (Reset on Null)
    descStart = getRiverScriptData(nearbyPlots[0][0])
    if descStart.rapids == 0:
        for (cur, prev, _) in nearbyPlots:
            descCur = getRiverScriptData(cur)
            if descCur.rapids == 0:
                continue

            descCur.rapids = 0
            updateRiverFeature(cur, descCur, True)

        return

    # Other cases
    lHandled = [nearbyPlots.pop(0)[0]]
    lNext = [(cur, prev, _) for (cur, prev, _) in nearbyPlots
             if prev == lHandled[0]]

    while lNext:
        (cur, prev, _) = lNext.pop(0)
        sourceDir = _sourcePlot(cur, prev)
        destDir = _destPlot(cur, prev)
        if sourceDir is not None:
            # Die Seite 'sourceDir' muss Quelle werden.
            _debugMsg("set source dir " + str(cur.getX())+","+str(cur.getY()))
            _setSourceDirection(cur, sourceDir)
        elif destDir is not None:
            _debugMsg("set dest dir " + str(cur.getX())+","+str(cur.getY()))
            # Die Seite 'destDir' muss Senke werden.
            _setDestDirection(cur, destDir)

        # Füge verbundene Plots zur Liste der Abzuarbeitenden hinzu.
        lNext.extend([(cur2, prev2, _2) for (cur2, prev2, _2)
                      in nearbyPlots if prev2 == cur])


def setWaterColor(nearbyPlots):
    """ Use water color of first entry of nearbyPlots and sets recursivly
    all color of the rest.
    - Uses HAVLE-Textur for the ending points and FULL in the middle.
    - Use return value of getAdjacentTiles as input!
    - Branch tiles and BTS-Rivers could be problematic.
    """
    COORD_TO_ROTATION_INDEX = {(-1, 0): 2, (0, -1): 3,
                               (0, 1): 1, (1, 0): 4}
    lHandled = [nearbyPlots.pop(0)[0]]
    lNext = [(cur, prev, _) for (cur, prev, _) in nearbyPlots
             if prev == lHandled[0]]

    while lNext:
        (cur, prev, _) = lNext.pop(0)

        relCoords = (prev.getX()-cur.getX(), prev.getY()-cur.getY())
        if relCoords not in COORD_TO_CARDINAL:
            continue
        rotation = COORD_TO_ROTATION_INDEX[relCoords]

        descPrev = getRiverScriptData(prev)
        descCur = getRiverScriptData(cur)
        w = descPrev.waterColor
        w -= 1-(w % 2)  # Normalize on index of full texture
        # Prev plot get FULL texture and cur Plot HALVE.
        descPrev.waterColor = max(0, w)
        descPrev.waterRotation = 0
        descCur.waterColor = w+1
        descCur.waterRotation = rotation

        # Neu zeichnen und Werte speichern.
        updateRiverFeature(prev, descPrev, True)
        updateRiverFeature(cur, descCur, True)

        # Füge verbundene Plots zur Liste der Abzuarbeitenden hinzu.
        lNext.extend([(cur2, prev2, _2) for (cur2, prev2, _2)
                      in nearbyPlots if prev2 == cur])


def setTexture(nearbyPlots, iSelectedSide, iNew):
    for (cur, prev, _) in nearbyPlots:
        descCur = getRiverScriptData(cur)
        if len(descCur.textures) <= iSelectedSide:
            continue

        iOld = descCur.textures[iSelectedSide]
        if iNew == iOld:
            continue

        descCur.textures[iSelectedSide] = iNew
        updateRiverFeature(cur, descCur, True)


def _debugMsg(m):
    CyInterface().addMessage(gc.getGame().getActivePlayer(), True, 5,
                             m, None, 2, None, ColorTypes(14), 0, 0,
                             False, False)
