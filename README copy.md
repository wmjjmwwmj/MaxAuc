# 简介




# TODO

## 在最优时间下，路径从非最优变最优

目前的算法只考虑了时间成本，没有考虑路径成本；
需要修改multi_pba构造时的weight，成为一个tuple，先是时间，再是总路径，比较的时候会依次比较。


# Tutorial

## Install
```
pip install -r requirements.txt
```

## Run

1. The main code is in auction_mp.py

## Draw trace

```
python .\draw.py
```
This will automatically parse the latest log file in the `.\outputs` folder.

The draw config may need change

## Others

### 清理输出 in powershell

Remove-Item ".\outputs\*" -Recurse  (-Force)

### 检查一个路径是否存在

python .\P_MAS_TG\utils\check_path_valid.py --path ("")

### 传大文件的问题

Issu: exceeds GitHub's file size limit of 100.00 MB

出现这个问题之后，即使删掉了文件重新commit，Git 可能仍然保留了该文件的历史记录，如果检测到这些文件的存在，就会拒绝提交。

#### 挽救

`git rev-list --objects --all | findstr "multi_ts.pkl"` 查找文件的历史记录 findstr 是 windows 的命令，相当于 grep

`pip install git-filter-repo` git 官方推荐，用于编辑历史记录

以上是gpt回答，不好用

stackoverflow 

`git lfs migrate import --include="*.pkl"` 好用



#### 确保大文件使用 LFS 管理

git lfs track "*.pkl"
git add .gitattributes

## 结果备份

