from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from proyectoEntrega.views import index, top_smartwatches, seller_statistics, login, callback, logout
from django.http import HttpResponse
import requests
import asyncio

class ViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.session = {'user_name': 'TestUser'}


    @patch('proyectoEntrega.views.render')
    def test_index_authenticated(self, mock_render):
        request = self.factory.get('/')
        request.session = {'user_name': 'TestUser'}  # Simular sesión de usuario
        response = index(request)
        mock_render.assert_called_once_with(request, 'index.html', {'user_name': 'TestUser'})

    """def test_index_authenticated(self):
        response = index(self.request, user_name='TestUser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'TestUser', response.content)"""

    @patch('proyectoEntrega.views.requests.get')
    def test_top_smartwatches_success(self, mock_get):
        request = self.factory.get('/')
        request.session = {'user_name': 'TestUser'}  # Simular sesión de usuario

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'title': 'Watch 1',
                    'price': 100,
                    'permalink': 'http://example.com/watch1',
                    'thumbnail': 'http://example.com/thumb1.jpg'
                }
            ]
        }
        mock_get.return_value = mock_response

        response = top_smartwatches(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Watch 1', response.content)
        self.assertIn(b'TestUser', response.content)

    @patch('proyectoEntrega.views.requests.get')
    def test_top_smartwatches_error(self, mock_get):
        request = self.factory.get('/')
        request.session = {'user_name': 'TestUser'}  # Simular sesión de usuario

        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        response = top_smartwatches(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No se pudo realizar la conexi\xc3\xb3n', response.content)

    @patch("proyectoEntrega.views.fetch_data")
    def test_seller_statistics(self, mock_fetch_data):
        mock_fetch_data.return_value = {
            'results': [
                {'seller': {'id': 1, 'nickname': 'Seller1'}, 'price': 100, 'listing_type_id': 'gold_special'}
            ]
        }
        response = asyncio.run(seller_statistics(self.request))
        self.assertIn(b'Seller1', response.content)

    def test_login(self):
        with patch('proyectoEntrega.views.redirect') as mock_redirect:
            mock_redirect.return_value = HttpResponse("Redirecting...")
            response = login(self.request)
            self.assertEqual(response.status_code, 200)

    @patch('proyectoEntrega.views.requests.post')
    @patch('proyectoEntrega.views.requests.get')
    def test_callback_success(self, mock_get, mock_post):
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            'access_token': 'fake_access_token'
        }
        mock_post.return_value = mock_post_response

        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'nickname': 'TestUser'
        }
        mock_get.return_value = mock_get_response

        self.request.GET = {'code': 'fake_code'}
        with patch('proyectoEntrega.views.redirect') as mock_redirect:
            mock_redirect.return_value = HttpResponse("Redirecting...")
            response = callback(self.request)
            self.assertEqual(response.status_code, 200)

    def test_callback_no_code(self):
        self.request.GET = {}
        response = callback(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Error: No se recibi\xc3\xb3 un c\xc3\xb3digo de autorizaci\xc3\xb3n.', response.content)

    def test_logout(self):
        with patch('proyectoEntrega.views.redirect') as mock_redirect:
            mock_redirect.return_value = HttpResponse("Redirecting...")
            response = logout(self.request)
            self.assertEqual(response.status_code, 200)
