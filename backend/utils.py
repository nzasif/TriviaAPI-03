NO_QUESTIONS_PER_PAGE = 10

# pagination setup
def get_paginated_qs(request, qsQuery):
    page = request.args.get('page', 1, type = int)
    start = (page - 1) * NO_QUESTIONS_PER_PAGE
    end = start + NO_QUESTIONS_PER_PAGE
    qs = [q.format() for q in qsQuery]
    current_qs = qs[start:end]
    
    return current_qs