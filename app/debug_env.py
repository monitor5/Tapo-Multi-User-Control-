import os
print("환경변수 목록:")
for key, value in os.environ.items():
    print(f"{key}={value}") 