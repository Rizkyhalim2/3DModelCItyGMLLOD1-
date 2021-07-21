import shapefile
from lxml import etree, objectify
import uuid



def build_gml_main():    
    # define Namespaces
    ns_base = "http://www.citygml.org/citygml/profiles/base/2.0"
    ns_gen = "http://www.opengis.net/citygml/generics/2.0"
    ns_core = "http://www.opengis.net/citygml/2.0"
    ns_bldg = "http://www.opengis.net/citygml/building/2.0"
    ns_gen = "http://www.opengis.net/citygml/generics/2.0"
    ns_gml = "http://www.opengis.net/gml"
    ns_xAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
    ns_xlink = "http://www.w3.org/1999/xlink"
    ns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
    ns_schemaLocation = "http://www.citygml.org/citygml/profiles/base/2.0 http://schemas.opengis.net/citygml/profiles/base/2.0/CityGML.xsd"

    #ns_core, ns_bldg, ns_gen, ns_gml, ns_xAL, ns_xlink, ns_xsi


    nsmap = {
        'core': ns_core,
        'bldg': ns_bldg,
        'gen': ns_gen,
        'gml': ns_gml,
        'xAL': ns_xAL,
        'xlink': ns_xlink,
        'xsi': ns_xsi,

    }

    # Main Element
    crs = 'EPSG:25833'
    cityModel = etree.Element("{%s}CityModel" % ns_core, nsmap=nsmap)
    cityModel.set('{%s}schemaLocation' % ns_xsi, ns_schemaLocation)
    # Add branch
    description = etree.SubElement(cityModel, "{%s}description" % ns_gml)
    description.text = "Created by Rizky"
    name = etree.SubElement(cityModel, "{%s}name" % ns_gml)
    name.text = "LoD_1Koica"
    # Add branch
    cityObjectMember = etree.SubElement(cityModel, '{%s}cityObjectMember' % ns_core)
    Building = etree.SubElement(cityObjectMember, '{%s}Building' % ns_bldg)
    Building.set('{%s}id' % ns_gml, 'ID_' + str('1'))
    boundedBy = etree.SubElement(Building, "{%s}boundedBy" % ns_gml)
    # Add branch to a branch

    envelop = etree.SubElement(boundedBy, '{%s}Envelope' % ns_gml, srsDimension='3')
    envelop.set('srsName', crs)
    lb = etree.SubElement(envelop, "{%s}lowerCorner" % ns_gml, srsDimension='3')
    lb.text = ''
    ub = etree.SubElement(envelop, "{%s}upperCorner" % ns_gml, srsDimension='3')
    ub.text = ''

    lod2Solid = etree.SubElement(Building, '{%s}lod2Solid' % ns_bldg)
    Solid = etree.SubElement(lod2Solid, '{%s}Solid' % ns_gml)
    exterior = etree.SubElement(Solid, '{%s}exterior' % ns_gml)
    CompositeSurface = etree.SubElement(exterior, '{%s}CompositeSurface' % ns_gml)
    # Read Shapefile
    shp_layer = read_shape()

    #lower corner
    point_min = None
    #upper corner
    point_max = None

    building_count = len(shp_layer.shapes())
    field_content = shp_layer.records()

    # iteration
    for i_build in range(building_count):


        # building shape area
        points_2D = shp_layer.shapes()[i_build].points

        # contents which are given in the shapefile and needed in the citygml model
        inits = building_inits(field_content[i_build], shp_layer)

        # for Citygml the lower and upper limit of all buildings are needed
        point_min, point_max = find_lower_upper_corner(points_2D, inits['roof'], point_min, point_max)

        # calculation of the polygon by useing the points from the building shape area
        polygon = polygon_caculation(inits, points_2D)
        roof2 = roof_calculation(inits, points_2D)
        ground2 = ground_calculation(inits, points_2D)


        # Add branch and sub-branche of a building
        creationDate = etree.SubElement(Building, "{%s}creationDate" % ns_core)
        creationDate.text = '2021-04-17'
        externalReference = etree.SubElement(Building, "{%s}externalReference" % ns_core)
        informationSystem = etree.SubElement(externalReference, "{%s}informationSystem" % ns_core)
        informationSystem.text = "TestKoicaLt1"
        externalObject = etree.SubElement(externalReference, "{%s}externalObject" % ns_core)
        name = etree.SubElement(externalObject, "{%s}name" % ns_core)
        name.text = inits['gml_id']


        function = etree.SubElement(Building, "{%s}function" % ns_bldg)
        function.text = str(inits['funktion'])

        measuredHeight = etree.SubElement(Building, "{%s}measuredHeight" % ns_bldg, uom="urn:adv:uom:m")
        measuredHeight.text = str(inits['roof'])


        # Add the 3d polygon
        Ground = '{%s}GroundSurface'
        Wall = '{%s}WallSurface'
        Roof = '{%s}RoofSurface'
        OuterFloor = '{%s}OuterFloorSurface'
        OuterCeiling = '{%s}OuterCeilingSurface'
        Closure = '{%s}ClosureSurface'

        for poly in polygon:
            surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
            boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
            Surface = etree.SubElement(boundedBy, Wall % ns_bldg)
            Surface.set('{%s}id' % ns_gml, surf_uuid)
            lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
            Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
            surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
            polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
            polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
            exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
            LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
            pos_text2 = ""
            for point in poly:
                pos_text1 = str(point[0]) + ' ' + str(point[1])+ ' ' + str(point[2])
                pos_text2 = pos_text2 + " " + pos_text1
                pos.text = pos_text2
            solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
            solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')

        surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
        boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
        Surface = etree.SubElement(boundedBy, Roof % ns_bldg)
        Surface.set('{%s}id' % ns_gml, surf_uuid)
        lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
        Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
        surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
        polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
        polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
        exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
        LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
        pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
        pos_text2 = ""
        for i in range(len(roof2)):
            pos_text1 = str(roof2[i][0]) + ' ' + str(roof2[i][1]) + ' ' +  str(roof2[i][2])
            pos_text2 = pos_text2 + " " + pos_text1
            pos.text = pos_text2
        solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
        solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')
        
        surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
        boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
        Surface = etree.SubElement(boundedBy,Ground % ns_bldg)
        Surface.set('{%s}id' % ns_gml, surf_uuid)
        lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
        Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
        surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
        polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
        polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
        exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
        LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
        pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
        pos_text2 = ""
        for i in range(len(ground2)):
            pos_text1 = str(ground2[i][0]) + ' ' + str(ground2[i][1]) + ' ' +  str(ground2[i][2])
            pos_text2 = pos_text2 + " " + pos_text1
            pos.text = pos_text2
        solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
        solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')

        print ('done')

    lb.text = str(point_min[0]) + ' ' + str(point_min[1])+ ' ' + str(point_min[2])
    ub.text = str(point_max[0]) + ' ' + str(point_max[1])+ ' ' + str(point_max[2])


    # Save File
    et = etree.ElementTree(cityModel)
    outFile = open('C:/Users/syams/Desktop/outputX.xml', 'wb')
    et.write(outFile, xml_declaration=True, encoding='utf-8', pretty_print= True)
    print ('done')

def iteration_buildings(cityModel, shp_layer, ns_core, ns_bldg, ns_gen, ns_gml, ns_xAL, ns_xlink, ns_xsi, Building, CompositeSurface):
    #lower corner
    point_min = None
    #upper corner
    point_max = None

    building_count = len(shp_layer.shapes())
    field_content = shp_layer.records()

    # iteration
    for i_build in range(building_count):


        # building shape area
        points_2D = shp_layer.shapes()[i_build].points

        # contents which are given in the shapefile and needed in the citygml model
        inits = building_inits(field_content[i_build], shp_layer)

        # for Citygml the lower and upper limit of all buildings are needed
        point_min, point_max = find_lower_upper_corner(points_2D, inits['roof'], point_min, point_max)

        # calculation of the polygon by useing the points from the building shape area
        polygon = polygon_caculation(inits, points_2D)
        roof2 = roof_calculation(inits, points_2D)
        ground2 = ground_calculation(inits, points_2D)


        # Add branch and sub-branche of a building
        creationDate = etree.SubElement(Building, "{%s}creationDate" % ns_core)
        creationDate.text = '2021-04-17'
        externalReference = etree.SubElement(Building, "{%s}externalReference" % ns_core)
        informationSystem = etree.SubElement(externalReference, "{%s}informationSystem" % ns_core)
        informationSystem.text = "TestKoicaLt1"
        externalObject = etree.SubElement(externalReference, "{%s}externalObject" % ns_core)
        name = etree.SubElement(externalObject, "{%s}name" % ns_core)
        name.text = inits['gml_id']


        function = etree.SubElement(Building, "{%s}function" % ns_bldg)
        function.text = str(inits['funktion'])

        measuredHeight = etree.SubElement(Building, "{%s}measuredHeight" % ns_bldg, uom="urn:adv:uom:m")
        measuredHeight.text = str(inits['roof'])


        # Add the 3d polygon
        Ground = '{%s}GroundSurface'
        Wall = '{%s}WallSurface'
        Roof = '{%s}RoofSurface'
        OuterFloor = '{%s}OuterFloorSurface'
        OuterCeiling = '{%s}OuterCeilingSurface'
        Closure = '{%s}ClosureSurface'

        for poly in polygon:
            surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
            boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
            Surface = etree.SubElement(boundedBy, Wall % ns_bldg)
            Surface.set('{%s}id' % ns_gml, surf_uuid)
            lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
            Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
            surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
            polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
            polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
            exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
            LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
            pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
            pos_text2 = ""
            for point in poly:
                pos_text1 = str(point[0]) + ' ' + str(point[1])+ ' ' + str(point[2])
                pos_text2 = pos_text2 + " " + pos_text1
                pos.text = pos_text2
            solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
            solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')

        surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
        boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
        Surface = etree.SubElement(boundedBy, Roof % ns_bldg)
        Surface.set('{%s}id' % ns_gml, surf_uuid)
        lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
        Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
        surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
        polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
        polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
        exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
        LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
        pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
        pos_text2 = ""
        for i in range(len(roof2)):
            pos_text1 = str(roof2[i][0]) + ' ' + str(roof2[i][1]) + ' ' +  str(roof2[i][2])
            pos_text2 = pos_text2 + " " + pos_text1
            pos.text = pos_text2
        solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
        solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')
        
        surf_uuid = 'UUID_' + str(uuid.uuid4()) + '_2'
        boundedBy = etree.SubElement(Building, '{%s}boundedBy' % ns_bldg)
        Surface = etree.SubElement(boundedBy,Ground % ns_bldg)
        Surface.set('{%s}id' % ns_gml, surf_uuid)
        lod2MultiSurface = etree.SubElement(Surface, "{%s}lod2MultiSurface" % ns_bldg)
        Multisurface = etree.SubElement(lod2MultiSurface, "{%s}MultiSurface" % ns_gml)
        surfaceMember = etree.SubElement(Multisurface, "{%s}surfaceMember" % ns_gml)
        polygon = etree.SubElement(surfaceMember, "{%s}Polygon" % ns_gml)
        polygon.set('{%s}id' % ns_gml, surf_uuid + '_poly')
        exterior = etree.SubElement(polygon, "{%s}exterior" % ns_gml)
        LinearRing = etree.SubElement(exterior, "{%s}LinearRing" % ns_gml)
        pos = etree.SubElement(LinearRing, "{%s}posList" % ns_gml, srsDimension='3')
        pos_text2 = ""
        for i in range(len(ground2)):
            pos_text1 = str(ground2[i][0]) + ' ' + str(ground2[i][1]) + ' ' +  str(ground2[i][2])
            pos_text2 = pos_text2 + " " + pos_text1
            pos.text = pos_text2
        solid_link = etree.SubElement(CompositeSurface, '{%s}surfaceMember' % ns_gml)
        solid_link.set('{%s}href' % ns_xlink, '#' + surf_uuid + '_poly')

        print ('done')


    return cityModel, point_max, point_min

def building_inits(content, shp_layer):
    inits = {}
    for i, field in zip(range(len(shp_layer.fields) - 1), shp_layer.fields[1:]):
        # print field[0]
        # print content[i]
        if field[0] == 'gml_id':
            inits['gml_id'] = content[i]
        elif field[0] == 'Elevasi':
            inits['roof_height'] = content[i]
        elif field[0] == 'Function':
            inits['funktion'] = content[i]

    # needed roof height for the 3d polygon
    # simple and mostly wrong calculation should be changed by user
    if int(inits['roof_height']):
        inits['roof'] = int(inits['roof_height'])
    else:
        inits['roof'] = 3.113    
    return inits

def read_shape():
  
    shp_read = shapefile.Reader('C:/Users/syams/Desktop/Koica Lt 1/Lobby_Koica.shp')
    return shp_read

def polygon_caculation(inits, points_2D):

    anz_polygone = len(points_2D)+2
    polygon = []
    ground = 0
    # extimated roof heigth
    roof = inits['roof'] + ground

    for point_A, point_B in zip(points_2D[:-1], points_2D[1:]):
        surface = []
        surface.append((point_A[0], point_A[1], roof))
        surface.append((point_B[0], point_B[1], roof))
        surface.append((point_B[0], point_B[1], ground))
        surface.append((point_A[0], point_A[1], ground))
        surface.append((point_A[0], point_A[1], roof))

        polygon.append(surface)

        print (point_A, point_B)

    

    return polygon

def roof_calculation(inits, points_2D) :

    # add roof, add ground
    anz_polygone = len(points_2D)+2
    polygon = []
    ground = 0
    # extimated roof heigth
    roof = inits['roof'] + ground
    roof = []
    for roof1 in points_2D:
        roof.append((roof1[0], roof1[1], roof))
    polygon.append(roof)

    
    

    return roof

def ground_calculation(inits, points_2D) :

    # add roof, add ground
    anz_polygone = len(points_2D)+2
    polygon = []
    ground = 0
    # extimated roof heigth
    roof = inits['roof'] + ground
    ground = []
    for ground1 in points_2D:
        ground.append((ground1[0], ground1[1], ground))
    polygon.append(ground)
    

    return ground

def find_lower_upper_corner(points_2D, roof, point_min, point_max):
    #compare the given points with the saved lower and upper limit
    # if lower or upper points exist, overwrite the saved ones
    points_2D_list = list(points_2D)
    if point_min is None:
        point_min = list(points_2D_list[0] + (0,))
        point_max = list(points_2D_list[0] + (0,))

    for point in points_2D_list:
        if point_min[0] > point[0]:
            point_min[0] = point[0]
        if point_max[0] < point[0]:
            point_max[0] = point[0]
        if point_min[1] > point[1]:
            point_min[1] = point[1]
        if point_max[1] < point[1]:
            point_max[1] = point[1]
        if point_max[2] < roof:
            point_max[2] = roof
    return point_min, point_max

build_gml_main()
