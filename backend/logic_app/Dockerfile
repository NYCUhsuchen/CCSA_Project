# 使用官方 Python 映像檔
FROM python:3.12-slim

# 設置工作目錄
WORKDIR /app

# 複製當前目錄下的所有檔案到 /app
COPY . .

# 安裝依賴
RUN pip3 install --no-cache-dir  -r requirements.txt

# 開放應用運行的端口
EXPOSE 5000

# 啟動 Flask 應用程式
CMD ["python", "app.py"]