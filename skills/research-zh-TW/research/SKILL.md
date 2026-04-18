---
name: research
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: 對目標話題進行初步調研，生成調研outline。用於學術調研、benchmark調研、技術選型等場景。
---

# Research Skill - 初步調研

## 觸發方式
`/research <topic>`

## 執行流程

### Step 1: 模型內部知識生成初步框架
基於topic，利用模型已有知識生成：
- 該領域的主要研究對象/items列表
- 建議的調研欄位框架

輸出{step1_output}，使用AskUserQuestion確認：
- items列表是否需要增減？
- 欄位框架是否滿足需求？

### Step 2: Web Search補充
使用AskUserQuestion詢問時間範圍（如：最近6個月、2024年至今、不限）。

**參數獲取**：
- `{topic}`: 用戶輸入的調研話題
- `{YYYY-MM-DD}`: 當前日期
- `{step1_output}`: Step 1生成的完整輸出內容
- `{time_range}`: 用戶指定的時間範圍

**硬約束**：以下prompt必須嚴格複述，僅替換{xxx}中的變數，禁止改寫結構或措辭。

啟動1個web-search-agent（後台），**Prompt模板**：
```python
prompt = f"""## 任務
調研話題: {topic}
當前日期: {YYYY-MM-DD}

基於以下初步框架，補充最新items和推薦調研欄位。

## 已有框架
{step1_output}

## 目標
1. 驗證已有items是否遺漏重要對象
2. 根據遺漏對象進行補充items
3. 繼續搜索{topic}相關且{time_range}內的items並補充
4. 補充新fields

## 輸出要求
直接返回結構化結果（不寫文件）：

### 補充Items
- item_name: 簡要說明（為什麼應該加入）
...

### 推薦補充欄位
- field_name: 欄位描述（為什麼需要這個維度）
...

### 資訊來源
- [來源1](url1)
- [來源2](url2)
"""
```

**One-shot示例**（假設調研AI Coding發展史）：
```
## 任務
調研話題: AI Coding 發展史
當前日期: 2025-12-30

基於以下初步框架，補充最新items和推薦調研欄位。

## 已有框架
### Items列表
1. GitHub Copilot: Microsoft/GitHub開發，首個主流AI編程助手
2. Cursor: AI-first IDE，基於VSCode
...

### 欄位框架
- 基本資訊: name, release_date, company
- 技術特性: underlying_model, context_window
...

## 目標
1. 驗證已有items是否遺漏重要對象
2. 根據遺漏對象進行補充items
3. 繼續搜索AI Coding 發展史相關且2024年至今內的items並補充
4. 補充新fields

## 輸出要求
直接返回結構化結果（不寫文件）：

### 補充Items
- item_name: 簡要說明（為什麼應該加入）
...

### 推薦補充欄位
- field_name: 欄位描述（為什麼需要這個維度）
...

### 資訊來源
- [來源1](url1)
- [來源2](url2)
```

### Step 3: 詢問用戶已有欄位
使用AskUserQuestion詢問用戶是否有已定義的欄位文件，如有則讀取並合併。

### Step 4: 生成Outline（分離文件）
合併{step1_output}、{step2_output}和用戶已有欄位，生成兩個文件：

**outline.yaml**（items + 配置）：
- topic: 調研主題
- items: 調研對象列表
- execution:
  - batch_size: 並行agent數量（需AskUserQuestion確認）
  - items_per_agent: 每個agent調研項目數（需AskUserQuestion確認）
  - output_dir: 結果輸出目錄（默認./results）

**fields.yaml**（欄位定義）：
- 欄位分類和定義
- 每個欄位的name、description、detail_level
- detail_level分層：極簡 → 簡要 → 詳細
- uncertain: 不確定欄位列表（保留欄位，deep階段自動填充）

### Step 5: 輸出並確認
- 創建目錄: `./{topic_slug}/`
- 保存: `outline.yaml` 和 `fields.yaml`
- 展示給用戶確認

## 輸出路徑
```
{current_working_directory}/{topic_slug}/
  ├── outline.yaml    # items列表 + execution配置
  └── fields.yaml     # 欄位定義
```

## 後續命令
- `/research-add-items` - 補充items
- `/research-add-fields` - 補充欄位
- `/research-deep` - 開始深度調研
