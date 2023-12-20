def paginationMeta(paginator, page_obj, pageSize):
    meta = {
        'currentPageNumber': page_obj.number,
        'totalPages': paginator.num_pages,
        'totalRecords': paginator.count,
        'totalFilteredRecords': paginator.count,
        'pageSize': pageSize
    }
    return meta
