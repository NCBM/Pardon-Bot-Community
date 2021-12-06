#!/usr/bin/env bash

echo "请输入数据存储位置："
read -p "Enter data storage path: " data_path
sed s/@PDBOT_DATA_PATH@/"${data_path}"/g userlib/paths.py.in > userlib/paths.py

echo "请输入自定义管理用户 QQ 号（可以留空，多个 QQ 号之间用英文逗号分割）："
read -p "Enter custom manager ID: " custom_managers
sed s/@PDBOT_CUSTOM_MANAGER@/"${custom_managers}"/g bot/plugins/botctl/plugins/develop/config.py.in > bot/plugins/botctl/plugins/develop/config.py
