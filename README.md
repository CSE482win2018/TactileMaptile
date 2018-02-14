# TactileMaptile

## Background

[TactileMaptile](https://digital.lib.washington.edu/researchworks/handle/1773/40212) is the name of a project by Jessica Hamilton, in which she seeks to understand how maps can be made more accessible to those who are visually impaired, and researches how tactile maps can help those who are visually impaired to learn features of the urban landscape. Jessica investigates how design elements of tactile maps such as symbols, textures, and raised or lowered features (such as buildings and roads) can most effectively communicate information  to the user.

This is a project as part of the University of Washington's [CSE482: Capstone Software Design to Empower Underserved Populations](https://courses.cs.washington.edu/courses/cse482/18wi) that will programatically create tactile maps implementing Jessica's designs from [OpenStreetMap](http://www.openstreetmap.org) data, as well as provide an accessible web interface so that users can design their own tactile maps by deciding the location of the map and configuring a variety of options. 

## Local Development

### Web

Dependencies:
* [node.js](https://nodejs.org/en/)
* [Yarn](https://yarnpkg.com/en/)

Run the web app from the `client` directory, first running `yarn install`.

To watch changes, run `yarn start`. To create a production build, run `yarn build`. The app will by default run at `http://localhost:3000`.

### Generating maps

Dependencies:
* [Java JRE or JDK (at least 7)](http://www.oracle.com/technetwork/java/javase/downloads/index.html)
* [Gradle](https://gradle.org/install/)
* [Blender](https://www.blender.org/download/)
* [Python 3](https://www.python.org/downloads/)

Creating a map goes as follows:
* An `.osm` file is the input, which describes an area of the world. A .osm file can be download for an arbitary location from [OpenStreetMap](http://www.openstreetmap.org).
* OSM2World converts the `.osm` file to a `.obj` file.
* Blender converts the `.obj` file to a `.stl` file and can change features of the map such as its size as well as adding, removing, and modifying features of the map.
* A slicer program converts the `.stl` file into a file that a 3D printer can use.

`cd` to `server/map_generator`, and build the converter with `gradle installDist`.

To convert a `.osm` file to a `.obj` file, run:

```
build/install/map_generator/bin/map_generator [path to input .osm file] [path to output .obj file] [path to output .json file]
```

You can also run with gradle, which will build the project first:
```
gradle run -PappArgs="['path to input .osm file', 'path to output .obj file', 'path to output .json file']"
```

To create a `.blend` file from the resulting `.obj` file, run:

```
blender -b -P convert.py -- --scale [scale] --size [size] [path to input .obj file] [path to input .json file] [path to input .blend file] [path to output .stl file]
```

The `.obj` and `.json` files for input are the ones created in the previous step.

You can then open up Blender and look at the resulting map.
