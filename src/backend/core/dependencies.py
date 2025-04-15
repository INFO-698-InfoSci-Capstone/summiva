from typing import Generator
from fastapi import Depends
from core.api.auth_client import AuthAPIClient
from core.api.document_client import DocumentAPIClient
from core.api.search_client import SearchAPIClient
from core.api.tagging_client import TaggingAPIClient
from core.api.grouping_client import GroupingAPIClient
from core.message_queue import MessageQueue

async def get_auth_client() -> Generator[AuthAPIClient, None, None]:
    client = AuthAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_document_client() -> Generator[DocumentAPIClient, None, None]:
    client = DocumentAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_search_client() -> Generator[SearchAPIClient, None, None]:
    client = SearchAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_tagging_client() -> Generator[TaggingAPIClient, None, None]:
    client = TaggingAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_grouping_client() -> Generator[GroupingAPIClient, None, None]:
    client = GroupingAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_message_queue() -> Generator[MessageQueue, None, None]:
    mq = MessageQueue()
    await mq.connect()
    try:
        yield mq
    finally:
        await mq.close() 