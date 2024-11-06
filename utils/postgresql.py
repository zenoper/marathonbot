from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from datetime import datetime, timedelta
from typing import Optional

import marathonbot.config as Config


class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(user=Config.DB_USER, password=Config.DB_PASS, host=Config.DB_HOST, port=Config.DB_PORT, database=Config.DB_NAME)
        return cls(pool)

    async def init_db(self):
        async with self.pool.acquire() as conn:
            # Create users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    referral_count INTEGER DEFAULT 0,
                    has_access BOOLEAN DEFAULT FALSE
                )
            ''')

            # Create invite links table with usage count
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS invite_links (
                    link_id TEXT PRIMARY KEY,
                    referrer_id BIGINT REFERENCES users(user_id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE,
                    usage_count INTEGER DEFAULT 0
                )
            ''')

            # Create referrals table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_id BIGINT REFERENCES users(user_id),
                    referred_id BIGINT,
                    invite_link_id TEXT REFERENCES invite_links(link_id),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            ''')


    async def delete_db(self):
        async with self.pool.acquire() as conn:
            # Create users table
            await conn.execute('''
                DROP TABLE IF EXISTS users CASCADE;
            ''')

            # Create invite links table with usage count
            await conn.execute('''
                DROP TABLE IF EXISTS invite_links CASCADE;
            ''')

            # Create referrals table
            await conn.execute('''
                DROP TABLE IF EXISTS referrals CASCADE;
            ''')

    async def create_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username)
                VALUES ($1, $2)
                ON CONFLICT (user_id) DO UPDATE 
                SET username = $2
            ''', user_id, username)

    async def store_invite_link(self, link_id: str, referrer_id: int, expires_at: datetime):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO invite_links (link_id, referrer_id, expires_at)
                VALUES ($1, $2, $3)
            ''', link_id, referrer_id, expires_at)

    async def check_link_validity(self, link_id: str) -> tuple[bool, Optional[int]]:
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow('''
                SELECT referrer_id, usage_count, expires_at
                FROM invite_links 
                WHERE link_id = $1
            ''', link_id)

            if not result:
                return False, None

            is_valid = (
                    result['usage_count'] < 10 and  # Less than 10 uses
                    result['expires_at'] > datetime.now()  # Not expired
            )

            return is_valid, result['referrer_id'] if is_valid else None

    async def add_referral(self, referrer_id: int, referred_id: int, invite_link_id: str):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Check if this user was already referred
                existing = await conn.fetchrow('''
                    SELECT id FROM referrals 
                    WHERE referred_id = $1
                ''', referred_id)

                if existing:
                    return False

                # Increment usage count for the invite link
                await conn.execute('''
                    UPDATE invite_links 
                    SET usage_count = usage_count + 1
                    WHERE link_id = $1
                ''', invite_link_id)

                # Add referral record
                await conn.execute('''
                    INSERT INTO referrals (referrer_id, referred_id, invite_link_id)
                    VALUES ($1, $2, $3)
                ''', referrer_id, referred_id, invite_link_id)

                # Update referrer's count
                await conn.execute('''
                    UPDATE users 
                    SET referral_count = referral_count + 1
                    WHERE user_id = $1
                ''', referrer_id)

                # Check if referrer has reached required referrals
                row = await conn.fetchrow('''
                    UPDATE users 
                    SET has_access = TRUE 
                    WHERE user_id = $1 
                    AND referral_count >= $2 
                    AND has_access = FALSE
                    RETURNING user_id
                ''', referrer_id, Config.REQUIRED_REFERRALS)

                return bool(row)

    async def get_link_stats(self, user_id: int) -> dict:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT 
                    u.referral_count,
                    u.has_access,
                    il.link_id,
                    SUM(CASE WHEN il.expires_at > NOW() AND il.usage_count < 10 THEN 10 - il.usage_count ELSE 0 END) as remaining_slots
                FROM users u
                LEFT JOIN invite_links il ON u.user_id = il.referrer_id
                WHERE u.user_id = $1
                GROUP BY u.referral_count, u.has_access, il.link_id
            ''', user_id)

    async def return_invite(self, user_id: int) -> dict:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT 
                    link_id
                FROM invite_links
                WHERE invite_links.user_id = $1
            ''', user_id)