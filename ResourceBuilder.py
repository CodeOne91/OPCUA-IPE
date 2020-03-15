from openmtc_onem2m.model import AE,  CSEBase, Container, ContentInstance 


class ResourceBuilder():
    

    def ae_builder(self, res):
        ae = AE(resourceName=res.resourceName,
                requestReachability=True,
                resourceType=res.resourceType,
                resourceID=res.resourceID,
                parentID=res.parentID,
                lastModifiedTime=res.lastModifiedTime,
                creationTime=res.creationTime, 
                App_ID=res.App_ID,
                AE_ID=res.AE_ID,
                appName= "app"
                )

        return ae

    def cse_base_builder(self, res):
        cseBase = CSEBase(resourceName=res.resourceName,
                          resourceType=res.resourceType,
                          resourceID=res.resourceID,
                          parentID=res.parentID,
                          lastModifiedTime=res.lastModifiedTime,
                          creationTime=res.creationTime,
                          CSE_ID=res.CSE_ID,
                         cseType=res.cseType)

        return cseBase

    def container_builder(self, res):
        container = Container(resourceName=res.resourceName,
                              resourceType=res.resourceType,
                              resourceID=res.resourceID,
                              parentID=res.parentID,
                              lastModifiedTime=res.lastModifiedTime,
                              creationTime=res.creationTime,
                              currentNrOfInstances=res.currentNrOfInstances)
        self.print_resource(res)

        return container

    def content_instance_builder(self, res):
        contentInstance = ContentInstance(resourceName=res.resourceName,
                                          resourceType=res.resourceType,
                                          resourceID=res.resourceID,
                                          parentID=res.parentID,
                                          lastModifiedTime=res.lastModifiedTime,
                                          creationTime=res.creationTime,
                                          content=res.content,
                                          contentSize=res.contentSize)
        return contentInstance
    
    def print_resource(self,res):
            print("ResourceName: "+res.resourceName)
            print("ResourceID: "+res.resourceID)
            print("ResourceType: "+str(res.resourceType))
            print("ParentID:  "+res.parentID)
            print("")
            print("")
            print("")
    #def groupBuilder(self): not implemented in openmtc
