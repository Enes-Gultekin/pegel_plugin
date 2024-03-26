import json
import os
import requests
import requests
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt


##fetch the past 30 days data.It returns measurement values and time_stamp(in iso format)
def monthsData(id):

    ##assign todays date and past 30 days dates. Also convert the date
    ##in order to fetch data
    current_time=datetime.datetime.now()
    onemonthduration=current_time-timedelta(30)
    current_time=current_time.isoformat()
    onemonthduration=onemonthduration.isoformat()


    url=f"https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/{id}/W/measurements.json?start={onemonthduration}&end={current_time}"

    ##fetch the values and dates
    value=[]
    time_stamp=[]

    request=requests.get(url)
    response=request.json()

    timestamp=response[-1]["timestamp"]
    time_nformat=datetime.datetime.fromisoformat(timestamp)

    ##append the date and values
    for i in range(len(response)):
        for k in range(30):
            time_def=time_nformat-timedelta(k)
            time_iso=datetime.datetime.isoformat(time_def)
            if time_iso==response[i]["timestamp"]:
                #print(response[i]["value"])
                value.append(response[i]["value"])
                time_stamp.append(response[i]["timestamp"])


    return value,time_stamp


if __name__=="__main__":
    ###
    ####get values and date of the measurement
    values=(monthsData("593647aa-9fea-43ec-a7d6-6476a76ae868")[0])
    date=monthsData("593647aa-9fea-43ec-a7d6-6476a76ae868")[1]
    #

    #
    ###This section is to only visualize the data

    ##Convert the data to make it understandble
    date2=list()
    for i in date:
        a=datetime.datetime.fromisoformat(str(i))
        a=a.strftime("%b %d %Y")
        date2.append(a)


    ##Edit x axis
    first=date2[0]
    last=date2[-1]
    mid=date2[len(date2)//2]

    ##Plot data
    plt.plot(date2,values)
    plt.ylabel("Water Level (mm)")
    plt.xlabel("Date")
    plt.xticks([first,mid,last])
    plt.show()
    #