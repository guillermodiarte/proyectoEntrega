# Proyecto de Entrega

Para poder realizar el login, una vez proporcionada las credenciales, es necesario
escribir la siguiente url en el navegador:

### localhost:8000/callback/

y agregar la respuesta que propocionó el navegador:

![login](/images/1.png "Login")

y modificarlo para que quede de la siguiente manera:

### ej: localhost:8000/callback/?code=TG-6792b2353d34730001ccf8d1-97741271

Esto es necesario porque la documentación de la API de ML exige que la URL de 
redireccionamiento sea exactamente igual a la que se proporciono al crear la app.

![error](/images/2.png "Error")

