from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os
import json
import shutil
from pathlib import Path
import platform
import time
import re

@register("astrbot_plugin_ex_skill", "落梦陳", "把前任蒸馏成 AI Skill，用ta的方式跟你说话", "1.0.6")
class ExSkillPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.context = context
        self.plugin_dir = Path(__file__).parent
        self.config = self._load_config()
        self.platform = platform.system()
        self.exes_dir = self.plugin_dir / self.config.get("exes_dir", "exes")
        self.prompts_dir = self.plugin_dir / self.config.get("prompts_dir", "prompts")
        self.tools_dir = self.plugin_dir / self.config.get("tools_dir", "tools")
        self.max_exes = self.config.get("max_exes", 10)
        self.enable_logging = self.config.get("enable_logging", False)
        self.auto_backup = self.config.get("auto_backup", True)
        self._ensure_directories()
        # 对话状态管理
        self.conversation_states = {}
        # 数据收集存储
        self.collected_data = {}

    def _load_config(self):
        """加载插件配置"""
        config_file = self.plugin_dir / "_conf_schema.json"
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    config = {}
                    for key, value in schema.items():
                        config[key] = value.get("default", "")
                    # 确保配置值类型正确
                    if "max_exes" in config:
                        try:
                            config["max_exes"] = int(config["max_exes"])
                        except ValueError:
                            config["max_exes"] = 10
                    if "enable_logging" in config:
                        config["enable_logging"] = bool(config["enable_logging"])
                    if "auto_backup" in config:
                        config["auto_backup"] = bool(config["auto_backup"])
                    return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
        # 默认配置
        return {
            "exes_dir": "exes",
            "prompts_dir": "prompts",
            "tools_dir": "tools",
            "max_exes": 10,
            "enable_logging": False,
            "auto_backup": True
        }

    def _ensure_directories(self):
        """确保必要的目录存在"""
        try:
            self.exes_dir.mkdir(exist_ok=True)
            self.prompts_dir.mkdir(exist_ok=True)
            self.tools_dir.mkdir(exist_ok=True)
        except Exception as e:
            logger.error(f"创建目录失败: {e}")

    async def initialize(self):
        """插件初始化方法"""
        logger.info("ExSkill 插件初始化开始")
        
        # 1. 检查运行平台
        logger.info(f"运行平台: {self.platform}")
        
        # 2. 检查插件配置
        logger.info(f"插件配置:")
        logger.info(f"  - exes_dir: {self.exes_dir}")
        logger.info(f"  - prompts_dir: {self.prompts_dir}")
        logger.info(f"  - tools_dir: {self.tools_dir}")
        logger.info(f"  - max_exes: {self.max_exes}")
        logger.info(f"  - enable_logging: {self.enable_logging}")
        logger.info(f"  - auto_backup: {self.auto_backup}")
        
        # 3. 检查目录结构
        logger.info("检查目录结构:")
        self._check_directories()
        
        # 4. 检查当前前任 Skill 列表
        self._check_exes_list()
        
        # 5. 检查文件权限
        self._check_file_permissions()
        
        # 6. 检查依赖项
        self._check_dependencies()
        
        # 7. 检查平台支持
        self._check_platform_support()
        
        logger.info("ExSkill 插件初始化完成")
        logger.info("插件已准备就绪，可以开始使用")
    
    def _check_directories(self):
        """检查目录结构"""
        directories = [
            ("exes_dir", self.exes_dir),
            ("prompts_dir", self.prompts_dir),
            ("tools_dir", self.tools_dir),
            ("backups_dir", self.plugin_dir / "backups")
        ]
        
        for name, path in directories:
            try:
                if path.exists():
                    if path.is_dir():
                        logger.info(f"  ✅ {name}: {path} (目录存在)")
                    else:
                        logger.warning(f"  ⚠️ {name}: {path} (存在但不是目录)")
                else:
                    path.mkdir(exist_ok=True, parents=True)
                    logger.info(f"  ✅ {name}: {path} (已创建)")
            except Exception as e:
                logger.error(f"  ❌ {name}: {path} (创建失败: {e})")
    
    def _check_exes_list(self):
        """检查当前前任 Skill 列表"""
        try:
            exes = []
            for item in self.exes_dir.iterdir():
                if item.is_dir():
                    exes.append(item.name)
            
            if exes:
                logger.info(f"  ✅ 已找到 {len(exes)} 个前任 Skill:")
                for ex in exes[:5]:  # 只显示前5个
                    logger.info(f"    - {ex}")
                if len(exes) > 5:
                    logger.info(f"    ... 等 {len(exes) - 5} 个更多")
            else:
                logger.info("  ✅ 还没有创建任何前任 Skill")
        except Exception as e:
            logger.error(f"  ❌ 检查前任 Skill 列表失败: {e}")
    
    def _check_file_permissions(self):
        """检查文件权限"""
        try:
            # 测试写入权限
            test_file = self.plugin_dir / ".test_permission"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("  ✅ 文件权限: 写入权限正常")
        except Exception as e:
            logger.error(f"  ❌ 文件权限: 写入权限失败: {e}")
    
    def _check_dependencies(self):
        """检查依赖项"""
        try:
            import yaml
            import json
            import shutil
            logger.info("  ✅ 依赖项: 核心模块已安装")
        except ImportError as e:
            logger.error(f"  ❌ 依赖项: 缺少核心模块: {e}")
    
    def _check_platform_support(self):
        """检查平台支持"""
        try:
            # 读取 metadata.yaml 中的支持平台
            import yaml
            metadata_file = self.plugin_dir / "metadata.yaml"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = yaml.safe_load(f)
                    if 'support_platforms' in metadata:
                        platforms = metadata['support_platforms']
                        logger.info(f"  ✅ 支持平台 ({len(platforms)}):")
                        for platform in platforms:
                            logger.info(f"    - {platform}")
                    else:
                        logger.warning("  ⚠️ 未在 metadata.yaml 中定义支持平台")
            else:
                logger.warning("  ⚠️ metadata.yaml 文件不存在")
        except Exception as e:
            logger.error(f"  ❌ 检查平台支持失败: {e}")

    @filter.command("create-ex")
    async def create_ex(self, event: AstrMessageEvent):
        """创建前任 Skill"""
        try:
            user_id = event.get_sender_id()
            user_name = event.get_sender_name()
            
            # 检查是否达到最大数量限制
            ex_count = len([d for d in self.exes_dir.iterdir() if d.is_dir()])
            if ex_count >= self.max_exes:
                yield event.plain_result(f"已达到最大前任 Skill 数量限制 ({self.max_exes})，请先删除一些再创建。")
                return
            
            # 初始化对话状态
            self.conversation_states[user_id] = {
                "step": 1,
                "data": {}
            }
            
            # 开始对话
            yield event.plain_result(f"{user_name} 开始创建前任 Skill。请按照提示输入信息：")
            yield event.plain_result("第一步：请输入前任的代号（用于调用，如 'first-love'）")
            yield event.plain_result("提示：如果要跳过此步骤，请输入 '跳过' 或直接发送空消息。")
        except Exception as e:
            logger.error(f"创建前任 Skill 失败: {e}")
            yield event.plain_result("创建前任 Skill 时发生错误，请稍后重试。")

    @filter.command("list-exes")
    async def list_exes(self, event: AstrMessageEvent):
        """列出所有前任 Skill"""
        try:
            exes = []
            for item in self.exes_dir.iterdir():
                if item.is_dir():
                    exes.append(item.name)
            if exes:
                yield event.plain_result("已创建的前任 Skill：")
                for ex in exes:
                    yield event.plain_result(f"- {ex}")
            else:
                yield event.plain_result("还没有创建任何前任 Skill，使用 /create-ex 开始创建。")
        except Exception as e:
            logger.error(f"列出前任 Skill 失败: {e}")
            yield event.plain_result("列出前任 Skill 时发生错误，请稍后重试。")

    @filter.command("delete-ex")
    async def delete_ex(self, event: AstrMessageEvent, slug: str):
        """删除前任 Skill"""
        try:
            if not slug:
                yield event.plain_result("请指定要删除的前任 Skill 代号，例如：/delete-ex first-love")
                return
            ex_dir = self.exes_dir / slug
            if ex_dir.exists():
                # 自动备份
                if self.auto_backup:
                    backup_dir = self.plugin_dir / "backups"
                    backup_dir.mkdir(exist_ok=True)
                    backup_path = backup_dir / f"{slug}_{int(os.time())}"
                    try:
                        shutil.copytree(ex_dir, backup_path)
                        if self.enable_logging:
                            logger.info(f"已备份前任 Skill 到: {backup_path}")
                    except Exception as backup_err:
                        logger.error(f"备份失败: {backup_err}")
                # 删除
                shutil.rmtree(ex_dir)
                yield event.plain_result(f"已删除前任 Skill: {slug}")
                if self.auto_backup:
                    yield event.plain_result("（已自动备份）")
            else:
                yield event.plain_result(f"未找到前任 Skill: {slug}")
        except Exception as e:
            logger.error(f"删除前任 Skill 失败: {e}")
            yield event.plain_result("删除前任 Skill 时发生错误，请稍后重试。")

    @filter.command("let-go")
    async def let_go(self, event: AstrMessageEvent, slug: str):
        """放下前任（删除的温柔别名）"""
        try:
            if not slug:
                yield event.plain_result("请指定要放下的前任 Skill 代号，例如：/let-go first-love")
                return
            await self.delete_ex(event, slug)
        except Exception as e:
            logger.error(f"放下前任失败: {e}")
            yield event.plain_result("放下前任时发生错误，请稍后重试。")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def handle_message(self, event: AstrMessageEvent):
        """处理用户消息，继续对话流程"""
        try:
            user_id = event.get_sender_id()
            message = event.message_str.strip()
            
            # 检查用户是否处于对话状态
            if user_id in self.conversation_states:
                state = self.conversation_states[user_id]
                step = state["step"]
                data = state["data"]
                
                # 处理用户输入
                if message.lower() == "跳过" or message == "":
                    # 跳过当前步骤
                    pass
                else:
                    # 存储用户输入
                    if step == 1:
                        data["slug"] = message
                    elif step == 2:
                        data["basic_info"] = message
                    elif step == 3:
                        data["personality"] = message
                    elif step == 4:
                        data["data_source"] = message
                
                # 推进对话步骤
                if step < 4:
                    # 进入下一步
                    state["step"] += 1
                    next_step = state["step"]
                    
                    if next_step == 2:
                        yield event.plain_result("第二步：请输入基本信息（如：在一起三年，大学时期）")
                        yield event.plain_result("提示：如果要跳过此步骤，请输入 '跳过' 或直接发送空消息。")
                    elif next_step == 3:
                        yield event.plain_result("第三步：请输入性格画像（如：ENFP，双子座，话痨）")
                        yield event.plain_result("提示：如果要跳过此步骤，请输入 '跳过' 或直接发送空消息。")
                    elif next_step == 4:
                        yield event.plain_result("第四步：请输入数据源（可选择：微信聊天记录、QQ消息、照片等）")
                        yield event.plain_result("提示：如果要跳过此步骤，请输入 '跳过' 或直接发送空消息。")
                else:
                    # 所有步骤完成，生成前任 Skill
                    yield event.plain_result("正在生成前任 Skill...")
                    
                    # 生成 Skill
                    success = await self._generate_skill(data)
                    
                    if success:
                        slug = data.get("slug", f"ex_{int(time.time())}")
                        # 清理 slug，确保它是有效的目录名
                        slug = re.sub(r'[^a-zA-Z0-9_-]', '_', slug)
                        yield event.plain_result(f"前任 Skill 创建成功！")
                        yield event.plain_result(f"你可以使用 /{slug} 命令与ta对话。")
                        yield event.plain_result(f"使用 /list-exes 查看所有已创建的前任 Skill。")
                    else:
                        yield event.plain_result("生成前任 Skill 时发生错误，请稍后重试。")
                    
                    # 清除对话状态
                    del self.conversation_states[user_id]
            else:
                # 检查是否是调用前任 Skill 的命令
                # 格式：/{slug} 消息内容
                # 或：/{slug}-memory 消息内容
                # 或：/{slug}-persona 消息内容
                message_parts = message.split(" ", 1)
                if len(message_parts) >= 1:
                    command = message_parts[0]
                    if command.startswith("/"):
                        # 提取 slug 和模式
                        command_parts = command[1:].split("-")
                        if len(command_parts) >= 1:
                            slug = command_parts[0]
                            mode = "full"
                            if len(command_parts) > 1:
                                mode = command_parts[1]
                            
                            # 检查 slug 是否存在
                            skill_dir = self.exes_dir / slug
                            if skill_dir.exists() and skill_dir.is_dir():
                                # 提取消息内容
                                content = ""
                                if len(message_parts) > 1:
                                    content = message_parts[1]
                                
                                # 调用前任 Skill
                                response = await self._call_ex_skill(slug, content, mode)
                                if response:
                                    yield event.plain_result(response)
                                else:
                                    yield event.plain_result("调用前任 Skill 时发生错误，请稍后重试。")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            # 清除对话状态
            if user_id in self.conversation_states:
                del self.conversation_states[user_id]
            yield event.plain_result("处理消息时发生错误，请重新开始创建。")

    async def _generate_skill(self, data):
        """生成前任 Skill"""
        try:
            # 获取数据
            slug = data.get("slug", f"ex_{int(time.time())}")
            # 清理 slug，确保它是有效的目录名
            slug = re.sub(r'[^a-zA-Z0-9_-]', '_', slug)
            basic_info = data.get("basic_info", "")
            personality = data.get("personality", "")
            data_source = data.get("data_source", "")
            
            # 创建 Skill 目录
            skill_dir = self.exes_dir / slug
            skill_dir.mkdir(exist_ok=True)
            
            # 创建 memory.md 文件
            memory_content = f"# 关系记忆\n\n"
            memory_content += f"## 基本信息\n{basic_info}\n\n"
            memory_content += f"## 共同经历\n基于提供的信息生成\n\n"
            memory_content += f"## 约会地点\n基于提供的信息生成\n\n"
            memory_content += f"## Inside Jokes\n基于提供的信息生成\n\n"
            memory_content += f"## 争吵模式\n基于提供的信息生成\n\n"
            memory_content += f"## 甜蜜瞬间\n基于提供的信息生成\n\n"
            memory_content += f"## 关系时间线\n基于提供的信息生成\n"
            
            (skill_dir / "memory.md").write_text(memory_content, encoding="utf-8")
            
            # 创建 persona.md 文件
            persona_content = f"# 人物性格\n\n"
            persona_content += f"## 硬规则\n- 以前任的身份和口吻说话\n- 保持真实的性格特点\n- 回忆共同经历\n\n"
            persona_content += f"## 身份\n前任\n\n"
            persona_content += f"## 说话风格\n基于提供的性格画像: {personality}\n\n"
            persona_content += f"## 情感模式\n基于提供的信息生成\n\n"
            persona_content += f"## 关系行为\n基于提供的信息生成\n"
            
            (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")
            
            # 创建版本目录
            versions_dir = skill_dir / "versions"
            versions_dir.mkdir(exist_ok=True)
            
            # 备份初始版本
            backup_dir = versions_dir / f"v1_{int(time.time())}"
            backup_dir.mkdir(exist_ok=True)
            shutil.copy2(skill_dir / "memory.md", backup_dir / "memory.md")
            shutil.copy2(skill_dir / "persona.md", backup_dir / "persona.md")
            
            logger.info(f"已生成前任 Skill: {slug}")
            return True
        except Exception as e:
            logger.error(f"生成前任 Skill 失败: {e}")
            return False

    async def _call_ex_skill(self, slug, content, mode):
        """调用前任 Skill"""
        try:
            skill_dir = self.exes_dir / slug
            
            # 读取 memory.md 和 persona.md 文件
            memory_file = skill_dir / "memory.md"
            persona_file = skill_dir / "persona.md"
            
            memory_content = ""
            persona_content = ""
            
            if memory_file.exists():
                memory_content = memory_file.read_text(encoding="utf-8")
            
            if persona_file.exists():
                persona_content = persona_file.read_text(encoding="utf-8")
            
            # 根据模式生成回复
            if mode == "memory":
                # 记忆模式：主要基于关系记忆回复
                response = f"【记忆模式】\n"
                response += f"根据我们的共同记忆：\n"
                response += f"{memory_content[:500]}...\n"
                response += f"\n关于你说的：{content}\n"
                response += "我记得我们曾经一起经历过很多美好的时光..."
            elif mode == "persona":
                # 性格模式：主要基于人物性格回复
                response = f"【性格模式】\n"
                response += f"根据我的性格特点：\n"
                response += f"{persona_content[:500]}...\n"
                response += f"\n关于你说的：{content}\n"
                response += "这就是我，一个真实的前任..."
            else:
                # 完整模式：综合关系记忆和人物性格
                response = f"【完整模式】\n"
                response += f"根据我们的共同记忆和我的性格特点：\n"
                response += f"\n关于你说的：{content}\n"
                response += "我想我会这样回应你..."
            
            # 模拟前任的回复风格
            response = self._simulate_ex_style(response, persona_content)
            
            return response
        except Exception as e:
            logger.error(f"调用前任 Skill 失败: {e}")
            return None

    def _simulate_ex_style(self, response, persona_content):
        """模拟前任的回复风格"""
        # 这里可以根据 persona_content 中的信息，调整回复风格
        # 简单示例：添加一些语气词和表情
        style_elements = ["...", "嗯", "你知道的", "对吧", "哈哈", "[微笑]", "[叹气]", "[开心]"]
        
        # 随机添加一些风格元素
        import random
        for i, element in enumerate(style_elements):
            if random.random() > 0.7:
                response += f" {element}"
        
        return response

    async def terminate(self):
        """插件销毁方法"""
        logger.info("ExSkill 插件已卸载")
