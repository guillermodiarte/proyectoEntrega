from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings as st
import requests
import asyncio
import aiohttp

# Decorador para verificar si el usuario está autenticado
def user_authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        request.user_name = request.session.get('user_name', 'Invitado')
        return view_func(request, *args, **kwargs)
    return wrapper

# Página principal
@user_authenticated
def index(request):
    return render(request, 'index.html', {'user_name': request.user_name})

# Listado de relojes inteligentes más populares
@user_authenticated
def top_smartwatches(request):
    url = f"{st.ML_BASE_URL}/sites/MLA/search?category={st.CATEGORY_ID}&sort={st.SORT}&limit={st.LIMIT}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Captura errores HTTP
        items = response.json().get('results', [])
        context = {
            'user_name': request.user_name,
            'items': [
                {
                    'title': item.get('title', 'Sin título'),
                    'price': item.get('price', 0),
                    'permalink': item.get('permalink', '#'),
                    'thumbnail': item.get('thumbnail', '')
                }
                for item in items
            ]
        }
    except requests.exceptions.RequestException as e:
        context = {'error': f"No se pudo realizar la conexión: {str(e)}"}
    except Exception as e:
        context = {'error': f"Error inesperado: {str(e)}"}
    return render(request, 'top_smartwatches.html', context)

# Función asíncrona para obtener datos
async def fetch_data(url, session):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return {'error': f"Error HTTP {response.status}"}
            return await response.json()
    except Exception as e:
        return {'error': f"Error al obtener datos: {str(e)}"}

# Estadísticas de vendedores
async def seller_statistics(request):
    sellers = {}
    try:
        urls = [
            f"{st.ML_BASE_URL}/sites/MLA/search?category={st.CATEGORY_ID}&offset={offset}&limit=50"
            for offset in range(0, 1000, 50)
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_data(url, session) for url in urls]
            responses = await asyncio.gather(*tasks)

            for response in responses:
                if 'error' in response:
                    continue  # Ignorar respuestas con errores
                items = response.get('results', [])
                for item in items:
                    try:
                        seller_id = item['seller']['id']
                        seller_data = sellers.setdefault(seller_id, {
                            'nickname': item['seller'].get('nickname', 'Desconocido'),
                            'count': 0,
                            'gold_special': 0,
                            'gold_pro': 0,
                            'prices': []
                        })
                        seller_data['count'] += 1
                        seller_data['prices'].append(item.get('price', 0))
                        if item.get('listing_type_id') == 'gold_special':
                            seller_data['gold_special'] += 1
                        elif item.get('listing_type_id') == 'gold_pro':
                            seller_data['gold_pro'] += 1
                    except KeyError as e:
                        print(f"Error procesando un ítem: {e}")

        sellers_list = [
            {
                'seller_id': seller_id,
                'seller_nickname': data['nickname'],
                'total_listings': data['count'],
                'gold_special': data['gold_special'],
                'gold_pro': data['gold_pro'],
                'average_price': round(sum(data['prices']) / len(data['prices']), 2) if data['prices'] else 0
            }
            for seller_id, data in sellers.items()
        ]

        sellers_list.sort(key=lambda x: x['total_listings'], reverse=True)
        return render(request, 'seller_statistics.html', {'sellers': sellers_list})
    except Exception as e:
        return render(request, 'seller_statistics.html', {'error': f"Error inesperado: {str(e)}"})

# Iniciar sesión
def login(request):
    try:
        auth_url = (
            f'https://auth.mercadolibre.com.ar/authorization?response_type=code'
            f'&client_id={st.ML_CLIENT_ID}'
            f'&redirect_uri={st.ML_REDIRECT_URI}'
        )
        return redirect(auth_url)
    except Exception as e:
        return HttpResponse(f"Error al intentar redirigir a la autenticación: {str(e)}", status=500)

# Callback de autenticación
def callback(request):
    code = request.GET.get('code')
    if not code:
        return HttpResponse('Error: No se recibió un código de autorización.', status=400)

    url = 'https://api.mercadopago.com/oauth/token'
    payload = {
        "client_secret": st.ML_CLIENT_SECRET,
        "client_id": st.ML_CLIENT_ID,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": st.ML_REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Captura errores HTTP
        data = response.json()
        access_token = data.get('access_token')

        # Obtener información del usuario
        user_info_url = 'https://api.mercadolibre.com/users/me'
        user_headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=user_headers)
        user_response.raise_for_status()

        user_data = user_response.json()
        request.session['user_name'] = user_data.get('nickname', 'Usuario')
        return redirect('index')
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"Error en la solicitud: {str(e)}", status=500)
    except KeyError as e:
        return HttpResponse(f"Error al procesar los datos: {str(e)}", status=500)
    except Exception as e:
        return HttpResponse(f"Error inesperado: {str(e)}", status=500)

# Cerrar sesión
def logout(request):
    try:
        request.session.flush()
    except Exception:
        pass
    return redirect('index')
