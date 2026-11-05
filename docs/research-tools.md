# 科研工具调查与借鉴范围

记录日期：2026-11-05。此前调查主要在 2026-11-04 进行。范围为仓库说明、部分 SKILL.md、许可证和相关公开文档的初步检查，未完成完整依赖审计、运行测试或安全认证。

| 项目 | 初步核查用途 | 本讨论可借鉴内容 | 仓库许可证记录 |
| --- | --- | --- | --- |
| [ai-skill-scholar](https://github.com/dsebastien/ai-skill-scholar) | OpenAlex 检索、引用追踪、分阶段筛选 | 检索与筛选分离，保留排除理由 | MIT |
| [research-agent-skills](https://github.com/KalarisLabs/research-agent-skills) | 查找、假设、批判、引用核验等技能 | 观察、假设、竞争解释、区分性实验与证据边界 | MIT，含第三方声明 |
| [PaperQA](https://github.com/Future-House/paper-qa) | 科学文档检索问答与引用 | 回到全文定位支持材料 | Apache-2.0 |
| [Ai2 Scholar QA](https://github.com/allenai/ai2-scholarqa-lib) | 片段检索、重排、多文档综合 | 逐项主张关联证据；检查 API 与模型配置 | Apache-2.0 |
| [Orchestra AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 构思、训练、评测、推理工程等 | 检查实验实现路径与研究工件结构 | MIT |
| [AI-Scientist-v3](https://github.com/SakanaAI/AI-Scientist-v3) | 编码 Agent 实验、消融、评测及论文流程 | Baseline、独立最终评测与记录方式 | Apache-2.0 |
| [open-instruct](https://github.com/allenai/open-instruct) | SFT、DPO、RLVR 基础设施 | 后训练实验的实现与复现入口 | Apache-2.0，模型／数据另查 |
| [awesome-academic-research-skills](https://github.com/Jason-Mar1/awesome-academic-research-skills) | 科研技能索引 | 发现候选工具，回到上游核验 | CC0-1.0，条目不继承索引许可 |

## 实际借鉴的结构

[hypothesis-generation](https://github.com/KalarisLabs/research-agent-skills/blob/main/skills/hypothesis-generation/SKILL.md) 的启发是把观察与机制故事分离，先写竞争解释，再设计具有不同预测的检验，并保留检索边界。这里只提炼方法，不复制或执行其脚本。

研究工件可记录主张、证据、实验、配置、失败和转向。编排结构、多个 AI 的一致意见及自动生成报告都不能独立证明科学结论。

## 待集成时再核查的事项

- 固定使用版本或提交；核查实际功能、维护情况、依赖、权限、数据去向、预算及各材料许可。
- AI-Scientist-v3 说明编码 Agent 使用完整工具权限；运行前需审查隔离、凭据和费用。
- ai-skill-scholar 中 API 访问描述需与 [OpenAlex 官方认证说明](https://help.openalex.org/api/authentication/) 交叉核对：基础查询与规模化、游标翻页的访问条件不同。
- 根许可证不能代替模型权重、数据、第三方代码与外部服务条款。
- 本仓库目前未安装这些技能，没有持续 API 接入；“已查看文档”不等于“已验证有效”。
