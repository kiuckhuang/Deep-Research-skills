---
name: research-add-items
user-invocable: true
description: 向現有調研outline補充items（調研對象）。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task, AskUserQuestion
---

# Research Add Items - 補充調研對象

## 觸發方式
`/research-add-items`

## 執行流程

### Step 1: 自動定位Outline
在當前工作目錄查找 `*/outline.yaml` 文件，自動讀取。

### Step 2: 並行獲取補充來源
同時進行：
- **A. 詢問用戶**：需要補充哪些items？有具體名稱嗎？
- **B. 詢問是否需要Web Search**：是否啟動agent搜索更多items？

### Step 3: 合併更新
- 將新items追加到outline.yaml
- 展示給用戶確認
- 避免重複
- 保存更新後的outline

## 輸出
更新後的 `{topic}/outline.yaml` 文件（原地修改）
