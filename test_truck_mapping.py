#!/usr/bin/env python3.6

"""
Unit Tests class for TruckMapping
"""
from truck_mapping_kdtree import TruckMapping

import strings


class TestTruckMapping(object):

    """
    Class which contains the unit tests for the TruckMapping class methods.
    """
    def test_get_optimal_mapping_best_case(self):
        """
        The best case is when for every cargo there's a different nearest
        truck. So, in just one iteration, our algorithm can return the optimal
        mapping.
        """
        trucks_file = 'test_cases/best_case_trucks.csv'
        cargos_file = 'test_cases/best_case_cargos.csv'
        truck_mapping = TruckMapping(trucks_file, cargos_file)
        mapping = truck_mapping.get_mapping()
        travel_information = truck_mapping.get_travel_information(mapping)
        truck = None
        for travel in travel_information:
            if float(travel[strings.ORIGIN_LAT_KEY]) == -21.807536:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -21.907536
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -22.283857:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -22.183857
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -22.895935:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -22.875935

    def test_get_optimal_mapping_worst_case(self):
        """
        The worst case is when every cargo shares the same nearest truck for
        every truck. So, our algorithm have to iterate over all the
        possibilities in order to achieve the optimal mapping.
        """
        trucks_file = 'test_cases/worst_case_trucks.csv'
        cargos_file = 'test_cases/worst_case_cargos.csv'
        truck_mapping = TruckMapping(trucks_file, cargos_file)
        mapping = truck_mapping.get_mapping()
        travel_information = truck_mapping.get_travel_information(mapping)
        truck = None
        for travel in travel_information:
            if float(travel[strings.ORIGIN_LAT_KEY]) == -21.768693:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -22.632956
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -21.747775:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -23.301845
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -21.739611:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -23.619809

    def test_get_optimal_mapping_missing_trucks(self):
        """
        This test covers the case where there's more cargos than trucks. So,
        there will be one or more cargos that will not be reached for any
        truck. However, the allocation of the existent trucks would be optimal.
        """
        trucks_file = 'test_cases/missing_trucks_trucks.csv'
        cargos_file = 'test_cases/missing_trucks_cargos.csv'
        truck_mapping = TruckMapping(trucks_file, cargos_file)
        mapping = truck_mapping.get_mapping()
        travel_information = truck_mapping.get_travel_information(mapping)
        truck = None
        for travel in travel_information:
            if float(travel[strings.ORIGIN_LAT_KEY]) == -21.768693:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -22.632956
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -21.747775:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -23.301845
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -21.739611:
                truck = travel[strings.TRUCK_LAT_KEY]
                assert truck == 'None'

    def test_get_optimal_mapping_more_trucks_than_cargos(self):
        """
        It's the trivial test.
        """
        trucks_file = 'test_cases/more_trucks_than_cargos_trucks.csv'
        cargos_file = 'test_cases/more_trucks_than_cargos_cargos.csv'
        truck_mapping = TruckMapping(trucks_file, cargos_file)
        mapping = truck_mapping.get_mapping()
        travel_information = truck_mapping.get_travel_information(mapping)
        truck = None
        for travel in travel_information:
            if float(travel[strings.ORIGIN_LAT_KEY]) == -21.768693:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -22.632956
            elif float(travel[strings.ORIGIN_LAT_KEY]) == -21.747775:
                truck = float(travel[strings.TRUCK_LAT_KEY])
                assert truck == -23.301845
