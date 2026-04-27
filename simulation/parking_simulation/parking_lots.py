import xml.etree.ElementTree as ET

def update_parking_lots(parking_add_path, net_path):
    # Read and parse the XML file
    tree = ET.parse("parkingareas_ingolstadt.add.xml")
    root = tree.getroot()

    # Read and parse the net XML file
    tree_net = ET.parse("ingolstadt_24h_.net.xml")
    root_net = tree_net.getroot()

    # Create dictionaries for parking area lanes and lengths
    lanes = {parking_area.get('id'): parking_area.get('lane') for parking_area in root.findall('parkingArea')}
    lengths = {}

    # Find the length of the lanes from the net file
    lane_ids = set(lanes.values())
    for edge in root_net.findall('edge'):
        for lane in edge.findall('lane'):
            lane_id = lane.get('id')
            if lane_id in lane_ids:
                parking_area_id = next(key for key, value in lanes.items() if value == lane_id)
                lengths[parking_area_id] = lane.get('length')

    # Update the parkingArea elements with the roadsideCapacity attribute
    for parking_area in root.findall('parkingArea'):
        parking_l = float(lengths[parking_area.get('id')])
        capacity = int(parking_l) // 5
        parking_area.set('roadsideCapacity', str(capacity))

    # Write the updated XML back to a file
    tree.write('updated_parking_new.add.xml', encoding='UTF-8', xml_declaration=True)

def create_parking_vehicles(parking_rate, parking_add_path, route_file_path):
    # Read the parking areas XML file
    tree = ET.parse(parking_add_path)
    root = tree.getroot()

    vehicle_root = ET.Element('routes')
    vtype = ET.SubElement(vehicle_root, 'vType')
    vtype.set('id', 'parked_vehicle')
    vtype.set('color', '0,1,0')

    # iterate over the parking areas and create vehicles for the parking sports accoring to the parking rate
    for parking_area in root.findall('parkingArea'):
        # extract the edge from the lane
        edge = parking_area.get('lane')[:-2]
        for vehicle in range(int(parking_rate * int(parking_area.get('roadsideCapacity')))):
            vehicle_id = f'{parking_area.get("id")}_{vehicle}'
            add_vehicle(vehicle_root, vehicle_id, 3400, edge, parking_area.get('id'))
    
    # save the vehicle file
    tree = ET.ElementTree(vehicle_root)
    tree.write(route_file_path, encoding='UTF-8', xml_declaration=True)



def add_vehicle(root, vehicle_id, depart_time, route_edges, parking_area): 
    vehicle = ET.SubElement(root, 'vehicle')
    vehicle.set('id', vehicle_id)
    vehicle.set('type', 'parked_vehicle')
    vehicle.set('depart', str(depart_time))

    route = ET.SubElement(vehicle, 'route')
    route.set('edges', route_edges)

    stop = ET.SubElement(vehicle, 'stop')
    stop.set('parkingArea', parking_area)


if __name__ == "__main__":
    create_parking_vehicles(1, "sumo_ingolstadt/simulation/parking_simulation/parking.add.xml",
                             "sumo_ingolstadt/simulation/parking_simulation/parked_vehicles.rou.xml")


