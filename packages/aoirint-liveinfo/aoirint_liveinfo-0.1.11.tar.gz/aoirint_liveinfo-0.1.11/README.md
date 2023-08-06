# liveinfopy

## Installation

- Python 3.10

### PyPI

- <https://pypi.org/project/aoirint-liveinfo/>

```shell
pip3 install aoirint-liveinfo
```

### Binary

- <https://github.com/aoirint/liveinfopy/releases>


## Usage

### ニコニコ生放送 `live.nicovideo.jp`

```shell
liveinfo -s nicolive "co5633084"

# 番組 （ 月刊ニコニコインフォチャンネル https://live.nicovideo.jp/watch/lv339313375 ）
liveinfo -s nicolive "lv339313375"

# コミュニティ （ ニコニコ動画プレミアムアワード https://com.nicovideo.jp/community/co5683564 ）
liveinfo -s nicolive "co5683564"

# ユーザー （ ニコニコプレミアムDAY https://www.nicovideo.jp/user/123430062 ）
liveinfo -s nicolive "user/123430062"

# ニコニコチャンネル （ウェザーニュースチャンネル https://ch.nicovideo.jp/weathernews ）
liveinfo -s nicolive "ch1072"
```

#### 期待される挙動と既知の問題

放送中の番組がある場合、その番組を返します。

最後に放送した番組がある場合、その番組を返します。
番組が放送中かどうか判定するには、放送開始時間（`start_date`）と放送終了時間（`end_date`）および現在時刻が利用できます。

番組ID（`lv*`）ではなく、コミュニティID（`co*`）やユーザID（`user/*`）、ニコニコチャンネルID（`ch*`）を渡した場合、`https://live.nicovideo.jp/watch/*`に各IDを設定したときと同じ挙動をします。

既知の問題として、ニコニコ公式チャンネルの[月刊ニコニコインフォチャンネル](https://ch.nicovideo.jp/weekly-niconico-info)が放送中でないときに上記操作をしたとき、番組が存在しない（`not_found`）扱いになることが確認されています。
これはニコニコまたは当該チャンネルの仕様として、修正は考えていません（「公式」番組を放送した場合または「公式」番組しか放送したことがない場合に起きる可能性があるかも？）。


```shell
# Return not_found (at least not-onair status)

# ニコニコチャンネル （月刊ニコニコインフォチャンネル https://ch.nicovideo.jp/weekly-niconico-info ）
liveinfo -s nicolive "ch2646073"
```


### YouTube Live

#### APIキー

YouTube Data API v3を使用します。APIキーが必要です。
以下の公式ドキュメントに沿って、YouTube Data API v3にアクセスできるAPIキーを発行してください。

- <https://developers.google.com/youtube/v3/getting-started>

CLIでは、APIキーは、引数の値・引数の値で指定されたファイル・環境変数の値・環境変数の値で指定されたファイル、のいずれかとして渡します。
自身の用途に適した安全な方法でAPIキーを渡すようにしてください。

なお、CLI以外の利用（ライブラリとしての利用）では、これらの引数や環境変数は使用されません。

- 引数の値: `--ytlive_api_key`
- 引数の値で指定されたファイル: `--ytlive_api_key_file`
- 環境変数の値: `LIVEINFO_YTLIVE_API_KEY`
- 環境変数の値で指定されたファイル: `LIVEINFO_YTLIVE_API_KEY_FILE`

#### 使用例

引数にはチャンネルID（URL・ハンドル名は使用不可）を渡してください。

```shell
liveinfo -s ytlive --ytlive_api_key_file /secrets/ytlive_api_key "UC7OazbQ3Eo9vrkcReXGIZkQ"
```

ハンドル名が設定されたチャンネルでは、チャンネルIDがURLに含まれなくなるため、
チャンネルIDを調べるのが難しいことがあります。
チャンネル個別ページを開き、開発者ツールで以下のJavaScriptコードを実行すると、簡単にチャンネルIDを確認できます（2022-11-28 現在）。

```shell
document.querySelector('meta[itemprop="channelId"]').content
```


#### 現在の仕様

- 最新5件の動画・生放送・プレミア公開動画から、生放送・プレミア公開動画を抽出
- 公開設定が「公開」のコンテンツのみを返す（限定公開、非公開は含まれない）
- `liveBroadcastContent`
  - ライブ配信予約: `upcoming`
  - ライブ配信中: `live`
  - 終了済みのライブ配信・動画: `none`
- `status.uploadStatus`
  - `uploaded`: ライブ配信中
  - `processed`: 終了済みのライブ配信・プレミア公開動画


## Development

### Install dependencies

```
python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt
```

If you are using pyenv, see [pyenv and PyInstaller](https://pyinstaller.org/en/stable/development/venv.html).


### Run test

```shell
flake8

mypy .

pytest tests/
```


## API研究

以下、未実装または実装予定のない内容が含まれます。

### ニコニコ生放送 `live.nicovideo.jp`

- `https://com.nicovideo.jp/api/v1/communities/{community_id}/lives/onair.json`
  - コミュニティで放送中の番組を返す（コミュニティ個別ページの放送Alert表示用）
  - `{community_id}`には、コミュニティID`co*`の数値部分（`*`）が入ります

### ニコニコチャンネルプラス `nicochannel.jp`

- `https://nfc-api.nicochannel.jp/fc/fanclub_sites/{fanclub_site_id}/live_pages?page={page}&live_type={live_type}&per_page={per_page}`
  - `https://nicochannel.jp/{channel_slug}/lives`で表示される生放送番組一覧
  - `fanclub_site_id`: `channel_slug`とは異なる数値ID
  - `live_type`
    - `1`(CURRENT): 放送中
    - `2`(SCHEDULED): 放送予定
    - `3`(FINISHED): 過去の放送（すべて）
    - `4`(ARCHIVED): 過去の放送（生放送アーカイブ）
      - 「すべて」と「生放送アーカイブ」の違い: 調査中（字面から、アーカイブが残っていない放送＝タイムシフト非公開相当？と残っている放送の区別？）
  - `page`
    - `1`始まり
  - `per_page`
    - 初期値 `live_type=1`: `10`
    - 初期値 `live_type=2`: `6`
    - 初期値 `live_type=3`: `8`
    - 初期値 `live_type=4`: `8`
