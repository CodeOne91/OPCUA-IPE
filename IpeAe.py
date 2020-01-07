from openmtc_app.flask_runner import FlaskRunner
from openmtc_app.onem2m import XAE
from openmtc_onem2m import OneM2MRequest
from openmtc_onem2m.client.http import OneM2MHTTPClient
from openmtc_onem2m.model import AE, ResourceTypeE, CSEBase, Container, ContentInstance




client = OneM2MHTTPClient("http://localhost:8000", False)


class IpeAe(XAE):

    resourceDiscovered = []

    #ipe activity, actually make a retrieve request of all reosurce in cse-gateway
    def _on_register(self):
        self.retrieveRequest()
        print(self.resourceDiscovered)
        exit()






    #resource discovery, and append resource content in list
    def retrieveRequest(self):
        content_request = self.discover()
        for resource in content_request:
            onem2m_request = OneM2MRequest("retrieve", to=resource)
            promise = client.send_onem2m_request(onem2m_request)
            onem2m_response = promise.get()
            response = onem2m_response.content
            self.resourceDiscovered.append(self.resourceRetrievedBuilder(response))

    #switch-case resource builder,
    def resourceRetrievedBuilder(self, response):
        #AE-Builder
        if response.resourceType == ResourceTypeE.AE:
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
                creationTime=response.creationTime, App_ID=response.App_ID,
                AE_ID=response.AE_ID)

        return ae

    def cseBaseBuilder(self, response):
        cseBase = CSEBase(resourceName=response.resourceName,
                          resourceType=response.resourceType,
                          resourceID=response.resourceID,
                          parentID=response.parentID,
                          lastModifiedTime=response.lastModifiedTime,
                          creationTime=response.creationTime,
                          CSE_ID=response.id,
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


    def connect_to_local(self):
        runner = FlaskRunner(self)
        runner.run("http://localhost:8000")


