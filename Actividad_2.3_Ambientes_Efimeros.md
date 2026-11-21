---
materia: Tendencias en entornos de desarrollo de aplicaciones y servicios
unidad: 2
actividad: Actividad 2.3. Ephemeral enviroments
profesor: OSCAR GREGORIO SILVA MARES
estudiante: Jonathan Daniel Gómez Peña
matricula: 224790932
fecha: 21/11/2026
---

# Ambientes efímeros para pruebas

Un ambiente efímero es una copia completa del entorno de ejecución que se crea para un propósito concreto y se destruye al terminar ese propósito. A diferencia del ambiente de producción, que permanece encendido y conserva sus datos, el efímero nace con una versión específica del código, sirve para validar un cambio y desaparece, de modo que no deja recursos ocupados ni configuraciones a medias. La ventaja práctica es que permite probar una rama, una corrección o una idea sin arriesgar el servicio que ya usan los usuarios (Chartier, 2020).

La literatura sobre el tema insiste en dos rasgos que separan al ambiente efímero de un simple servidor de pruebas. El primero es que se aprovisiona solo, a partir de la configuración que vive en el repositorio, sin pasos manuales que dependan de la memoria de quien lo levanta. El segundo es que su vida está acotada: al cerrar la rama o el pull request, el ambiente y sus recursos se eliminan, y con ellos desaparece la costumbre de acumular servidores de prueba que nadie recuerda haber creado (ReleaseHub, s. f.).

Para esta actividad se construyó una aplicación pequeña en Node.js y se desplegó con ese esquema: el código vive en GitHub, la configuración del servicio vive en un archivo del mismo repositorio y el proveedor crea el ambiente a partir de ahí, sin intervención manual.

# La aplicación desplegada

La aplicación es un servicio de monitoreo de ejemplo escrito en Node.js. No usa dependencias externas, sólo el módulo http de la plataforma, para que el build no dependa de paquetes de terceros y el resultado sea fácil de revisar. Su función es responder en tres rutas:

- La raíz muestra una página con los datos de ejecución del contenedor: plataforma, nombre del servicio, rama desplegada, commit, identificador de la instancia y segundos que lleva encendida.
- /health devuelve el estado del servicio en JSON, con el mismo conjunto de datos, y sirve como verificación automática después de cada despliegue.
- /api/estado devuelve esos datos como JSON formateado, útil para revisarlos desde la terminal.

El interés de la aplicación no está en su interfaz, sino en lo que expone: los valores de la página se leen de las variables de entorno que el proveedor inyecta en cada contenedor. Eso permite comprobar que la URL pública que se está viendo pertenece a una instancia concreta, con un commit concreto, y no a una copia en la máquina local.

La aplicación está publicada en https://ambiente-efimero-demo.onrender.com y el código en https://github.com/JonathanDa16/ambiente-efimero-demo.

# Proceso de despliegue

El despliegue siguió el flujo que describe la guía de Heroku para Node.js: un repositorio con el proyecto, un archivo de arranque que declara el comando del servidor y un build automático al hacer push (Heroku, s. f.). El proveedor utilizado fue Render, que mantiene un plan gratuito vigente para servicios web; el procedimiento es el mismo porque también construye desde el repositorio y publica el resultado en una URL propia.

1. Se creó el repositorio público en GitHub con el proyecto: server.js con el servidor, package.json con el comando de arranque, Procfile y README con las instrucciones.

2. Se agregó el archivo render.yaml, que declara el servicio web, el plan gratuito, la región, el comando de construcción y el de arranque, y la versión de Node que debe usarse. Este archivo es la definición del ambiente: no hay configuración hecha a mano en el panel del proveedor.

3. Se conectó el repositorio al proveedor con la cuenta de GitHub y se aplicó el blueprint. El proveedor leyó render.yaml, creó el servicio y ejecutó el build sin pasos adicionales.

4. Cada push a la rama main dispara un despliegue nuevo. La versión anterior sigue respondiendo hasta que la nueva queda sana, y el commit que aparece en la página permite confirmar cuál está en línea.

5. La verificación posterior se hizo sobre la URL pública con /health y /api/estado, y con el campo commit de la página, que debe coincidir con el último push. Ese es el criterio para saber que el ambiente quedó actualizado.

# Verificación del despliegue

La página responde con los datos del contenedor que atendió la petición: plataforma Render, servicio ambiente-efimero-demo, rama main y el commit que corresponde al último push del repositorio.

# Ambientes efímeros por rama

La misma configuración deja el proyecto listo para generar un ambiente por cada propuesta de cambio. Al abrir un pull request, el proveedor puede crear una instancia nueva, con su propia URL, que toma el código de esa rama; ahí se prueba el cambio sin tocar el servicio principal. Cuando el pull request se cierra o se fusiona, la instancia y sus recursos se destruyen. La página informa si la instancia es de este tipo mediante el campo Review app, que responde sí en esos casos y no en el servicio principal.

# Conclusión

Lo difícil de un ambiente efímero no es levantar el servidor, sino dejar escrita la definición del ambiente para que cualquiera pueda reproducirlo y destruirlo sin consecuencias. Con el proyecto en GitHub y la configuración versionada, el despliegue se reduce a un push y la verificación a dos rutas del servicio. La aplicación sirve de ejemplo porque expone los datos de la instancia que responde: esa es la evidencia de que el ambiente es nuevo y no una copia local.

# Referencias

Chartier, C. (2020, 16 de noviembre). What is an ephemeral environment? webapp.io. https://webapp.io/blog/what-is-an-ephemeral-environment/

Heroku. (s. f.). Getting started on Heroku with Node.js. https://devcenter.heroku.com/articles/getting-started-with-nodejs

Node.js. (s. f.). HTTP: Servidores web. https://nodejs.org/api/http.html

ReleaseHub. (s. f.). What is an ephemeral environment? https://releasehub.com/ephemeral-environments

Render. (s. f.). Free instances. https://render.com/docs/free
