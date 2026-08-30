# 推し活オールインワン 現行仕様書

> このファイルは、推し活オールインワンの現在の実装状況・構成・仕様を記録する現行仕様書です。
> 今後の開発では、このファイルの内容を現行仕様の基準とします。
>
> 最終更新日：2026-08-30

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
* ユーザー登録は常時可能とする
* 招待コードによる登録制限は設けない

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

### 2.7 外部API

* Open-Meteo Weather API
* 会場の緯度・経度を使用して天気予報を取得する
* 天気予報は開催予定イベントの表示に使用する

### 2.8 UI方針

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

# 4. DB構成

## 4.1 DB

Supabase PostgreSQLを使用する。

DB接続は `python.core.database.get_connection()` を使用する。

## 4.2 DB設計の基本方針

* PostgreSQLを使用する
* 既存テーブルを利用できる場合は、新規テーブルを増やさない
* 論理削除を使用するテーブルでは `is_deleted` を使用する
* 公開・非公開を管理するデータでは `public_flag` または `is_public` を使用する
* 外部キーによるテーブル間の関連を維持する
* DB定義を変更する場合は、既存機能への影響を確認する
* 会場情報は `m_venue` で一元管理する
* ライブ・町民集会から会場情報を直接保持せず、`venue_id` によって `m_venue` を参照する

---

## 4.3 ユーザー関連テーブル

### `m_user`

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

### ユーザー登録

現在、ユーザー登録は常時可能とする。

* 招待コード不要
* 招待制なし
* 登録停止機能なし
* 登録時の特別なシステム設定は使用しない

以前使用していた `m_system_setting` および `m_invitation_code` は
現行仕様では使用しない。

---

### `m_user_setting`

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

### `m_user_public_setting`

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

### ゲスト利用

未ログイン状態でも、ゲストとしてホーム画面を利用できる。

ゲスト利用では、ログインユーザーと同様に一部の機能を利用できる。

ゲスト利用時に作成・変更した個人データは、
ゲスト用のCookie／Sessionに紐付けて保持する。

そのため、

* 同一ブラウザ
* 同一Cookie／Session

が維持されている間は、ゲスト利用時のデータを継続して利用できる。

Cookie／Sessionがクリアされた場合、
ゲストとして保持していたデータも利用できなくなる。

ゲストデータは永続的なユーザーアカウントのデータとして扱わない。

また、ゲストユーザーについては、
最終利用から一定期間経過した場合に不要なデータを削除する
自動削除処理を設ける。

---

## 4.4 マスターテーブル

### `m_prefecture`

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

### `m_venue`

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

### `m_song`

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
`song_name` または `song_group_id` を基準として重複をまとめる。

特にセトリ予測では、同じ楽曲が複数表示されないようにする。

---

### `m_live`

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

### `m_meeting`

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

### `m_meeting_guest`

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

### `m_setlist`

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

`event_type` と `event_id` により、
ライブまたは町民集会のイベントを識別する。

`song_id` は `m_song.song_id` を参照する。

---

### `m_expense_type`

ライブ・町民集会関連の費用種類を管理する。

現在の登録データ：

| コード         | 名称    | 表示順 |
| ----------- | ----- | --: |
| `ticket`    | チケット代 |   1 |
| `transport` | 交通費   |   2 |
| `hotel`     | 宿泊費   |   3 |
| `food`      | 食費    |   4 |
| `goods`     | グッズ   |   5 |
| `other`     | その他   |   6 |

---

### `m_lost_item`

忘れ物チェックリストのマスタ。

現在の登録データ：

| 表示順 | 項目      |
| --: | ------- |
|   1 | チケット    |
|   2 | スマートフォン |
|   3 | 財布      |
|   4 | 身分証     |
|   5 | ペンライト   |
|   6 | タオル     |
|   7 | 飲み物     |
|   8 | 双眼鏡     |
|   9 | 会員証     |

---

## 4.5 推し情報関連マスタ

### `m_oshi_basic`

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

### `m_oshi_anniversary`

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

### `m_oshi_program`

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

### `m_oshi_work`

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

### `m_oshi_official_link`

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

## 4.6 推し情報とライブ情報の連携

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

## 4.7 ワークテーブル

### `w_weather_forecast`

ライブ・町民集会の開催予定に対する天気予報を一時的に保持する。

Open-Meteo Weather APIから取得した天気予報を、
会場単位・予報日単位で保存する。

主な項目：

* `forecast_id`
* `venue_id`
* `forecast_date`
* `weather`
* `created_at`
* `updated_at`

`venue_id` は `m_venue.venue_id` を参照する。

`venue_id` と `forecast_date` の組み合わせは一意とする。

天気情報はJSON形式で `weather` に保存する。

保存する主な情報：

* 日付
* 曜日
* 天気アイコン
* 天気名称
* 最高気温
* 最低気温
* 降水確率
* 表示ラベル

天気予報は開催予定のライブ・町民集会を対象として定期的に更新する。

予報対象期間は当日から15日先までとする。

イベント画面では開催日の前日・開催日・翌日の天気予報を表示する。

`updated_at` により天気予報の最終更新日時を管理する。

---

## 4.8 天気予報

ライブ・町民集会の開催予定に対して、
会場の天気予報を表示する。

### 天気予報の取得

`m_venue` に登録された緯度・経度を使用し、
Open-Meteo Weather APIから天気予報を取得する。

### 予報期間

現在日から15日先までを取得対象とする。

イベントの開催日に対して、

* 前日
* 開催日
* 翌日

の3日分を表示する。

対象期間外の場合は天気予報を表示しない。

### 表示内容

各日の天気予報として以下を表示する。

* 天気アイコン
* 日付
* 曜日
* 前日・開催日・翌日の区分
* 天気
* 最低気温
* 最高気温
* 降水確率

天気予報の最終更新日時も表示する。

### 更新

天気予報はワークテーブル `w_weather_forecast` に保存する。

同一会場・同一予報日のデータが存在する場合は、
既存データを更新する。

天気予報の取得に失敗した場合は、
該当イベントの天気予報を表示しない。

---

## 4.9 トランザクションテーブル

### `t_live_record`

ユーザーのライブ参加記録を管理する。

主な項目：

* `record_id`
* `user_id`
* `live_id`
* `seat_info`
* `memo`

`user_id` と `live_id` の組み合わせは一意。

---

### `t_live_expense`

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

### `t_meeting_record`

ユーザーの町民集会参加記録を管理する。

主な項目：

* `record_id`
* `user_id`
* `meeting_id`
* `seat_info`
* `memo`

`user_id` と `meeting_id` の組み合わせは一意。

---

### `t_meeting_expense`

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

### `t_setlist_prediction`

ユーザーが作成した予測セトリを管理する。

主な項目：

* `prediction_id`
* `user_id`
* `live_id`

`user_id` と `live_id` の組み合わせは一意。

予測セトリはライブを対象とし、
町民集会を対象としない。

---

### `t_setlist_prediction_song`

予測セトリに登録する楽曲を管理する。

主な項目：

* `prediction_id`
* `song_id`
* `song_order`
* `is_medley`
* `medley_order`

`prediction_id` と `song_id` の組み合わせは一意。

予測セトリで選択できる楽曲は、
`m_song` の以下の条件を満たす楽曲を対象とする。

* `is_deleted = FALSE`
* `is_public = TRUE`
* `song_type = 'INORI'`

`OTHER` の楽曲はセトリ予測の選択対象から除外する。

`m_setlist` への登録有無は選択条件としないため、
まだLIVEのセトリに登録されていない新曲も対象とする。

同一楽曲について複数の `m_song` レコードが存在する場合は、
`song_group_id` 単位でまとめて表示する。

楽曲の表示順は、以下の順とする。

1. `release_date` 昇順
2. `display_order` 昇順

---

### `t_live_user`

ユーザーとライブの参加状況を管理する。

主な項目：

* `user_id`
* `live_id`
* `is_join`

`user_id` と `live_id` の組み合わせを主キーとする。

---

### `t_meeting_user`

ユーザーと町民集会の参加状況を管理する。

主な項目：

* `user_id`
* `meeting_id`
* `is_join`

`user_id` と `meeting_id` の組み合わせを主キーとする。

---

### `t_user_lost_item`

ユーザーごとの忘れ物チェック項目を管理する。

主な項目：

* `user_lost_item_id`
* `user_id`
* `lost_item_id`
* `item_name`
* `is_checked`

`lost_item_id` は `m_lost_item.lost_item_id` を参照する。

---

### `t_inquiry`

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

# 5. Router構成

## 5.1 Routerの基本方針

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

# 6. Model / Service構成

## 6.1 基本方針

DBへのアクセスはModelにまとめる。

Routerから直接SQLを実行せず、
原則としてModelを経由してDBへアクセスする。

複数のModelを組み合わせた処理や、
画面表示だけでは完結しない業務処理はServiceにまとめる。

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

# 7. Template構成

## 7.1 基本方針

HTMLテンプレートはJinja2を使用する。

テンプレートは `templates/` 配下に機能単位で配置する。

基本的に、

```text
Router
 ↓
Template
```

---

# 8. 認証・アカウント仕様

## 8.1 通常ユーザー

通常ユーザーはログインIDとパスワードを使用してログインする。

ログイン成功時にはSessionへ以下の情報を保持する。

* `user_id`
* `user_name`
* `role`
* `font_id`

---

## 8.2 ログインID忘れ

登録済みメールアドレスとパスワードを確認し、
ログインIDをメールで案内する。

---

## 8.3 パスワード忘れ

登録済みログインIDとメールアドレスを確認し、
パスワード再設定用トークンを発行する。

メールに記載されたURLから
パスワード再設定画面を表示する。

パスワード再設定用URLには有効期限を設定する。

---

## 8.4 パスワード変更

ログインユーザーはマイページから
現在のパスワードを確認したうえで、
新しいパスワードへ変更できる。

パスワード条件：

* 8～32文字
* 小文字を1文字以上
* 大文字を1文字以上
* 数字を1文字以上
* 現在と同じパスワードは不可

---

## 8.5 退会

ログインユーザーはアカウントを退会できる。

退会時にはユーザーに紐付く個人データについて、
関連データを適切に削除する。

詳細な削除方法は現行実装を正とする。

---

# 9. 今後の開発予定

現在の優先順位は以下のとおり。

1. グッズマスタ
2. グッズユーザー機能
3. グッズ関連機能の既存画面への連携・調整

グッズ関連機能では、
管理者が登録するグッズ情報をマスタとして管理し、
ユーザー側で購入・所持状況などを管理できる機能を実装する。

---

# 10. 開発時の注意事項

* 既存機能を壊さないことを最優先とする
* 新規テーブルを作成する前に既存テーブルで対応できないか確認する
* DB変更時は既存Router・Model・Templateへの影響を確認する
* スマートフォン表示を最優先とする
* 基本最大幅は430pxとする
* 既存のデザイン・CSS命名規則を維持する
* HachiMaruPop-Regularを基本フォントとする
* ゲスト利用とログイン利用の両方を考慮する
* 個人データとマスターデータを混在させない
* ユーザー固有の設定は原則 `m_user_setting` に追加する
* 操作履歴・アクセスログなどは実装しない
* 不要になった旧機能・旧テーブルはREADMEに残さず、現行仕様から除外する

---

# 11. 現在の開発方針

現時点では、認証・ユーザー設定・ライブ・町民集会・セトリ・セトリ予測・天気予報・推し情報などの主要機能を実装済み。

ゲスト利用についても、
ログインユーザーと同様に利用できる範囲を拡張している。

今後は、

```text
ゲスト・アカウント関連の最終調整
        ↓
グッズマスタ
        ↓
グッズユーザー機能
        ↓
既存機能との連携
```

の順で開発を進める。

---

# 12. 旧仕様について

以下の機能・テーブルは現在の仕様では使用しない。

### `m_system_setting`

以前はユーザー登録設定などを管理していたが、
現在はユーザー登録を常時可能としているため使用しない。

現行DBでは不要なデータを削除し、
今後も当面利用しない。

### `m_invitation_code`

以前は招待制ユーザー登録に使用していたが、
現在はユーザー登録を誰でも可能としているため使用しない。

招待コードによる登録制限は廃止する。

今後、再び登録制限機能が必要になった場合は、
現行仕様・DB構成を確認したうえで新たに設計する。
