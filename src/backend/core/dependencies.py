from typing import AsyncGenerator
from src.backend.core.api_client.auth_client import AuthAPIClient
from src.backend.core.api_client.document_client import DocumentAPIClient
from src.backend.core.api_client.search_client import SearchAPIClient
from src.backend.core.api_client.tagging_client import TaggingAPIClient
from src.backend.core.api_client.grouping_client import GroupingAPIClient
from src.backend.core.message_queue import MessageQueue

async def get_auth_client() -> AsyncGenerator[AuthAPIClient, None]:
    client = AuthAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_document_client() -> AsyncGenerator[DocumentAPIClient, None]:
    client = DocumentAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_search_client() -> AsyncGenerator[SearchAPIClient, None]:
    client = SearchAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_tagging_client() -> AsyncGenerator[TaggingAPIClient, None]:
    client = TaggingAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_grouping_client() -> AsyncGenerator[GroupingAPIClient, None]:
    client = GroupingAPIClient()
    try:
        yield client
    finally:
        await client.close()

async def get_message_queue() -> AsyncGenerator[MessageQueue, None]:
    mq = MessageQueue()
    await mq.connect()
    try:
        yield mq
    finally:
        await mq.close() 