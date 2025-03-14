from fileops import read_json
import numpy as np

if __name__ == "__main__":
    # 读取 JSON 文件
    data = read_json("extracted_results.json")
    
    results = {
        "4.2.2": [],
        "5.2.2": [],
        "6.2.2": [],
        "7.2.2": [],
        "8.2.2": []
    }
    
    time_results = {
        "4.2.2": [],
        "5.2.2": [],
        "6.2.2": [],
        "7.2.2": [],
        "8.2.2": []
    }
    
    for time, prop in data[0].items():
        
        for setting in ["4.2.2", "5.2.2", "6.2.2", "7.2.2", "8.2.2"]:
        
            if prop["settings_n"] == setting:
                results[setting].append(prop["makespan"])
                time_results[setting].append(prop["total_time"])
            
    
    for i in ["4.2.2", "5.2.2", "6.2.2", "7.2.2", "8.2.2"]:
        print(f"Setting: {i}")
        print(f"batch_size: {len(results[i])}")
        print(f"makespan: {sum(results[i])/len(results[i])}")
        print("makespan_std: ", np.std(results[i]))
        print(f"total_time: {sum(time_results[i])/len(time_results[i])}")
        print("total_time_std: ", np.std(time_results[i]))
        print("=====================================")