# Applications Web Hostinger - Guide technique pour développeurs

> Environnement cible : **Business Web Hosting** · Node.js (Next.js inclus) · Python · MySQL/MariaDB

---

## 🏗️ Logique générale de l'environnement

L'environnement **Applications Web** de Hostinger repose sur un hébergement mutualisé LiteSpeed avec un système de **Managed Web Apps** - c'est-à-dire que tu n'as pas accès root, mais tu disposes d'un environnement d'exécution géré, distinct d'un simple hébergement PHP.

**Ce que ça implique concrètement :**

- Chaque app tourne dans un **process Node.js ou Python isolé**, exposé derrière un reverse proxy LiteSpeed.
    
- Ton app écoute sur un **port local assigné** (variable `PORT` injectée automatiquement) - tu ne choisis pas le port toi-même.
    
- Le process est géré par un **supervisor interne** : il redémarre automatiquement en cas de crash.
    
- Le système de fichiers est **persistant** (contrairement à Docker/Heroku) - les fichiers écrits sur disque survivent aux redémarrages.
    
- Tu n'as **pas besoin de configurer un reverse proxy** toi-même - LiteSpeed fait le pont entre le domaine et ton process.
    

---

## 🚀 Déploiement d'une application web

### Via hPanel - workflow standard

1. Dans hPanel → **Hébergement → Applications Web → Créer une application**
    
2. Choisis le runtime : **Node.js** (versions 18, 20, 22 disponibles) ou **Python** (3.10, 3.11…)
    
3. Connecte ton dépôt **Git** (GitHub, GitLab, Bitbucket) ou déploie via **SFTP/SSH**
    
4. Définis le **fichier d'entrée** (entry point) et la commande de démarrage
    

### Commandes de démarrage typiques

**Next.js (mode production) :**

```bash
npm run build && npm run start
```

> ⚠️ Le build doit être lancé **avant** le start. Si tu utilises le CI/CD Git automatique, place le build dans un script `postinstall` ou configure une **build command** séparée dans hPanel.

**Node.js classique (Express, Fastify…) :**

```bash
node server.js
```

ou avec PM2 si disponible :

```bash
npm install && node index.js
```

**Python (FastAPI, Flask, Django) :**

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
# ou
gunicorn app:application --bind 0.0.0.0:$PORT
```

### Point critique - le PORT

Ton app **doit écouter sur `process.env.PORT`** (Node.js) ou `$PORT` (Python). Le port est injecté par la plateforme.

```js
// Node.js / Express
const PORT = process.env.PORT || 3000;
app.listen(PORT);

python
# FastAPI / uvicorn - passer PORT via variable d'env
import os
port = int(os.environ.get("PORT", 8000))
```

---

## ⚙️ Variables d'environnement

### Configuration dans hPanel

Onglet **Applications Web → ton app → Variables d'environnement**. Chaque paire clé/valeur est injectée dans le process au démarrage.

### Bonnes pratiques

- **Ne jamais committer** `.env` ou tout fichier contenant des secrets dans Git.
    
- Utilise `.env.local` (Next.js) ou `.env` **uniquement en local** pour le dev.
    
- En production, toutes les valeurs sensibles passent exclusivement par hPanel.
    
- En Next.js, les variables accessibles côté **serveur uniquement** n'ont pas besoin du préfixe `NEXT_PUBLIC_`. Garde ce préfixe **uniquement** pour ce qui doit être exposé au navigateur.
    

```bash
# Exemples de variables à définir dans hPanel
DATABASE_URL=mysql://user:password@localhost:3306/mydb
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://monsite.fr/api
JWT_SECRET=un_secret_long_et_aleatoire
```

### Lecture dans le code

```js
// Next.js / Node.js
const dbUrl = process.env.DATABASE_URL;
const isProduction = process.env.NODE_ENV === 'production';

python
import os
db_url = os.environ.get("DATABASE_URL")
```

> 💡 Tout changement de variable d'environnement dans hPanel nécessite un **redémarrage de l'app** pour être pris en compte.

---

## 🗄️ Connexion MySQL / MariaDB

### Créer la base de données

Dans hPanel → **Bases de données → MySQL** → créer une base + un utilisateur avec tous les droits sur cette base.

L'host de connexion en interne est **`localhost`** (ou `127.0.0.1`) - pas un host externe.

### Node.js avec `mysql2`

```js
// lib/db.js
import mysql from 'mysql2/promise';

const pool = mysql.createPool({
  host: process.env.DB_HOST,       // 'localhost'
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});

export default pool;
```

### Next.js - attention aux connexions en Serverless/Edge

En Next.js App Router avec des Route Handlers, instancie le pool **une seule fois** via un singleton pour éviter les connexions multiples lors des hot-reloads :

```js
// lib/db.js
let pool;

if (!global._mysqlPool) {
  global._mysqlPool = mysql.createPool({ /* config */ });
}
pool = global._mysqlPool;

export default pool;
```

### Python avec `PyMySQL` ou `SQLAlchemy`

```python
# SQLAlchemy (recommandé pour Django/FastAPI)
from sqlalchemy import create_engine

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

python
# PyMySQL direct
import pymysql
conn = pymysql.connect(
    host=os.environ.get("DB_HOST"),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME"),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
```

---

## 📁 Stockage des fichiers uploadés

### Système de fichiers local - ce qui fonctionne

Contrairement à des plateformes éphémères (Vercel, Railway par défaut), le disque est **persistant** ici. Tu peux écrire des fichiers et les retrouver après un redémarrage.

**Chemin recommandé pour les uploads :**

```plaintext
/home/u582943705/domains/mondomaine.fr/public_html/uploads/
```

ou, dans le répertoire de ton app :

```plaintext
/home/u582943705/applications/mon-app/public/uploads/
```

> ⚠️ Ne jamais écrire en dehors du répertoire `home` de ton compte - tu n'as pas les droits et ça ne persistera pas.

### Node.js avec `multer`

```js
import multer from 'multer';
import path from 'path';

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(process.cwd(), 'public', 'uploads'));
  },
  filename: (req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    cb(null, `${unique}${path.extname(file.originalname)}`);
  },
});

export const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB max
});
```

### Python avec FastAPI

```python
from fastapi import UploadFile
import shutil, os

UPLOAD_DIR = os.path.join(os.getcwd(), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload(file: UploadFile):
    dest = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return dest
```

### Droits d'écriture

```bash
# Via SSH - s'assurer que le dossier uploads est accessible en écriture
chmod 755 public/uploads
# ou 775 si l'app tourne sous un user différent du propriétaire
```

### Pour les gros volumes ou le multi-instance

Le disque local est limité et ne scale pas si tu as plusieurs instances. Dans ce cas, passe sur un **stockage objet externe** (Cloudflare R2, Backblaze B2, AWS S3) et stocke les URLs en base de données. L'implémentation reste identique côté code - tu remplaces juste le `diskStorage` par un client S3.

---

## 🔒 Sécurité, persistance et droits

### Sécurité applicative

|Pratique|Détail|
|---|---|
|**HTTPS forcé**|Activé automatiquement via Let's Encrypt - vérifie la redirection HTTP→HTTPS dans hPanel|
|**Variables sensibles**|Uniquement via hPanel, jamais dans le code source|
|**SQL Injection**|Toujours des requêtes paramétrées - jamais de concaténation de strings SQL|
|**Headers de sécurité**|Ajoute `helmet` (Node.js) ou les middlewares équivalents en Python|
|**Rate limiting**|Implémente `express-rate-limit` ou `slowapi` (FastAPI) sur les endpoints exposés|
|**Uploads**|Valide le MIME type côté serveur, pas seulement l'extension|

### Persistance des données

- **Base de données** → seule source de vérité pour les données structurées. Toujours.
    
- **Fichiers uploadés** → disque local (persistant) ou stockage objet externe.
    
- **Sessions** → stocke-les en base ou Redis, pas en mémoire (un redémarrage vide tout).
    
- **Cache** → même chose : Redis ou cache fichier, pas en mémoire process.
    

### Droits d'écriture - règle simple

```plaintext
Seuls /home/u582943705/ et ses sous-répertoires sont writable.
Tout le reste → permission denied.
```

Ton répertoire de travail effectif est dans `/home/u582943705/applications/` ou `/home/u582943705/domains/`. Configure tous tes chemins relatifs à `process.cwd()` (Node) ou `os.getcwd()` (Python) pour rester portable.

---

## 🔄 Mise en production et redémarrage

### Checklist avant go-live

- [ ] `NODE_ENV=production` défini dans les variables d'environnement
    
- [ ] Build de production exécuté (`next build`, `vite build`…)
    
- [ ] Secrets hors du repo Git (`.gitignore` à jour)
    
- [ ] Base de données migrée (migrations Prisma, Alembic, Sequelize…)
    
- [ ] Dossier uploads créé avec les bons droits
    
- [ ] Redirection HTTPS active
    

### Redémarrage de l'application

Depuis hPanel → **Applications Web → ton app → Redémarrer**.

Via SSH si disponible :

```bash
# Hostinger injecte un script de gestion - vérifie avec :
pm2 restart all
# ou
systemctl restart ton-app  # selon la configuration
```

> 💡 Tout changement de variable d'environnement, de fichier de config, ou de dépendance nécessite un redémarrage explicite. Le supervisor ne détecte pas les changements automatiquement (hors mode watch dev).

### Logs applicatifs

```bash
# Via SSH
tail -f ~/logs/error.log
tail -f ~/logs/access.log

# Ou dans hPanel → Applications Web → Logs
```

Redirige tes logs applicatifs vers `stdout`/`stderr` - ils sont capturés automatiquement par la plateforme et accessibles depuis hPanel.

---

## ⚡ Points d'attention spécifiques Next.js

- **Static Export (`output: 'export'`)** - si tu n'as pas besoin du SSR, génère un export statique servi directement sans process Node.
    
- **App Router + Server Actions** - ça fonctionne, mais assure-toi que le pool de connexions DB est un singleton (cf. section DB).
    
- **`next.config.js` - `output: 'standalone'`** - recommandé en production sur cet environnement : réduit drastiquement la taille du build déployé.
    

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
};

export default nextConfig;
```
