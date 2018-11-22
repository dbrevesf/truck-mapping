Optimal Mapping of Trucks and Cargos (Post-office Problem)

* Author

  * Daniel Breves Ferreira
  * dbrevesf@gmail.com

* Introduction

  Given a list of trucks and their current locations and a list of cargos and their pickup and delivery locations, the algorithms find the optimal mapping of trucks to cargos to minimize the overall distances the trucks must travel​. That's a variation of the Post-Office Problem proposed by Donald Knuth in vol. 3 of The Art of Computer Programming (1973).

* Files

  This project contains the following files:

  - truck_mapping.py : The first implementation of the solution. It uses a quadratic algorithm to solve the problem.

  - truck_mapping_kdtree.py: The second implementation of the solution. Now, using an efficient algorithm which brought us a logarithmic solution. 

  - test_truck_mapping.py: Unit tests for the truck_mapping_kdtree.py.

  - strings.py : File containing all the strings used in our scripts.

  - cargos.csv : Cargos dataset

  - trucks.csv : Trucks Dataset 

  - README.md : This file :p

  - /test_cases : Directory containing all the dataset for the unit tests.

* Description of The Solution

  First, I made a solution using a 'brute force' algorithm, which is:

  1) Get all the distances between the trucks and the origin of the cargos.

  2) Sort the distances

  3) Get the first element of the sorted list

  4) If the truck is already allocated, discard this element and repeat 3)

  5) If the truck is available, store it in a list of optimal distances. 

  6) It stops when all the cargos were allocated to a truck.

  This solution is good for small cases but it doesn't scale for a large dataset due to its quadratic time complexity. So, I went for another solution and I found the kd-tree data structure that has a logarithmic time complexity, which is great for our problem. So, as the purpose of this challenge was the selection of minimal distances, I took the Scipy library to construct the kd-tree. Once it was done, the solution to get the optimal mapping was:

  1) Find the k-nearest trucks from each cargo. Where k is the number of cargos.

  2) Take the nearest truck of a cargo

    2.1) If the truck is available, save it in a list of minimal distances

    2.2) If the truck is already being used, compare the distance between this truck and the two cargos and selects the one with the smallest distance

  3) If we iterate over the cargos and don't complete the list of minimal distances, repeat 2) for the second (and third, fourth, etc) nearest truck until the list is completed.


* Running

  To run our script we need to execute the following command:

  ```python truck_mapping_kdtree.py trucks.csv cargo.csv```

  or, if you want to run the quadratic solution:

  ```python truck_mapping.py trucks.csv cargo.csv```


* Testing

  There are some unit tests written to test ```truck_mapping_kdtree.py```. To run the unit tests, you'll need the pytest installed and execute:

  ```pytest -q test_truck_mapping.py```


* Work Environment

  This project was developed in a MacBook with the following specs:

  * Model: MacBook Pro Retina 13-inch
  * Processor: Intel Core i5 2,7 GHz
  * Memory: 8 Gb
  * O.S.: macOS High Sierra

  The software specifications of this project are:

  * Programming Language: Python 3.6.5
  * Libraries: 
    * Scipy 1.0.1
    * Haversine 1.0.2

