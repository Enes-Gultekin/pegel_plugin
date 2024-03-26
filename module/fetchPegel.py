import os
import json
import requests
import datetime

#This script is to fetch stations with time series properties.

#datetime converts timestamp into standart date time

class PegelFetch:
    def __init__(self):
        self.url="https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json?includeTimeseries=true&includeCurrentMeasurement=true&hasTimeseries=Q"

    #fetch pegel data
    def fetch_json(self):
        request=requests.get(self.url)
        response=request.json()
        return response

    #convert features to geojson format
    def convert2geojson(self,json):
        features={
            "type": "Feature",
            "properties": {
                "uuid":json["uuid"],"number":json["number"],
                "shortname":json["shortname"],"longname":json["longname"],
                "agency":json["agency"],
                "water_name": json["water"]["longname"],
                "current_waterlevel": json["timeseries"][0]["currentMeasurement"]["value"],
                "measured_date":datetime.datetime.fromisoformat(json["timeseries"][0]["currentMeasurement"]["timestamp"]).strftime("%a %d %b %Y, %I:%M%p")


            },
            "geometry": {
                "type": "Point",
                "coordinates": [json['longitude'],json['latitude']]
            },

        }

        return features

    #append all pegel points into a list
    def geojson2list(self):
        feature=[]

        response=self.fetch_json()





        #if a station has coordinates, it will be added as point

        for feat in response:
            if "longitude" in feat:
                feature.append((self.convert2geojson(feat)))

        geojson={
            "type": "FeatureCollection",
            "features": feature
        }

        return geojson

    #appends all station names into a list
    def station_names(self):
        stations=[]

        for keys in self.geojson2list()["features"]:
            stations.append(keys["properties"]["longname"])
        return stations







