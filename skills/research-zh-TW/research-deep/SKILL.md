---
name: research-deep
user-invocable: true
description: 讀取調研outline，為每個item啟動獨立agent進行深度調研。禁用task output。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - 深度調研

## 觸發方式
`/research-deep`

## 執行流程

### Step 1: 自動定位Outline
在當前工作目錄查找 `*/outline.yaml` 文件，讀取items列表、execution配置（含items_per_agent）。

### Step 2: 斷點續傳檢查
- 檢查output_dir下已完成的JSON文件
- 跳過已完成的items

### Step 3: 分批執行
- 按batch_size分批（完成一批需要得到用戶同意才可進行下一批）
- 每個agent負責items_per_agent個項目
- 啟動web-search-agent（後台並行，禁用task output）

**參數獲取**：
- `{topic}`: outline.yaml中的topic欄位
- `{item_name}`: item的name欄位
- `{item_related_info}`: item的完整yaml內容（name + category + description等）
- `{output_dir}`: outline.yaml中execution.output_dir（默認./results）
- `{fields_path}`: {topic}/fields.yaml的絕對路徑
- `{output_path}`: {output_dir}/{item_name_slug}.json的絕對路徑（slugify處理item_name：空格替換為_，移除特殊字元）

**硬約束**：以下prompt必須嚴格複述，僅替換{xxx}中的變數，禁止改寫結構或措辭。

**Prompt模板**：
```python
prompt = f"""## 任務
調研 {item_related_info}，輸出結構化JSON到 {output_path}

## 欄位定義
讀取 {fields_path} 獲取所有欄位定義

## 輸出要求
1. 按fields.yaml定義的欄位輸出JSON
2. 不確定的欄位值標註[不確定]
3. JSON末尾添加uncertain陣列，列出所有不確定的欄位名
4. 所有欄位值必須使用中文輸出（調研過程可用英文，但最終JSON值為中文）
5. 必須包含sources欄位，格式為包含url同description欄位的對象列表
```

**One-shot示例**（假設調研GitHub Copilot）：
```
## 任務
調研 name: GitHub Copilot
category: 國際產品
description: Microsoft/GitHub開發，首個主流AI編程助手，市場份額約40%，輸出結構化JSON到 {project_dir}/results/GitHub_Copilot.json

## 欄位定義
讀取 {project_dir}/fields.yaml 獲取所有欄位定義

## 輸出要求
1. 按fields.yaml定義的欄位輸出JSON
2. 不確定的欄位值標註[不確定]
3. JSON末尾添加uncertain陣列，列出所有不確定的欄位名
4. 所有欄位值必須使用中文輸出（調研過程可用英文，但最終JSON值為中文）
5. 必須包含sources欄位，格式為包含url同description欄位的對象列表

## 輸出路徑
{project_dir}/results/GitHub_Copilot.json

## 驗證
完成JSON輸出後，運行驗證腳本確保欄位完整覆蓋：
python ~/.claude/skills/research/validate_json.py -f {project_dir}/fields.yaml -j {project_dir}/results/GitHub_Copilot.json
驗證通過後才算完成任務。
```

### Step 4: 等待與監控
- 等待當前批次完成
- 啟動下一批
- 顯示進度

### Step 5: 匯總報告
全部完成後輸出：
- 完成數量
- 失敗/不確定標記的items
- 輸出目錄

## Agent配置
- 後台執行: 是
- Task Output: 禁用（agent完成時有明確輸出文件）
- 斷點續傳: 是
