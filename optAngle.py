
from math import *
from pysolar.solar import *
from scipy.optimize import minimize_scalar
import datetime




def fun(B,l,d,h,Z):

        return (acos(sin(l)*sin(d)*cos(B)
        -cos(l)*sin(d)*sin(B)*cos(Z)+cos(l)*cos(d)*cos(h)*cos(B)+sin(l)*cos(d)*cos(h)*sin(B)*cos(Z)+cos(d)
        *sin(h)*sin(B)*sin(Z)))  # angle of incidence


def opt_Tilt(latitude,longitude,Z):
        date = datetime.datetime.now()
        hour = date.hour
        minute = date.minute
        second = date.second
        msecond=date.microsecond
        year = date.year
        month = date.month
        day = date.day
        n = int(date.strftime("%j"),10)	
	
	
        date = datetime.datetime(year,month,day,hour,minute,second,msecond,tzinfo=datetime.timezone.utc)
        
	

        l = radians(latitude)
	
        d = radians( 23.45*sin(radians(360*(284 + n)/365 ))) # declanation angle
        h = radians( ((hour+minute/60) -12)*15 ) #hour angle

        #a =  asin(sin(l)*sin(d)+cos(l)*cos(d)*cos(h)) #altitude angle
        #z = asin( cos(d)*sin(h)/cos(a) ) # solar azimuth angle
        a = get_altitude(latitude, longitude, date)
        z = get_azimuth(latitude, longitude, date)

	
        phi = (90 - a) #solar zenith angle
        optimumTilt = minimize_scalar(fun, bounds=(0, pi),args=(l,d,h,Z) ,method='bounded')
        return optimumTilt.x
        












