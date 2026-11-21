# Ambiente efímero de demostración (Heroku)

Aplicación mínima en Node.js que sirve una página con los datos de ejecución del dyno
y dos endpoints de verificación. Se usa para mostrar cómo un ambiente efímero se crea,
se prueba y se destruye sin tocar el ambiente principal.

## Rutas

- `/` página con los datos del ambiente (app, release, dyno, commit).
- `/health` estado del servicio en JSON.
- `/api/estado` los mismos datos en JSON.

## Ejecutar en local

```bash
npm start
# http://localhost:3000
```

No tiene dependencias externas: usa sólo el módulo `http` de Node.

## Desplegar en Heroku

```bash
heroku login
heroku create ambiente-efimero-jonathan
git push heroku main
heroku open
```

## Ambientes efímeros (review apps)

El archivo `app.json` permite habilitar review apps en el pipeline: cada pull request
levanta una app temporal con su propia URL y se destruye al cerrar o fusionar el cambio.

```bash
heroku pipelines:create -a ambiente-efimero-jonathan
heroku pipelines:update -a <app-de-review> --stage review
```
