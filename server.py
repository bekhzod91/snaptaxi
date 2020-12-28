from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect

global sessions

sessions = {}

templates = Jinja2Templates(directory='templates')

async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})

async def admin(request):
    users = [user for user in sessions.keys()]
    context = {
        'users': users,
        'request': request
    }
    return templates.TemplateResponse('admin.html', context)

async def order_create(request):
    data = await request.json()
    websocket = sessions.get(data['username'])
    await websocket.send_json({'message': 'New order'})
    return JSONResponse({'status': 'Success'})

async def websocket_endpoint(websocket):
    username = None
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            action = data.get('action')
            message = data.get('message')
	
            if action == 'login':
                username = message
                sessions[username] = websocket
    except WebSocketDisconnect as e:
        if sessions.get(username):
            del sessions[username]


routes = [
    Route('/', homepage),
    Route('/admin', admin),
    Route('/api/order-create', order_create, methods=['POST']),
    WebSocketRoute('/ws', websocket_endpoint)
]

app = Starlette(debug=True, routes=routes)
