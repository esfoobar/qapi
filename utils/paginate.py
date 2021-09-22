import math
from typing import TYPE_CHECKING
from sqlalchemy import select
from sqlalchemy.sql.expression import func

if TYPE_CHECKING:
    from databases import Database
    from sqlalchemy.sql.selectable import Select


class Page(object):
    def __init__(
        self, items: list, page: int, page_size: int, total: int
    ) -> None:
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 1
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


async def paginate(
    conn: "Database", query: "Select", page: int, page_size: int
) -> Page:
    items_page_query = query.limit(page_size).offset((page - 1) * page_size)
    items = await conn.fetch_all(items_page_query)
    total_items_query = (
        select([func.count()])
        .select_from(query.froms[0])
        .where(query.whereclause)
    )
    total_result = await conn.execute(total_items_query)
    return Page(items, page, page_size, total_result)
