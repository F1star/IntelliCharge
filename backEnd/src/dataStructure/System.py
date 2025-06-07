from ChargerPile import ChargingPile
from WaitingQueue import Queue

class System:
    def __init__(self):
        ChargeFNums = {"A", "B"}
        ChargeTNums = {"C", "D", "E"}
        self.charger_pile = dict()
        for chargeNum in ChargeFNums:
            self.charger_pile[chargeNum] = ChargingPile(chargeNum, "F")
        for chargeNum in ChargeTNums:
            self.charger_pile[chargeNum] = ChargingPile(chargeNum, "T")
        self.waiting_queue = Queue()

    def add_vehicle(self, charge_type, vehicle_info):
        self.waiting_queue.add_vehicle(charge_type, vehicle_info)

    def remove_vehicle(self, queue_number):
        self.waiting_queue.remove_vehicle(queue_number)
