# Proyecto de Entrega

Durante el desarrollo del proyecto, me encontré con varios problemas que detallo a continuación:

1. **Complicaciones con el login mediante OAuth de MercadoLibre**  
   Tuve dificultades con la respuesta que retorna su API, ya que la `redirect_uri` debe coincidir exactamente con la registrada en la configuración de la aplicación para evitar errores de acceso. Esto complicó el desarrollo al trabajar de forma local.

2. **Logout incompleto**  
   No logré implementar un sistema de logout que, además de cerrar la sesión en mi aplicación, también cierre la sesión en MercadoLibre. Esto deja la sesión activa en el entorno de MercadoLibre, lo que no es ideal.

3. **Problemas al obtener datos del usuario autenticado**  
   No pude acceder a los datos del usuario autenticado al realizar llamadas asíncronas para obtener información sobre los vendedores. Esto provoca que los datos de la sesión no se transmitan correctamente, mostrando el botón de "Login" en lugar de "Logout" incluso cuando el usuario ya está autenticado.

## Instrucciones para realizar el login

Para realizar el login correctamente, después de proporcionar las credenciales, es necesario acceder a la siguiente URL en el navegador:


### localhost:8000/callback/

A continuación, se debe tomar la respuesta proporcionada por el navegador:

![login](/images/1.png "Login")

Y modificarla para que quede de la siguiente forma:

### ej: localhost:8000/callback/?code=TG-6792b2353d34730001ccf8d1-97741271

Esto es necesario porque la documentación de la API de MercadoLibre exige que la URL de redireccionamiento coincida exactamente con la que se registró al crear la aplicación.

![error](/images/2.png "Error")


