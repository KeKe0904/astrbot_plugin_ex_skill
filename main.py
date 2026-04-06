from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import os
import json
import shutil
from pathlib import Path

@register("astrbot_plugin_ex_skill", "落梦陳", "把前任蒸馏成 AI Skill，用ta的方式跟你说话", "1.0.0")
class ExSkillPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.exes_dir = Path(__file__).parent / "exes"
        self.exes_dir.mkdir(exist_ok=True)
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.tools_dir = Path(__file__).parent / "tools"

    async def initialize(self):
        """插件初始化方法"""
        logger.info("ExSkill 插件初始化完成")

    @filter.command("create-ex")
    async def create_ex(self, event: AstrMessageEvent):
        """创建前任 Skill"""
        user_name = event.get_sender_name()
        yield event.plain_result(f"{user_name}，开始创建前任 Skill。请按照提示输入信息：")
        yield event.plain_result("1. 前任的代号（用于调用，如 'first-love'）")
        yield event.plain_result("2. 基本信息（如：在一起三年，大学时期）")
        yield event.plain_result("3. 性格画像（如：ENFP，双子座，话痨）")
        yield event.plain_result("4. 数据源（可选择：微信聊天记录、QQ消息、照片等）")
        yield event.plain_result("所有字段均可跳过，仅凭描述也能生成。")

    @filter.command("list-exes")
    async def list_exes(self, event: AstrMessageEvent):
        """列出所有前任 Skill"""
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

    @filter.command("delete-ex")
    async def delete_ex(self, event: AstrMessageEvent, slug: str):
        """删除前任 Skill"""
        ex_dir = self.exes_dir / slug
        if ex_dir.exists():
            shutil.rmtree(ex_dir)
            yield event.plain_result(f"已删除前任 Skill: {slug}")
        else:
            yield event.plain_result(f"未找到前任 Skill: {slug}")

    @filter.command("let-go")
    async def let_go(self, event: AstrMessageEvent, slug: str):
        """放下前任（删除的温柔别名）"""
        await self.delete_ex(event, slug)

    async def terminate(self):
        """插件销毁方法"""
        logger.info("ExSkill 插件已卸载")
