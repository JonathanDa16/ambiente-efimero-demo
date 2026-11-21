// Servidor mínimo en Node.js: no usa dependencias externas para que el
// despliegue en Heroku no dependa de un npm install con paquetes de terceros.
const http = require('http');
const fs = require('fs');
const path = require('path');

const PUERTO = process.env.PORT || 3000;
const INICIO = Date.now();

// Heroku inyecta estas variables en cada dyno. Se leen para que la página
// muestre de qué release y de qué app salió la respuesta.
const datos = () => ({
  aplicacion: process.env.HEROKU_APP_NAME || 'local',
  release: process.env.HEROKU_RELEASE_VERSION || 'local',
  dyno: process.env.DYNO || 'local',
  commit: process.env.HEROKU_SLUG_COMMIT
    ? process.env.HEROKU_SLUG_COMMIT.slice(0, 7)
    : 'sin commit',
  version: process.env.HEROKU_RELEASE_CREATED_AT || new Date().toISOString(),
  encendido_segundos: Math.round((Date.now() - INICIO) / 1000),
});

const pagina = () => {
  const d = datos();
  const filas = Object.entries(d)
    .map(([k, v]) => `<tr><th>${k.replace(/_/g, ' ')}</th><td>${v}</td></tr>`)
    .join('');
  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ambiente efímero | ${d.aplicacion}</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100vh; display: grid; place-items: center;
    font-family: ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif;
    background: #101828; color: #e8eefc; padding: 24px;
  }
  main { width: min(680px, 100%); }
  h1 { font-size: 28px; margin: 0 0 4px; letter-spacing: -.02em; }
  p.sub { margin: 0 0 24px; color: #96a3bd; font-size: 15px; }
  .tag {
    display: inline-block; font-size: 12px; letter-spacing: .08em;
    text-transform: uppercase; color: #7dd3a0; border: 1px solid #2d4a3d;
    background: #14251d; border-radius: 999px; padding: 4px 10px; margin-bottom: 18px;
  }
  table { width: 100%; border-collapse: collapse; background: #16213a;
          border: 1px solid #253253; border-radius: 12px; overflow: hidden; }
  th, td { text-align: left; padding: 11px 14px; font-size: 14px;
           border-bottom: 1px solid #1f2b47; }
  tr:last-child th, tr:last-child td { border-bottom: 0; }
  th { color: #96a3bd; font-weight: 500; text-transform: capitalize; width: 46%; }
  td { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  footer { margin-top: 18px; font-size: 13px; color: #7b88a3; line-height: 1.5; }
  a { color: #7aa7ff; }
</style>
</head>
<body>
<main>
  <span class="tag">Ambiente efímero</span>
  <h1>Servicio de monitoreo de ejemplo</h1>
  <p class="sub">Node.js desplegado en Heroku. Cada ambiente responde con sus propios datos de ejecución.</p>
  <table>${filas}</table>
  <footer>
    Datos leídos de las variables de entorno del dyno. Endpoints:
    <a href="/health">/health</a> y <a href="/api/estado">/api/estado</a>.
  </footer>
</main>
</body>
</html>`;
};

const servidor = http.createServer((req, res) => {
  const ruta = new URL(req.url, `http://${req.headers.host}`).pathname;

  if (ruta === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ estado: 'ok', ...datos() }));
    return;
  }

  if (ruta === '/api/estado') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify(datos(), null, 2));
    return;
  }

  if (ruta === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(pagina());
    return;
  }

  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('No encontrado');
});

servidor.listen(PUERTO, () => {
  console.log(`Servidor escuchando en el puerto ${PUERTO}`);
});
