# TactileMaptile

## Background

[TactileMaptile](https://digital.lib.washington.edu/researchworks/handle/1773/40212) is the name of a project by Jessica Hamilton, in which she seeks to understand how maps can be made more accessible to those who are visually impaired, and researches how tactile maps can help those who are visually impaired to learn features of the urban landscape. Jessica investigates how design elements of tactile maps such as symbols, textures, and raised or lowered features (such as buildings and roads) can most effectively communicate information  to the user.

This is a project as part of the University of Washington's [CSE482: Capstone Software Design to Empower Underserved Populations](https://courses.cs.washington.edu/courses/cse482/18wi) that will programatically create tactile maps implementing Jessica's designs from [OpenStreetMap](http://www.openstreetmap.org) data, as well as provide an accessible web interface so that users can design their own tactile maps by deciding the location of the map and configuring a variety of options. 

## Local Development

### Web
TBD

### Generatin maps

Prerequisite software:
* [Java JRE or JDK (at least 8)](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
    ** After installing, ensure that `java` is available on your system's `PATH`.
* [Blender](https://www.blender.org/download/)
    ** After installing, ensure that `blender` is available on your system's `PATH`. 
* [Python 3](https://www.python.org/downloads/)
    ** After installing, ensure that `python3` is available on your system's `PATH`.
* [OSM2World](http://osm2world.org/download/) - the necessary JAR file can either be downloaded from the site or built from source, and should be put under the `map_generator` directory.

Creating a map goes as follows:
* An `.osm` file is the input, which describes an area of the world. A .osm file can be download for an arbitary location from [OpenStreetMap](http://www.openstreetmap.org).
* OSM2World converts the `.osm` file to a `.obj` file
* Blender converts the `.obj` file to a .stl file and can change features of the map such as its size as well as adding, removing, and modifying features of the map.
* A slicer program converts the `.stl` file into a file that a 3D printer can use.

To create an `.osm` file, run this command:

```
java -jar OSM2World.jar -i [path to input .osm file] -o [path to output .obj file]
```

To create a `.blend` file from the resulting `.obj` file, run this command (inside the `map_generator` directory)

```
blender -b -P convert.py -- [path to input .obj file] -o [path to output .blend file]
```

You can then open up Blender and look at the resulting map.
