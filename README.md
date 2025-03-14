# 简介




# TODO

之后的发展方向




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

### copy baseline's settings 

注意分支名要完整

git checkout remotes/origin/baseline/makespan_optimal -- settings

