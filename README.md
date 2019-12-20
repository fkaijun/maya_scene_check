# maya_scene_check
当前的检查函数：
### model check
- find_triangle_edge: 检查三边面
- find_many_edge: 检查多边面
- find_non_manifold_edges： 检查非流形边
- find_lamina_faces： 检查薄边面
- find_bivalent_faces: 检查两个边共享一个点的同时两个面共享一个点
- find_zero_area_faces: 检查不足面积的面
- find_mesh_border_edges: 检查边界边
- find_crease_edges: 检查折痕边
- find_zero_length_edges: 检查不足长度的边
- find_unfrozen_vertices: 检查点的世界坐标是否为0.0进而判断点未进行冻结变换
- has_vertex_pnts_attr: 检查点的世界坐标是否为0.0，可将值修复为0

### uv check
- uv_face_cross_quadrant: 检查跨越uv象限的面
- missing_uv_faces: 检查面的uv时候丢失