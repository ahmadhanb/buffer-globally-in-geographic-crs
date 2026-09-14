# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import re
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSource,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFeatureSink)
import processing


class CreateBufferGlobally(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT_POINT'
    INPUT2 = 'INPUT_POLYGON'
    BUFFERDIST = 'BUFFERDIST'
    SEGMENT = 'SEGMENT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateBufferGlobally()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'buffer_globally_in_geographic'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Buffer Globally in Geographic CRS')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('My scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'myscripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("This tool creates a buffer distance in METER for data \
                        distributed globally. It uses input point data in WGS 84 \
                        while in the same time accept buffer distance in meter, \
                        and the output polygon data will be in WGS 84. The tool \
                        considers the correct location of each point with reference\
                        to the UTM zone that is located in.\n\
                        Therefore, the UTM zone feature must be used and as Input UTM\
                        zone layer in order for the tool to work correctly.\n\
                        <b>Input Layer:</b> use point vector layer only.\n\
                        <b>Input UTM Zone Layer:</b> use the UTM polygon layer.\n\
                        <b>Buffer Distance (meter):</b> enter the buffer distance in meter.\n\
                        <b>Number of Segments:</b> enter the number of segments, the \
                        default value is 50.\n\
                        <b>Output layer:</b> save the output polygon data to a shapefile\
                        or memory.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer (Point)'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT2,
                self.tr('Input UTM Zone Layer (Polygon)'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )        

        self.addParameter(
            QgsProcessingParameterNumber(
                'BUFFERDIST',
                self.tr('Buffer Distance (meter)'),
                defaultValue = 1000.0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                'SEGMENT',
                self.tr('Number of Segments'),
                defaultValue = 50
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output layer'),
                QgsProcessing.TypeVectorAnyGeometry
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        source2 = self.parameterAsSource(
            parameters,
            self.INPUT2,
            context
        )
        
        buffer_dis = self.parameterAsDouble(
            parameters, 
            'BUFFERDIST', 
            context
        )
        
        segment = self.parameterAsInt(
            parameters, 
            'SEGMENT', 
            context
        )
        
        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

#            sink = self.parameterAsOutputLayer(
#            parameters,
#            self.OUTPUT,
#            context
#        )

#        (sink, dest_id) = self.parameterAsSink(
#           parameters,
#           self.OUTPUT,
#            context,
#           source.fields(),
#            source.wkbType(),
#            source.sourceCrs()
#        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # If sink was not created, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSinkError method to return a standard
        # helper text for when a sink cannot be evaluated
#        if sink is None:
#            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            # sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # To run another Processing algorithm as part of this algorithm, you can use
        # processing.run(...). Make sure you pass the current context and feedback
        # to processing.run to ensure that all temporary layer outputs are available
        # to the executed algorithm, and that the executed algorithm can send feedback
        # reports to the user (and correctly handle cancelation and progress reports!)
        fieldName = "UTM_ZONE"
        
        params = {
            'INPUT' : parameters['INPUT_POINT'],
            'JOIN' : parameters['INPUT_POLYGON'], 
            'PREDICATE': 0,
            'JOIN_FIELDS': ['HEMISPHERE','ZONE'],
            'METHOD': 1,
            'DISCARD_NONMATCHING': 1,
            'PREFIX': '',
            'OUTPUT' : 'memory:'
        }
            
        # Performing Spatial Join between the location points and the UTM Zone Polygon  
        sp_join = processing.run("qgis:joinattributesbylocation", params)
        
        params = {
            'INPUT' : sp_join['OUTPUT'],
            'FIELD_NAME' : fieldName, 
            'FIELD_TYPE': 2,
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': 1,
            'FORMULA': '\"ZONE\" + upper(\"HEMISPHERE\")',
            'OUTPUT' : 'memory:'
        }
        
        # Add a new field population the UTM Zones
        newField = processing.run("qgis:fieldcalculator", params)
    
        newField_layer = newField['OUTPUT']
        
        shpfiles = []
        uniqueValues = sorted({feature[fieldName] for feature in newField_layer.getFeatures()})
        for uniqueValue in uniqueValues:
            params = {
                'INPUT' : newField['OUTPUT'],
                'FIELD' : fieldName, 
                'OPERATOR': 0,
                'VALUE': uniqueValue,
                'OUTPUT' : 'memory:'
            }
            
            # Add a new field population the UTM Zones
            memoryLayer = processing.run("qgis:extractbyattribute", params,)
            
            crs = QgsCoordinateReferenceSystem()
            zone = re.findall('\d+',uniqueValue)[0]
            zone = str(int(zone))
            hemisphere = re.findall('\D+',uniqueValue)[0]
            hemi= '+south' if hemisphere == 'S' else ''
            my_proj = f"+proj=utm +zone={zone} +datum=WGS84 +units=m +no_defs {hemi}"
            crs.createFromProj4(my_proj)
            crs_target = f"PROJ4:{crs.toProj4()}"
        #    crs_target = f"EPSG:{crs.postgisSrid()}"
            params = {
                'INPUT' : memoryLayer['OUTPUT'],
                'TARGET_CRS' : crs_target, 
                'OUTPUT' : 'memory:'
            }
            utmLayer = processing.run("qgis:reprojectlayer", params)
    
            params = {
                'INPUT' : utmLayer['OUTPUT'],
                'DISTANCE' : buffer_dis,
                'SEGMENTS' : segment,
                'END_CAP_STYLE' : 0,
                'JOIN_STYLE' : 0,
                'DISSOLVE' : False,
                'OUTPUT' : 'memory:'
            }
            
            buffer = processing.run("native:buffer", params)
            
            shpfiles.append(buffer['OUTPUT'])
    
        params = {
            'LAYERS' : shpfiles,
            'CRS' : "EPSG:4326", 
            'OUTPUT' : 'memory:'
        }
        mergeWGS = processing.run("qgis:mergevectorlayers", params)
        
        params = {
            'INPUT' : mergeWGS['OUTPUT'],
            'COLUMN' : ['Layer','Path'],
            'OUTPUT' : parameters['OUTPUT']
        }
        dropField = processing.run("qgis:deletecolumn", params, context=context, feedback=feedback)
        
        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        
        #return {self.OUTPUT: dest_id}
        return {self.OUTPUT: dropField['OUTPUT']}
