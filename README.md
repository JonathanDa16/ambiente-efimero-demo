# Ambiente efímero de demostración

Aplicación mínima en Node.js que sirve una página con los datos de ejecución del
contenedor y dos endpoints de verificación. Se usa para mostrar cómo un ambiente
efímero se crea, se prueba y se destruye sin tocar el ambiente principal.

Desplegada en Render (plan gratuito): https://ambiente-efimero-demo.onrender.com

## Rutas

- `/` página con los datos del ambiente (plataforma, servicio, commit, instancia).
- `/health` estado del servicio en JSON.
- `/api/estado` los mismos datos en JSON.

## Ejecutar en local

```bash
npm start
# http://localhost:3000
```

No tiene dependencias externas: usa sólo el módulo `http` de Node.

## Desplegar en Render

El archivo `render.yaml` define el servicio como Blueprint: Render lo lee del
repositorio y crea el servicio web en el plan gratuito, sin tarjeta.

1. Entrar a render.com con la cuenta de GitHub.
2. New → Blueprint → elegir este repositorio.
3. Apply. El build y el despliegue corren solos.

Un servicio gratuito se duerme a los 15 minutos sin tráfico y despierta en cerca
de un minuto con la siguiente visita, que es el comportamiento esperado de un
ambiente temporal.

## Ambientes efímeros (review apps)

`render.yaml` deja el servicio listo para crear ambientes por pull request: cada
rama o PR puede levantar su propia instancia con su propia URL y se destruye al
cerrarla, sin tocar el servicio principal. La variable `IS_PULL_REQUEST` indica
en la página si la instancia es una review app.

## Nota sobre Heroku

La consigna sugería Heroku; desde noviembre de 2022 esa plataforma no tiene plan
gratuito y el dyno más barato (eco) requiere tarjeta. El procedimiento documentado
aquí es el mismo concepto con un proveedor sin costo: repositorio en GitHub, build
automático, URL pública y ambientes desechables por rama. El archivo `app.json` se
conserva porque describe los mismos datos que Heroku pediría en un pipeline.
