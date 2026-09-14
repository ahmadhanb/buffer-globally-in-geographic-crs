# Buffer Globally In Meter Units Using Geographic Coordinate Reference System (CRS)

This tool creates a buffer distance in METER for data distributed globally. It uses input point data in WGS 84 while in the same time accept buffer distance in meter, and the output polygon data will be in WGS 84. The tool considers the correct location of each point with reference to the UTM zone that is located in.
Therefore, the UTM zone feature must be used and as Input UTM zone layer in order for the tool to work correctly.

## How to install
Import the Python code directly from the QGIS Processing Toolbox. 

### Input Layer:
use point vector layer only.

### Input UTM Zone Layer:
Use the UTM polygon layer.

### Buffer Distance (meter):
Enter the buffer distance in meter.

### Number of Segments:
Enter the number of segments, the default value is 50.

### Output layer:
Save the output polygon data to a shapefile or memory.
