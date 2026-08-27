# 推し活オールインワン 現行仕様書

> このファイルは、推し活オールインワンの現在の実装状況・構成・仕様を記録する現行仕様書です。
> 今後の開発では、このファイルの内容を現行仕様の基準とします。
>
> 最終更新日：2026-08-27

---

## 1. プロジェクト概要

### 1.1 プロジェクト名

推し活オールインワン

### 1.2 概要

水瀬いのりさんのファン向けに、
ライブ・セトリ・参加履歴・支出・楽曲・推し情報などを
一元管理できるWebアプリ。

### 1.3 基本方針

* スマートフォンでの利用を前提とする
* シンプルで使いやすいUIを重視する
* 既存機能との連携を重視する
* 既存データを活用できる機能を優先する
* 管理コストが高い機能は無理に追加しない
* 無料での運用を前提とする
* 必要な業務データのみ保存する
* 操作履歴・アクセス履歴などのログ機能は実装しない

---

## 2. 開発環境・技術構成

### 2.1 Backend

* Python
* FastAPI
* Uvicorn

### 2.2 Template

* Jinja2
* Jinja2Templates

### 2.3 Database

* Supabase PostgreSQL
* psycopg

### 2.4 Authentication / Session

* Starlette SessionMiddleware
* セッションによるログイン状態管理

### 2.5 Frontend

* HTML
* CSS
* JavaScript

### 2.6 開発環境

* PyCharm
* Windows

### 2.7 UI方針

* スマートフォンファースト
* コンテンツ最大幅：約430px
* HachiMaruPop-Regular.ttf をUIフォントとして使用
* 共通CSSと機能別CSSを使い分ける

---

## 3. ディレクトリ構成

### 3.1 プロジェクト全体

現在のプロジェクト構成については、
`project_tree.txt` を基準とする。

### 3.2 Python構成

Python配下の詳細構成については、
`python_tree.txt` を基準とする。

### 3.3 基本構成

```text
python/
├── core/
├── models/
├── routers/
├── services/
└── ...

templates/
├── commons/
├── home/
├── admin/
└── ...

static/
├── css/
├── img/
└── fonts/

```

---

## 4. DB構成

### 4.1 DB

Supabase PostgreSQLを使用する。

DB接続は `python.core.database.get_connection()` を使用する。

### 4.2 DB設計の基本方針

* PostgreSQLを使用する
* 既存テーブルを利用できる場合は、新規テーブルを増やさない
* 論理削除を使用するテーブルでは `is_deleted` を使用する
* 公開・非公開を管理するデータでは `public_flag` または `is_public` を使用する
* 外部キーによるテーブル間の関連を維持する
* DB定義を変更する場合は、既存機能への影響を確認する
* 会場情報は `m_venue` で一元管理する
* ライブ・町民集会から会場情報を直接保持せず、`venue_id` によって `m_venue` を参照する

---

### 4.3 マスターテーブル

#### `m_system_setting`

システム設定を管理する。

主な用途：

* ユーザー登録設定などのシステム設定

登録可否の値：

* `0`：登録不可
* `1`：登録可能（通常）
* `2`：登録可能（招待限定）

---

#### `m_invitation_code`

招待コードを管理する。

主な項目：

* 招待コード
* 有効状態
* 最大利用回数
* 利用回数
* 有効期限
* 登録日時
* 更新日時

---

#### `m_user`

ユーザー情報を管理する。

主な項目：

* `user_id`
* `user_name`
* `password`
* `role`
* `profile_image`
* `member_since`
* `email`
* `gender`
* `birthday`
* `prefecture`
* `x_account`
* `instagram_account`
* `discord_account`
* `profile_message`
* `is_active`

`prefecture` は `m_prefecture.prefecture_code` を参照する。

---

#### `m_user_setting`

ユーザーごとの表示・利用設定を管理する。

`m_user.user_id` と1対1で関連する。

主な項目：

* `user_id`
* `font_id`
* `created_at`
* `updated_at`

現在管理している設定：

* UIフォント

`font_id` により、ユーザーが選択したUIフォントを管理する。

フォント未設定の場合はシステムのデフォルトフォントを使用する。

ログインユーザーの設定は `m_user_setting` に保存し、
ユーザーごとに独立して管理する。

未ログインユーザー（ゲスト）の設定はDBには保存せず、
セッション単位で管理する。

そのため、ゲスト利用時のフォント設定が
他のゲストユーザーや他のブラウザ・端末の設定によって
上書きされることはない。

---

#### `m_user_public_setting`

ユーザー情報の公開設定を管理する。

公開設定対象：

* 性別
* 誕生日
* 年齢
* 町民開始日
* 都道府県
* SNS
* ライブ
* 町民集会

公開設定値：

* `0`：非公開
* その他の値については現行実装を正とする

`m_user.user_id` と1対1で関連する。

---

#### `m_prefecture`

都道府県マスタ。

主な項目：

* `prefecture_code`
* `prefecture_name`
* `area_name`
* `display_order`
* `is_overseas`
* `is_active`

`0` は「未設定」、`99` は「海外」。

---

#### `m_venue`

ライブ・町民集会などで使用する会場情報を管理する。

会場情報はライブ・町民集会から分離して管理し、
会場名・住所・都道府県・緯度・経度などを一元管理する。

主な項目：

* `venue_id`
* `venue_name`
* `address`
* `prefecture_code`
* `latitude`
* `longitude`
* `public_flag`
* `is_deleted`

`prefecture_code` は `m_prefecture.prefecture_code` を参照する。

`is_deleted` により論理削除を管理する。

`public_flag` により公開・非公開を管理する。

会場情報を利用するテーブルでは `venue_id` を保持し、
`m_venue.venue_id` を外部キーとして参照する。

現在、以下のイベントで会場マスタを利用する。

* `m_live`
* `m_meeting`

将来的に天気予報などの会場情報を利用する機能についても、
`m_venue` に登録された住所・緯度・経度などを利用する。

---

#### `m_song`

楽曲情報を管理する。

主な項目：

* `song_id`
* `song_group_id`
* `song_name`
* `song_type`
* `release_date`
* `album_name`
* `display_order`
* `lyricist`
* `composer`
* `arranger`
* `tie_up`
* `youtube_url`
* `apple_music_url`
* `spotify_music_url`
* `is_public`
* `is_deleted`

`album_name` と `song_name` の組み合わせは一意。

`song_group_id` により同一楽曲のアルバム等によるグループ管理を行う。

`song_type` により楽曲の種別を管理する。

* `INORI`：水瀬いのり名義の楽曲
* `OTHER`：水瀬いのり名義以外の楽曲、カバー曲、町民集会等で歌唱されるその他の楽曲

既存の楽曲は `INORI` として扱う。

`m_setlist` から楽曲を参照する際は、`song_id` を使用する。

同一楽曲が複数の `m_song` レコードに存在する場合があるため、
楽曲一覧等で同一楽曲を1件として扱う必要がある場合は、
`song_name` を基準として重複をまとめる。

特にセトリ予測では、同じ楽曲名が複数表示されないようにする。

---

#### `m_live`

ライブ情報を管理する。

主な項目：

* `live_id`
* `live_name`
* `tour_name`
* `tour_order`
* `live_date`
* `venue_id`
* `blu_ray_url`
* `official_url`
* `public_flag`
* `is_deleted`

`venue_id` は `m_venue.venue_id` を参照する。

ライブの会場名・住所・都道府県などの情報は `m_venue` で管理する。

ライブ自身には会場情報を重複して保持しない。

---

#### `m_meeting`

町民集会情報を管理する。

主な項目：

* `meeting_id`
* `meeting_name`
* `meeting_date`
* `performance_type`
* `venue_id`
* `official_url`
* `public_flag`
* `is_deleted`

`venue_id` は `m_venue.venue_id` を参照する。

町民集会の会場名・住所・都道府県などの情報は `m_venue` で管理する。

町民集会自身には会場情報を重複して保持しない。

`performance_type` は以下の値を使用する。

* `DAY`：昼公演
* `NIGHT`：夜公演
* `PART1`：第1部
* `PART2`：第2部
* `PART3`：第3部

---

#### `m_meeting_guest`

町民集会ごとのゲスト情報を管理する。

1つの町民集会に対して複数のゲストを登録できる。

主な項目：

* `meeting_id`
* `guest_id`
* `guest_name`
* `display_order`
* `is_deleted`

`meeting_id` は `m_meeting.meeting_id` を参照する。

`display_order` によりゲストの表示順を管理する。

`is_deleted` により論理削除を管理する。

---

#### `m_setlist`

ライブ・町民集会などのセットリストを管理する。

イベント種別：

* `LIVE`
* `CHOMIN`

主な項目：

* `event_type`
* `event_id`
* `song_id`
* `song_order`
* `is_medley`
* `medley_order`

`event_type` と `event_id` により、ライブまたは町民集会のイベントを識別する。

`song_id` は `m_song.song_id` を参照する。

---

#### `m_expense_type`

ライブ・町民集会関連の費用種類を管理する。

現在の登録データ：

| コード | 名称 | 表示順 |
|---|---|---:|
| `ticket` | チケット代 | 1 |
| `transport` | 交通費 | 2 |
| `hotel` | 宿泊費 | 3 |
| `food` | 食費 | 4 |
| `goods` | グッズ | 5 |
| `other` | その他 | 6 |

---

#### `m_lost_item`

忘れ物チェックリストのマスタ。

現在の登録データ：

| 表示順 | 項目 |
|---:|---|
| 1 | チケット |
| 2 | スマートフォン |
| 3 | 財布 |
| 4 | 身分証 |
| 5 | ペンライト |
| 6 | タオル |
| 7 | 飲み物 |
| 8 | 双眼鏡 |
| 9 | 会員証 |

---

### 4.4 推し情報関連マスタ

#### `m_oshi_basic`

推しの基本情報を管理する。

現在は `oshi_id = 1` の1レコードのみを使用する。

主な項目：

* `oshi_id`
* `oshi_name`
* `birthday`
* `voice_actor_debut_date`
* `singer_debut_date`
* `profile_image`
* `profile_message`

---

#### `m_oshi_anniversary`

推しに関する記念日を管理する。

主な項目：

* `anniversary_id`
* `anniversary_name`
* `anniversary_date`
* `description`
* `display_order`
* `public_flag`
* `is_deleted`

---

#### `m_oshi_program`

ラジオ・番組情報を管理する。

番組種別：

* `RADIO`
* `TV`
* `WEB`
* `OTHER`

主な項目：

* `program_id`
* `program_name`
* `program_type`
* `start_date`
* `end_date`
* `official_url`
* `description`
* `display_order`
* `public_flag`
* `is_deleted`

---

#### `m_oshi_work`

出演作品を管理する。

作品種別：

* `ANIME`
* `MOVIE`
* `GAME`
* `DRAMA`
* `OTHER`

放送時期：

* `SPRING`
* `SUMMER`
* `AUTUMN`
* `WINTER`

主な項目：

* `work_id`
* `work_name`
* `work_type`
* `character_name`
* `release_date`
* `official_url`
* `description`
* `display_order`
* `public_flag`
* `is_deleted`
* `broadcast_year`
* `broadcast_season`

---

#### `m_oshi_official_link`

公式リンクを管理する。

主な項目：

* `link_id`
* `link_name`
* `url`
* `icon`
* `description`
* `display_order`
* `public_flag`
* `is_deleted`

---

### 4.5 推し情報とライブ情報の連携

推し情報トップから既存のライブ機能へ遷移できる。

導線：

```text
推し情報
  ↓
ライブ
  ↓
ライブ一覧
  ↓
ライブ詳細
  ↓
セットリスト
```
---

### 4.6 トランザクションテーブル

#### `t_live_record`

ユーザーのライブ参加記録を管理する。

主な項目：

* `record_id`
* `user_id`
* `live_id`
* `seat_info`
* `memo`

`user_id` と `live_id` の組み合わせは一意。

---

#### `t_live_expense`

ライブ関連の支出を管理する。

主な項目：

* `expense_id`
* `user_id`
* `live_id`
* `expense_type_id`
* `amount`
* `memo`

`amount` は0以上。

---

#### `t_meeting_record`

ユーザーの町民集会参加記録を管理する。

主な項目：

* `record_id`
* `user_id`
* `meeting_id`
* `seat_info`
* `memo`

`user_id` と `meeting_id` の組み合わせは一意。

---

#### `t_meeting_expense`

町民集会関連の支出を管理する。

主な項目：

* `expense_id`
* `user_id`
* `meeting_id`
* `expense_type_id`
* `amount`
* `memo`

`amount` は0以上。

---

#### `t_setlist_prediction`

ユーザーが作成した予測セトリを管理する。

主な項目：

* `prediction_id`
* `user_id`
* `live_id`

`user_id` と `live_id` の組み合わせは一意。

予測セトリはライブを対象とし、町民集会を対象としない。

---

#### `t_setlist_prediction_song`

予測セトリに登録する楽曲を管理する。

主な項目：

* `prediction_id`
* `song_id`
* `song_order`
* `is_medley`
* `medley_order`

`prediction_id` と `song_id` の組み合わせは一意。

予測セトリで選択できる楽曲は、`m_song` の以下の条件を満たす楽曲を対象とする。

* `is_deleted = FALSE`
* `is_public = TRUE`
* `song_type = 'INORI'`

`OTHER` の楽曲はセトリ予測の選択対象から除外するため、
町民集会等で使用される楽曲は対象外となる。

`m_setlist` への登録有無は選択条件としないため、
まだLIVEのセトリに登録されていない新曲も対象とする。

同一楽曲について複数の `m_song` レコードが存在する場合は、
`song_group_id` 単位でまとめて表示する。

楽曲の表示順は、以下の順とする。

1. `release_date` 昇順
2. `display_order` 昇順

---

#### `t_live_user`

ユーザーとライブの参加状況を管理する。

主な項目：

* `user_id`
* `live_id`
* `is_join`

`user_id` と `live_id` の組み合わせを主キーとする。

---

#### `t_meeting_user`

ユーザーと町民集会の参加状況を管理する。

主な項目：

* `user_id`
* `meeting_id`
* `is_join`

`user_id` と `meeting_id` の組み合わせを主キーとする。

---

#### `t_user_lost_item`

ユーザーごとの忘れ物チェック項目を管理する。

主な項目：

* `user_lost_item_id`
* `user_id`
* `lost_item_id`
* `item_name`
* `is_checked`

`lost_item_id` は `m_lost_item.lost_item_id` を参照する。

---

#### `t_inquiry`

問い合わせ情報を管理する。

問い合わせ種別：

* `INQUIRY`：問い合わせ
* `REQUEST`：要望
* `BUG`：不具合

ステータス：

* `UNRESOLVED`：未対応
* `IN_PROGRESS`：対応中
* `RESOLVED`：解決済み

主な項目：

* `inquiry_id`
* `user_id`
* `inquiry_type`
* `subject`
* `email`
* `message`
* `status`
* `admin_memo`

`INQUIRY` の場合はメールアドレスが必須。

---

### 4.7 セトリ予測

ライブごとにユーザーが予測したセットリストを登録できる。

#### 対象イベント

セトリ予測の対象は `m_live` に登録されているライブのみとする。

町民集会（`m_meeting`）はセトリ予測の対象外とする。

#### 対象楽曲

セトリ予測で選択できる楽曲は、
`m_setlist` に以下の条件で登録されている楽曲とする。

```text
event_type = 'LIVE'
```
---

## 5. Router構成

### 5.1 Routerの基本方針

RouterはFastAPIの `APIRouter` を使用して機能ごとに分割する。

基本的な構成は、

```text
Router
 ↓
Model / Service
 ↓
Database
```

---

## 6. Model / Service構成

### 6.1 基本方針

DBへのアクセスはModelにまとめる。

Routerから直接SQLを実行せず、原則としてModelを経由してDBへアクセスする。

複数のModelを組み合わせた処理や、画面表示だけでは完結しない業務処理はServiceにまとめる。

基本的な役割は以下のとおり。

```text
Router
 ↓
Service
 ↓
Model
 ↓
Database
```

---

## 7. Template構成

### 7.1 基本方針

HTMLテンプレートはJinja2を使用する。

テンプレートは `templates/` 配下に機能単位で配置する。

基本的に、

```text
Router
 ↓
Template
```
