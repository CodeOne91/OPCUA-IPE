from IpeAe import IpeAe
from opcua import ua
import os.path
import opcua
from openmtc_onem2m.model import CSEBase, AE, Container, ContentInstance
from CustomSession import CustomInternalServer
from openmtc_onem2m.transport import OneM2MRequest
import json
from threading import Thread
import time
from test.support import resource

class InterworkingManager(Thread):
    
    def __init__(self, xae):
        self.xae = xae
        self.aeNodes = []
        self.cseBaseNodes= []
        self.containerNodes = []
        self.nodeid_uri_dict = {}
        self.nodeid_attr_dict = {}
        self.opc_openmtc_attrname_dict = self.parse_json()
        
    def map_resource_to_node(self,server):
        self.node_builder(self.xae.resourceDiscovered, server)
        
    def resource_node_builder(self, myobj,resource):
        listChildren = myobj.get_children()
        for child in listChildren:           
            if child.get_browse_name().to_string() == "2:resourceName":
                child.set_value(resource.resourceName)
            elif child.get_browse_name().to_string() == "2:resourceType":
                child.set_value(resource.resourceType)
            elif child.get_browse_name().to_string() == "2:resourceID":
                child.set_value(resource.resourceID)
            elif child.get_browse_name().to_string() == "2:parentID":
                child.set_value(resource.parentID)
            elif child.get_browse_name().to_string() == "2:creationTime":
                child.set_value(resource.creationTime)
            elif child.get_browse_name().to_string() == "2:lastModifiedTime":
                child.set_value(resource.lastModifiedTime)
          
    def cse_node_builder(self,server, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        cseBaseObjectType = ua.NodeId.from_string('ns=%d;i=1003' % idx)
        myobj = server.nodes.objects.add_object(idx, resource.resourceName, cseBaseObjectType)            
        listChildren = myobj.get_children()
        for child in listChildren:
            self.populate_dict_name(child)                    
            if child.get_browse_name().to_string() == "2:CSE-ID":
                child.set_value(resource.CSE_ID)
            elif child.get_browse_name().to_string() == "2:cseType":
                child.set_value(resource.cseType-1)
        self.resource_node_builder(myobj, resource)
        if resource.resourceID is not None:
            self.populate_dict(myobj,resource)
        
        return myobj
    
    def ae_node_builder(self,myobj, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        aeObjectType = ua.NodeId.from_string('ns=%d;i=1007' % idx)
        aeNode = myobj.add_object(idx,resource.resourceName, aeObjectType)
        listChildren = aeNode.get_children()
        for child in listChildren:
            self.populate_dict_name(child)                    
            if child.get_browse_name().to_string() == "2:AE-ID":
                child.set_value(resource.AE_ID)
            elif child.get_browse_name().to_string() == "2:App-ID":
                child.set_value(resource.App_ID)                            
            elif child.get_browse_name().to_string() == "2:appName":
                child.set_value(resource.appName)                            
        self.resource_node_builder(aeNode, resource)
        self.populate_dict(aeNode, resource)
        return aeNode
    
    def container_node_builder(self,aeNodesList, containerNodesList, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        containerObjectType = ua.NodeId.from_string('ns=%d;i=1005' % idx)
        listChildren = []
        for aeNode in aeNodesList:
            if resource.parentID == aeNode.get_child("2:resourceID").get_value():
                containerNodeAdded = aeNode.add_object(idx,resource.resourceName, containerObjectType)
                listChildren = containerNodeAdded.get_children()
        for containerNode in containerNodesList:
            if resource.parentID == containerNode.get_child("2:resourceID").get_value():
                containerNodeAdded = containerNode.add_object(idx,resource.resourceName, containerObjectType)
                listChildren = containerNodeAdded.get_children()
        
        for child in listChildren:
            self.populate_dict_name(child)
            if child.get_browse_name().to_string() == "2:creationTime":
                child.set_value(resource.creationTime)
            elif child.get_browse_name().to_string() == "2:currentNrOfInstances":
                child.set_value(resource.currentNrOfInstances)
        self.resource_node_builder(containerNodeAdded, resource)
        self.populate_dict(containerNodeAdded, resource)

        return containerNodeAdded
                
    def content_instance_node_builder(self,containerNodesList, resource):
        idx = server.get_namespace_index("http://dieei.unict.it/oneM2M-OPCUA/")
        contentInstanceObjectType = ua.NodeId.from_string('ns=%d;i=1004' % idx)
        for containerNode in containerNodesList:
            if resource.parentID == containerNode.get_child("2:resourceID").get_value():
                contentInstanceNode = containerNode.add_object(idx,resource.resourceName, contentInstanceObjectType)
                listChildren = contentInstanceNode.get_children()
                for child in listChildren:
                    self.populate_dict_name(child)                    
                    if child.get_browse_name().to_string() == "2:content":
                        child.set_value(resource.content.decode("utf-8"))
                    elif child.get_browse_name().to_string() == "2:contentSize":
                        child.set_value(resource.contentSize)
                self.resource_node_builder(contentInstanceNode, resource)
                self.populate_dict(contentInstanceNode, resource)
               
    def populate_dict(self, myobj, resource):
        listChildren = myobj.get_children()
        for child in listChildren:
            self.nodeid_uri_dict[child.nodeid] = self.xae.find_uri(resource)
    
    def populate_dict_name(self, child):
        self.nodeid_attr_dict[child.nodeid] = (child.get_browse_name().to_string())[2:]

            
    def init_server(self):
        custom_iserver = CustomInternalServer(self)
        server = opcua.Server(iserver=custom_iserver)
        #server.iserver.isession.read = MethodType(manager.read_builder(), server.iserver.isession)
        server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
        server.import_xml(os.path.dirname(__file__) + '/onem2m-opcua.xml')
        
        return server
                
    def node_builder(self, resourceDiscovered,server):
        for resource in resourceDiscovered:
            if isinstance(resource, CSEBase):
                cseNode = self.cse_node_builder(server, resource)
            elif isinstance(resource, AE):
                self.aeNodes.append((self.ae_node_builder(cseNode, resource)))
            elif isinstance(resource, Container):
                self.containerNodes.append(self.container_node_builder(self.aeNodes,self.containerNodes, resource))
            elif isinstance(resource, ContentInstance):
                self.content_instance_node_builder(self.containerNodes,resource)
                
    
    def translate_read_request(self,node_to_read, old_value):
            if self.nodeid_uri_dict.get(node_to_read, None) is not None:
                onem2m_request = OneM2MRequest("retrieve", to=self.nodeid_uri_dict.get(node_to_read))
                promise = self.xae.client.send_onem2m_request(onem2m_request)
                onem2m_response = promise.get()
                response = onem2m_response.content
                attr_to_read = self.opc_openmtc_attrname_dict[self.nodeid_attr_dict[node_to_read]]
                
                new_value =self.decode_response(attr_to_read, getattr(response,attr_to_read))
                print(" HTTP-Read_Value: "+ str(new_value))
                if old_value != new_value:
                    server.get_node(node_to_read).set_value(new_value)
                
                
    def translate_write_request(self,node_to_write,value_to_write):
            if self.nodeid_uri_dict.get(node_to_write, None) is not None:
                #take uri from nodeid
                resource_uri = self.nodeid_uri_dict.get(node_to_write)
                #take resource from uri
                res = self.xae.uri_resource_dict.get(resource_uri)
                #take attr from node id
                attr_to_write = self.nodeid_attr_dict.get(node_to_write)
                
                update_instance = self.decode_request(res, 
                                                      attr_to_write, value_to_write)
                onem2m_request = OneM2MRequest("update",
                                                to=self.nodeid_uri_dict.get(node_to_write),
                                                pc=update_instance)
                self.xae.client.send_onem2m_request(onem2m_request)
       
                
                   
    def parse_json(self):
        f = open('opc_openmtc_name_map.json')
        data = json.load(f)
        f.close()
        return data
    
    def decode_response(self, attr_to_read, datavalue):
        if attr_to_read == "content":
            return datavalue.decode("utf-8")
        if attr_to_read == "cseType":
            return datavalue-1
        return datavalue
    
    def decode_request(self, resource,attr_to_write , value_to_write):
        if isinstance(resource, CSEBase):
            cse = CSEBase()
            setattr(cse, attr_to_write, value_to_write)
            return cse
        elif isinstance(resource, AE):
            ae = AE()
            setattr(ae, attr_to_write, value_to_write)
            return ae
        elif isinstance(resource, Container):
            cnt = Container()
            setattr(cnt, attr_to_write, value_to_write)
            return cnt
        elif isinstance(resource, ContentInstance):
            cin = ContentInstance()
            setattr(cin, attr_to_write, value_to_write)
            return cin
        return resource


ipe = IpeAe("ipe_ae", ['http://0.0.0.0:21346'])
ipe_ae_thread = Thread(target= ipe.connect_to_local)
ipe_ae_thread.start()
#need to initialize ipe_ae, can be used thread-lock
time.sleep(5)
ipe.retrieveRequest()
print("RESOURCE DISCOVERED FROM IPE-AE:")
print(ipe.uri_resource_dict.keys())
in_manager = InterworkingManager(ipe)
server = in_manager.init_server()
in_manager.map_resource_to_node(server)
server.start()



