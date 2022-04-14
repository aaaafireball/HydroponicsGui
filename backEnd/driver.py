'''import time
from machine import Pin
import machine
import uasyncio as asyncio
import sys
sys.path.append('/WaterPumps')
from WaterPumps.flowMeters import flowMeter,flowRunData
import micropython
import gc
#-------------------------------------------------------------------------------------------------------------------------------------
# pins to controll each hardware device and defines if the pins are taking in or letting out signals

pump = Pin(0,Pin.OUT)
sol = Pin(1,Pin.OUT)
water = Pin(2,Pin.IN)
nut = Pin(3,Pin.OUT)
hall_sensor_flow = Pin(4,Pin.OUT)
hall_sensor_data = Pin(5,Pin.IN)
try:
    # timings and other stuff:
    how_many_nutrients = 5 # in mL
    time_for_nut_pump = how_many_nutrients # peristaltic pump dispenses 1 ml per second

    floodTime = 5 * 60 # 5 minutes (in seconds), time water stays on roots of plantsbefore draining
    floodWait =  3 * 60 * 60 # 3 Hours (in seconds), time between floods
    interval = 12 * 60 * 60 # 12 hours (in seconds), time between acvtive and inactive periods
    active_period = "yes" # to give the plant water or not
    there_is_power = True # to make the program allways run
    water_drain_time = 14 # seconds for the water to drain from the tank (maybe improve with another sensor?)

    mainFlowMeter = flowMeter(flowPin=5, rate=4.8) # to set up the hall efect flow sensor
    mainFlowData = flowRunData() # to do calculations on our data
    global flowCount # to make sure this variable can be accessed everythwere
    flowCount = 0 # initializing the pulses

    # turns off pumps and solinoid just to be safe
    pump.off()
    sol.off()

    # turns on and off nutrient pump for predefined amount of time
    nut.on()
    time.sleep(time_for_nut_pump)
    nut.off()

    time_last_checked = time.time() # time that the program started

    #--------------------------------------------------------------------------------------------------------------------------------------

    def callbackflow(p): # function to count how many times the hall effect flow sensor rotates completly
        global flowCount
        flowCount += 1 # raises the counter by one when this is ran

    #initialize flow sensor to calculate data
    mainFlowMeter.counterPin.irq(trigger=mainFlowMeter.counterPin.IRQ_RISING, handler=callbackflow) # when there is an interupt, run callbackflow
    main_loop = asyncio.get_event_loop()

    #--------------------------------------------------------------------------------------------------------------------------------------
    def addWater():
        # keeps filling the planet container
        try: # try to do this, but stop if there is an error
            global flowCount

            main_loop.create_task(mainFlowMeter.monitorFlowMeter()) # starts data collection on water flow

            #start pumping in water inot plant reservoir
            pump.on()
            sol.on()
            hall_sensor_flow.on()

            flow_time_start = time.time() #counting how long each fill takes


            while water.value() == 1: #keep looping this code untill water hits the water sensor
                #keep the pump on,the solenoid valve open, and the hall sensor reading data
                pass

            print("{} PIT".format(time.time()-flow_time_start)) #print the time it took to pump in water

            #calculating and sending flowrate per minute
            AFR = (450/time.time()-flow_time_start)/60
            print("{} AFR".format(AFR))

            main_loop.close() # stops reading from hall sensor
            mainFlowData.totalCount = flowCount # sets the total pulse count in a python class (for data analysis)

            print("{} GIT".format(mainFlowData.totalFlow())) # prints how many liters filled the tank
            #sys.stdout.write("%.3f Liters in tank\n" % mainFlowData.totalFlow())

            flowCount = 0 # resets back to 0 so we can get accurate measurements for every time the pump is on

            #turn the pump off and close the solenoid valve
            sol.off()
            pump.off()
            hall_sensor_flow.off()

            water_on_sensor_start = time.time()

            time.sleep(floodTime) #keeps roots wet for the time we defined earlier

            sol.on() #opens the solenoid valve to drain the water

            timer_start = time.time()
            while water.value() == 0: #if it over flows, keep draining
                sol.on()
                timer_end = time.time()
                if timer_end-timer_start >= 10: # error occured, drain for 4 minutes to return to normal flow
                    time.sleep(360)

            time.sleep(water_drain_time) # wait predefined amount of seconds for the water to completly drain (might need trial and error)

            #calculating and sending flowrate per minute
            AFR = (450/time.time()-water_on_sensor_start)/60
            print("{} AFR".format(AFR))

            print("{} WST".format(time.time()-water_on_sensor_start))

            sol.off() # close solenoid valve to stop draining

            time.sleep(floodWait) # waits for a certain amount of time till this code might run again

            gc.collect() #free up memory

        except: # if something does break, catch the error and turn everything off
            pump.off()
            nut.off()
            hall_sensor_flow.off()

            print("big error occured")

            # keeps the valve open to drain
            while water.value() == 0:
                sol.on()

            time.sleep(120) # wait predefined amount of seconds for the water to completly drain (might need trial and error)

            sol.off() # close solenoid valve to stop draining

    #--------------------------------------------------------------------------------------------------------------------------------------
    # always loop this code over and over again
    while there_is_power:
        time.sleep(1)
        current_time = time.time() # get current timer

        if active_period == "yes": # whether or not we are giving the plant water for 12 hours (day-night cycle)

            #--------------------------------------------------------------------------------------------
            if current_time - time_last_checked >= interval: # Stops the water cycling for 12 hours if its been running for 12 hours
                active_period = "no"
                time_last_checked = current_time # resets the time we are counting to

            else: #if it hasnt been 12 hours yet....
                addWater() # starts water cycle that goes every 3 hours (or whatever you change it to)
            #--------------------------------------------------------------------------------------------

        else:

            #--------------------------------------------------------------------------------------------
            if current_time - time_last_checked >= interval: # Stops the water cycling for 12 hours if its been running for 12 hours

                machine.reset() # resets the pico to start over again

            else: #if it hasnt been 12 hours yet....

                gc.collect() #do nothing and free up memory!!!!


except: # if something does break, catch the error and turn everything off
    pump.off()
    nut.off()
    hall_sensor_flow.off()

    print("big error occured")

    # keeps the valve open to drain
    while water.value() == 0:
        sol.on()

    time.sleep(120) # wait predefined amount of seconds for the water to completly drain (might need trial and error)

    sol.off() # close solenoid valve to stop draining
'''
import multiprocessing
import time
import datetime
import json


def stop(kill_event):
    kill_event.value = True

    with open("./backEnd/system.json", "w") as f:
        json.dump({}, f)


def water_cycle():
    pass


def main(kill_event):
    with open('./backEnd/config.json', 'r') as json_file:
        config = json.load(json_file)

    # always loop this code over and over again
    while True:
        if kill_event.value:
            break

        time.sleep(1)
        current_time = datetime.datetime.now()  # get current timer

        with open('./backEnd/system.json', 'r') as f:
            json_temp = json.load(f)


        if json_temp != "{}":
            time_water_cycle = int(json_temp["timeWaterCycle"])
            time_start = int(json_temp["timeStart"])
            time_stop = int(json_temp["timeStop"])
            '''bin1Nutrient1 = json_temp["bin1Nutrient1"]
            bin1Nutrient2 = json_temp["bin1Nutrient2"]
            bin1Nutrient3 = json_temp["bin1Nutrient3"]
            bin1Nutrient4 = json_temp["bin1Nutrient4"]
            bin1Nutrient5 = json_temp["bin1Nutrient5"]
            bin1Nutrient6 = json_temp["bin1Nutrient6"]
            bin1Nutrient7 = json_temp["bin1Nutrient7"]
            bin1Nutrient8 = json_temp["bin1Nutrient8"]
            bin1lights = json_temp["bin1lights"]
            bin2Nutrient1 = json_temp["bin2Nutrient1"]
            bin2Nutrient2 = json_temp["bin2Nutrient2"]
            bin2Nutrient3 = json_temp["bin2Nutrient3"]
            bin2Nutrient4 = json_temp["bin2Nutrient4"]
            bin2Nutrient5 = json_temp["bin2Nutrient5"]
            bin2Nutrient6 = json_temp["bin2Nutrient6"]
            bin2Nutrient7 = json_temp["bin2Nutrient7"]
            bin2Nutrient8 = json_temp["bin2Nutrient8"]
            bin2lights = json_temp["bin2lights"]'''
        else:
            time_start = -1
            time_stop = -1
            time_water_cycle = -1

        if time_start < current_time.hour < time_stop:

            last_water_cycle = datetime.datetime.strptime(config["lastWaterCycle"], "%Y-%m-%d %H:%M:%S.%f")

            with open('test.txt', 'a') as f:
                f.write('test')
                f.write(str(last_water_cycle + datetime.timedelta(seconds=time_water_cycle)))
                f.write(str(current_time))
                f.write('-----------------------------------------------------------------------------')

            if (last_water_cycle + datetime.timedelta(seconds=time_water_cycle)) < current_time:
                multiprocessing.Process(target=water_cycle).start()
                config["lastWaterCycle"] = str(current_time)

        with open('./backEnd/system.json', 'w') as f:
            json.dump(json_temp, f)
        with open('./backEnd/config.json', 'w') as f:
            json.dump(config, f)