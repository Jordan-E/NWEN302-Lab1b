'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)
'''
from switchyard.lib.userlib import *
import time

def main(net):
    my_interfaces = net.interfaces()
    mymacs = [intf.ethaddr for intf in my_interfaces]

    #switchTable = dict()
    switch = Switch()

    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            return

        switch.removeExpired()
        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))
        if packet[0].dst in mymacs: #drop packet
            log_debug ("Packet intended for me")
            print("packet for me")
        else: #not intended for me
            if not switch.containKey(packet[0].src): #adds mac adress and port from recived packet
                switch.add(packet[0].src, input_port)
                print("Added mac adress: {} to switch table on port".format(packet[0].src, input_port))

            if switch.containKey(packet[0].dst): #fowarding - if we have the mac adress to port
                print ("Forwarding packet from switch table")
                net.send_packet(switch.get(packet[0].dst), packet)
            else: #flood
                print("Flood")
                for intf in my_interfaces:
                    if input_port != intf.name:
                        log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                        net.send_packet(intf.name, packet)
    net.shutdown()


class Switch:
    def __init__(self):
        self.switchTable = dict()
        self.timeRecived = dict()
        self.tableSize = 2
        self.timeout = 20

    #if the switchtable contains a key given
    def containKey(self, address):
        if address in self.switchTable.keys():
            return True
        else:
            return False

    #add address to switch table and get save its time recived. Remove item if table size to big
    def add(self, key, value):
        self.switchTable[key] = value
        self.timeRecived[key] = time.time()
        if len(self.switchTable) > self.tableSize:
            self.removeOldest()

    def get(self, key):
        return self.switchTable[key]

    #remove switch entry
    def removeItem(self, key):
        del self.switchTable[key]
        del self.timeRecived[key]

    #get time that entry was created
    def getTimeAdded(self, key):
        return self.timeRecived[key]

    #remove oldest entry in the dictonary
    def removeOldest(self):
        lowestValue = 100000000000000000;
        lowestAddy = None
        for address in self.timeRecived:
            if self.timeRecived[address] < lowestValue:
                lowestValue = self.timeRecived[address]
                lowestAddy = address
        self.removeItem(lowestAddy)
        print("Table full removed {}".format(lowestAddy))

    #removed entries that have expired
    def removeExpired(self):
        for adress in list(self.timeRecived):
            if time.time() - self.timeRecived[adress] >= self.timeout:
                self.removeItem(adress)
                print("{} Expired removed".format(adress))
