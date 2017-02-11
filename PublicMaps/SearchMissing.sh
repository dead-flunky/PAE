#!/bin/bash
#
# Listet Einheittypen, etc auf, die nicht mehr vorkommen.
#

function help ()
{
  echo "Usage: $0 [all|Unit|Feature|...]"
  echo "Available:
  Unit
  Tech
  Promotion
  Terrian
  Feature
  Improvement
  Route
  "
}

if [ $# -le 0 ] ; then
  help
  exit 0
fi

# Example argumets: "<Type>UNIT_" [Path to xml] "UNIT_" "UnitType" 1
#
# Fith argument should be > 1 if sed pattern in $4 contain pattern braches \(\)...
function search ()
{
  USED_NAMES=$(grep "$3" *.CivBeyondSwordWBSave \
    | sed -n -e "s/^.*$4=\([^, ]\+\).*\$/\\$5/p" \
    | sed -e "s/\r//p" \
    | sort | uniq )
  EXISTING_NAMES=$(grep "$1" "$2" | sed -n -e 's/^.*>\([^<]*\)<.*$/\1/p' | sort | uniq)

  MISSING_NAMES=$(echo -e "$USED_NAMES\n$EXISTING_NAMES\n$EXISTING_NAMES" \
    | sort | uniq -u)

  echo -e "Missing $4:\n$MISSING_NAMES\n"

  if [ "$DEBUG" = "1" ] ; then
    echo "$EXISTING_NAMES" > DebugSearchExisting.txt
    echo "$USED_NAMES" > DebugSearchUsed.txt
  fi
}

if [ "$1" = "all" -o "$1" = "Unit" ] ; then
  search "<Type>UNIT_" "../Assets/XML/Units/CIV4UnitInfos.xml" "UNIT_" "UnitType" 1
fi

if [ "$1" = "all" -o "$1" = "Tech" ] ; then
  search "<Type>TECH_" "../Assets/XML/Technologies/CIV4TechInfos.xml" "TECH_" "Tech" 1
fi

if [ "$1" = "all" -o "$1" = "Promotion" ] ; then
  search "<Type>PROMOTION_" "../Assets/XML/Units/CIV4PromotionInfos.xml" "PROMOTION_" "PromotionType" 1
fi

if [ "$1" = "all" -o "$1" = "Terrain" ] ; then
  search "<Type>TERRAIN_" "../Assets/XML/Terrain/CIV4TerrainInfos.xml" "TERRAIN_" "TerrainType" 1
fi

if [ "$1" = "all" -o "$1" = "Feature" ] ; then
  search "<Type>FEATURE_" "../Assets/XML/Terrain/CIV4FeatureInfos.xml" "FEATURE_" "FeatureType" 1
fi

if [ "$1" = "all" -o "$1" = "Building" ] ; then
  search "<Type>BUILDING_" "../Assets/XML/Buildings/CIV4BuildingInfos.xml" "BUILDING_" "\(BuildingType\|ProductionBuilding\)" 2
fi

if [ "$1" = "all" -o "$1" = "Improvement" ] ; then
  search "<Type>IMPROVEMENT_" "../Assets/XML/Terrain/CIV4ImprovementInfos.xml" "IMPROVEMENT_" "ImprovementType" 1
fi

if [ "$1" = "all" -o "$1" = "Route" ] ; then
  search "<Type>ROUTE_" "../Assets/XML/Misc/CIV4RouteInfos.xml" "ROUTE_" "RouteType" 1
fi

