import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
# Python 会先运行文件中的全局代码（即未包含在函数或类中的代码），然后再导入你指定的变量或对象。
# 其实应该读文件的，不能直接导入变量
from parse_log_second import log_df, outputs_path, latest_dir
import pandas as pd
import os
from settings import marker_shapes, regions, n, fps, regions

# Convert timestamp to datetime object for accurate time-based animation
# log_df['timestamp'] = pd.to_datetime(log_df['timestamp'], format='%Y-%m-%d %H:%M:%S')



# Create a figure and axis for plotting
fig, (ax_map, ax_text) = plt.subplots(1, 2, figsize=(12, 6))
ax_map.set_ylim(-0.5, n-0.5)
ax_map.set_xlim(-0.5, n-0.5)
ax_map.set_xticks(range(n))
ax_map.set_yticks(range(n))
ax_map.grid(True)

# 设置文字框为单独的图表
ax_text.axis('off')  # 隐藏坐标轴

# bbox=dict(facecolor='black', alpha=0.5)：这是一个字典，定义了文本框的边框属性。
# facecolor='black'：文本框的背景颜色为黑色。
# alpha=0.5：文本框的透明度为 0.5（50% 透明）。
text_box = ax_text.text(0.5, 0.5, '', fontsize=14, ha='center', va='center', bbox=dict(facecolor='black', alpha=0.5))

# 标记特殊区域
for (x, y), label in regions.items():
    if label:
        ax_map.text(x, y, label, fontsize=12, ha='center', va='center', color='red', bbox=dict(facecolor='yellow', alpha=0.5), zorder = 0)

# Store each robot's path
robot_paths = {robot_id: {'x': [], 'y': []} for robot_id in log_df['robot_id'].unique()}
robot_markers = {}

for robot_id in robot_paths.keys():
    marker = marker_shapes.get(robot_id, 'o')  # 如果没有指定，则使用默认圆形
    robot_markers[robot_id], = ax_map.plot([], [], marker=marker, label=robot_id) #, markersize=10)

# 为图例中的标记去掉线条，只显示形状
handles, labels = ax_map.get_legend_handles_labels()
for handle in handles:
    handle.set_linestyle('None')  # 去掉线条，只保留标记

ax_map.legend(handles, labels, loc = 'upper right')


# Update function for the animation, updating robot positions
def update(frame_time):
    # Filter data up to the current time
    current_time_data = log_df[log_df['timestamp'] <= frame_time]
    
    # iloc: 这是 Pandas 数据框的一个方法，用于基于整数位置（即行号）来选择数据。iloc 是“integer location”的缩写。
    
    # BUG update 函数中的 frame_time 参数是一个时间戳，而 log_df.iloc 需要一个整数索引。为了修复这个问题，我们需要将 update 函数的 frame_time 参数转换为整数索引。
    # current_time = log_df.iloc[frame_time]['timestamp']
    # current_frame_actions = log_df[log_df['timestamp'] == current_time]['action'] 
    
    # if 'finished' in current_frame_actions.values:
    #     text_box.set_text(f"Frame {frame_time}: Action 'finished' detected")
    # else:
    #     text_box.set_text(f"Frame {frame_time}: No 'finished' action detected")
    
    for robot_id in robot_paths.keys():
        # Get the latest position for the robot at the current time
        robot_data = current_time_data[current_time_data['robot_id'] == robot_id]
        if not robot_data.empty:
            latest_position = robot_data.iloc[-1]['position']
            x, y = latest_position
            robot_markers[robot_id].set_data([x], [y])
        else:
            robot_markers[robot_id].set_data([], [])

    # 检查是否存在 'finished' 的 action 条目
    finished_data = log_df[(log_df['timestamp'] == frame_time) & (log_df['action'] == 'finished')]
    finished_text = ""
    for index, row in finished_data.iterrows():
        robot_id = row['robot_id']
        option = row['option']
        finished_text += f"At {frame_time}s, {robot_id} finished action '{option}'\n"
    
    text_box.set_text(finished_text)
    
    return list(robot_markers.values()) + [text_box]

# Create an animation
timestamps = log_df['timestamp'].unique()

ani = animation.FuncAnimation(fig, update, frames=timestamps, blit=True, repeat=False)

# Save the animation as an mp4 file
output_video_path = os.path.join(outputs_path, latest_dir, 'multi_robot_motion.mp4')
ani.save(output_video_path, writer='ffmpeg', fps=fps)

print(f"Animation saved to: {output_video_path}")

# plt.legend()
# plt.show()

