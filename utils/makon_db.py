from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):

        if self.pool is None:
            await self.create()

        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        date_of_birth VARCHAR(255) NOT NULL,
        phone_number VARCHAR NOT NULL,
        grade VARCHAR(255) NOT NULL,
        public_private VARCHAR(255) NOT NULL,
        SAT VARCHAR(255) NOT NULL,
        IELTS VARCHAR(255) NOT NULL,
        Duolingo VARCHAR(255) NOT NULL,
        visa_rejection VARCHAR(255) NOT NULL,
        travel_history VARCHAR(255) NOT NULL,
        average_funding VARCHAR(255) NOT NULL,
        username varchar(255) NOT NULL UNIQUE,
        telegram_id BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, date_of_birth, phone_number, grade, public_private, SAT, IELTS, Duolingo, visa_rejection, travel_history, average_funding,  username, telegram_id):
        sql = "INSERT INTO Users(full_name, date_of_birth, phone_number, grade, public_private, SAT, IELTS, Duolingo, visa_rejection, travel_history, average_funding, username, telegram_id) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) returning *"
        return await self.execute(sql, full_name, date_of_birth, phone_number, grade, public_private, SAT, IELTS, Duolingo, visa_rejection, travel_history, average_funding, username, telegram_id, fetchrow=True)


    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)


    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)


    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def delete_user(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)