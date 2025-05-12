from aiogram import Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

import config as Config
from utils.postgresql import Database

from aiogram.types import ChatJoinRequest
from aiogram.utils.markdown import bold, code, text, link, underline


class ReferralBot:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.router = Router()
        self.setup_handlers()
        self.private_link = None

    def setup_handlers(self):
        self.router.message.register(self.start_command, Command("start"))
        self.router.callback_query.register(self.check_referrals, lambda c: c.data == "check_my_referrals")
        self.router.message.register(self.check_refers, Command("check_my_referrals"))
        self.router.message.register(self.top_referrers, Command("top_referrers"))
        self.router.message.register(self.admin_check_user_referrals, Command("admin_check"))
        # Change this line to register for chat join requests
        self.router.chat_join_request.register(self.handle_new_member)

    async def create_invite_link(self, user_id: int) -> str:
        # Create a regular invite link with a unique ref parameter
        try:
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=Config.MAIN_CHANNEL_ID,
                expire_date=datetime.now() + timedelta(days=7),
                name=f"ref_{user_id}",  # Use this to track referrer
                creates_join_request=True
            )

            await self.db.store_invite_link(
                link_id=invite_link.invite_link.split('/')[-1],
                referrer_id=user_id,
                expires_at=datetime.now() + timedelta(days=7)
            )

            return invite_link.invite_link

        except Exception as e:
            print(f"Error creating invite link: {e}")
            raise

    async def start_command(self, message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username

        # Create or update user in database
        await self.db.create_user(user_id, username)

        # Get user's link stats
        stats = await self.db.get_link_stats(user_id)

        if stats['link_id']:
            # If there's an existing link, verify it's still valid
            invite_link = f"https://t.me/{stats['link_id']}"
        else:
            invite_link = await self.create_invite_link(user_id)

        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Check My Referrals",
            callback_data="check_my_referrals"
        ))

        stats_text = (
            f"🔗 Active link: {invite_link}\n"
            f"👥 Available slots: {stats['remaining_slots']}\n"
            f"✅ Total referrals: {stats['referral_count']}"
        )

        # await message.answer(
        #     text=f"'3 Free SAT seats + 3 day SAT Marathon'\n\n"
        #     f"📣Farg'onadagi eng katta SAT markazlardan biri 'Master SAT'dan bomba yangilik💣💣\n\n"
        #     f"SATdan 1500 olgan Farg'onaning eng malakali SAT Mentorlaridan biri Abdulahad teacher bu marafonda barcha sirlarni ochadi.🎙\n\n"
        #     f"Bu marafondan keyin SAT balingizni bemalol 100-200 balga oshirsangiz bo'ladi.💥 \n\n"
        #     f"Shoshmang, bu xali hammasi emas \n\n"
        #     f"3 kunlik marafonimizda har kuni bittadan FREE SAT SEAT o'ynaymiz. 💎 \nHar kunlik Masterklassdan keyin darsda qatnashgan bir kishiga o'zi xohlagan SAT imtixon sanasiga bepulga registratsiya qilib beramiz. \nBunaqasi xali O'zbekistonda bo'lmagan.\n\n"
        #     f"Bunday imkoniyatni qo'ldan boy bermang⚡️",
        #     reply_markup=builder.as_markup()
        #)

        await message.answer_photo(photo="https://imgur.com/a/PwqNLfn",
                                   caption=f"<b>'SAT'ni Tekinga Topshiramiz 👍</b>\n\n"
            f"14-May kuni 'Free SAT Seat + Acing the SAT' marafonida qatnashing 🔵\n\n"
            f"<b>Quyidagilar sizni kutyabdi:</b>\n"
            f"✅ Free SAT Seat\n"
            f"✅ Lesson full of SAT magic\n"
            f"✅ Tips for acing the EBRW and Math.\n\n"
            f"<blockquote>SATni tekinga topshiring, qo'shimchasiga Expertlardan eng zo'r tiplar oling. Bunday imkoniyat qaytib bo'lmaydi 😉</blockquote>\n\n"
            f"'Master SAT Fergana' doim sizni o'ylaydi 🤝\n\n"
            f"{invite_link}",
                                    reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

    async def handle_new_member(self, event: ChatJoinRequest):
        user_id = event.from_user.id
        chat_id = event.chat.id

        try:
            invite_link = event.invite_link
            if invite_link:
                # Extract referrer_id from the name (ref_123456)
                if invite_link.name and invite_link.name.startswith('ref_'):
                    referrer_id = int(invite_link.name.split('_')[1])

                    # Process referral
                    gained_access = await self.db.add_referral(
                        referrer_id=referrer_id,
                        referred_id=user_id,
                        invite_link_id=invite_link.invite_link.split('/')[-1]
                    )

                    if gained_access:
                        invite_link_private = await self.bot.create_chat_invite_link(
                            chat_id=Config.PRIVATE_CHANNEL_ID,
                            expire_date=datetime.now() + timedelta(days=7),
                            member_limit=1
                        )
                        self.private_link = invite_link_private.invite_link
                        await self.bot.send_message(
                            chat_id=referrer_id,
                            text=(
                                f"🎉 Congratulations! You've reached {Config.REQUIRED_REFERRALS} referrals.\n\n"
                                f"Here's your private channel link: \n{self.private_link}"
                            )
                        )

            # Approve the join request
            await self.bot.approve_chat_join_request(
                chat_id=chat_id,
                user_id=user_id
            )
        except Exception as e:
            print(f"Error processing join request: {e}")
            print(f"Event details: {event}")

    async def check_referrals(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        stats = await self.db.get_link_stats(user_id)

        remaining = max(0, Config.REQUIRED_REFERRALS - stats['referral_count'])

        message = (
            f"Your referral stats:\n\n"
            f"🔗 Active invite links: https://t.me/{stats['link_id']}\n"
            f"👥 Available slots in active links: {stats['remaining_slots']}\n"
            f"✅ Total referrals: {stats['referral_count']}\n"
            f"🎯 Referrals needed: {remaining}\n"
        )

        if stats['has_access']:
            message += f"\n🎉 You have access to the private channel: {self.private_link}"

        await callback.message.answer(text=message, reply_markup=callback.message.reply_markup)

    async def check_refers(self, message: types.Message):
        user_id = message.from_user.id
        stats = await self.db.get_link_stats(user_id)

        remaining = max(0, Config.REQUIRED_REFERRALS - stats['referral_count'])

        msg = (
            f"Your referral stats:\n\n"
            f"🔗 Active invite links: https://t.me/{stats['link_id']}\n"
            f"👥 Available slots in active links: {stats['remaining_slots']}\n"
            f"✅ Total referrals: {stats['referral_count']}\n"
            f"🎯 Referrals needed: {remaining}\n"
        )

        if stats['has_access']:
            msg += f"\n🎉 You have access to the private channel: {self.private_link}"

        await message.answer(text=msg, reply_markup=message.reply_markup)

    async def top_referrers(self, message: types.Message):
        top_users = await self.db.get_top_referrers()
        
        if not top_users:
            await message.answer("No referrals yet! Be the first to refer someone!")
            return

        msg = "🏆 Top 10 Referrers:\n\n"
        for i, user in enumerate(top_users, 1):
            username = user['username'] or 'Anonymous'
            msg += f"{i}. @{username}: {user['referral_count']} referrals"
            if i == 1:
                msg += " 🎁 (Free SAT Seat)"
            msg += "\n"

        await message.answer(text=msg)
        
    async def admin_check_user_referrals(self, message: types.Message):
        # Check if user is admin
        if str(message.from_user.id) not in Config.ADMIN:
            return
            
        # Parse command: /admin_check username or user_id
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer("Usage: /admin_check username_or_id")
            return
            
        user_identifier = parts[1]
        
        # Check if it's a user ID or username
        try:
            user_id = int(user_identifier)
            # It's a user ID
            async with self.db.pool.acquire() as conn:
                user_info = await conn.fetchrow('''
                    SELECT user_id, username, referral_count, has_access
                    FROM users
                    WHERE user_id = $1
                ''', user_id)
        except ValueError:
            # It's a username
            username = user_identifier.lstrip('@')
            async with self.db.pool.acquire() as conn:
                user_info = await conn.fetchrow('''
                    SELECT user_id, username, referral_count, has_access
                    FROM users
                    WHERE username = $1
                ''', username)
        
        if not user_info:
            await message.answer(f"User not found: {user_identifier}")
            return
            
        # Get user's referrals
        user_id = user_info['user_id']
        referrals = await self.db.get_user_referrals_by_timestamp(user_id)
        
        # Prepare response
        response = f"User: @{user_info['username'] or 'Anonymous'} (ID: {user_info['user_id']})\n"
        response += f"Total Referrals: {user_info['referral_count']}\n\n"
        
        if referrals:
            # If there are many referrals, just show the count and the most recent ones
            if len(referrals) > 20:
                response += f"Showing 10 most recent of {len(referrals)} referrals:\n\n"
                referrals = referrals[:10]  # Only show the 10 most recent
            else:
                response += f"All {len(referrals)} referrals:\n\n"
            
            for i, ref in enumerate(referrals, 1):
                username = ref['referred_username'] or 'Anonymous'
                timestamp = ref['created_at'].strftime('%Y-%m-%d %H:%M')
                response += f"{i}. @{username} - {timestamp}\n"
        else:
            response += "No referrals found for this user."
            
        await message.answer(response)
