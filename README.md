# GoogleスプシとWeb上DBの同期デモ

Google Form の回答を、 **Google スプレッドシート** と **Web上のデータベース（Railwayでデプロイ）** の両方に蓄積するデモ。
FormとDBの仲介にWebアプリケーションフレームワークであるDjangoを使用。
大型ゲームコーチングコミュニティでの情報管理用に試作。

## デモ URL

| 用途 | URL |
|---|---|
| Google Form（回答送信） | https://forms.gle/NCXtchA7FdCB5tN5A |
| Django 管理画面（DB 確認） | https://gas-django-sync-demo-production.up.railway.app/admin/ |

管理画面のログイン情報は別途共有。

## 仕組み

```text
Google Form 送信
    ├─→ Google スプレッドシート（自動保存）
    └─→ Google Apps Script（onFormSubmit）
            └─→ Django API（Railway）
                    └─→ PostgreSQL（Railway）
```

Google Formから情報を送信すると、スプレッドシートへの保存に加えて、Apps ScriptがRailway上のAPIを叩き、同じ内容がWeb上のDBにも保存される。
本格的にコミュニティ全体の情報を移そうとしたらRailwayのHobbyプランにする必要があるかもしれない（月700-800円くらいかかる）。

## 動作確認手順

1. [Google Form](https://forms.gle/NCXtchA7FdCB5tN5A) を開き、1件回答を送信する
2. リンクされた Google スプレッドシートに行が追加されることを確認する
3. [Django 管理画面](https://gas-django-sync-demo-production.up.railway.app/admin/) にログインする
4. **Demo requests**（`DemoRequest`）に、送信した **生徒の名前** と同じレコードがあることを確認する

3つとも一致すれば、デモは正常動作。

---

## GAS 側の再現手順

自分の Google Form + スプレッドシート + Apps Script で同じ仕組みを再現する場合は、以下↓

**前提:** Railway上のDjangoAPIはすでに公開済み。GASからは次のURLにPOST。

```text
https://gas-django-sync-demo-production.up.railway.app/api/demo/requests/
```

再現実験する場合API キー（`DEMO_API_KEY`）は別途共有します。後で設定に必要。

### 1. Google Form を用意する

[デモ Form](https://forms.gle/NCXtchA7FdCB5tN5A) と同じ構成にする。

### 2. Formをスプレッドシートにリンクする

### 3. Apps Script を設定する

Apps Scriptのデータ送信部分は以下：

```javascript
const API_URL = "https://gas-django-sync-demo-production.up.railway.app/api/demo/requests/";

function onFormSubmit(e) {
  const API_KEY = PropertiesService.getScriptProperties().getProperty("DEMO_API_KEY");

  if (!API_KEY) {
    throw new Error("DEMO_API_KEY が Script Properties に設定されていません");
  }

  const values = e.namedValues;

  const studentName = values["生徒の名前"] ? values["生徒の名前"][0] : null;
  const problemText = values["課題"] ? values["課題"][0] : null;

  if (!studentName || !problemText) {
    throw new Error(
      "Form の項目名が一致していません。実際のキー: " + Object.keys(values).join(", ")
    );
  }

  const payload = {
    student_name: studentName,
    problem_text: problemText,
    submitted_at: new Date().toISOString(),
    raw_payload: values,
  };

  const options = {
    method: "post",
    contentType: "application/json",
    headers: { "X-DEMO-API-KEY": API_KEY },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  };

  const response = UrlFetchApp.fetch(API_URL, options);
  const status = response.getResponseCode();
  const body = response.getContentText();

  Logger.log("status: " + status);
  Logger.log("body: " + body);

  if (status !== 201) {
    throw new Error("API error: status=" + status + " body=" + body);
  }
}

function testOnFormSubmit() {
  onFormSubmit({
    namedValues: {
      "生徒の名前": ["テスト太郎"],
      "課題": ["テスト課題"],
      "タイムスタンプ": ["2026/05/24 12:00:00"],
    },
  });
}
```

### 4. Script Properties を設定する

Apps Script → **プロジェクトの設定** → **スクリプト プロパティ** に追加

| 名前 | 値 |
|---|---|
| `DEMO_API_KEY` | 別途共有の API キー |

### 5. トリガーを設定する

Apps Script 左メニュー **トリガー** → **トリガーを追加**

| 項目 | 値 |
|---|---|
| 実行する関数 | `onFormSubmit` |
| デプロイ時に実行 | `Head` |
| イベントのソース | スプレッドシートから |
| イベントの種類 | フォーム送信時 |
| エラー通知設定 | すぐに通知を受け取る（推奨） |

以下の権限を許可する：

- Google スプレッドシートの表示・編集
- Google フォームの表示・管理（Form 連携時）
- 外部サービスへの接続（Railway API への POST）

### 6. 動作テスト

#### 手動テスト（GAS エディタ）

1. 関数プルダウンで `testOnFormSubmit` を選択
2. **実行**
3. **実行数** のログで `status: 201` を確認

#### 通しテスト（Form 送信）

1. Form から1件送信
2. スプレッドシートに行が増える
3. [管理画面](https://gas-django-sync-demo-production.up.railway.app/admin/) の **DemoRequest** に同じ内容がある

---

## API 仕様（参考）

### POST /api/demo/requests/

| 項目 | 内容 |
|---|---|
| URL | `https://gas-django-sync-demo-production.up.railway.app/api/demo/requests/` |
| 認証 | リクエストヘッダー `X-DEMO-API-KEY` |
| Content-Type | `application/json` |

リクエスト例:

```json
{
  "student_name": "テスト太郎",
  "problem_text": "動作確認",
  "submitted_at": "2026-05-24T12:00:00+09:00",
  "raw_payload": {}
}
```

成功時レスポンス:

```json
{
  "ok": true,
  "id": 1
}
```

---

## 仕様メモ

- モデル: `requests_demo.models.DemoRequest`
- API: `requests_demo.views.DemoRequestCreateAPIView`
- 認証: `requests_demo.permissions.HasDemoApiKey`
- DB 接続: 環境変数 `DATABASE_URL`
