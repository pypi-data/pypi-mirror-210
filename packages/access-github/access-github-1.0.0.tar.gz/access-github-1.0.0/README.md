# Access GitHub

## 緣由與動機
🔑關鍵：最關鍵的動機是讓全球百萬開發者，都能免費享受分散運算 20 VMs 加速能力!驅動 Github Actions。
💣地雷：直接去用 gpt-4 開發 github api 會撞牆，寫出一堆與最新文件不相容的程式碼，因此要避開此地雷。

而在日常的軟體開發過程中，我們經常需要和 GitHub 進行交互。例如，從不同的存儲庫中讀取文件，更新文件，創建和刪除文件等。雖然我們可以通過 GitHub 網站界面完成這些操作，但在某些情況下，使用命令行或 Python 腳本來進行這些操作會更加方便。
為了解決這些問題，本專案設計了一個簡單可用的 Python 庫和對應的命令行工具，以幫助開發者在不離開終端或編程環境的情況下與 GitHub 進行交互。這將大大提高我們的工作效率，使得開發過程更加流暢。

## 安裝方法
通過以下命令安裝 `access-github`：
```
python3 -m pip install access-github
```

## 命令行工具用法
使用 `python3 -m access_github` 可以使用命令行工具，下面是具體用法：

```
python3 -m access_github [operation] --token TOKEN --url URL [other_arguments]
```

### 可用操作
- `get_tree`: 獲取指定存儲庫的代碼樹
- `read_file`: 讀取指定路徑的文件內容
- `update_file`: 更新指定路徑的文件內容
- `create`: 創建指定路徑的文件或文件夾
- `delete`: 刪除指定路徑的文件或文件夾
- `create_or_update_github_action`: 創建或更新 GitHub Actions 工作流配置文件
- `dispatch_github_action`: 觸發指定的 GitHub Actions 工作流

### 用法範例：
以下是一些常見的用法示例：
1. 獲取存儲庫的代碼樹：
   ```
   python3 -m access_github get_tree --token TOKEN --url REPO_URL
   ```

2. 讀取指定路徑的文件內容：
   ```
   python3 -m access_github read_file --token TOKEN --url REPO_URL --path FILE_PATH
   ```

3. 更新指定路徑的文件內容：
   ```
   python3 -m access_github update_file --token TOKEN --url REPO_URL --path FILE_PATH --content NEW_CONTENT --name YOUR_NAME --email YOUR_EMAIL
   ```

4. 創建文件：
   ```
   python3 -m access_github create --token TOKEN --url REPO_URL --path FILE_PATH_OR_FOLDER --content FILE_CONTENT --name YOUR_NAME --email YOUR_EMAIL
   ```

5. 刪除文件：
   ```
   python3 -m access_github delete --token TOKEN --url REPO_URL --path FILE_PATH
   ```

6. 創建 GitHub Actions 工作流：
   ```
   python3 -m access_github create_or_update_github_action --token TOKEN --url REPO_URL --path WORKFLOW_YML_FILE_PATH --content WORKFLOW_YML_CONTENT
   ```

7. 觸發 GitHub Actions 工作流：
   ```
   python3 -m access_github dispatch_github_action --token TOKEN --url REPO_URL --workflow_yml_filename WORKFLOW_YML_FILENAME --event_type EVENT_TYPE --client_payload CLIENT_PAYLOAD
   ```

## Python 庫用法
可以通過 `from access_github import FUNCTION_NAME` 來導入需要使用的功能，如：
```python
from access_github import get_tree, read_file, update_file, create, delete, create_or_update_github_action, dispatch_github_action
```

### 函數參考
1. `get_tree(token: str, url: str) -> dict`: 獲取指定存儲庫的代碼樹
2. `read_file(token: str, url: str, path: str) -> dict`: 讀取指定路徑的文件內容
3. `update_file(token: str, name: str, email: str, url: str, path: str, content: str) -> dict`: 更新指定路徑的文件內容
4. `create(token: str, name: str, email: str, url: str, path: str, content: str) -> dict`: 創建指定路徑的文件
5. `delete(token: str, url: str, path: str) -> dict`: 刪除指定路徑的文件
6. `create_or_update_github_action(token: str, url: str, path: str, content: str) -> dict`: 創建或更新 GitHub Actions 工作流配置文件
7. `dispatch_github_action(token: str, url: str, workflow_yml_filename: str, event_type: str, client_payload: str) -> str`: 觸發指定的 GitHub Actions 工作流

### 函數使用範例
以下是使用 Python 庫操作的示例：
```python
from access_github import get_tree, read_file, update_file, create, delete
token = 'your_token'
url = 'https://github.com/user/repo.git'
path = 'path/to/file.txt'

# 獲取代碼樹
tree = get_tree(token, url)

# 讀取文件
content = read_file(token, url, path)

# 更新文件
update_result = update_file(token, 'your_name', 'your_email', url, path, 'new_content')

# 創建文件
create_result = create(token, 'your_name', 'your_email', url, 'path/to/new/file', 'file_content')

# 刪除文件
delete_result = delete(token, url, 'path/to/file')
```
請根據您的需求選擇合適的函數進行操作。