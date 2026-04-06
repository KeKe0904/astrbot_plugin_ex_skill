# astrbot_plugin_ex_skill - ASTRBOT 插件

> 把前任蒸馏成 AI Skill，用ta的方式跟你说话。

## 功能特性

- **多数据源支持**：微信聊天记录、QQ消息、朋友圈截图、照片、口述记忆
- **智能性格分析**：基于 MBTI、星座、依恋类型等标签构建真实的人物性格
- **关系记忆提取**：自动分析共同经历、约会地点、inside jokes 等
- **进化机制**：支持追加记忆、对话纠正、版本管理
- **温柔的管理命令**：包括删除和放下前任的选项
- **启动自检功能**：全面检查运行环境、配置和目录结构
- **自动备份**：在删除前任 Skill 前自动备份
- **平台兼容性**：支持多种消息平台，包括 satori
- **详细的日志记录**：便于排查问题和调试

## 安装方法

1. 将 `astrbot_plugin_ex_skill` 目录复制到 AstrBot 的 `data/plugins/` 目录
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 在 AstrBot WebUI 中启用插件

## 使用方法

### 创建前任 Skill
```
/create-ex
```
按照提示输入：
1. 前任的代号（用于调用，如 'first-love'）
2. 基本信息（如：在一起三年，大学时期）
3. 性格画像（如：ENFP，双子座，话痨）
4. 数据源（可选择：微信聊天记录、QQ消息、照片等）

所有字段均可跳过，仅凭描述也能生成。

### 管理命令

| 命令 | 说明 |
|------|------|
| `/list-exes` | 列出所有前任 Skill |
| `/delete-ex {slug}` | 删除指定的前任 Skill |
| `/let-go {slug}` | 放下前任（删除的温柔别名） |

## 技术架构

### 项目结构
```
astrbot_plugin_ex_skill/
├── main.py                # 插件主文件
├── metadata.yaml          # 插件元数据
├── _conf_schema.json      # 插件配置
├── requirements.txt       # 依赖文件
├── README.md              # 自述文件
├── logo.png               # 插件图标
├── prompts/               # Prompt 模板
├── tools/                 # 工具脚本
└── exes/                  # 生成的前任 Skill（自动创建）
```

### 核心模块

- **prompts/**：包含各种 Prompt 模板，用于信息录入、记忆分析、性格分析等
- **tools/**：包含数据解析工具，支持微信聊天记录、QQ 消息、照片等数据源
- **exes/**：存储生成的前任 Skill

### 运行逻辑
1. 收到消息 → Persona 判断ta会怎么回 → Memory 补充共同记忆 → 用ta的方式输出
2. 支持增量学习，可随时追加记忆和纠正对话

## 配置选项

在 AstrBot WebUI 中可以配置以下选项：
- **exes_dir**：前任 Skill 存储目录
- **prompts_dir**：Prompt 模板目录
- **tools_dir**：工具脚本目录
- **max_exes**：最大前任 Skill 数量

## 注意事项

- ⚠️ 本插件仅用于个人回忆与情感疗愈，不用于骚扰、跟踪或侵犯他人隐私
- 聊天记录质量决定还原度：微信导出 + 口述 > 仅口述
- 建议优先提供：深夜对话 > 争吵记录 > 日常消息（最能体现真实性格）
- 如果你发现自己过于沉浸，请寻求专业帮助
- 你的前任是一个真实的人，ta有自己的人生。这个 Skill 只是你记忆中的ta

## 推荐的聊天记录导出工具

以下工具为独立的开源项目，本项目不包含它们的代码，仅在解析器中适配了它们的导出格式：

- **WeChatMsg** — 微信聊天记录导出（Windows）
- **PyWxDump** — 微信数据库解密导出（Windows）
- **留痕** — 微信聊天记录导出（macOS）

## 平台支持

### 支持的平台
- telegram
- discord
- aiocqhttp (QQ 个人号)
- qq_official (QQ 官方机器人)
- wecom (企业微信)
- lark (飞书)
- dingtalk (钉钉)
- slack
- kook
- vocechat
- satori
- misskey
- line

## 许可证

本插件基于 GNU Affero General Public License v3.0 开源。

## 引用与致谢

- **插件模板**：基于 [AstrBot 插件模板](https://github.com/Soulter/helloworld)
- **原项目地址**：[ex-skill](https://github.com/therealXiaomanChu/ex-skill)
- **架构灵感**：来源于 [同事.skill](https://github.com/titanwings/colleague-skill)，致敬原作者的创意和开源精神。

## 更新记录

请查看 [CHANGELOG.md](CHANGELOG.md) 文件了解插件的更新历史。
