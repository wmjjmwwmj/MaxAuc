import matplotlib.pyplot as plt
import ast
import matplotlib.animation as animation

from P_MAS_TG.utils.import_module import import_module_from_path
from P_MAS_TG.utils.re_find import extract_from_file
from P_MAS_TG.utils.latest_output_path import latest_output_path
from pathlib import Path

def acquire_xy(index, env_size):
    """
    根据环境大小和索引返回坐标。
    """
    x = index // env_size
    y = index % env_size
    return (x, y)

if __name__ == '__main__':
    
    outputs_dir, log_file_path = latest_output_path()
    
    settings_n_pattern = r"\| settings_n\s*\| ([\d\.]+) \|"
    settings_n = extract_from_file(log_file_path, settings_n_pattern)
    
    # 给定路径数据
    path_pattern = r'MainThread - INFO - path: (\[\(.*\)\])'
    path_str = extract_from_file(log_file_path, path_pattern)
    path = ast.literal_eval(path_str)
    
    # 给定PBA路径数据
    PBA_path_pattern = r'MainThread - INFO - PBA path: (\[\(.*\)\])'
    PBA_path_str = extract_from_file(log_file_path, PBA_path_pattern)
    PBA_path = ast.literal_eval(PBA_path_str)
    

    settings_cls_draw = import_module_from_path(f"./settings/{settings_n}/settings.py")
    marker_shapes = settings_cls_draw.marker_shapes
    regions = settings_cls_draw.regions
    n = settings_cls_draw.n
    robot_num = settings_cls_draw.robot_num
    fps = settings_cls_draw.fps
    task_num = settings_cls_draw.task_num
    
    # 提取机器人的路径位置
    robot_positions = [[] for _ in range(robot_num)]

    for r in range(robot_num):
        for step in path:
            robot_positions[r].append(acquire_xy(step[r][0], n))
            
    # task_finished_aps = [[]]*task_num

    # for i in range(task_num):
    #     for step in PBA_path:
    #         task_finished_aps[i].append(step[r][0])

    # Create a figure and axis for plotting
    fig, (ax_map, ax_text) = plt.subplots(1, 2, figsize=(12, 6))
    # 设置坐标轴范围
    ax_map.set_xlim(-0.5, n-0.5)
    ax_map.set_ylim(-0.5, n-0.5)
    ax_map.set_xticks(range(n))
    ax_map.set_yticks(range(n))
    ax_map.grid(True)

    # 设置文字框为单独的图表
    ax_text.axis('off')  # 隐藏坐标轴
    
    text_box = ax_text.text(0.5, 0.5, '', fontsize=14, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))
    
    # 标记特殊区域
    for (x, y), label in regions.items():
        if label:
            ax_map.text(x, y, label, fontsize=12, ha='center', va='center', color='red', bbox=dict(facecolor='yellow', alpha=0.5), zorder = 0)

    robot_markers = {}  # 机器人的图标

    # 创建机器人的icon
    for id in range(robot_num):
        marker = marker_shapes.get(f"Robot-{id}", 'o')  # 如果没有指定，则使用默认圆形
        robot_markers[id], = ax_map.plot([], [], marker = marker, label=id)

    # 为图例中的标记去掉线条，只显示形状
    handles, labels = ax_map.get_legend_handles_labels()
    for handle in handles:
        handle.set_linestyle('None')  # 去掉线条，只保留标记

    ax_map.legend(handles, labels, loc = 'upper right')

    # 更新函数
    def update(frame):
        finished_text = ""
        # 更新机器人的位置
        for id in range(robot_num):
            robot_markers[id].set_data(robot_positions[id][frame][0], robot_positions[id][frame][1])
            if path[frame][id][1]:
                finished_text += f"Robot-{id} completes {path[frame][id][1]}\n"
        
        text_box.set_text(finished_text)
        return list(robot_markers.values()) + [text_box]

    # 创建动画
    ani = animation.FuncAnimation(fig, update, frames=len(path), interval=fps*1000, blit=True, repeat=False)

    # Save the animation as an mp4 file
    output_video_path = Path("outputs") / outputs_dir / 'multi_robot_motion.mp4'
    ani.save(output_video_path, writer='ffmpeg', fps=fps)

    print(f"Animation saved to: {output_video_path}")
