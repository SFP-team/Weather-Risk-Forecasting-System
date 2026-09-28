// Local-only static preview and fixed-destination proxy. Never accepts a target URL.
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const root=path.resolve('dist');
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.json':'application/json','.gz':'application/gzip','.png':'image/png','.svg':'image/svg+xml','.txt':'text/plain; charset=utf-8'};
http.createServer(async(req,res)=>{
  if(!['127.0.0.1:5173','localhost:5173'].includes(req.headers.host)){res.writeHead(403);return res.end('Forbidden host')}
  if(req.method!=='GET'){res.writeHead(405);return res.end()}
  if(req.headers.origin&&!['http://127.0.0.1:5173','http://localhost:5173'].includes(req.headers.origin)){res.writeHead(403);return res.end()}
  if(req.url.startsWith('/api/')){
    const upstream=http.get({hostname:'127.0.0.1',port:8787,path:req.url,timeout:95000},r=>{res.writeHead(r.statusCode,{'Content-Type':'application/json','Cache-Control':'no-store'});r.pipe(res)});
    // `code` separates a missing archive connection from the archive's own 503 (another analysis is running).
    upstream.on('timeout',()=>upstream.destroy());upstream.on('error',()=>{if(!res.headersSent)res.writeHead(503,{'Content-Type':'application/json'});res.end(JSON.stringify({error:'Private archive connection is unavailable',code:'archive_unavailable'}))});return;
  }
  try{const p=path.resolve(root,'.'+decodeURIComponent(req.url.split('?')[0]==='/'?'/index.html':req.url.split('?')[0]));if(!p.startsWith(root+path.sep))throw Error();const body=await fs.readFile(p);res.writeHead(200,{'Content-Type':types[path.extname(p)]??'application/octet-stream','Cache-Control':'no-store'});res.end(body)}catch{res.writeHead(404);res.end('Not found')}
}).listen(5173,'127.0.0.1',()=>console.log('Local: http://127.0.0.1:5173/'));
