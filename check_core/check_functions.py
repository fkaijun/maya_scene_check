# -*- coding: utf-8 -*-
# ================================
# @Time    : 2019/10/26 23:00
# @Author  : KaiJun Fan
# @Email   : qq826530928@163.com
# ================================
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
    has_vertex_pnts_attr: 检查点的世界坐标是否为0.0，可将值修复为0
    uv_face_cross_quadrant: 检查跨越uv象限的面
    missing_uv_faces: 检查面的uv时候丢失
    check_uv_overlapping.main_function: 检查uv重叠面
    find_double_faces：检查两个面共用所有点
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
    Check mesh crease edges
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
    Check mesh zero length edges
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


def has_vertex_pnts_attr(mesh_name, fix):
    """
    check vertex pnts attr value and reset value
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :param fix: Whether to reset 
    :return: bool
    :rtype: bool
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    dag_path.extendToShape()
    dag_node = om.MFnDagNode(dag_path)
    pnts_array = dag_node.findPlug("pnts", True)
    data_handle = pnts_array.asMDataHandle()

    arraydata_handle = om.MArrayDataHandle(data_handle)

    if not fix:
        while True:
            output_handle = arraydata_handle.outputValue()
            xyz = output_handle.asFloat3()
            if xyz:
                if xyz[0] != 0.0:
                    pnts_array.destructHandle(data_handle)
                    return True
                if xyz[1] != 0.0:
                    pnts_array.destructHandle(data_handle)
                    return True
                if xyz[2] != 0.0:
                    pnts_array.destructHandle(data_handle)
                    return True
            status = arraydata_handle.next()
            if not status:
                break
    else:
        pntx = dag_node.attribute("pntx")
        pnty = dag_node.attribute("pnty")
        pntz = dag_node.attribute("pntz")
        while True:
            output_handle = arraydata_handle.outputValue()

            xHandle = output_handle.child(pntx)
            yHandle = output_handle.child(pnty)
            zHandle = output_handle.child(pntz)
            xHandle.setFloat(0.0)
            yHandle.setFloat(0.0)
            zHandle.setFloat(0.0)

            status = arraydata_handle.next()
            if not status:
                break
        pnts_array.setMdata_handle(data_handle)
    pnts_array.destructHandle(data_handle)
    return False


def uv_face_cross_quadrant(mesh_name):
    """
    Check uv face cross quadrant
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: face index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)
    uv_face_list = []

    face_it = om.MItMeshPolygon(dag_path)

    while not face_it.isDone():
        u_quadrant = None
        v_quadrant = None
        uvs = face_it.getUVs()

        for index, uv_coordinates in enumerate(uvs):
            # u
            if index == 0:
                for u_coordinate in uv_coordinates:
                    if u_quadrant is None:
                        u_quadrant = int(u_coordinate)
                    if u_quadrant != int(u_coordinate):
                        component_name = '{0}.f[{1}]'.format(mesh_name, face_it.index())
                        if component_name not in uv_face_list:
                            uv_face_list.append(component_name)
                        print index, uv_coordinates
            # v
            if index == 1:
                for v_coordinate in uv_coordinates:
                    if v_quadrant is None:
                        v_quadrant = int(v_coordinate)
                    if v_quadrant != int(v_coordinate):
                        component_name = '{0}.f[{1}]'.format(mesh_name, face_it.index())
                        if component_name not in uv_face_list:
                            uv_face_list.append(component_name)
                        print index, uv_coordinates

        face_it.next(None)
    return uv_face_list


def missing_uv_faces(mesh_name):
    """
    Check face has uv
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: face index
    :rtype: list
    """
    miss_uv_face = []
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    face_it = om.MItMeshPolygon(dag_path)

    while not face_it.isDone():
        if face_it.hasUVs() is False:
            component_name = '{0}.f[{1}]'.format(mesh_name, face_it.index())
            miss_uv_face.append(component_name)
        face_it.next(None)

    return miss_uv_face


def find_double_faces(mesh_name):
    """
    Check all points common to both faces
    :param str mesh_name: object long name eg.'|group3|pSphere1'
    :return: vertex index
    :rtype: list
    """
    mesh_list = om.MSelectionList()
    mesh_list.add(mesh_name)
    dag_path = mesh_list.getDagPath(0)

    vertex_it = om.MItMeshVertex(dag_path)
    vertex_indices = []

    face_id = []

    while not vertex_it.isDone():
        connect_faces = vertex_it.getConnectedFaces()
        connect_edges = vertex_it.getConnectedEdges()
        # print connect_faces, connect_edges
        if len(connect_faces) == 5 and len(connect_edges) == 4:

            vertex_indices.append(vertex_it.index())
            if face_id == []:
                face_id = list(connect_faces)
            else:
                face_id = list(set(face_id).intersection(set(list(connect_faces))))
            print face_id
        vertex_it.next()
    cmds.select(['{0}.f[{1}]'.format(mesh_name, a) for a in face_id])


if __name__ == '__main__':
    mesh_name = '|group3|pSphere1'
    print find_unfrozen_vertices(mesh_name)
