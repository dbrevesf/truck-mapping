#!/usr/bin/env python3.6

"""
Truck Mapping - finds the optimal mapping of trucks and cargos.
"""
from haversine import haversine
from operator import itemgetter
import argparse
import csv
import strings

TRUCKS_FILE_NAME = 'trucks.csv'
CARGO_FILE_NAME = 'cargo.csv'


class TruckMapping(object):
    """
    Class which contains the methods used to obtain an optimal mapping of
    trucks that will travel the minimum distance to take some cargo from the
    origin to destination.
    """
    def __init__(self, trucks_file, cargos_file):

        self.trucks_file = trucks_file
        self.cargos_file = cargos_file

    def get_distance(self, origin, destination):
        """
        Calculates the Haversine distance between two points. The Haversine
        distance is a formula which determines the great-circle distance
        between two points on a sphere given their longitude and latitude.

        Arguments:
            origin (tuple): origin coordinates
            destination (tuple): destination coordinates

        Return:
            distance (float): Haversine distance between origin and destination
        """
        return haversine(origin, destination)

    def get_distance_list(self, trucks, cargos):
        """
        Given trucks and the cargos, this method calls the function
        get_distance() for each pair of truck and cargo and creates a list
        with every distance calculated.

        Arguments:
            trucks (list): list of trucks
            cargos (list): list of cargos

        Return:
            distance_list (list): list of the distances between each pair of
            truck and cargo.
        """
        distance_list = []
        for cargo in cargos:
            cargo_id = cargo[0]
            cargo_info = cargo[1]
            cargo_coordinates = (float(cargo_info[strings.ORIGIN_LAT_KEY]),
                                 float(cargo_info[strings.ORIGIN_LNG_KEY]))
            for truck in trucks:
                truck_id = truck[0]
                truck_info = truck[1]
                truck_coordinates = (float(truck_info[strings.TRUCK_LAT_KEY]),
                                     float(truck_info[strings.TRUCK_LNG_KEY]))

                # get the distance between a truck and the cargo's origin
                distance = self.get_distance(truck_coordinates,
                                             cargo_coordinates)

                # create a dictionary with all the truck and cargo information
                distance_info = cargo_info.copy()
                distance_info.update(truck_info)
                distance_info[strings.TRUCK_ID_KEY] = truck_id
                distance_info[strings.CARGO_ID_KEY] = cargo_id
                distance_info[strings.DISTANCE_KEY] = distance

                # insert the dictionary in the distance list
                distance_list.append(distance_info)

        return distance_list

    def get_mapping(self):
        """
        Gets the optimal mapping of trucks to cargos.
        """
        cargos = None
        trucks = None
        allocated_trucks = []
        allocated_cargos = []
        minimal_distances = []

        # load data
        trucks, cargos = self.load_files()

        # get the distance list
        distance_list = self.get_distance_list(trucks, cargos)

        # sort the distance list
        sorted_distance_list = sorted(distance_list,
                                      key=itemgetter(strings.DISTANCE_KEY))

        # while there's still a cargo to be allocated
        while len(allocated_cargos) < len(cargos):

            # get the first truck of the sorted distance list
            minimal_distance = sorted_distance_list[0]
            truck_id = minimal_distance[strings.TRUCK_ID_KEY]
            cargo_id = minimal_distance[strings.CARGO_ID_KEY]

            # check if the truck and the cargo isn't allocated yet
            if truck_id not in allocated_trucks and \
               cargo_id not in allocated_cargos:

                # store the minimal distance
                minimal_distances.append(minimal_distance)

                # remove the allocated distance
                sorted_distance_list.pop(0)

                # register the truck and the cargo allocated
                allocated_trucks.append(truck_id)
                allocated_cargos.append(cargo_id)

            # the truck or the cargo is already allocated
            else:

                # remove the distance from the list
                sorted_distance_list.pop(0)

        return minimal_distances

    def load_files(self):
        """
        Load the data from trucks and cargos.

        Return:

            trucks (list): list of OrderedDict with the trucks' data
            cargos (list): list of OrderedDict with the cargos' data
        """
        # load the trucks
        with open(self.trucks_file, 'r') as trucks_file:
            trucks = list(enumerate(csv.DictReader(trucks_file)))

        # load the cargos
        with open(self.cargos_file, 'r') as cargos_file:
            cargos = list(enumerate(csv.DictReader(cargos_file)))

        return trucks, cargos

    def print_result(self, minimal_distances):
        """
        Given the list of the minimal distance dictionary, this method prints
        the formatted result message.

        Arguments:
            minimal_distances (list): a list of the minimal distance
            dictionary.
        """
        for d in minimal_distances:
            result_message = strings.RESULT_MESSAGE
            product = d.get(strings.PRODUCT_KEY, '')
            origin_city = d.get(strings.ORIGIN_CITY_KEY, '')
            origin_state = d.get(strings.ORIGIN_STATE_KEY, '')
            destination_city = d.get(strings.DESTINATION_CITY_KEY, '')
            destination_state = d.get(strings.DESTINATION_STATE_KEY, '')
            truck = d.get(strings.TRUCK_KEY, '')
            city = d.get(strings.CITY_KEY, '')
            state = d.get(strings.STATE_KEY, '')
            distance = d.get(strings.DISTANCE_KEY, '')
            print(result_message % (product,
                                    origin_city,
                                    origin_state,
                                    destination_city,
                                    destination_state,
                                    truck,
                                    city,
                                    state,
                                    distance))


if __name__ == "__main__":

    # parse the arguments
    parser = argparse.ArgumentParser(description=strings.SCRIPT_DESCRIPTION)
    parser.add_argument(strings.TRUCKS_ARG_NAME,
                        type=str,
                        help=strings.TRUCKS_ARG_HELP)
    parser.add_argument(strings.CARGOS_ARG_NAME,
                        type=str,
                        help=strings.CARGOS_ARG_HELP)
    args = parser.parse_args()
    trucks_file = args.trucks_file
    cargos_file = args.cargos_file

    # get the optimal mapping
    truck_mapping = TruckMapping(trucks_file, cargos_file)
    mapping = truck_mapping.get_mapping()
    truck_mapping.print_result(mapping)
