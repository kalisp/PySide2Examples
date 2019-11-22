from maya import cmds

def create_gear(teeth=10, length=0.3):
    """
    Creates gear object with teeth and their's specific lenght
    :param teeth: number of teeth sprocket gear should have
    :param length: length of teeth
    :return: tuple of transform, constructor, extrude for printing
    """
    spans = spans_count(teeth)

    transform, constructor = cmds.polyPipe(subdivisionsAxis=spans)
    print("{}, {}".format(transform, constructor))

    side_faces = create_side_faces(spans)
    cmds.select(clear=True)

    for face in side_faces:
        cmds.select("{}.f[{}]".format(transform, face), add=True)

    extrude = cmds.polyExtrudeFacet(localTranslateZ = length)[0] # extrude selected faces along Z axis

    return transform, constructor, extrude

def update_gear(constructor, extrude, teeth=10, length=0.3):
    """
    Updates created gear object with new values
    :param constructor: gear object
    :param extrude: list of extruded faces
    :param teeth: new number of teeth
    :param length: new length of teeth
    :return: void
    """
    spans = spans_count(teeth)
    side_faces = create_side_faces(spans)

    cmds.polyPipe(constructor, subdivisionsAxis=spans, edit=True)

    face_names = []

    for face in side_faces:
        face_name = "f[{}]".format(face)
        face_names.append(face_name)

    cmds.setAttr("{}.inputComponents".format(extrude),
                 len(face_names),
                 *face_names,
                 type="componentList")

    cmds.polyExtrudeFacet(extrude, edit=True, ltz=length)

def spans_count(teeth):
    """
    Returns number of spans for gear to be created. S
    :param teeth: number of teeth of the sprocket
    :return: number of spans (currently teeth * 2)
    """
    return teeth * 2

def create_side_faces(spans):
    """
    Returns list of numbers to use in face selection on the gear
    :param spans: number of spans in the modified gear
    :return: list of numbers used to select face of the gear to extrude
    """
    return range(spans * 2, spans * 3, 2)

# testing
transform, constructor, extrude = create_gear()

update_gear(constructor, extrude, 30)

