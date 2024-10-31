#!/bin/sh

# 校验必须的环境变量
if [ -z "$SECRET_CODE" ]; then
  echo "Error: SECRET_CODE is not set.\n 需要一个密钥变量SECRET_CODE"
  exit 1
fi

#if [ -z "$ANOTHER_REQUIRED_VAR" ]; then
#  echo "Error: ANOTHER_REQUIRED_VAR is not set."
#  exit 1
#fi

# 如果所有环境变量都存在，则启动uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 80 --workers 4 "$@"
