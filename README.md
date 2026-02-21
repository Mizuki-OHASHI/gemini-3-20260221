# Ghost Whisper (仮)

恋人を殺した犯人を、幽霊となって現れた恋人のヒントを頼りに突き止める謎解きゲーム。

## コンセプト

- 恋人が殺害されるところからストーリーが始まる
- 自宅に幽霊となって現れた恋人は喋れないが、指さしなどのジェスチャーでヒントをくれる
- プレイヤーは自宅をカメラで撮影し、Gemini の画像生成 (NanoBanana) で幽霊の恋人が合成された画像を受け取る
- 幽霊のヒントを元に、テキスト入力で推理したり、別の場所/物を撮影して調査を進める
- コンテキスト画面で生前の二人のストーリーを閲覧できる
- 最終的に犯人を特定するとクリア

### ゲームループ

```
撮影 → Gemini 画像生成 (幽霊合成) → ヒント表示
  ↓                                    ↓
次の撮影 ←────────────────── テキスト入力で推理
  ↓
(繰り返し → 犯人特定でクリア)
```

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python 3.12, uv) |
| AI | Gemini API (画像生成 / Live API) |
| DB | Firestore |
| Storage | Cloud Storage |
| Infra | Cloud Run |
| API 型生成 | Orval (OpenAPI → TypeScript) |

## プロジェクト構成

```
.
├── api/                  # FastAPI バックエンド
│   ├── app/
│   │   ├── main.py       # FastAPI エントリーポイント
│   │   ├── config.py     # 環境変数
│   │   ├── gemini.py     # Gemini クライアント
│   │   ├── firebase.py   # Firebase 初期化
│   │   ├── schemas.py    # Pydantic モデル
│   │   └── routers/
│   │       ├── game.py   # ゲーム CRUD
│   │       ├── live.py   # Gemini Live WebSocket
│   │       └── storage.py# ファイルアップロード
│   ├── Dockerfile
│   └── pyproject.toml
├── web/                  # React フロントエンド
│   └── src/
│       ├── App.tsx       # ルーティング
│       ├── pages/
│       │   ├── MainPage.tsx    # カメラ + メイン画面
│       │   └── ContextPage.tsx # ストーリー閲覧
│       ├── hooks/
│       │   └── useCamera.ts
│       └── api/          # Orval 自動生成
└── gemini3.code-workspace
```

## セットアップ

### 前提

- Python 3.12+
- [Bun](https://bun.sh/)
- [uv](https://docs.astral.sh/uv/)
- GCP プロジェクト (Firestore, Cloud Storage 有効化済み)
- Gemini API Key

### API

```bash
cd api
cp .env.example .env
# .env を編集: GEMINI_API_KEY, FIREBASE_STORAGE_BUCKET を設定
# Firebase のサービスアカウントキーを配置

uv sync
uv run uvicorn app.main:app --reload
```

### Web

```bash
cd web
bun install
bun dev
```

## デプロイ

API は Cloud Run にデプロイ:

```bash
cd api
gcloud run deploy game-api \
  --source . \
  --set-env-vars GEMINI_API_KEY=xxx,FIREBASE_STORAGE_BUCKET=xxx
```
