# Deep Research Skill for Claude Code / OpenCode / Codex

[English](README.md) | [中文](README.zh.md) | [繁體中文](README.zh-TW.md)

> 如果覺得呢個專案有用，麻煩俾個 star 啦！:star:

> 靈感來源：[RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

適用於 Claude Code、OpenCode 同 Codex 嘅結構化調研工作流技能，支援兩階段調研：outline 生成（可擴展）同深度調查。人喺迴路設計確保每個階段嘅精確控制。

![Deep Research Skills 工作流](workflow.png)

## 使用場景

- **學術研究**：論文綜述、benchmark 評測、文獻分析
- **技術研究**：技術對比、框架評估、工具選型
- **市場研究**：競品分析、行業趨勢、產品比較
- **盡職調查**：公司研究、投資分析、風險評估

## 安裝

```bash
git clone https://github.com/Weizhena/deep-research-skills.git
cd deep-research-skills
```

### Claude Code
```bash
# 繁體中文版
cp -r skills/research-zh-TW/* ~/.claude/skills/

# 英文版
cp -r skills/research-en/* ~/.claude/skills/

# 英文版（簡體中文版）
cp -r skills/research-zh/* ~/.claude/skills/

# 必需：安裝 agent 同模組
cp agents/web-search-agent.md ~/.claude/agents/
cp -r agents/web-search-modules ~/.claude/agents/

# 必需：安裝 Python 依賴
pip install pyyaml
```

### OpenCode (預設: llama-local/Qwen-3.6-35B-A3B)
```bash
# Skills
mkdir -p ~/.config/opencode/skills
cp -r skills/research-zh-TW/* ~/.config/opencode/skills/   # 或 research-en 英文版

# 必需：為目前 shell 啟用 web search
export OPENCODE_ENABLE_EXA=1

# 可選：寫入 ~/.bashrc，永久生效
echo 'export OPENCODE_ENABLE_EXA=1' >> ~/.bashrc
source ~/.bashrc

# 必需：安裝 agent 同模組
cp agents/web-search-opencode.md ~/.config/opencode/agents/web-search.md
cp -r agents/web-search-modules ~/.config/opencode/agents/

# 必需：安裝 Python 依賴
pip install pyyaml
```

> **重要**：喺 OpenCode 入面，任何模型要想使用 `websearch`，需要設置 `OPENCODE_ENABLE_EXA=1`。單純 `export` 只對目前 shell 生效；寫入 `~/.bashrc` 後先係永久生效。唔設置時，只有 `web fetch`，對深度調研階段會弱好多。

### Codex
```bash
# 繁體中文版
mkdir -p ~/.codex/skills ~/.codex/agents
cp -r skills/research-codex-zh/* ~/.codex/skills/

# 英文版
mkdir -p ~/.codex/skills ~/.codex/agents
cp -r skills/research-codex-en/* ~/.codex/skills/

# 必需：安裝 web researcher agent 同模組
cp agents-codex/web-researcher.toml ~/.codex/agents/
cp -r agents-codex/web-search-modules ~/.codex/agents/

# 必需：安裝 Python 依賴
pip install pyyaml
```

使用以下兩種方式之一更新 `~/.codex/config.toml`：

**方式 A：自動腳本**

```bash
cd deep-research-skills
bash scripts/install-codex.sh
```

**方式 B：手動編輯**

```toml
suppress_unstable_features_warning = true

[features]
multi_agent = true
default_mode_request_user_input = true

[agents.web_researcher]
description = "Use this agent when you need to research information on the internet, particularly for debugging issues, finding solutions to technical problems, or gathering comprehensive information from multiple sources. This agent excels at finding relevant discussions. Use when you need creative search strategies, thorough investigation, or compilation of findings from multiple sources."
config_file = "agents/web-researcher.toml"
```

## 命令

> **Claude Code 2.1.0+**：而家支援直接 `/skill-name` 觸發！
>
> **舊版本**：請使用 `run /skill-name` 格式。
>
> **Codex**：可以透過 `/skills` -> `List Skills` 選擇這些 skills，也可以用自然語言觸發，例如 `Use the research skill to build an outline for AI Agent Demo 2025`。

| 命令 (2.1.0+) | 描述 |
|---------------|------|
| `/research` | 生成包含 items 同 fields 嘅調研 outline |
| `/research-add-items` | 向現有 outline 添加更多調研對象 |
| `/research-add-fields` | 向現有 outline 添加更多欄位定義 |
| `/research-deep` | 使用並行 agents 對每個 item 進行深度調研 |
| `/research-report` | 從 JSON 結果生成 markdown 報告 |

## 工作流 & 示例

> **示例**：調研 "AI Agent Demo 2025"

### 階段 1：生成 Outline
```
/research AI Agent Demo 2025
```
💡 **會發生咩**：話佢你知道你要研究咩 → 佢幫你列出調研清單

對於 Codex，可以咁講：
```
Use the research skill to build an outline for AI Agent Demo 2025
```

**你會得到**：17 個待調研嘅 AI Agent 清單（ChatGPT Agent、Claude Computer Use、Cursor 等）+ 每個要收集邊啲資訊

### （可選）唔滿意？繼續添加
```
/research-add-items
/research-add-fields
```
💡 **會發生咩**：補充更多調研對象或欄位定義

### 階段 2：深度調研
```
/research-deep
```
💡 **會發生咩**：AI 自動上網搜索每個 item 嘅詳細資料，逐一完成

**你會得到**：每個 Agent 嘅詳細資料（公司、發佈日期、定價、技術規格、用戶評價...）

### 階段 3：生成報告
```
/research-report
```
💡 **會發生咩**：所有數據 → 一份整理好嘅報告

**你會得到**：`report.md` - 帶目錄嘅完整 Markdown 報告，可直接閱讀或分享

## 遇到問題？

如果過程中有咩唔明，可以俾 Claude Code、OpenCode 或者 Codex 幫你理解呢個專案：
```
幫我理解呢個專案: https://github.com/Weizhena/deep-research-skills
```

## 參考文獻

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## 許可證

MIT
