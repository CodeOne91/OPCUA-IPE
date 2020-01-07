from IpeAe import IpeAe
from opcua import ua
import os.path
import sys
import opcua
from openmtc_onem2m.model import CSEBase, AE, Container, ContentInstance


sys.path.insert(0, "..")


class InterworkingManager:
    aeNodes = []
    cseBaseNodes= []
    containerNodes = []
    
    def __init__(self, xae):
        self.xae = xae
        


    def mapResourceToNode(self,server):
        self.nodeBuilder(self.xae.resourceDiscovered, server)

            

    def resourcenodeBuilder(self, myobj,resource):
        listChildren = myobj.get_children()
        for child in listChildren:
           
            if child.get_browse_name().to_string() == "2:resourceName":
                child.set_value(resource.resourceName)
            if child.get_browse_name().to_string() == "2:resourceType":
                child.set_value(resource.resourceType)
            if child.get_browse_name().to_string() == "2:resourceID":
                child.set_value(resource.resourceID)
            if child.get_browse_name().to_string() == "2:parentID":
                child.set_value(resource.parentID)
            if child.get_browse_name().to_string() == "2:creationTime":
                child.set_value(resource.creationTime)
            if child.get_browse_name().to_string() == "2:lastModifiedItem":
                child.set_value(resource.lastModifiedTime)
        
          
            
            
        
    def cseNodeBuilder(self,server, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        cseBaseObjectType = ua.NodeId.from_string('ns=%d;i=1003' % idx)
        myobj = server.nodes.objects.add_object(idx, "cseBase", cseBaseObjectType)
                
        listChildren = myobj.get_children()
        for child in listChildren:
            if child.get_browse_name().to_string() == "2:cseID":
                child.set_value(resource.CSE_ID)
            if child.get_browse_name().to_string() == "2:cseType":
                child.set_value(resource.cseType-1)
            
                         
        self.resourcenodeBuilder(myobj, resource)
        return myobj
    
      #inserire meccanismo di creazione del resource tree, quindi sotto il cseBase (magari considerando il parentID)  
    def aeNodeBuilder(self,myobj, resource):
        #entrare dentro <ae>
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        aeObjectType = ua.NodeId.from_string('ns=%d;i=1007' % idx)
        
        aeNode = myobj.add_object(idx,resource.resourceName, aeObjectType)
        listChildren = aeNode.get_children()
        for child in listChildren:
            if child.get_browse_name().to_string() == "2:ae-ID":
                child.set_value(resource.AE_ID)
            if child.get_browse_name().to_string() == "2:app-ID":
                child.set_value(resource.App_ID)
                            
        self.resourcenodeBuilder(aeNode, resource)
        return aeNode
        
    def containerNodeBuilder(self,aeNodesList, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        containerObjectType = ua.NodeId.from_string('ns=%d;i=1005' % idx)
        for aeNode in aeNodesList:
            if resource.parentID == aeNode.get_child("2:resourceID").get_value():
                containerNode = aeNode.add_object(idx,resource.resourceName, containerObjectType)
                listChildren = containerNode.get_children()

                for child in listChildren:
                    if child.get_browse_name().to_string() == "2:creationTime":
                        child.set_value(resource.creationTime)
                    if child.get_browse_name().to_string() == "2:currentNrOfInstances":
                        child.set_value(resource.currentNrOfInstances)
                self.resourcenodeBuilder(containerNode, resource)
                return containerNode
                
    def contentInstanceNodeBuilder(self,containerNodesList, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        contentInstanceObjectType = ua.NodeId.from_string('ns=%d;i=1004' % idx)
        for containerNode in containerNodesList:
            if resource.parentID == containerNode.get_child("2:resourceID").get_value():
                contentInstanceNode = containerNode.add_object(idx,resource.resourceName, contentInstanceObjectType)
                listChildren = contentInstanceNode.get_children()

                for child in listChildren:
                    if child.get_browse_name().to_string() == "2:content":

                        child.set_value(resource.content.decode("utf-8"))
                    if child.get_browse_name().to_string() == "2:contentSize":
                        child.set_value(resource.contentSize)
                self.resourcenodeBuilder(contentInstanceNode, resource)


            
        
        
        
        
        
                
    def initServer(self):
        server = opcua.Server()
        server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
        server.import_xml(os.path.dirname(__file__) + '/onem2m-opcua.xml')
        server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        
        return server
                
    def nodeBuilder(self, resourceDiscovered,server):
        for resource in resourceDiscovered:
            if isinstance(resource, CSEBase):
                cseNode = self.cseNodeBuilder(server, resource)
            if isinstance(resource, AE):
                self.aeNodes.append((self.aeNodeBuilder(cseNode, resource)))
            if isinstance(resource, Container):
                self.containerNodes.append(self.containerNodeBuilder(self.aeNodes,resource))
            if isinstance(resource, ContentInstance):
                self.contentInstanceNodeBuilder(self.containerNodes,resource)
         
                
        

ipe = IpeAe()
ipe.connect_to_local()
manager = InterworkingManager(ipe)
server = manager.initServer()
manager.mapResourceToNode(server)
server.start()







