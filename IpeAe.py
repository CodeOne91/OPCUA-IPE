from openmtc_app.flask_runner import FlaskRunner
from openmtc_app.onem2m import XAE
from openmtc_onem2m import OneM2MRequest
from openmtc_onem2m.client.http import OneM2MHTTPClient
from openmtc_onem2m.model import AE,  CSEBase, Container, ContentInstance,ResourceTypeE 
from random import random

#subscription net 1 regard update to all attr of subscribed resource



class IpeAe(XAE):
    
    def __init__(self, name_ae, poas):
        XAE.__init__(self,name=name_ae,poas=poas,)
        self.max_nr_of_instances=0
        #self.lock = threading.Lock()
        #self.lock.acquire()
        

        
    remove_registration = True

    # sensors to create
    sensors = [
        'tmp'

    ]

    # available actuators
    actuators = [
        'a1'
    ]

    # settings for random sensor data generation
    threshold = 0.2
    temp_range = 25
    temp_offset = 10
    humi_range = 50
    humi_offset = 30

    resourceDiscovered = []
    uri_resource_dict = {}
    client = OneM2MHTTPClient("http://localhost:8000",False)
    
    
    
        
    def _on_register(self):
        
        self.example_init()

      
        # trigger periodically new data generation
        #self.run_forever(3, self.get_random_data)
        self.get_random_data()
        self.get_random_data()
        self.get_random_data()
        self.get_random_data()
        self.get_random_data()
        
        # log message
        self.logger.debug('registered')
                #exit()
        
    def retrieveRequest(self):
        app = AE(appName = "appName")
        onem2m_request = OneM2MRequest("update", to="onem2m/ipe_ae", pc=app)
        promise = self.client.send_onem2m_request(onem2m_request)
            
        content_request = self.discover()
        for resource in content_request:
            onem2m_request = OneM2MRequest("retrieve", to=resource)
            promise = self.client.send_onem2m_request(onem2m_request)
            onem2m_response = promise.get()
            response = onem2m_response.content
            
            self.resourceDiscovered.append(self.resourceRetrievedBuilder(response))
            self.uri_resource_dict[resource] = self.resourceRetrievedBuilder(response)
        # to remove None values in list 
        self.resourceDiscovered = [i for i in self.resourceDiscovered if i]
    
    def resourceRetrievedBuilder(self, response):
        #AE-Builder
        if response.resourceType == ResourceTypeE.AE and response.AE_ID != "ipe-ae":
            return self.aeBuilder(response)
        #CSEBase-Builder
        elif response.resourceType == ResourceTypeE.CSEBase:
            return self.cseBaseBuilder(response)
        #Container-Builder
        elif response.resourceType == ResourceTypeE.container:
            return self.containerBuilder(response)
        #ContentInstance-Builder
        elif response.resourceType == ResourceTypeE.contentInstance:
            return self.contentInstanceBuilder(response)

    def aeBuilder(self, response):
        ae = AE(resourceName=response.resourceName,
                requestReachability=True,
                resourceType=response.resourceType,
                resourceID=response.resourceID,
                parentID=response.parentID,
                lastModifiedTime=response.lastModifiedTime,
                creationTime=response.creationTime, 
                App_ID=response.App_ID,
                AE_ID=response.AE_ID,
                appName= "app"
                )

        return ae

    def cseBaseBuilder(self, response):
        cseBase = CSEBase(resourceName=response.resourceName,
                          resourceType=response.resourceType,
                          resourceID=response.resourceID,
                          parentID=response.parentID,
                          lastModifiedTime=response.lastModifiedTime,
                          creationTime=response.creationTime,
                          CSE_ID=response.CSE_ID,
                         cseType=response.cseType)

        return cseBase

    def containerBuilder(self, response):
        container = Container(resourceName=response.resourceName,
                              resourceType=response.resourceType,
                              resourceID=response.resourceID,
                              parentID=response.parentID,
                              lastModifiedTime=response.lastModifiedTime,
                              creationTime=response.creationTime,
                              currentNrOfInstances=response.currentNrOfInstances)
        self.print_resource(response)

        return container

    def contentInstanceBuilder(self, response):
        contentInstance = ContentInstance(resourceName=response.resourceName,
                                          resourceType=response.resourceType,
                                          resourceID=response.resourceID,
                                          parentID=response.parentID,
                                          lastModifiedTime=response.lastModifiedTime,
                                          creationTime=response.creationTime,
                                          content=response.content,
                                          contentSize=response.contentSize)
        return contentInstance

    #def groupBuilder(self): not implemented in openmtc
    
    def print_resource(self,response):
        print("ResourceName: "+response.resourceName)
        print("ResourceID: "+response.resourceID)
        print("ResourceType: "+str(response.resourceType))
        print("ParentID:  "+response.parentID)
        print("")
        print("")
        print("")
    
    
    def find_uri(self,resource):
        #la via del pitone
        return next((k for k, v in self.uri_resource_dict.items() if v is not None and  v.resourceID == resource.resourceID), None)
    
    def connect_to_local(self):
        print("IpeAe Starting....")
        runner = FlaskRunner(self)
        runner.run("http://localhost:8000")

    def handle_command(self, container, value):
            print('handle_command...')
            print('container: %s' % container)
            print('value: %s' % value)
            print('')
            
    def handle_command_2(self, sub, net, rep):
        print('handle_command_general...')
        print('subscription path: %s' % sub)
        print('notification event type: %s' % net)
        print('representation: %s' % rep)
        print('')

    def get_random_data(self):

        # at random time intervals
        if random() > self.threshold:

            # select a random sensor
            sensor = self.sensors[int(random() * len(self.sensors))]

            # set parameters depending on sensor type
            if sensor.startswith('Temp'):
                value_range = self.temp_range
                value_offset = self.temp_offset
            else:
                value_range = self.humi_range
                value_offset = self.humi_offset

            # generate random sensor data
            value = int(random() * value_range + value_offset)
            self.handle_sensor_data(sensor, value)

    def handle_sensor_data(self, sensor, value):

        # initialize sensor structure if never done before
        if sensor not in self._recognized_sensors:
            self.create_sensor_structure(sensor)
        self.push_sensor_data(sensor, value)

    
    def example_init(self):
                # init variables
        self._recognized_sensors = {}
        self._recognized_measurement_containers = {}
        self._command_containers = {}

        # init base structure
        label = 'devices'
        container = Container(resourceName=label)
        self._devices_container = self.create_container(None,
                                                        container,
                                                        labels=[label],
                                                        max_nr_of_instances=0)

        # create container for each actuator
        for actuator in self.actuators:
            actuator_container = Container(resourceName=actuator)
            self.create_container(
                self._devices_container.path,  # the target resource/path parenting the Container
                actuator_container,            # the Container resource or a valid container ID
                max_nr_of_instances=0,         # the container's max_nr_of_instances (here: 0=unlimited)
                labels=['actuator']            # (optional) the container's labels
            )
            # create container for the commands of the actuators
            commands_container = Container(resourceName='commands')
            commands_container = self.create_container(
                actuator_container.path,
                commands_container,
                max_nr_of_instances=0,
                labels=['commands']
            )
            # add commands_container of current actuator to self._command_containers
            self._command_containers[actuator] = commands_container
            # subscribe to command container of each actuator to the handler command
            self.add_container_subscription(
                commands_container.path,    # the Container or it's path to be subscribed
                self.handle_command         # reference of the notification handling function
            )
            
    
    def create_sensor_structure(self, sensor):
        print('initializing sensor: %s' % sensor)

        # create sensor container
        device_container = Container(resourceName=sensor)
        device_container = self.create_container(self._devices_container.path,
                                                 device_container,
                                                 labels=['sensor'],
                                                 max_nr_of_instances=0)

        # add sensor to _recognized_sensors
        self._recognized_sensors[sensor] = device_container

        # create measurements container
        labels = ['measurements']
        if sensor.startswith('Temp'):
            labels.append('temperature')
        else:
            labels.append('humidity')
        measurements_container = Container(resourceName='measurements')
        measurements_container = self.create_container(device_container.path,
                                                       measurements_container,
                                                       labels=labels,
                                                       max_nr_of_instances=0)

        # add measurements_container from sensor to _recognized_measurement_containers
        self._recognized_measurement_containers[sensor] = measurements_container

    def push_sensor_data(self, sensor, value):

        # build data set with value and metadata
        if sensor.startswith('Temp'):
            data = {
                'value': value,
                'type': 'temperature',
                'unit': 'degreeC'
            }
        else:
            data = {
                'value': value,
                'type': 'humidity',
                'unit': 'percentage'
            }

        # print the new data set
        print ('%s: %s' % (sensor, data))

        # finally, push the data set to measurements_container of the sensor
        self.push_content(self._recognized_measurement_containers[sensor], data)
        
        
    

