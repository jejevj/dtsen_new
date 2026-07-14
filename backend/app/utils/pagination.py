def paginate_query(query, page: int, per_page: int) -> dict:
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': paginated.items,
        'meta': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev,
        }
    }
