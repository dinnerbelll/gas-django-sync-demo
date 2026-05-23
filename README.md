# coach_demo

Google Form -> Google Spreadsheet -> Google Apps Script -> Django API -> PostgreSQL の同期を確認するための小規模デモアプリ。

Googleフォームの回答をスプレッドシートだけでなくWeb上のPostgreSQLにも蓄積できることを開発者向けに確認する目的のもの。

## 使用技術

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL
- Docker / docker-compose
- Django Admin

## セットアップ

`.env.example` をコピーして `.env` を作成

```bash
cp .env.example .env
```

コンテナを起動

```bash
docker compose up --build
```

## マイグレーション

別ターミナルで以下を実行

```bash
docker compose exec web python manage.py migrate
```

## 管理ユーザー作成

```bash
docker compose exec web python manage.py createsuperuser
```

管理画面は以下で確認可能↓

```text
http://localhost:8000/admin/
```

Adminでは `DemoRequest` の `id`, `student_name`, `submitted_at`, `created_at` を一覧表示している。

## API

### POST /api/demo/requests/

Google Apps Script などからJSONをPOSTすると、PostgreSQLへ保存する

認証には `X-DEMO-API-KEY` ヘッダーを使用。値は `.env` の `DEMO_API_KEY` と一致させる。

```bash
curl -X POST http://localhost:8000/api/demo/requests/ \
  -H "Content-Type: application/json" \
  -H "X-DEMO-API-KEY: your-secret-key" \
  -d '{
    "student_name": "あいうえお",
    "problem_text": "敵を見る",
    "submitted_at": "2026-05-22T18:30:00+09:00",
    "raw_payload": {
      "student_name": "あいうえお",
      "problem_text": "敵を見る"
    }
  }'
```

成功時レスポンス例

```json
{
  "ok": true,
  "id": 1
}
```

API Keyが不正または未指定の場合は `403 Forbidden` を返す。

## Google Apps Script からの接続例

Google Form送信時にDjango APIへPOSTするサンプル。

```javascript
function onFormSubmit(e) {
const values = e.namedValues;

const payload = {
student_name: values["生徒名"][0],
problem_text: values["課題"][0],
submitted_at: new Date().toISOString(),
raw_payload: values
};

const options = {
method: "post",
contentType: "application/json",
headers: {
"X-DEMO-API-KEY": "your-secret-key"
},
payload: JSON.stringify(payload),
muteHttpExceptions: true
};

UrlFetchApp.fetch(
"http://localhost:8000/api/demo/requests/",
options
);
}
```

Google Apps Script はGoogle側のサーバーで実行されるため、実際にGASからローカルPCの `localhost:8000` へ直接アクセスすることはできない。ローカル検証では RailwayでDjango APIを一時公開し、URLを `https://.../api/demo/requests/` に変更する。

## Railwayで公開する場合

このリポジトリにはRailway向けの `railway.json` を含めている。RailwayではDockerfileでビルドし、GunicornでDjangoを起動する。Django Adminの静的ファイルはWhiteNoiseで配信する。

### Railway側でやること

1. Railwayで新規Projectを作成
2. GitHubリポジトリ、またはRailway CLIからこのDjangoアプリを追加
3. 同じProject内にPostgreSQL serviceを追加
4. Djangoアプリ側のVariablesにPostgreSQLの `DATABASE_URL` を参照できるように設定
5. Djangoアプリ側のVariablesに必要な環境変数を追加
6. Deployを実行

RailwayのPostgreSQLを追加すると、DB接続用の `DATABASE_URL` を使える。DjangoアプリのVariablesで `DATABASE_URL` が設定されていることを確認する。

最低限必要なVariables:

```text
DJANGO_SECRET_KEY=本番用の長いランダム文字列
DJANGO_DEBUG=false
DEMO_API_KEY=your-secret-key
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

Railwayの公開ドメインを使う場合、`RAILWAY_PUBLIC_DOMAIN` から `ALLOWED_HOSTS` と `CSRF_TRUSTED_ORIGINS` へ自動反映される。独自ドメインや手動指定を使う場合は以下も追加する。

```text
DJANGO_ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
```

`railway.json` の `preDeployCommand` で、デプロイ時に以下が実行される。

```bash
python manage.py migrate
```

手動でマイグレーションを実行する場合はRailway CLIで以下を実行する。

```bash
railway run python manage.py migrate
```

管理ユーザーを作成する。

```bash
railway run python manage.py createsuperuser
```

ヘルスチェック用URL

```text
https://your-app-name.up.railway.app/health/
```

GASから接続する場合は、送信先をRailwayのURLに変更する。

```javascript
UrlFetchApp.fetch(
"https://your-app-name.up.railway.app/api/demo/requests/",
options
);
```

## 開発メモ

- モデル: `requests_demo.models.DemoRequest`
- API: `requests_demo.views.DemoRequestCreateAPIView`
- 認証: `requests_demo.permissions.HasDemoApiKey`
- DB接続: 環境変数 `DATABASE_URL`

ここから色々広げるかもしれないのでSerializer、View、URLをアプリ内で分離済。
