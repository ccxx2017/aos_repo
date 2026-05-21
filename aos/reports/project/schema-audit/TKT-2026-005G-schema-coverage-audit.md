# TKT-2026-005G · strategy_researcher schema 覆盖审计

- 审计对象: `aos/org/skills/strategy_researcher/`
- schema 权威源: `data/knowledge/schema.md`
- 审计范围: `SKILL.md`、`TOOLS.md`、`prompts/`，以及与其直接相关的后端落地链路
- 审计方式: 仅做静态审计；不执行 builder/backtest；不产生新的研究运行数据
- 结论口径:
  - `已由后端保证`: 规则已由当前后端/知识库实现直接落实，skill 无需机械复写
  - `已被 skill 显式吸收`: 规则已进入 `strategy_researcher` 的运行时手册或报告约束
  - `仅被引用未吸收`: 文档提到了 `schema.md` 或相关概念，但没有形成可执行约束
  - `尚未覆盖`: 当前技能资产源和后端主链路都没有把该规则落实到 strategy_researcher 的现实工作流

## 1. 执行摘要

本次审计结论是：`strategy_researcher` 对 `schema.md` 的覆盖呈现明显的“三层分化”。

1. 已经进入运行时约束的，主要是研究流程本身必须使用的规则:
   `先读 KB 再研究`、`只读 KB`、`run_id / strategy_id 可追溯`、
   `样本内外对比`、`never_triggered_transitions`、报告数值 `4 位小数`。
2. 已经由后端承担的，主要是 KB 归档的机械性动作:
   `create_strategy_archive()`、`append_backtest_result()`、`update_index()`、
   `### Run {run_id}` 块格式、回测区块追加写入、指标格式化为 `4 位小数`。
3. 仍然存在空档的，主要是“研究发现如何回流到 KB 结构化资产”的规则:
   `strategy_created` 日志、`关联策略更新` 触发、`市场认知文档触发时机`、
   `字段完整性自检`、`Notes / 净值穿零解释`、以及当前主链路下真正可执行的样本内外写回。

最关键的判断是：

- 不应把 `schema.md` 的 KB 文档结构、字段字典、Lint 清单全文复制到 skill 文件中。
- 但当前 skill 仍然缺少一层“最小运行时桥接”:
  需要把会影响研究判断和报告升级的少数规则显式吸收进运行时手册，
  例如 `字段完整性异常要报`、`发现新关联策略/市场认知候选时要升级为后续工单建议`。

## 2. 不应复制进入 Skill 的规则

以下规则不建议机械复制进 `SKILL.md` / `TOOLS.md` / `prompts/`，保留交叉引用更合适：

| 规则簇 | 判断 | 理由 |
|:---|:---|:---|
| KB 目录结构、档案 front matter 字段字典、市场认知文档模板 | 只保留引用 | `strategy_researcher` 当前是 **KB 只读**；这些属于 `schema.md` 的数据契约，不应在 skill 侧形成第二份权威描述 |
| `create_strategy_archive()` / `append_backtest_result()` / `update_index()` 的精确写法 | 只保留引用 | 这些属于后端副作用或知识库实现细节，重复到 skill 文档会导致漂移 |
| Lint 清单中的纯机械格式项 | 只保留引用，必要时只保留“检查入口” | 例如字段顺序、标题格式、市场认知字段齐全性，本质是 schema/后端测试应守护的内容 |
| 市场认知文档的完整结构与 confidence 分级表 | 只保留引用 | 运行时只需要知道“何时提请升级为 market insight”，不需要在 skill 侧再复制一份模板 |

相反，以下内容应该保留在运行时手册中：

- 任何会影响研究员判断路径的规则:
  `读 KB 的先后顺序`、`比较基线的方法`、`样本内外对比`、`never_triggered_transitions`、`可追溯性`
- 任何需要研究员在报告中主动暴露的规则:
  `字段完整性异常`、`关联策略候选`、`market insight 候选`、`后端写回异常`

## 3. 覆盖矩阵

### 3.1 KB 读写边界

| ID | 规则提取 | 状态 | 证据路径 | 判断与建议落点 |
|:---|:---|:---|:---|:---|
| KB-01 | 新策略设计前先读 `index.md` + 相关策略档案，避免重复设计 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/research_workflow.md` | Phase 2 已明确 `archives -> archive -> log -> index` 的读取顺序 |
| KB-02 | 回测分析 / 策略改进时，阅读历史回测记录和同 Intent 档案形成基线 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/research_workflow.md` | 已进入主流程，属于运行时必需约束 |
| KB-03 | 市场认知相关研究时，应读取相关 `market_insights/` 文档 | 仅被引用未吸收 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/hypothesis_heuristics.md`、`aos/org/skills/strategy_researcher/prompts/README.md` | skill 知道 insight 存在，但没有稳定的读取流程或 API 支撑；建议落在 `research_workflow.md`，写成“通过档案引用反查 insight” 的固定步骤 |
| KB-04 | 新策略生成后应创建策略档案 | 已由后端保证 | `backend/app/api/endpoints/strategy_builder.py`、`quant_intelligence/strategy_builder/knowledge_base.py` | `compile-ir` 成功后调用 `create_strategy_archive()` |
| KB-05 | 回测完成后应追加回测结果到档案 | 已由后端保证 | `backend/app/api/endpoints/backtests/start.py`、`quant_intelligence/strategy_builder/knowledge_base.py`、`backend/tests/api/endpoints/test_backtests_refactored.py` | 当前 `execution-config` 主链路已自动 `append_backtest_result()` |
| KB-06 | 研究发现应写入 `market_insights/` | 尚未覆盖 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/README.md` | 当前 skill 明确只读 KB，后端也没有对应写入链路；建议不在 skill 中复制文档模板，但要在 `research_workflow.md` / `report_template.md` 增加“触发后续工单”出口 |
| KB-07 | 发现策略关系时应更新 `## 关联策略` | 尚未覆盖 | `data/knowledge/schema.md`、`quant_intelligence/strategy_builder/knowledge_base.py`、`aos/org/skills/strategy_researcher/prompts/research_workflow.md` | skill 会读 `## 关联策略`，但不会在运行时输出“新的关联策略候选”；建议落在 `report_template.md` 与 `research_workflow.md` |
| KB-08 | skill 不得直接写 KB，由后端副作用完成写入 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/SKILL.md`、`aos/org/skills/strategy_researcher/prompts/README.md` | 这是当前 source of truth 的核心边界，吸收状态清晰 |

### 3.2 策略档案字段与结构

| ID | 规则提取 | 状态 | 证据路径 | 判断与建议落点 |
|:---|:---|:---|:---|:---|
| ARC-01 | 策略档案应包含 `Intent`、`Created`、`IR Summary`、`Universe` 及 `假设/回测记录/分析/关联策略` 基本结构 | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`quant_intelligence/tests/test_knowledge_base.py` | `create_strategy_archive()` 会生成基础骨架 |
| ARC-02 | `Universe` 字段应来自真实标的范围，而不是占位值 | 尚未覆盖 | `data/knowledge/schema.md`、`backend/app/api/endpoints/strategy_builder.py`、`aos/org/skills/strategy_researcher/prompts/research_workflow.md` | `compile-ir` 主链路默认把 `Universe` 写成 `compile_ir`；研究员主流程也未在 compile 阶段传 metadata universe。建议落在后端 `compile-ir` / 或增加后置校验提示 |
| ARC-03 | 创建策略档案后应记录 `strategy_created` 研究日志 | 尚未覆盖 | `data/knowledge/schema.md`、`backend/app/api/endpoints/strategy_builder.py`、`quant_intelligence/strategy_builder/graph.py` | 旧 graph 路径会 `log_research_event("strategy_created")`，当前 `compile-ir` 路径不会；建议后端补齐 |
| ARC-04 | 创建或更新档案后应调用 `update_index()` | 已由后端保证 | `backend/app/api/endpoints/strategy_builder.py`、`backend/app/api/endpoints/backtests/start.py`、`quant_intelligence/strategy_builder/knowledge_base.py` | create / append 两条主链路都已调用 `update_index()` |
| ARC-05 | 字段完整性应有自检，不得缺失必填项 | 尚未覆盖 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/README.md`、`aos/org/skills/strategy_researcher/prompts/research_workflow.md` | skill 只引用 schema，但没有把“发现缺字段要显式报出”写成运行时检查；建议落在 `research_workflow.md`，只做 sanity check，不复制完整 schema |

### 3.3 回测结果追加规则

| ID | 规则提取 | 状态 | 证据路径 | 判断与建议落点 |
|:---|:---|:---|:---|:---|
| BT-01 | 回测区块应追加 `Period / Universe / Train Split / 样本内外标记 / Overall Metrics / Wall Clock / Phase Stats / IR 规则` | 已由后端保证 | `backend/app/api/endpoints/backtests/start.py`、`quant_intelligence/strategy_builder/knowledge_base.py`、`backend/tests/manual/validate_tkt_2026_005e.py` | 当前 `execution-config` 主链路会自动追加这些内容 |
| BT-02 | 回测记录采用 `### Run {run_id}` 标题格式，并能回溯到具体 run | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`quant_intelligence/tests/test_knowledge_base.py` | run block 标题格式固定，且测试覆盖 |
| BT-03 | 回测记录只能追加，不能删除历史 run | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`quant_intelligence/tests/test_knowledge_base.py` | `_upsert_run_entry()` 保留既有 run；同一 `run_id` 只做幂等替换 |
| BT-04 | 指标数值保留 `4 位小数` | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`quant_intelligence/tests/test_knowledge_base.py`、`aos/org/skills/strategy_researcher/prompts/report_template.md` | KB 归档由后端格式化；报告侧也有显式约束 |
| BT-05 | 如有 split 回测，应同时记录样本内外年化收益、总收益和对应区间天数 | 尚未覆盖 | `data/knowledge/schema.md`、`quant_intelligence/strategy_builder/backtest_api.py`、`backend/app/api/endpoints/strategy_builder.py`、`backend/app/api/endpoints/backtests/start.py` | `backtest_api._run_split_backtest()` 支持，但当前 `strategy_researcher` 主链路 `call_backtest.py -> /backtests/execution-config` 没有 `train_split` 接口；skill 文档要求比较样本内外，但现实调用路径未接通 |
| BT-06 | 净值穿零时，风险调整指标应记为 `N/A`，并在 `Notes` 说明原因 | 尚未覆盖 | `data/knowledge/schema.md`、`quant_intelligence/strategy_builder/knowledge_base.py` | 当前归档没有 `Notes` 渲染，也没有显式“穿零 -> Notes”规则落地；建议后端补充 |
| BT-07 | `never_triggered_transitions` 非空时，应在分析中说明 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/research_workflow.md`、`aos/org/skills/strategy_researcher/prompts/hypothesis_heuristics.md`、`aos/org/skills/strategy_researcher/prompts/report_template.md` | 该规则已进入 round analysis 与报告叙述，不必复制成 KB 模板细节 |
| BT-08 | Period 日期应与回测参数一致 | 已由后端保证 | `backend/app/api/endpoints/backtests/start.py`、`quant_intelligence/strategy_builder/backtest_api.py`、`quant_intelligence/strategy_builder/knowledge_base.py` | `start_date/end_date` 直接来自请求参数并写入 `BacktestResult` 与 KB 区块 |

### 3.4 分析 / 关联策略更新规则

| ID | 规则提取 | 状态 | 证据路径 | 判断与建议落点 |
|:---|:---|:---|:---|:---|
| ANA-01 | 分析应优先写观察与归因，不重复原始数据 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/report_template.md` | 模板已写明 `分析 > 陈述` |
| ANA-02 | 分析应引用 `run_id` / `strategy_id` / insight topic，保证可追溯 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/README.md`、`aos/org/skills/strategy_researcher/prompts/report_template.md`、`aos/org/skills/strategy_researcher/TOOLS.md` | 高风险项之一，当前已进入运行时手册 |
| ANA-03 | 分析应明确样本内外差异，识别过拟合 | 已被 skill 显式吸收 | `aos/org/skills/strategy_researcher/prompts/research_workflow.md`、`aos/org/skills/strategy_researcher/prompts/report_template.md` | 文档已要求比较 `train_metrics/test_metrics`，但底层调用链尚未贯通，故这里是“手册已吸收、实现仍有缺口” |
| ANA-04 | 发现显著变化、冲突/印证、历史规律时，应更新档案 `## 分析` 章节 | 尚未覆盖 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/research_workflow.md` | 当前 skill 只负责研究报告，不负责把这些触发点升级为 KB 更新动作或 follow-up 提示；建议落在 `report_template.md` 的“后续动作”部分 |
| ANA-05 | 发现同 Intent / 互补 / 变体关系时，应更新 `## 关联策略` 章节 | 尚未覆盖 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/research_workflow.md` | 当前仅读取旧关联，不输出新关联候选；建议落在 `report_template.md` |
| ANA-06 | 发现可复用市场规律、多策略共性失效模式时，应触发 `market_insights/` 更新 | 尚未覆盖 | `data/knowledge/schema.md`、`aos/org/skills/strategy_researcher/prompts/hypothesis_heuristics.md` | 高风险项之一；建议不要复制 insight 模板，但要把“何时升级成 insight 工单”写进运行时手册 |

### 3.5 Lint / 格式规范

| ID | 规则提取 | 状态 | 证据路径 | 判断与建议落点 |
|:---|:---|:---|:---|:---|
| LINT-01 | 必填字段 `Intent / Created / IR Summary / Universe` 不缺失 | 尚未覆盖 | `data/knowledge/schema.md`、`backend/app/api/endpoints/strategy_builder.py`、`quant_intelligence/strategy_builder/knowledge_base.py` | 后端会写字段名，但当前主链路下 `Universe=compile_ir` 暴露出“字段存在但语义不完整”；建议先做后端/运行时 sanity check，而不是复制字段表 |
| LINT-02 | 指标数值统一为 `4 位小数` | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`aos/org/skills/strategy_researcher/prompts/report_template.md`、`aos/org/skills/strategy_researcher/TOOLS.md` | KB 写入由后端保证；报告与 `metrics.py` 也有同口径要求 |
| LINT-03 | 不删除已有回测记录，只追加 | 已由后端保证 | `quant_intelligence/strategy_builder/knowledge_base.py`、`quant_intelligence/tests/test_knowledge_base.py` | 归档层已经实现，不需要复制到 skill 文件 |
| LINT-04 | 市场认知文档必须包含 `置信度` 和 `证据` | 尚未覆盖 | `data/knowledge/schema.md` | 当前 `strategy_researcher` 无 market insight 写回能力，也没有对应工单升级提示；建议保持 schema 为模板权威源，同时补一个“候选 insight” 触发规则 |
| LINT-05 | 更新策略档案后调用 `update_index()` | 已由后端保证 | `backend/app/api/endpoints/strategy_builder.py`、`backend/app/api/endpoints/backtests/start.py`、`backend/tests/api/endpoints/test_backtests_refactored.py` | 主链路已覆盖 |

## 4. 高风险项专项排查

| 高风险项 | 结论 | 说明 |
|:---|:---|:---|
| `4 位小数` | 已覆盖 | KB 归档由后端格式化；报告模板和 `metrics.py` 也同步要求 |
| `run_id / strategy_id 可追溯` | 已覆盖 | prompts 与 TOOLS 都把可追溯性写成硬约束 |
| `never_triggered_transitions` | 已覆盖 | research workflow / heuristics / report template 都已显式吸收 |
| `样本内外对比` | 部分覆盖 | 运行时手册显式要求比较，但当前 `execution-config` 主链路没有把 `train_split` 接入 |
| `关联策略更新` | 未覆盖 | 只读旧关联，未输出新关联候选或升级动作 |
| `市场认知文档触发时机` | 未覆盖 | 只知道可引用 insight，不知道何时把新发现升级成 insight 资产 |
| `只追加不删除` | 已覆盖 | KB 归档层已实现并有测试 |
| `字段完整性自检` | 未覆盖 | 只引用 schema，没有运行时 sanity check；且 `Universe=compile_ir` 暴露了真实缺口 |

## 5. Gap List

### P0

1. `样本内外对比` 在运行时手册中已是硬要求，但当前主链路
   `scripts/call_backtest.py -> /api/v1/backtests/execution-config`
   不支持 `train_split`，导致 `train_metrics/test_metrics` 在 strategy_researcher 正式路径下不可达。
   - 建议落点: 后端 `backend/app/api/endpoints/backtests/start.py` + `aos/org/skills/strategy_researcher/scripts/call_backtest.py`
2. `字段完整性自检` 没有进入 strategy_researcher 的运行时手册，
   且当前 `compile-ir` 创建的档案前置 `Universe` 对主流程会退化为 `compile_ir` 占位值。
   - 建议落点: 后端 `compile-ir` 路径或 `research_workflow.md` 的最小 sanity check

### P1

1. 当前 `compile-ir` 主链路不会追加 `strategy_created` 日志，
   与 `schema.md` 的“创建档案 -> 记日志 -> 更新索引”链路不一致。
   - 建议落点: `backend/app/api/endpoints/strategy_builder.py`
2. `关联策略更新` 触发规则未进入运行时手册。
   - 建议落点: `aos/org/skills/strategy_researcher/prompts/report_template.md`
3. `市场认知文档触发时机` 未进入运行时手册。
   - 建议落点: `aos/org/skills/strategy_researcher/prompts/research_workflow.md`
4. `Notes / 净值穿零解释` 未进入当前 KB 归档块。
   - 建议落点: `quant_intelligence/strategy_builder/knowledge_base.py`

### P2

1. 缺少一条面向 source-of-truth 的自动化审计测试，
   用来持续检查 `compile-ir` / `execution-config` 与 `schema.md` 的关键契约是否漂移。
   - 建议落点: `backend/tests/api/endpoints/` 或 `quant_intelligence/tests/`
2. insight 读取链路仍依赖档案中的间接引用，没有稳定的只读查询入口。
   - 建议落点: 后端 knowledge API 扩展，或在 skill 中把“反查方式”文档化

## 6. 后续工单建议

建议拆成小工单，不要打成一张“大而全修复”：

1. `execution-config` 增加 `train_split` 透传，并让 `call_backtest.py` 支持 split 回测。
2. `compile-ir` 成功后补 `log_research_event("strategy_created")`。
3. 为 `strategy_researcher` 增加最小 KB sanity check:
   只检查 `Intent / Created / IR Summary / Universe` 是否语义完整，
   以及回测后档案是否存在对应 `run_id` 区块。
4. 在 `report_template.md` 新增“关联策略候选 / market insight 候选”小节，
   只输出候选和理由，不复制 schema 模板。
5. 在 `knowledge_base.py` 的回测归档块中补 `Notes` 渲染与“净值穿零说明”。
6. 增加一条 source-of-truth 契约测试，
   固定检查 `### Run {run_id}`、`update_index()`、`4 位小数`、`append-only`、`strategy_created` 日志。

## 7. 最终结论

`aos/org/skills/strategy_researcher/` 已经把“研究如何进行”这部分规则吸收得比较完整，
也明确与 `schema.md` 划清了“谁负责 KB 结构、谁负责运行时判断”的边界。

但当前还缺少一层把 `schema.md` 中高价值规则桥接到运行时的最小约束层。
如果不补，这个 skill 后续继续迭代 `SKILL.md` / `TOOLS.md` / `prompts/` 时，
仍然会出现两类风险：

- 研究员知道要分析什么，但不知道何时应把发现升级为 `关联策略` / `market insight` 资产；
- 文档里要求检查的内容，在当前主链路下并不总是可达或可验证，
  典型就是 `train_split` 和档案字段完整性。

因此，本工单之后最优动作不是“复制更多 schema 内容到 skill 文件”，
而是补三类小而准的桥接补丁：
`主链路可达性`、`最小 sanity check`、`候选升级出口`。
