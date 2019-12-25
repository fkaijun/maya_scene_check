# -*- coding: utf-8 -*-
# ================================
# @Time    : 2019/12/25 09:00
# @Author  : KaiJun Fan
# @Email   : qq826530928@163.com
# ================================
import maya.api.OpenMaya as om
import maya.cmds as cmds


def judge_edge_position(edges_point, edges_point_ju):
    """
    Determine if two edges may intersect
    :param edges_point:
    :param edges_point_ju:
    :return:
    """
    # judge u
    if min(edges_point[0][0], edges_point[1][0]) > max(edges_point_ju[0][0], edges_point_ju[1][0]) or \
            min(edges_point_ju[0][0], edges_point_ju[1][0]) > max(edges_point[0][0], edges_point[1][0]):
        return True
    # judge v
    elif min(edges_point[0][1], edges_point[1][1]) > max(edges_point_ju[0][1], edges_point_ju[1][1]) or\
            min(edges_point_ju[0][1], edges_point_ju[1][1]) > max(edges_point[0][1], edges_point[1][1]):
        return True
    else:
        return False


def get_max_min_uv(face_point):
    """
    get face max uv value and min uv value
    :param face_point: face point uv value
    :return:
    """
    if len(face_point) == 4:
        return min(face_point[0][0], face_point[1][0], face_point[2][0], face_point[3][0]), \
               max(face_point[0][0], face_point[1][0], face_point[2][0], face_point[3][0]), \
               min(face_point[0][1], face_point[1][1], face_point[2][1], face_point[3][1]), \
               max(face_point[0][1], face_point[1][1], face_point[2][1], face_point[3][1])
    elif len(face_point) == 3:
        return min(face_point[0][0], face_point[1][0], face_point[2][0]), \
               max(face_point[0][0], face_point[1][0], face_point[2][0]), \
               min(face_point[0][1], face_point[1][1], face_point[2][1]), \
               max(face_point[0][1], face_point[1][1], face_point[2][1])


def judge_face_position(edges_point, edges_point_ju):
    """
    Determine if two faces may intersect
    :param tuple edges_point: edges point uv value
    :param tuple edges_point_ju: edges point uv value
    :return:
    """

    if edges_point[0] >= edges_point_ju[1] or \
            edges_point_ju[0] >= edges_point[1] or \
            edges_point[2] >= edges_point_ju[3] or \
            edges_point_ju[2] >= edges_point[3]:
        return True
    elif (edges_point[0] == edges_point_ju[0] and edges_point[1] == edges_point_ju[1]) and \
            (edges_point[2] == edges_point_ju[2] and edges_point[3] == edges_point_ju[3]):

        return True
    else:
        return False


def judge_edge(edges_point, edges_point_ju):
    """
    judge edge intersect
    :param list edges_point: edges point uv value
    :param list edges_point_ju: edges point uv value
    :return: bool
    """

    x1 = edges_point[0][0] - edges_point[1][0]
    y1 = edges_point[0][1] - edges_point[1][1]

    x2 = edges_point_ju[0][0] - edges_point[1][0]
    y2 = edges_point_ju[0][1] - edges_point[1][1]

    x3 = edges_point_ju[1][0] - edges_point[1][0]
    y3 = edges_point_ju[1][1] - edges_point[1][1]

    x4 = edges_point_ju[0][0] - edges_point_ju[1][0]
    y4 = edges_point_ju[0][1] - edges_point_ju[1][1]

    x5 = edges_point[0][0] - edges_point_ju[1][0]
    y5 = edges_point[0][1] - edges_point_ju[1][1]

    x6 = edges_point[1][0] - edges_point_ju[1][0]
    y6 = edges_point[1][1] - edges_point_ju[1][1]

    if (x1 * y2 - x2 * y1) * (x1 * y3 - x3 * y1) < 0.0 and (x4 * y5 - x5 * y4) * (x4 * y6 - x6 * y4) < 0.0:
        return True
    else:
        return False


def main_function(mesh):
    """
    check overlapping uv
    :param str mesh : object long name eg.'|group3|pSphere1'
    :return: mesh face list
    :rtype: list
    """
    # get MFnMesh
    select_list = om.MSelectionList()
    select_list.add(mesh)
    dag_path = select_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)

    face_id_over = []   # store overlapping face
    all_uv_value_dict = {}   # store all uv value on the face
    max_min_uv_dict = {}   # store all uv max and min value on the face
    face_edges_dict = {}   # Store all edges on the face

    for face_id in xrange(mfn_mesh.numPolygons):
        face_edges_dict[face_id] = []
        uv_value_list = []
        for point_index in xrange(len(mfn_mesh.getPolygonVertices(face_id))):
            uv_value_list.append(mfn_mesh.getPolygonUV(face_id, point_index))

        all_uv_value_dict[face_id] = uv_value_list
        max_min_uv_dict[face_id] = get_max_min_uv(uv_value_list)
        for i in xrange(len(uv_value_list)):
            if i == len(uv_value_list) - 1:
                edges_value = [(uv_value_list[i][0], uv_value_list[i][1]), (uv_value_list[0][0], uv_value_list[0][1])]
            else:
                edges_value = [(uv_value_list[i][0], uv_value_list[i][1]), (uv_value_list[i + 1][0], uv_value_list[i+1][1])]

            face_edges_dict[face_id].append(edges_value)

    for face_id in xrange(mfn_mesh.numPolygons):

        edges_list = face_edges_dict[face_id]
        for face_id_next in xrange(face_id + 1, mfn_mesh.numPolygons):
            have = 0   # if edges intersect 'have is 1'
            edg_list_next = face_edges_dict[face_id_next]

            if not judge_face_position(max_min_uv_dict[face_id], max_min_uv_dict[face_id_next]):

                for edges_point in edges_list:
                    if have == 0:
                        for edg_point_ju in edg_list_next:

                            if not judge_edge_position(edges_point, edg_point_ju):

                                if judge_edge(edges_point, edg_point_ju):

                                    if face_id not in face_id_over:
                                        have = 1
                                        face_id_over.append(face_id)
                                    if face_id_next not in face_id_over:
                                        have = 1
                                        face_id_over.append(face_id_next)

                                    break
                    else:
                        break

    return ['{0}.f[{1}]'.format(mesh, face_id_num) for face_id_num in face_id_over]


if __name__ == '__main__':
    cmds.select(main_function('pSphereShape1'), r=1)
