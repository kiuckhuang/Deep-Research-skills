---
name: research-report
user-invocable: true
description: 將deep調研結果匯總為markdown報告，覆蓋所有欄位，跳過不確定值。
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Research Report - 匯總報告

## 觸發方式
`/research-report`

## 執行流程

### Step 1: 定位結果目錄
在當前工作目錄查找 `*/outline.yaml`，讀取topic和output_dir配置。

### Step 2: 掃描可選摘要欄位
讀取所有JSON結果，提取適合在目錄中顯示的欄位（數值型、簡短指標），例如：
- github_stars
- google_scholar_cites
- swe_bench_score
- user_scale
- valuation
- release_date

使用AskUserQuestion詢問用戶：
- 目錄中除了item名稱外，還需要顯示哪些欄位？
- 提供動態選項列表（基於實際JSON中存在的欄位）

### Step 3: 生成Python轉換腳本
在 `{topic}/` 目錄下生成 `generate_report.py`，腳本要求：
- 讀取output_dir下所有JSON
- 讀取fields.yaml獲取欄位結構
- 覆蓋每個JSON的所有欄位值
- 跳過值包含[不確定]的欄位
- 跳過uncertain陣列中列出的欄位
- 生成markdown報告格式：目錄（帶錨點跳轉+用戶選擇的摘要欄位）+ 詳細內容（按欄位分類）
- 保存到 `{topic}/report.md`

**目錄格式要求**：
- 必須包含每一個item
- 每個item顯示：序號、名稱（錨點連結）、用戶選擇的摘要欄位
- 示例：`1. [GitHub Copilot](#github-copilot) - Stars: 10k | Score: 85%`

#### 腳本技術要點（必須遵循）

**1. JSON結構相容**
支援兩種JSON結構：
- 扁平結構：欄位直接在頂層 `{"name": "xxx", "release_date": "xxx"}`
- 巢狀結構：欄位在category子dict中 `{"basic_info": {"name": "xxx"}, "technical_features": {...}}`

欄位查找順序：頂層 -> category映射key -> 遍歷所有巢狀dict

**2. Category多語言映射**
fields.yaml的category名與JSON的key可能是任意組合（中中、中英、英中、英英）。必須建立雙向映射：
```python
CATEGORY_MAPPING = {
    "基本資訊": ["basic_info", "基本資訊"],
    "技術特性": ["technical_features", "technical_characteristics", "技術特性"],
    "效能指標": ["performance_metrics", "performance", "效能指標"],
    "里程碑意義": ["milestone_significance", "milestones", "里程碑意義"],
    "商業資訊": ["business_info", "commercial_info", "商業資訊"],
    "競爭與生態": ["competition_ecosystem", "competition", "競爭與生態"],
    "歷史沿革": ["history", "歷史沿革"],
    "市場定位": ["market_positioning", "market", "市場定位"],
}
```

**3. 複雜值格式化**
- list of dicts（如key_events, funding_history）：每個dict格式化為一行，用` | `分隔kv
- 普通list：短列表用逗號連接，長列表換行顯示
- 巢狀dict：遞迴格式化，用分號或換行顯示
- 長文本字串（超過100字元）：添加換行符`<br>`或使用blockquote格式，提高可讀性

**4. 額外欄位收集**
收集JSON中有但fields.yaml中沒定義的欄位，放入"其他資訊"分類。注意過濾：
- 內部欄位：`_source_file`, `uncertain`
- 巢狀結構頂層key：`basic_info`, `technical_features`等
- `uncertain`陣列：需要逐行顯示每個欄位名，不要壓縮成一行

**5. 資訊來源展示**
每個item部分必須展示sources欄位。格式如下：
```markdown
### Sources
1. [描述](url)
2. [描述](url)
```
如果sources為空或缺失，則跳過此部分。

**6. 不確定值跳過**
跳過條件：
- 欄位值包含`[不確定]`字串
- 欄位名在`uncertain`陣列中
- 欄位值為None或空字串

### Step 4: 執行腳本
運行 `python {topic}/generate_report.py`

## 輸出
- `{topic}/generate_report.py` - 轉換腳本
- `{topic}/report.md` - 匯總報告
