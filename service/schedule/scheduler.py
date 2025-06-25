from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.methods.get import get_user
from database.methods.update import update_user
from service.AI.GPT import generate, prompts
from bot.keyboards.inline import journal_keyboard
from aiogram import Bot
from datetime import datetime

class DailyScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

        self.scheduler.add_job(
            self.send_reminder,
            trigger="cron",
            hour=22, minute=00,
        )

        self.scheduler.add_job(
            self.reset_daily,
            trigger="cron",
            hour=22, minute=30,
        )

        self.scheduler.add_job(
            self.send_reminder,
            trigger="cron",
            hour=7, minute=0
        )

        self.scheduler.start()

    async def send_reminder(self) -> None:
        users = await get_user.all()

        for user in users:
            tasks = "\n".join([f"{i}. {'✅' if task.is_completed else '❌'} {task.name}: {task.description}" for i, task in enumerate(user.tasks)])
            if tasks == '': tasks = 'Задач пока не поставлено...'
            journal = user.parsed_journal if user.parsed_journal != '' else 'Пока в журнале пусто...'
            date = datetime.strftime(datetime.now(), "%d.%m.%Y"),
            time = datetime.strftime(datetime.now(), "%H:%M")

            user_info = f"""Имя: {user.info.name}
Возраст: {user.info.age}
Город: {user.info.city}
Работа: {user.info.job}
Хобби: {user.info.hobby}
Мечта: {user.info.dream}
Характер: {user.info.personality}
Пожелания в ответах ИИ:
{user.info.wishes}"""

            prompt = prompts.review.format(
                date = date,
                time = time,
                tasks = tasks,
                journal = journal,
                user_ask = "",
                user_info = user_info
            )
            sent = True
            while sent:
                try:
                    response = await generate(prompt)
                    await self.bot.send_message(chat_id=user.userid, text=response, parse_mode='HTML')
                    sent = False
                except:
                    pass
    
    async def reset_daily(self) -> None:
        users = await get_user.all()

        for user in users:
            date = datetime.strftime(datetime.now(), "%d.%m.%Y")
            task_text = '<pre>'+'\n'.join([f'- [{'x' if task.is_completed else ' '}] {task.name}: {task.description}' for task in user.tasks])+'</pre>' if user.tasks != [] else 'Журнал пока пуст...'

            text = f"""<b>Сегодня:</b> <i>{date}</i>

{f'<pre>{user.parsed_journal}</pre>' if user.parsed_journal != '' else 'Журнал пока пуст...'}

{task_text}"""
            
            # keyboard = journal_keyboard(user.list_journal != [], user.settings.note_link_parsed)
            
            await self.bot.send_message(chat_id=user.userid,text=text, parse_mode='HTML')
            await update_user.journal(user.userid, '')
            for task in user.tasks:
                await update_user.remove_task(user.userid, task.name)
