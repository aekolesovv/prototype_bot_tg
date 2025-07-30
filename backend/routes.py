from fastapi import APIRouter

router = APIRouter()

@router.get('/schedule')
def get_schedule():
    return {'schedule': []}

@router.post('/book')
def book_lesson():
    return {'result': 'success'}

@router.get('/clubs')
def get_clubs():
    return {'clubs': []}

@router.get('/profile')
def get_profile():
    return {'profile': {}}

@router.post('/test')
def submit_test():
    return {'result': 'test submitted'}
