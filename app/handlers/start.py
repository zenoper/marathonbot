from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

import config as Config
from utils.postgresql import Database

from aiogram.types import ChatJoinRequest


class ReferralBot:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self.router = Router()
        self.setup_handlers()
        self.private_link = None

    def setup_handlers(self):
        self.router.message.register(self.start_command, Command("start"))
        self.router.callback_query.register(self.check_referrals, lambda c: c.data == "check_referrals")
        self.router.message.register(self.check_refers, Command("check_referrals"))
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
        print(f"User stats: {stats}")

        if stats['link_id']:
            # If there's an existing link, verify it's still valid
            invite_link = stats['link_id']
        else:
            invite_link = await self.create_invite_link(user_id)

        # Create keyboard
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text="Check My Referrals",
            callback_data="check_referrals"
        ))

        stats_text = (
            f"🔗 Active link: {invite_link}\n"
            f"👥 Available slots: {stats['remaining_slots']}\n"
            f"✅ Total referrals: {stats['referral_count']}"
        )

        await message.answer(
            f"Welcome to the Marathon!\n\n"
            f"Share this link with others: {invite_link}\n\n"
            f"Your stats:\n{stats_text}\n\n"
            f"When {Config.REQUIRED_REFERRALS} people join through your links, "
            f"you'll get access to the private channel!\n\n"
            f"⚠️ Each link expires in 7 days.",
            reply_markup=builder.as_markup()
        )

    async def handle_new_member(self, event: ChatJoinRequest):
        user_id = event.from_user.id
        chat_id = event.chat.id
        print(event)

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
