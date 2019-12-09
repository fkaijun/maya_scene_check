# coding=utf-8
"""
maya check functions:
    find_triangle_edge: 检查三边面
    find_many_edge: 检查多边面
    find_non_manifold_edges： 检查非流形边
    find_lamina_faces： 检查薄边面
    find_bivalent_faces: 检查两个边共享一个点的同时两个面共享一个点
    find_zero_area_faces: 检查不足面积的面
    find_mesh_border_edges: 检查边界边
    find_crease_edges: 检查折痕边
    find_zero_length_edges: 检查不足长度的边
    find_unfrozen_vertices: 检查点的世界坐标是否为0.0进而判断点未进行冻结变换
"""
import maya.cmds as cmds
import maya.api.OpenMaya as om


def find_triangle_edge(mesh_name):
    """
    check triangle edge
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: Component list
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)

    dag_path = mesh_list.getDagPath(0)

    mfn_mesh = om.MFnMesh(dag_path)
    face_numbers = mfn_mesh.numPolygons

    triangle_face_list = ['{0}.f[{1}]'.format(cmds.listRelatives(mesh_name, p=1)[0], a) for a in xrange(face_numbers) if
                          mfn_mesh.polygonVertexCount(a) < 4]

    return triangle_face_list


def find_many_edge(mesh_name):
    """
    Check faces larger than 4 sides
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: Component list
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)

    dag_path = mesh_list.getDagPath(0)

    mfn_mesh = om.MFnMesh(dag_path)
    face_numbers = mfn_mesh.numPolygons

    triangle_face_list = ['{0}.f[{1}]'.format(cmds.listRelatives(mesh_name, p=1)[0], a) for a in xrange(face_numbers) if
                          mfn_mesh.polygonVertexCount(a) >= 5]

    return triangle_face_list


def find_non_manifold_edges(mesh_name):
    """
    Check for non-manifold edges
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: edge index
    :rtype: list
    """

    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    edge_it = om.MItMeshEdge(dag_path)

    edge_indices = []

    while not edge_it.isDone():
        face_count = edge_it.numConnectedFaces()
        if face_count > 2:
            edge_indices.append(edge_it.index())
        edge_it.next()
    return edge_indices


def find_lamina_faces(mesh_name):
    """
    Check lamina faces
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: face index
    :rtype: list
    """

    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    poly_it = om.MItMeshPolygon(dag_path)
    poly_indices = []

    while not poly_it.isDone():

        if poly_it.isLamina():
            poly_indices.append(poly_it.index())
        poly_it.next(1)

    return poly_indices


def find_bivalent_faces(mesh_name):
    """
    Check bivalent faces
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: vertex index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    vertex_it = om.MItMeshVertex(dag_path)
    vertex_indices = []

    while not vertex_it.isDone():
        connect_faces = vertex_it.getConnectedFaces()
        connect_edges = vertex_it.getConnectedEdges()

        if len(connect_faces) == 2 and len(connect_edges) == 2:
            vertex_indices.append(vertex_it.index())
        vertex_it.next()

    return vertex_indices


def find_zero_area_faces(mesh_name, max_face_area):
    """
    Check zero area faces
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :param float max_face_area: max face area
    :return: face index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    poly_it = om.MItMeshPolygon(dag_path)
    poly_indices = []

    while not poly_it.isDone():

        if poly_it.getArea() < max_face_area:
            poly_indices.append(poly_it.index())
        poly_it.next(1)

    return poly_indices


def find_mesh_border_edges(mesh_name):
    """
    Check mesh border edges
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: edge index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    edge_it = om.MItMeshEdge(dag_path)

    edge_indices = []

    while not edge_it.isDone():
        if edge_it.onBoundary():
            edge_indices.append(edge_it.index())
        edge_it.next()
    return edge_indices


def find_crease_edges(mesh_name):
    """
    Check mesh border edges
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: edge index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)

    dag_path = mesh_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)

    edge_ids, crease_data = mfn_mesh.getCreaseEdges()

    edge_indices = []

    for index in xrange(len(edge_ids)):
        if crease_data[index] != 0:
            edge_indices.append(edge_ids[index])
    return edge_indices


def find_zero_length_edges(mesh_name, min_edge_length):
    """
    Check mesh border edges
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :param float min_edge_length: min edge length
    :return: edge index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    edge_it = om.MItMeshEdge(dag_path)

    edge_indices = []

    while not edge_it.isDone():
        if edge_it.length() < min_edge_length:
            edge_indices.append(edge_it.index())
        edge_it.next()
    return edge_indices


def find_unfrozen_vertices(mesh_name):
    """
    Check unfrozen vertices
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: vertice index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    mesh_fn = om.MFnMesh(dag_path)
    dag_path.extendToShape()

    dag_node = om.MFnDagNode(dag_path)

    pnts_plug = dag_node.findPlug("pnts", True)

    num_vertices = mesh_fn.numVertices

    vertice_indices = []

    for i in xrange(num_vertices):
        xyz_plug = pnts_plug.elementByLogicalIndex(i)
        if xyz_plug.isCompound:
            xyz = [0.0, 0.0, 0.0]
            for a in range(3):
                xyz[a] = xyz_plug.child(a).asFloat()
            if not (abs(xyz[0]) <= 0.0 and abs(xyz[1]) <= 0.0 and abs(xyz[2]) <= 0.0):
                vertice_indices.append(i)
    return vertice_indices


if __name__ == '__main__':
    mesh_name = '|group3|pSphere1'
    print find_unfrozen_vertices(mesh_name)
