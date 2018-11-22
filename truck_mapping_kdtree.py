#!/usr/bin/env python3.6

"""
Truck Mapping - finds the optimal mapping of trucks and cargos.
"""
from haversine import haversine
from scipy.spatial import KDTree

import csv
import argparse
import strings


class TruckMapping(object):
    """
    A class which contains the methods used to obtain an optimal mapping of
    trucks that will travel the minimum distance to take some cargo from the
    origin to destination.
    """

    def __init__(self, trucks_file, cargos_file):

        self.trucks_file = trucks_file
        self.cargos_file = cargos_file

    def get_empty_cargo_dictionary(self):
        """
        Returns an empty dictionary with the cargo keys.

        Return:
            empty_dict (dictionary): dictionary with empty values
        """
        empty_value = strings.EMPTY_VALUE
        empty_dict = {strings.PRODUCT_KEY: empty_value,
                      strings.ORIGIN_CITY_KEY: empty_value,
                      strings.ORIGIN_STATE_KEY: empty_value,
                      strings.ORIGIN_LAT_KEY: empty_value,
                      strings.ORIGIN_LNG_KEY: empty_value,
                      strings.DESTINATION_CITY_KEY: empty_value,
                      strings.DESTINATION_STATE_KEY: empty_value}
        return empty_dict

    def get_empty_truck_dictionary(self):
        """
        Returns an empty dictionary with the truck keys.

        Return:
            empty_dict (dictionary): dictionary with empty values
        """
        empty_value = strings.EMPTY_VALUE
        empty_dict = {strings.TRUCK_KEY: empty_value,
                      strings.CITY_KEY: empty_value,
                      strings.STATE_KEY: empty_value,
                      strings.TRUCK_LAT_KEY: empty_value,
                      strings.TRUCK_LNG_KEY: empty_value}

        return empty_dict

    def get_distance(self, origin, destination):
        """
        Calculates the Haversine distance between two points. The Haversine
        distance is a formula which determines the great-circle distance
        between two points on a sphere given their longitude and latitude.

        This method was created due to future needs of changing it to call some
        Maps API to calculate the distance instead of Haversine. The chosen of
        Haversine was made because the Google Maps API doesn't accept more than
        100 requests for a free account.

        Arguments:
            origin (tuple): origin coordinates
            destination (tuple): destination coordinates

        Return:
            distance (float): Haversine distance between origin and destination
        """
        distance = 0
        if origin is not None and destination is not None:
            distance = haversine(origin, destination)

        return distance

    def get_mapping(self):
        """
        Get the optimal mapping of trucks to cargos using a k-d tree.

        Return:
            optimal_mapping (list): the optimal mapping to trucks and cargos
        """
        # load data
        trucks, cargos = self.load_files()

        # create list of coordinates for trucks and cargos
        trucks_coord = [(float(t[strings.TRUCK_LAT_KEY]),
                         float(t[strings.TRUCK_LNG_KEY])) for t in trucks]
        cargos_coord = [(float(c[strings.ORIGIN_LAT_KEY]),
                         float(c[strings.ORIGIN_LNG_KEY])) for c in cargos]

        # create the kdtree for trucks
        trucks_kd_tree = KDTree(trucks_coord)

        # get the mapping
        nearest_trucks = self.get_nearest_trucks(cargos_coord, trucks_kd_tree)

        # build the optimal mapping array
        optimal_mapping = []
        for truck_index, cargo_coord in zip(nearest_trucks, cargos_coord):
            truck_exists = truck_index >= 0
            if truck_exists:
                truck_coord = trucks_kd_tree.data[truck_index]
                optimal_mapping.append([truck_coord, cargo_coord])
            else:
                optimal_mapping.append([None, cargo_coord])

        return optimal_mapping

    def get_nearest_trucks(self, cargos_coord, kd_tree):
        """
        Given the kd-tree with the trucks coordinates, this method returns the
        nearest trucks from the cargos. The KDTree class from scipy is used to
        build the tree and calculate the k nearest trucks, but it's on the
        method responsibility solving conflicts between cargos with the same
        nearest truck.

        Arguments:
            cargos_coord (list): a list of cargos' coordinates
            kd_tree (KDTree): Kd-tree with the trucks' coordinates

        Return:
            optimal_mapping (list): a list containing pairs of cargo and truck
            with the smallest distance possible.
        """
        # get the amount of cargos
        length_of_cargos = len(cargos_coord)

        # get the k nearest trucks where k is the amount of cargos
        query = kd_tree.query(cargos_coord, length_of_cargos)

        # get the distances of the k nearest trucks from the cargos
        distances = query[0]

        # get the index of the k nearest trucks from the cargos
        k_nearest_trucks_index = query[1]

        # initialize the array for the nearest trucks.
        # nearest_trucks[i] = -1 means that any truck was allocated for the
        # cargo i
        nearest_trucks = length_of_cargos * [-1]

        # get the nearest trucks

        for position in range(length_of_cargos):
            for cargo in range(length_of_cargos):

                # get the current truck
                truck = k_nearest_trucks_index[cargo][position]

                # check existence of the truck. This check is necessary to
                # deal with cases with less trucks than needed. The query over
                # kd-tree returns a value even if the truck isn't exists. So,
                # we need to check the kd-tree for the truck existence
                try:
                    kd_tree.data[truck]
                    truck_exists = True
                except IndexError:
                    truck_exists = False

                # check if current cargo's still not allocated to any truck
                cargo_deallocated = nearest_trucks[cargo] == -1

                if cargo_deallocated:

                    # check if the current truck is allocated
                    truck_allocated = truck in nearest_trucks

                    if truck_allocated:

                        # get the index of the allocated truck
                        allocated_truck_index = nearest_trucks.index(truck)

                        # clear the allocation for the allocated truck
                        nearest_trucks[allocated_truck_index] = -1

                        # get the distances between the trucks
                        truck_distance = distances[cargo][position]
                        alloc_truck_distance = distances[allocated_truck_index]
                        alloc_truck_distance = alloc_truck_distance[position]

                        # select the truck nearest from the cargo
                        if truck_distance < alloc_truck_distance:
                            if truck_exists:
                                nearest_trucks[cargo] = truck
                        else:
                            if truck_exists:
                                nearest_trucks[allocated_truck_index] = truck

                    # if the truck isn't allocated, allocate it to the cargo
                    else:
                        if truck_exists:
                            nearest_trucks[cargo] = truck

                # current cargo is allocated to a truck
                else:

                    # if all the cargo is allocated, our job is done here
                    cargos_allocated = -1 not in nearest_trucks
                    if cargos_allocated:
                        break

        return nearest_trucks

    def get_travel_information(self, optimal_mapping):
        """
        Given the mapping with trucks and cargos coordinates, this method
        builds a list of dictionaries with the information about them.

        Arguments:
            optimal_mapping (list): a list of pairs of truck and cargos with
            the smallest path between them.

        Return:
            travel_information (list): a list of dictionaries with the travel
            information.
        """
        # load files
        trucks, cargos = self.load_files()

        # get the information details for each coordinate
        travel_information = []
        for truck_coord, cargo_coord in optimal_mapping:
            minimal_distance_info = {}
            if cargo_coord is not None:
                for cargo in cargos:
                    if float(cargo[strings.ORIGIN_LAT_KEY]) == cargo_coord[0] \
                       and float(cargo[strings.ORIGIN_LNG_KEY]) == \
                       cargo_coord[1]:
                        minimal_distance_info = cargo.copy()
            else:
                # if for some case the returned cargo coordinates were None
                # we add an empty dictionary to the list of informations
                minimal_distance_info = self.get_empty_cargo_dictionary()

            if truck_coord is not None:
                for truck in trucks:
                    if float(truck[strings.TRUCK_LAT_KEY]) == truck_coord[0] \
                       and float(truck[strings.TRUCK_LNG_KEY]) == \
                       truck_coord[1]:
                        minimal_distance_info.update(truck)
            else:
                # if for some case the returned trucks coordinates were None
                # we add an empty dictionary to the list of informations
                minimal_distance_info.update(self.get_empty_truck_dictionary())

            # get the distance between a truck and a cargo
            distance = self.get_distance(truck_coord, cargo_coord)
            minimal_distance_info[strings.DISTANCE_KEY] = distance
            travel_information.append(minimal_distance_info)

        return travel_information

    def load_files(self):
        """
        Load the data from trucks and cargos.

        Return:

            trucks (list): a list of OrderedDict with the trucks' data
            cargos (list): a list of OrderedDict with the cargos' data
        """
        # load the trucks
        with open(self.trucks_file, 'r') as trucks_file:
            trucks = list(csv.DictReader(trucks_file))

        # load the cargos
        with open(self.cargos_file, 'r') as cargos_file:
            cargos = list(csv.DictReader(cargos_file))

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
            empty_value = strings.EMPTY_VALUE
            result_message = strings.RESULT_MESSAGE
            product = d.get(strings.PRODUCT_KEY, empty_value)
            origin_city = d.get(strings.ORIGIN_CITY_KEY, empty_value)
            origin_state = d.get(strings.ORIGIN_STATE_KEY, empty_value)
            destination_city = d.get(strings.DESTINATION_CITY_KEY, empty_value)
            destination_state = d.get(strings.DESTINATION_STATE_KEY,
                                      empty_value)
            truck = d.get(strings.TRUCK_KEY, empty_value)
            city = d.get(strings.CITY_KEY, empty_value)
            state = d.get(strings.STATE_KEY, empty_value)
            distance = d.get(strings.DISTANCE_KEY, empty_value)
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

    # you can stop here, if you want

    # get information details about the truck and cargo
    travel_information = truck_mapping.get_travel_information(mapping)

    # print the information
    truck_mapping.print_result(travel_information)
