# =========================================================
# フォント設定
# =========================================================

FONT_LIST = [
    {
        "id": "hachi_maru_pop",
        "name": "パターン1",
        "css_class": "font-hachi-maru-pop"
    },
    {
        "id": "kiwi_maru",
        "name": "パターン2",
        "css_class": "font-kiwi-maru"
    },
    {
        "id": "mplus_rounded",
        "name": "パターン3",
        "css_class": "font-mplus-rounded"
    },
    {
        "id": "noto_sans_jp",
        "name": "パターン4",
        "css_class": "font-noto-sans-jp"
    },
    {
        "id": "yusei_magic",
        "name": "パターン5",
        "css_class": "font-yusei-magic"
    }
]

DEFAULT_FONT_ID = "hachi_maru_pop"


def get_font(font_id: str):
    """
    フォントIDからフォント情報を取得
    """

    for font in FONT_LIST:

        if font["id"] == font_id:
            return font

    return None


def get_font_class(font_id: str):
    """
    フォントIDからCSSクラスを取得
    """

    font = get_font(font_id)

    if not font:
        return get_font(DEFAULT_FONT_ID)["css_class"]

    return font["css_class"]


def is_valid_font_id(font_id: str) -> bool:
    """
    フォントIDが有効か確認
    """

    return get_font(font_id) is not None
