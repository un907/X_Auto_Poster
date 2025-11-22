import os
import sys

# --- Playwright Browser Path Setup ---
def get_base_path():
    """実行ファイルのディレクトリを取得（frozen対応）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Windows/Mac共通:
# インストーラー/Zipが 'browsers' フォルダを同梱するため、それを参照するように設定
browsers_path = os.path.join(get_base_path(), "browsers")
if os.path.exists(browsers_path):
    # フォルダが存在する場合のみ環境変数を上書き
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path

# Windowsでの文字化け対策
if sys.platform == 'win32':
    if sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr:
        sys.stderr.reconfigure(encoding='utf-8')

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import google.generativeai as genai
import csv
import json
import time
import random
import threading
import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- 設定・定数 ---
BASE_DIR = get_base_path()
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts.csv')
PROFILES_DIR = os.path.join(BASE_DIR, 'profiles')
APP_TITLE = "X自動投稿ツール"
CURRENT_VERSION = "1.6.0"
WINDOW_SIZE = "900x600"

# --- テーマ設定 ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# フォント設定 (Windowsでの表示改善)
if sys.platform == "win32":
    FONT_FAMILY = "Meiryo UI"
else:
    FONT_FAMILY = "Hiragino Maru Gothic ProN" # Macはデフォルトでも綺麗だが丸ゴシック指定

# CTkのデフォルトフォントを変更するAPIはないため、各ウィジェットで指定するか、
# テーマJSONをカスタムするが、ここでは簡易的に定数として持ち、主要な箇所に適用する設計とする。
# ただし、CTkはデフォルトでRobotoを使うため、日本語が中華フォントになる場合がある。
# そこで、Widget初期化時にフォントを指定するヘルパーを使うか、
# 全体的に font=(FONT_FAMILY, size) を適用する。


# --- 定数定義 ---
EMOJIS = ["😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😊", "😇", "🙂", "🙃", "😉", "😌", "😍", "🥰", "😘", "😗", "😙", "😚", "😋", "😛", "😝", "😜", "🤪", "🤨", "🧐", "🤓", "😎", "🤩", "🥳", "😏", "😒", "😞", "😔", "😟", "😕", "🙁", "☹️", "😣", "😖", "😫", "😩", "🥺", "😢", "😭", "😤", "😠", "😡", "🤬", "🤯", "😳", "🥵", "🥶", "😱", "😨", "😰", "😥", "😓", "🤗", "🤔", "🤭", "🤫", "🤥", "😶", "😐", "😑", "😬", "🙄", "😯", "😦", "😧", "😮", "😲", "🥱", "😴", "🤤", "😪", "😵", "🤐", "🥴", "🤢", "🤮", "😷", "🤒", "🤕", "🤑", "🤠", "😈", "👿", "👹", "👺", "💩", "👻", "💀", "☠️", "👽", "👾", "🤖", "🎃", "🤡", "✅", "❌", "⚠️", "🚸", "⛔", "🚫", "🚳", "🚭", "🚯", "🚱", "🚷", "📵", "🔞", "☢️", "☣️", "⬆️", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️", "↕️", "↔️", "↩️", "↪️", "⤴️", "⤵️", "🔃", "🔄", "🔙", "🔚", "🔛", "🔜", "🔝", "🛐", "⚛️", "🕉️", "✡️", "☸️", "☯️", "✝️", "☦️", "☪️", "☮️", "🕎", "🔯", "♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓", "⛎", "🔀", "🔁", "🔂", "▶️", "⏩", "⏭️", "⏯️", "◀️", "⏪", "⏮️", "🔼", "⏫", "🔽", "⏬", "⏸️", "⏹️", "⏺️", "⏏️", "🎦", "🔅", "🔆", "📶", "📳", "📴", "♀️", "♂️", "⚧️", "✖️", "➕", "➖", "➗", "♾️", "‼️", "❓", "❔", "❕", "❗", "〰️", "💱", "💲", "⚕️", "♻️", "⚜️", "🔱", "📛", "🔰", "⭕", "✅", "☑️", "✔️", "❌", "❎", "➰", "➿", "〽️", "✳️", "✴️", "❇️", "©️", "®️", "™️", "#️⃣", "*️⃣", "0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🔠", "🔡", "🔢", "🔣", "🔤", "🅰️", "🆎", "🅱️", "🆑", "🆒", "🆓", "ℹ️", "🆔", "Ⓜ️", "🆕", "🆖", "🅾️", "🆗", "🅿️", "🆘", "🆙", "🆚", "🈁", "🈂️", "🈷️", "🈶", "指", "🉐", "🈹", "🈚", "🈲", "🉑", "🈸", "🈴", "🈳", "㊗️", "㊙️", "🈺", "🈵", "🔴", "🟠", "🟡", "🟢", "🔵", "🟣", "🟤", "⚫", "⚪", "🟥", "🟧", "🟨", "🟩", "🟦", "🟪", "🟫", "⬛", "⬜", "◼️", "◻️", "◾", "◽", "▪️", "▫️", "🔶", "🔷", "🔸", "🔹", "🔺", "🔻", "💠", "🔘", "🔲", "🔳"]

ACTIONS = [
    "作業に集中しています。", "新しいアイデアを模索中。", "ちょっと一息ついてます。", "情報収集中。",
    "目標に向かって前進中。", "好きな音楽を聴きながら。", "コーヒーブレイク中。", "整理整頓してスッキリ。",
    "読書でインプット中。", "散歩して気分転換。", "美味しいものを食べて幸せ。", "次の計画を立てています。",
    "ニュースをチェック中。", "ストレッチして体をほぐし中。", "メールチェック完了。", "資料作成に没頭中。",
    "新しいスキルを習得中。", "友人と連絡を取り合っています。", "部屋の掃除をしました。", "瞑想して心を整えています。"
]

POST_PATTERNS = {
    "morning": [
        "{emoji} おはようございます！今日も一日頑張りましょう！",
        "{emoji} 朝のコーヒーが美味しいです。素敵な一日の始まり！",
        "{emoji} 早起きは三文の徳。今日も良い日になりますように。",
        "{emoji} おはようございます。朝の空気は澄んでて気持ちいいですね。",
        "{emoji} 新しい朝が来ました！元気にいきましょう！"
    ],
    "day": [
        "{emoji} こんにちは！午後も気合入れていきましょう！",
        "{emoji} ランチは何にしようかな？お腹が空いてきました。",
        "{emoji} ちょっと休憩。リフレッシュして後半戦も頑張ります。",
        "{emoji} 良い天気ですね。空を見上げると気分転換になります。",
        "{emoji} こんにちは。マイペースに進めていきましょう。"
    ],
    "night": [
        "{emoji} こんばんは！今日もお疲れ様でした。",
        "{emoji} ゆっくり休みましょう。明日も頑張りましょうね。",
        "{emoji} 一日の振り返りタイム。良い夢が見られますように。",
        "{emoji} 夜風が心地よいですね。リラックスタイムです。",
        "{emoji} こんばんは。自分へのご褒美を忘れずに。"
    ]
}

# --- 文章生成ロジック ---
# この関数はAutoPostAppクラスのメソッドに移動し、AI生成ロジックが追加されます。
# def generate_post_content():
#     """
#     現在時刻に合わせて投稿内容を生成する
#     """
#     # --- 拡張された文章生成ロジック (組み合わせで1万通り以上を実現) ---
#     hour = datetime.datetime.now().hour
    
#     # 1. 時間帯別の挨拶 (3パターン * 10種類 = 30)
#     if 5 <= hour < 11:
#         time_greeting = "おはようございます！"
#         greetings = [
#             "今日も一日頑張りましょう", "朝のコーヒーが美味しい", "早起きは三文の徳ですね", "素敵な一日の始まり",
#             "よく眠れましたか？", "朝活スタート！", "清々しい朝ですね", "今日も良い日になりますように",
#             "朝の空気は澄んでて気持ちいい", "元気にいきましょう！"
#         ]
#     elif 11 <= hour < 18:
#         time_greeting = "こんにちは！"
#         greetings = [
#             "午後も気合入れていきましょう", "ランチは何にしようかな", "ちょっと休憩", "良い天気ですね",
#             "午後の紅茶がおいしい", "眠気に負けず頑張ろう", "おやつタイムにしたい", "後半戦も集中！",
#             "空を見上げるとリフレッシュできます", "マイペースに進めましょう"
#         ]
#     else:
#         time_greeting = "こんばんは！"
#         greetings = [
#             "今日もお疲れ様でした", "ゆっくり休みましょう", "明日も頑張りましょう", "夜更かしはほどほどに",
#             "一日の振り返りタイム", "お風呂でリラックス", "良い夢が見られますように", "夜風が心地よいですね",
#             "自分へのご褒美を忘れずに", "明日の準備をして寝ます"
#         ]

#     # 2. 現在の状況・アクション (20種類)
#     actions = [
#         "作業に集中しています。", "新しいアイデアを模索中。", "ちょっと一息ついてます。", "情報収集中。",
#         "目標に向かって前進中。", "好きな音楽を聴きながら。", "コーヒーブレイク中。", "整理整頓してスッキリ。",
#         "読書でインプット中。", "散歩して気分転換。", "美味しいものを食べて幸せ。", "次の計画を立てています。",
#         "ニュースをチェック中。", "ストレッチして体をほぐし中。", "メールチェック完了。", "資料作成に没頭中.",
#         "新しいスキルを習得中。", "友人と連絡を取り合っています。", "部屋の掃除をしました。", "瞑想して心を整えています。"
#     ]

#     # 3. ポジティブな一言・格言 (20種類)
#     thoughts = [
#         "継続は力なり。", "新しいことに挑戦したい気分。", "積み重ねが大事。", "リフレッシュも必要。",
#         "ポジティブに行こう！", "学びのある一日でした。", "一歩ずつ前進。", "失敗は成功のもと。",
#         "自分を信じて。", "感謝の気持ちを忘れずに。", "笑顔が一番。", "明日はもっと良くなる。",
#         "小さな幸せを見つけよう。", "焦らずマイペースで。", "健康第一ですね。", "ピンチはチャンス。",
#         "努力は裏切らない。", "直感を信じて。", "変化を楽しむ。", "シンプルに生きる。"
#     ]

#     # 4. 顔文字 (30種類)
#     kaomojis = [
#         "(｀・ω・´)", "(*'ω'*)", "(^o^)", "(´・ω・`)", "＼(^o^)／", "( *´艸｀)", "('◇')ゞ",
#         "(≧▽≦)", "(・∀・)", "(Tkinter)", "(;´∀｀)", "(*^^)v", "(>_<)", "(ToT)",
#         "(*‘∀‘)", "( ˘ω˘ )", "(´-ω-`)", "(*^▽^*)", "(´▽｀*)", "(o^―^o)",
#         "(/・ω・)/", "(*'▽')", "(´･ω･｀)", "(｀・ω・´)ゞ", "(^_-)-☆", "(*^-^*)",
#         "(´・ω・)つ旦", "(=ﾟωﾟ)ﾉ", "(｡･ω･｡)ﾉ♡", "(｀・ω・´)b"
#     ]

#     # 組み合わせ: 3(時間) * 10(挨拶) * 20(状況) * 20(思考) * 30(顔文字) = 360,000通り
#     # さらにランダムで構成を変える
    
#     pattern = random.randint(1, 3)
    
#     if pattern == 1:
#         # パターン1: 挨拶 + 状況 + 顔文字
#         content = f"{time_greeting}\n{random.choice(greetings)}\n\n{random.choice(actions)} {random.choice(kaomojis)}"
#     elif pattern == 2:
#         # パターン2: 挨拶 + 思考 + 顔文字
#         content = f"{time_greeting}\n{random.choice(greetings)}\n\n{random.choice(thoughts)} {random.choice(kaomojis)}"
#     else:
#         # パターン3: 挨拶 + 状況 + 思考 + 顔文字
#         content = f"{time_greeting}\n{random.choice(greetings)}\n\n{random.choice(actions)}\n{random.choice(thoughts)} {random.choice(kaomojis)}"
    
#     return content

# --- 設定管理クラス ---
class SettingsManager:
    DEFAULT_SETTINGS = {
        "headless": False,
        "wait_min": 120,
        "wait_max": 300,
        "gif_probability": 30,
        "auto_like": True,
        "like_min": 1,
        "like_max": 5,
        "ai_mode": False,
        "gemini_api_key": ""
    }
    SETTINGS_FILE = "settings.json"

    @classmethod
    def load(cls):
        if not os.path.exists(cls.SETTINGS_FILE):
            return cls.DEFAULT_SETTINGS.copy()
        try:
            with open(cls.SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # マージして不足項目を補完
                settings = cls.DEFAULT_SETTINGS.copy()
                settings.update(data)
                return settings
        except:
            return cls.DEFAULT_SETTINGS.copy()

    @classmethod
    def save(cls, settings):
        try:
            with open(cls.SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"設定保存エラー: {e}")

class PersonaManager:
    PERSONAS_FILE = "personas.json"

    @classmethod
    def load(cls):
        if not os.path.exists(cls.PERSONAS_FILE):
            return {}
        try:
            with open(cls.PERSONAS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"ペルソナ読み込みエラー: {e}")
            return {}

    @classmethod
    def save(cls, personas):
        try:
            with open(cls.PERSONAS_FILE, "w", encoding="utf-8") as f:
                json.dump(personas, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"ペルソナ保存エラー: {e}")

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None
        if api_key:
            genai.configure(api_key=api_key)
            # 利用可能なモデルを動的に探す
            try:
                all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                print(f"Available Gemini Models: {all_models}")
                
                # フィルタリングと優先順位付け
                # 1. flash系 (高速・安価)
                flash_models = [m for m in all_models if 'flash' in m.lower() and 'exp' not in m.lower() and 'preview' not in m.lower()]
                # 2. pro系 (高性能)
                pro_models = [m for m in all_models if 'pro' in m.lower() and 'exp' not in m.lower() and 'preview' not in m.lower()]
                # 3. その他 (exp/preview含む)
                other_models = [m for m in all_models if m not in flash_models and m not in pro_models]
                
                target_model = None
                if flash_models:
                    target_model = flash_models[0] # 最新のflash
                elif pro_models:
                    target_model = pro_models[0]
                elif other_models:
                    target_model = other_models[0]
                
                # フォールバック: リストになくても定番を試す
                if not target_model:
                    target_model = 'models/gemini-1.5-flash'

                print(f"Selected Gemini Model: {target_model}")
                self.model = genai.GenerativeModel(target_model)

            except Exception as e:
                print(f"Model listing failed: {e}")
                # フォールバック
                self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_persona(self, profile_text, recent_posts):
        if not self.model:
            return None
        
        prompt = f"""
        以下のX(Twitter)ユーザーのプロフィールと直近の投稿から、このユーザーの「ペルソナ（性格・役割）」と「口調」を分析・抽出してください。
        また、今後AIがこのユーザーになりきって投稿するための「投稿例文」を3つ作成してください。

        【プロフィール】
        {profile_text}

        【直近の投稿】
        {recent_posts}

        出力は以下のJSON形式のみで行ってください。余計な説明は不要です。
        {{
            "persona": "...",
            "tone": "...",
            "example_posts": ["...", "...", "..."]
        }}
        """
        try:
            response = self.model.generate_content(prompt)
            # JSON部分だけ抽出（Markdownのコードブロック除去）
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini生成エラー: {e}")
            return None

    def generate_post(self, persona, tone, examples):
        if not self.model:
            return None

        prompt = f"""
        あなたは以下の設定を持つX(Twitter)ユーザーです。
        今の気分や状況に合わせて、自然な投稿を1つ作成してください。
        ハッシュタグは付けないでください。
        【重要】文字数は「必ず140文字以内」に収めてください。長すぎるとエラーになります。100文字程度が目安です。

        【ペルソナ】
        {persona}

        【口調】
        {tone}

        【投稿例】
        {examples}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini投稿生成エラー: {e}")
            return None

# --- 設定画面クラス ---
class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_settings, on_save_callback):
        super().__init__(parent)
        self.title("設定")
        self.geometry("400x600") # 高さを拡張
        self.resizable(False, False)
        self.attributes("-topmost", True) # 前面に表示
        
        self.settings = current_settings
        self.on_save_callback = on_save_callback

        self.create_widgets()

    def create_widgets(self):
        # ヘッドレスモード
        self.headless_var = ctk.BooleanVar(value=self.settings["headless"])
        switch = ctk.CTkSwitch(self, text="ヘッドレスモード (ブラウザ非表示)", variable=self.headless_var, font=ctk.CTkFont(family=FONT_FAMILY))
        switch.pack(pady=20, padx=20, anchor="w")

        # 待機時間
        ctk.CTkLabel(self, text="アカウント間待機時間 (秒)", font=ctk.CTkFont(family=FONT_FAMILY)).pack(pady=(20, 5), padx=20, anchor="w")
        
        time_frame = ctk.CTkFrame(self, fg_color="transparent")
        time_frame.pack(pady=0, padx=20, anchor="w")
        
        self.wait_min_entry = ctk.CTkEntry(time_frame, width=60, font=ctk.CTkFont(family=FONT_FAMILY))
        self.wait_min_entry.insert(0, str(self.settings["wait_min"]))
        self.wait_min_entry.pack(side="left")
        
        ctk.CTkLabel(time_frame, text=" 〜 ", font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left")
        
        self.wait_max_entry = ctk.CTkEntry(time_frame, width=60, font=ctk.CTkFont(family=FONT_FAMILY))
        self.wait_max_entry.insert(0, str(self.settings["wait_max"]))
        self.wait_max_entry.pack(side="left")

        # 画像/GIF添付確率
        ctk.CTkLabel(self, text=f"画像/GIF添付確率: {self.settings['gif_probability']}%", font=ctk.CTkFont(family=FONT_FAMILY)).pack(pady=(20, 5), padx=20, anchor="w")
        self.gif_prob_slider = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=100, command=self.update_slider_label)
        self.gif_prob_slider.set(self.settings["gif_probability"])
        self.gif_prob_slider.pack(pady=0, padx=20, fill="x")
        self.gif_prob_label = ctk.CTkLabel(self, text=f"{self.settings['gif_probability']}%", font=ctk.CTkFont(family=FONT_FAMILY))
        self.gif_prob_label.pack(pady=0)

        # 自動いいね
        self.auto_like_var = ctk.BooleanVar(value=self.settings["auto_like"])
        ctk.CTkCheckBox(self, text="タイムラインを巡回して「いいね」する", variable=self.auto_like_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(pady=5, padx=20, anchor="w")

        # いいね数範囲 (v1.6)
        like_frame = ctk.CTkFrame(self, fg_color="transparent")
        like_frame.pack(pady=5, padx=20, anchor="w")
        ctk.CTkLabel(like_frame, text="いいね数 (Min-Max):", font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=5)
        
        self.like_min_entry = ctk.CTkEntry(like_frame, width=50)
        self.like_min_entry.pack(side="left", padx=5)
        self.like_min_entry.insert(0, str(self.settings.get("like_min", 1)))
        
        ctk.CTkLabel(like_frame, text="~", font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=5)
        
        self.like_max_entry = ctk.CTkEntry(like_frame, width=50)
        self.like_max_entry.pack(side="left", padx=5)
        self.like_max_entry.insert(0, str(self.settings.get("like_max", 5)))

        # --- AI設定 (v1.5) ---
        ctk.CTkLabel(self, text="--- AI設定 ---", font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")

        # AIモード有効化
        self.ai_mode_var = ctk.BooleanVar(value=self.settings.get("ai_mode", False))
        ctk.CTkSwitch(self, text="AIモードを有効にする (ペルソナ投稿)", variable=self.ai_mode_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(pady=5, padx=20, anchor="w")

        # API Key
        ctk.CTkLabel(self, text="Gemini API Key:", font=ctk.CTkFont(family=FONT_FAMILY)).pack(pady=(5, 0), padx=20, anchor="w")
        self.api_key_entry = ctk.CTkEntry(self, width=300, show="*", font=ctk.CTkFont(family=FONT_FAMILY)) # パスワード形式
        self.api_key_entry.insert(0, self.settings.get("gemini_api_key", ""))
        self.api_key_entry.pack(pady=5, padx=20, anchor="w")
        
        # APIキー取得リンク
        def open_api_url():
            import webbrowser
            webbrowser.open("https://aistudio.google.com/app/apikey")

        link_btn = ctk.CTkButton(self, text="🔑 APIキーを無料で取得する (Google AI Studio)", 
                                 command=open_api_url, 
                                 fg_color="transparent", border_width=1, 
                                 text_color=("blue", "lightblue"),
                                 font=ctk.CTkFont(family=FONT_FAMILY, size=12, underline=True))
        link_btn.pack(pady=0, padx=20, anchor="w")

        # 保存ボタン
        self.save_btn = ctk.CTkButton(self, text="保存して閉じる", command=self.save_settings, fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(family=FONT_FAMILY))
        self.save_btn.pack(pady=30, padx=20, fill="x")

    def update_slider_label(self, value):
        self.gif_prob_label.configure(text=f"{int(value)}%")

    def save_settings(self):
        try:
            wait_min = int(self.wait_min_entry.get())
            wait_max = int(self.wait_max_entry.get())
            if wait_min < 0 or wait_max < 0 or wait_min > wait_max:
                raise ValueError("待機時間が不正です")
        except ValueError:
            messagebox.showerror("エラー", "待機時間は正の整数で、最小 <= 最大 である必要があります。")
            return

        new_settings = {
            "headless": self.headless_var.get(),
            "wait_min": wait_min,
            "wait_max": wait_max,
            "gif_probability": int(self.gif_prob_slider.get()),
            "auto_like": self.auto_like_var.get(),
            "like_min": int(self.like_min_entry.get()),
            "like_max": int(self.like_max_entry.get()),
            "gemini_api_key": self.api_key_entry.get().strip(),
            "ai_mode": self.ai_mode_var.get()
        }
        self.on_save_callback(new_settings)
        self.destroy()

class PersonaEditorWindow(ctk.CTkToplevel):
    def __init__(self, master, username, on_save_callback):
        super().__init__(master)
        self.title(f"ペルソナ設定: {username}")
        self.geometry("500x600")
        self.username = username
        self.on_save_callback = on_save_callback
        
        # 最前面に表示
        self.attributes("-topmost", True)
        self.lift()
        self.focus_force()

        # 既存データの読み込み
        self.personas = PersonaManager.load()
        self.data = self.personas.get(username, {"persona": "", "tone": "", "example_posts": ""})

        self.create_widgets()

    def create_widgets(self):
        # 1. キャラクター設定 (Persona)
        ctk.CTkLabel(self, text="キャラクター設定 (性格・役割など)", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.persona_text = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family=FONT_FAMILY))
        self.persona_text.pack(pady=5, padx=20, fill="x")
        self.persona_text.insert("1.0", self.data.get("persona", ""))

        # 2. 口調 (Tone)
        ctk.CTkLabel(self, text="口調 (例: デスマス調、タメ口、絵文字多め)", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.tone_entry = ctk.CTkEntry(self, font=ctk.CTkFont(family=FONT_FAMILY))
        self.tone_entry.pack(pady=5, padx=20, fill="x")
        self.tone_entry.insert(0, self.data.get("tone", ""))

        # 3. 投稿例文 (Example Posts)
        ctk.CTkLabel(self, text="投稿例文 (AIの参考用、複数行可)", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).pack(pady=(10, 5), padx=20, anchor="w")
        self.examples_text = ctk.CTkTextbox(self, height=150, font=ctk.CTkFont(family=FONT_FAMILY))
        self.examples_text.pack(pady=5, padx=20, fill="both", expand=True)
        # example_posts はリストか文字列かで保存されている可能性があるが、ここでは文字列(改行区切り)として扱う
        examples = self.data.get("example_posts", "")
        if isinstance(examples, list):
            examples = "\n".join(examples)
        self.examples_text.insert("1.0", examples)

        # 自動抽出ボタン (プレースホルダー)
        self.extract_btn = ctk.CTkButton(self, text="プロフィールから自動抽出 (AI)", command=self.auto_extract, fg_color="purple", hover_color="#500050", font=ctk.CTkFont(family=FONT_FAMILY))
        self.extract_btn.pack(pady=10, padx=20, fill="x")

        # 保存ボタン
        self.save_btn = ctk.CTkButton(self, text="保存して閉じる", command=self.save_persona, fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(family=FONT_FAMILY))
        self.save_btn.pack(pady=(0, 20), padx=20, fill="x")

    def auto_extract(self):
        # 設定からAPIキーを取得
        settings = SettingsManager.load()
        api_key = settings.get("gemini_api_key", "")
        
        if not api_key:
            messagebox.showerror("エラー", "Gemini API Keyが設定されていません。\n設定画面でキーを入力してください。")
            return

        # 確認ダイアログ
        if not messagebox.askyesno("確認", "ブラウザを起動してプロフィールと過去の投稿を取得します。\nよろしいですか？"):
            return

        try:
            # ブラウザ起動 (ヘッドレス推奨だが、ログイン状態維持のためGUIありでいくか、既存のプロファイルを使う)
            # ここでは簡易的に既存のブラウザ起動ロジックを流用したいが、クラス外なのでPlaywrightを直接呼ぶ
            # ただし、ログインセッションが必要なので、profilesディレクトリを指定する
            
            base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            user_data_dir = os.path.join(base_path, "profiles", self.username)
            
            if not os.path.exists(user_data_dir):
                messagebox.showerror("エラー", f"{self.username} のプロファイルが見つかりません。\n一度ログインを行ってください。")
                return

            from playwright.sync_api import sync_playwright
            
            self.extract_btn.configure(state="disabled", text="抽出中... (ブラウザ起動)")
            self.update()

            with sync_playwright() as p:
                # ブラウザ起動
                browser = p.firefox.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False, # 視覚的にわかるように
                    viewport={"width": 1280, "height": 720}
                )
                page = browser.pages[0]
                
                # プロフィールページへ
                page.goto(f"https://twitter.com/{self.username.replace('@', '')}")
                page.wait_for_timeout(3000)
                
                # プロフィール文取得
                profile_text = ""
                try:
                    profile_elm = page.locator('[data-testid="UserDescription"]').first
                    if profile_elm.is_visible():
                        profile_text = profile_elm.inner_text()
                except:
                    pass
                
                # 過去の投稿取得 (自分のツイートのみ)
                recent_posts = []
                try:
                    # 少しスクロール
                    page.evaluate("window.scrollBy(0, 500)")
                    page.wait_for_timeout(1000)
                    
                    articles = page.locator('article').all()
                    for article in articles[:5]: # 最新5件
                        try:
                            text_elm = article.locator('[data-testid="tweetText"]').first
                            if text_elm.is_visible():
                                recent_posts.append(text_elm.inner_text())
                        except:
                            continue
                except:
                    pass
                
                browser.close()

            # Geminiで生成
            self.extract_btn.configure(text="抽出中... (AI分析)")
            self.update()
            
            client = GeminiClient(api_key)
            result = client.generate_persona(profile_text, "\n".join(recent_posts))
            
            if result:
                # UIに反映
                self.persona_text.delete("1.0", "end")
                self.persona_text.insert("1.0", result.get("persona", ""))
                
                self.tone_entry.delete(0, "end")
                self.tone_entry.insert(0, result.get("tone", ""))
                
                self.examples_text.delete("1.0", "end")
                examples = result.get("example_posts", [])
                if isinstance(examples, list):
                    self.examples_text.insert("1.0", "\n".join(examples))
                
                messagebox.showinfo("成功", "ペルソナの抽出に成功しました！\n内容を確認・編集して保存してください。")
            else:
                messagebox.showerror("エラー", "AIによる分析に失敗しました。")

        except Exception as e:
            messagebox.showerror("エラー", f"抽出処理中にエラーが発生しました:\n{e}")
        finally:
            self.extract_btn.configure(state="normal", text="プロフィールから自動抽出 (AI)")

    def save_persona(self):
        new_data = {
            "persona": self.persona_text.get("1.0", "end").strip(),
            "tone": self.tone_entry.get().strip(),
            "example_posts": self.examples_text.get("1.0", "end").strip().split("\n") # リストとして保存
        }
        # 空文字除去
        new_data["example_posts"] = [x for x in new_data["example_posts"] if x.strip()]
        
        self.on_save_callback(self.username, new_data)
        self.destroy()

# --- ターゲットアクション（拡散・交流）フレーム ---
class TargetActionFrame(ctk.CTkFrame): # クラス定義を追加
    def __init__(self, master, start_callback):
        super().__init__(master, fg_color="transparent")
        self.start_callback = start_callback
        self.settings_file = "target_settings.json"
        
        # グリッド設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # テキストエリアを伸縮

        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # 1. 対象URL入力
        ctk.CTkLabel(self, text="対象の投稿URL (1行に1つ)", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=0, column=0, sticky="w", pady=(10, 5))
        self.url_textbox = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family=FONT_FAMILY))
        self.url_textbox.grid(row=1, column=0, sticky="ew", padx=5)

        # 2. アクション選択
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.like_var = ctk.BooleanVar(value=True)
        self.repost_var = ctk.BooleanVar(value=False)
        self.quote_var = ctk.BooleanVar(value=False)
        self.reply_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(action_frame, text="いいね", variable=self.like_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=10)
        ctk.CTkCheckBox(action_frame, text="リポスト", variable=self.repost_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=10)
        ctk.CTkCheckBox(action_frame, text="引用RP", variable=self.quote_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=10)
        ctk.CTkCheckBox(action_frame, text="リプライ", variable=self.reply_var, font=ctk.CTkFont(family=FONT_FAMILY)).pack(side="left", padx=10)

        # 3. 引用/リプライ用テキスト
        ctk.CTkLabel(self, text="引用/リプライ用テキスト (1行に1パターン、ランダム選択)", font=ctk.CTkFont(family=FONT_FAMILY, weight="bold")).grid(row=3, column=0, sticky="w", pady=(10, 5))
        self.text_textbox = ctk.CTkTextbox(self, height=100, font=ctk.CTkFont(family=FONT_FAMILY))
        self.text_textbox.grid(row=4, column=0, sticky="nsew", padx=5)
        # デフォルト値は load_settings で上書きされなければ設定

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            self.text_textbox.insert("1.0", "最高です！\n応援してます！\n素晴らしい取り組みですね✨\n詳細気になります！")
            return
        
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                self.url_textbox.delete("1.0", "end")
                self.url_textbox.insert("1.0", data.get("urls", ""))
                
                self.text_textbox.delete("1.0", "end")
                self.text_textbox.insert("1.0", data.get("texts", ""))
                
                actions = data.get("actions", {})
                self.like_var.set(actions.get("like", True))
                self.repost_var.set(actions.get("repost", False))
                self.quote_var.set(actions.get("quote", False))
                self.reply_var.set(actions.get("reply", False))
        except Exception as e:
            print(f"ターゲット設定読み込みエラー: {e}")
            self.text_textbox.insert("1.0", "最高です！\n応援してます！\n素晴らしい取り組みですね✨\n詳細気になります！")

    def save_settings(self):
        data = {
            "urls": self.url_textbox.get("1.0", "end").strip(),
            "texts": self.text_textbox.get("1.0", "end").strip(),
            "actions": {
                "like": self.like_var.get(),
                "repost": self.repost_var.get(),
                "quote": self.quote_var.get(),
                "reply": self.reply_var.get()
            }
        }
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"ターゲット設定保存エラー: {e}")

    def on_start(self):
        self.save_settings() # 開始時に保存

        urls = self.url_textbox.get("1.0", "end").strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        texts = self.text_textbox.get("1.0", "end").strip().split('\n')
        texts = [t.strip() for t in texts if t.strip()]

        actions = {
            "like": self.like_var.get(),
            "repost": self.repost_var.get(),
            "quote": self.quote_var.get(),
            "reply": self.reply_var.get()
        }

        if not urls:
            messagebox.showwarning("入力エラー", "対象のURLを入力してください。")
            return
        
        if (actions["quote"] or actions["reply"]) and not texts:
            messagebox.showwarning("入力エラー", "引用RPまたはリプライを行う場合は、テキストを入力してください。")
            return

        if not any(actions.values()):
            messagebox.showwarning("入力エラー", "アクションを少なくとも1つ選択してください。")
            return

        self.start_callback(urls, actions, texts)

class AutoPostApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)

        # 設定読み込み
        self.settings = SettingsManager.load()

        # 実行中フラグと制御用イベント
        self.is_running = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.is_running = False
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set() # 初期状態は「一時停止していない（進む）」
        
        # v1.1: 手動ブラウザ管理
        self.manual_browsers = 0
        self.manual_lock = threading.Lock()
        self.active_manual_users = set() # 起動中のユーザー名セット

        # アカウント情報の初期化
        self.accounts = self.get_accounts()

        # グリッドレイアウト設定 (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        """サイドバー（操作パネル）の作成"""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        # グリッド設定: 行7(スペーサー)を伸縮させて、それ以降を下に押しやる
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # 1. タイトル (Row 0)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="X Auto Poster", font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # バージョン (Row 0 - sticky south)
        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v{CURRENT_VERSION}", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color="gray")
        self.version_label.grid(row=0, column=0, padx=20, pady=(50, 0), sticky="s")

        # 2. 初回セットアップ (Row 1)
        self.setup_btn = ctk.CTkButton(self.sidebar_frame, text="初回ログイン設定\n(手動)", command=self.start_setup, font=ctk.CTkFont(family=FONT_FAMILY))
        self.setup_btn.grid(row=1, column=0, padx=20, pady=10)

        # 3. 自動投稿開始 (Row 2)
        self.start_button = ctk.CTkButton(self.sidebar_frame, text="自動投稿開始", command=self.start_process, fg_color="green", hover_color="darkgreen", font=ctk.CTkFont(family=FONT_FAMILY))
        self.start_button.grid(row=2, column=0, padx=20, pady=(10, 5))

        # 4. 一時停止 (Row 3)
        self.pause_button = ctk.CTkButton(self.sidebar_frame, text="一時停止", command=self.toggle_pause, fg_color="orange", hover_color="darkorange", font=ctk.CTkFont(family=FONT_FAMILY))
        self.pause_button.grid(row=3, column=0, padx=20, pady=5)
        
        # 5. 停止 (Row 4)
        self.stop_button = ctk.CTkButton(self.sidebar_frame, text="停止", command=self.stop_process, fg_color="red", hover_color="darkred", font=ctk.CTkFont(family=FONT_FAMILY))
        self.stop_button.grid(row=4, column=0, padx=20, pady=5)

        # 6. 実行数指定 (Row 5)
        self.count_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.count_frame.grid(row=5, column=0, padx=20, pady=5)
        ctk.CTkLabel(self.count_frame, text="実行数:", font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left")
        
        self.max_count_combo = ctk.CTkComboBox(self.count_frame, width=60, 
                                             values=["All", "1", "2", "3", "5", "10"],
                                             font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.max_count_combo.pack(side="left", padx=5)
        self.max_count_combo.set("All")

        # 7. 設定 (Row 6)
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="設定", command=self.open_settings, font=ctk.CTkFont(family=FONT_FAMILY))
        self.settings_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Row 7 is Spacer (Weight 1)

        # 8. テーマ切り替え (Row 8, 9)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w", font=ctk.CTkFont(family=FONT_FAMILY))
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                                       command=self.change_appearance_mode_event, font=ctk.CTkFont(family=FONT_FAMILY))
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # 9. 署名 (Row 10)
        self.signature_label = ctk.CTkLabel(self.sidebar_frame, text="Powered by Midori\nInnocence.inc", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color="gray")
        self.signature_label.grid(row=10, column=0, padx=20, pady=(0, 20), sticky="s")

    def open_persona_settings(self, username):
        """ペルソナ設定画面を開く"""
        PersonaEditorWindow(self, username, self.save_persona_callback)

    def save_persona_callback(self, username, new_data):
        """ペルソナ保存コールバック"""
        personas = PersonaManager.load()
        personas[username] = new_data
        PersonaManager.save(personas)
        self.log(f"ペルソナ設定を保存しました: {username}")

    def bulk_auto_extract(self):
        """全アカウントのペルソナを一括抽出する"""
        settings = SettingsManager.load()
        api_key = settings.get("gemini_api_key", "")
        if not api_key:
            messagebox.showerror("エラー", "Gemini API Keyが設定されていません。")
            return

        # オプション確認
        skip_existing = messagebox.askyesno("オプション", "既にペルソナ設定があるアカウントはスキップしますか？")
        
        if not messagebox.askyesno("確認", f"全 {len(self.accounts)} アカウントのペルソナ抽出を開始します。\nこれには時間がかかります。\n開始してよろしいですか？"):
            return

        # スレッドで実行
        threading.Thread(target=self.run_bulk_extract, args=(api_key, skip_existing), daemon=True).start()

    def run_bulk_extract(self, api_key, skip_existing):
        self.log("--- ペルソナ一括抽出を開始します ---")
        self.bulk_extract_btn.configure(state="disabled", text="一括抽出中...")
        
        personas = PersonaManager.load()
        client = GeminiClient(api_key)
        
        from playwright.sync_api import sync_playwright

        try:
            with sync_playwright() as p:
                for i, account in enumerate(self.accounts):
                    username = account["username"]
                    
                    if skip_existing and username in personas and personas[username].get("persona"):
                        self.log(f"スキップ: {username} (設定済み)")
                        continue

                    self.log(f"抽出中 ({i+1}/{len(self.accounts)}): {username}")
                    self.update_account_status(username, "分析中...", "purple")
                    
                    base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                    user_data_dir = os.path.join(base_path, "profiles", username)
                    
                    if not os.path.exists(user_data_dir):
                        self.log(f"スキップ: {username} (プロファイルなし)")
                        self.update_account_status(username, "待機中", "gray")
                        continue

                    try:
                        browser = p.firefox.launch_persistent_context(
                            user_data_dir=user_data_dir,
                            headless=False, # 視覚的に確認
                            viewport={"width": 1280, "height": 720}
                        )
                        page = browser.pages[0]
                        
                        # プロフィールへ
                        page.goto(f"https://twitter.com/{username.replace('@', '')}")
                        page.wait_for_timeout(3000)
                        
                        # 凍結チェック
                        if page.locator('text="Account suspended"').is_visible() or \
                           page.locator('text="アカウントは凍結されています"').is_visible() or \
                           page.locator('[data-testid="emptyState"]').is_visible(): # 凍結時は空の状態になることが多い
                            
                            self.log(f"警告: {username} は凍結されている可能性があります。")
                            self.update_account_status(username, "凍結", "red")
                            browser.close()
                            continue

                        # プロフィール文取得
                        profile_text = ""
                        try:
                            profile_elm = page.locator('[data-testid="UserDescription"]').first
                            if profile_elm.is_visible():
                                profile_text = profile_elm.inner_text()
                        except:
                            pass
                        
                        # 過去の投稿取得
                        recent_posts = []
                        try:
                            page.evaluate("window.scrollBy(0, 500)")
                            page.wait_for_timeout(1000)
                            articles = page.locator('article').all()
                            for article in articles[:5]:
                                try:
                                    text_elm = article.locator('[data-testid="tweetText"]').first
                                    if text_elm.is_visible():
                                        recent_posts.append(text_elm.inner_text())
                                except:
                                    continue
                        except:
                            pass
                        
                        browser.close()
                        
                        # AI生成
                        if client.model:
                            result = client.generate_persona(profile_text, "\n".join(recent_posts))
                            if result:
                                personas[username] = result
                                PersonaManager.save(personas)
                                self.log(f"抽出成功: {username}")
                                self.update_account_status(username, "完了", "green")
                            else:
                                self.log(f"AI生成失敗: {username}")
                                self.update_account_status(username, "AIエラー", "orange")
                        else:
                             self.log("Geminiモデルが利用できません。")
                             break

                    except Exception as e:
                        self.log(f"エラー ({username}): {e}")
                        self.update_account_status(username, "エラー", "red")
                        try:
                            browser.close()
                        except:
                            pass
                    
                    time.sleep(1) # 間隔

        except Exception as e:
            self.log(f"一括抽出全体エラー: {e}")
        finally:
            self.bulk_extract_btn.configure(state="normal", text="全アカウント ペルソナ一括抽出 (AI)")
            self.log("--- 一括抽出完了 ---")
            # ステータスリセット（完了以外）
            for account in self.accounts:
                u = account["username"]
                # 現在のラベル色を取得して、完了(green)や凍結(red)以外なら待機中に戻す... としたいが
                # 簡易的に、処理が終わったら数秒後に待機中に戻すのが親切かも。
                # ここではそのままにしておく。

    def open_settings(self):
        """設定画面を開く"""
        if self.is_running:
            messagebox.showwarning("警告", "実行中は設定を変更できません。")
            return
        SettingsWindow(self, self.settings, self.save_settings)

    def save_settings(self, new_settings):
        """設定を保存して反映"""
        self.settings = new_settings
        SettingsManager.save(self.settings)
        self.log("設定を保存しました。")

    def create_main_area(self):
        """メインエリア（ログ・ステータス）の作成"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # ステータス表示 (全体)
        self.status_label = ctk.CTkLabel(self.main_frame, text="ステータス: 待機中", font=ctk.CTkFont(family=FONT_FAMILY, size=16))
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # タブビュー作成
        self.progressbar = ctk.CTkProgressBar(self.main_frame)
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.grid(row=2, column=0, sticky="nsew")
        
        self.tab_log = self.tab_view.add("ログ")
        self.tab_accounts = self.tab_view.add("アカウント一覧")
        # self.tab_target = self.tab_view.add("拡散・交流") # v2.0で有効化
        self.tab_view._segmented_button.configure(font=ctk.CTkFont(family=FONT_FAMILY))
        
        # --- ログタブ ---
        self.tab_log.grid_columnconfigure(0, weight=1)
        self.tab_log.grid_rowconfigure(0, weight=1)
        
        self.log_textbox = ctk.CTkTextbox(self.tab_log, width=600, height=400, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.log_textbox.grid(row=0, column=0, sticky="nsew")
        self.log_textbox.configure(state="disabled")

        # --- アカウント一覧タブ ---
        self.tab_accounts.grid_columnconfigure(0, weight=1)
        self.tab_accounts.grid_rowconfigure(0, weight=1)
        # アカウント一覧フレーム
        # アカウント一覧フレーム
        self.account_list_frame = ctk.CTkScrollableFrame(self.tab_view.tab("アカウント一覧"), width=700, height=400)
        self.account_list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # 一括操作ボタンエリア
        bulk_action_frame = ctk.CTkFrame(self.tab_view.tab("アカウント一覧"), fg_color="transparent")
        bulk_action_frame.pack(pady=5, padx=10, fill="x")
        
        # 全アカウントペルソナ一括抽出ボタン
        self.bulk_extract_btn = ctk.CTkButton(bulk_action_frame, text="全アカウント ペルソナ一括抽出 (AI)", 
                                              command=self.bulk_auto_extract,
                                              fg_color="purple", hover_color="#500050",
                                              font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"))
        self.bulk_extract_btn.pack(side="right", padx=5)

        # 凍結アカウント削除ボタン
        self.delete_frozen_btn = ctk.CTkButton(bulk_action_frame, text="凍結アカウントを削除", 
                                               command=self.delete_frozen_accounts,
                                               fg_color="darkred", hover_color="#800000",
                                               font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"))
        self.delete_frozen_btn.pack(side="right", padx=5)

        # 既存のUI更新メソッドを呼ぶ
        self.account_labels = {} # username -> {"status_label": label, "row_frame": frame}
        self.refresh_account_list()
        
        # 保存されたステータスを復元
        self.load_account_statuses()

        # --- 拡散・交流タブ (v2.0) ---
        # self.target_action_frame = TargetActionFrame(self.tab_target, self.start_target_process)
        # self.target_action_frame.pack(fill="both", expand=True, padx=10, pady=10)


    def refresh_account_list(self):
        """アカウントリストを再描画"""
        # 既存のウィジェットをクリア
        for widget in self.account_list_frame.winfo_children():
            widget.destroy()
        self.account_labels = {}
        
        # アカウントリストを更新
        self.accounts = self.get_accounts()
        accounts = self.accounts

        # 実行数プルダウンの更新 (v1.6)
        if hasattr(self, 'max_count_combo'):
            count = len(accounts)
            if count > 0:
                values = ["All"] + [str(i) for i in range(1, count + 1)]
                self.max_count_combo.configure(values=values)
            else:
                self.max_count_combo.configure(values=["All"])

        if not accounts:
            ctk.CTkLabel(self.account_list_frame, text="アカウントが見つかりません").pack(pady=10)
            return

        # 保存されたステータスを読み込む
        status_data = {}
        STATUS_FILE = os.path.join(BASE_DIR, "status_cache.json")
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    status_data = json.load(f)
            except:
                pass

        for i, account in enumerate(accounts):
            username = account['username']
            
            # キャッシュから表示名と最終実行日時を取得
            display_name = username
            last_run_str = "未実行"
            if username in status_data:
                if "display_name" in status_data[username]:
                    display_name = f"{status_data[username]['display_name']} ({username})"
                if "last_run" in status_data[username]:
                    try:
                        dt = datetime.datetime.fromisoformat(status_data[username]["last_run"])
                        last_run_str = dt.strftime("%m/%d %H:%M")
                    except:
                        pass
            
            # 行フレーム
            row_frame = ctk.CTkFrame(self.account_list_frame)
            row_frame.pack(fill="x", padx=5, pady=2)
            row_frame.grid_columnconfigure(1, weight=1)

            # ユーザー名 (表示名)
            ctk.CTkLabel(row_frame, text=display_name, width=200, anchor="w").grid(row=0, column=0, padx=10, pady=5)
            
            # ステータス
            status_label = ctk.CTkLabel(row_frame, text="待機中", text_color="gray", anchor="w")
            status_label.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

            # 最終実行日時
            ctk.CTkLabel(row_frame, text=last_run_str, width=100, text_color="gray", font=ctk.CTkFont(size=10)).grid(row=0, column=2, padx=5, pady=5)
            
            # 単体実行ボタン (v1.6)
            run_btn = ctk.CTkButton(row_frame, text="▶", width=40,
                                    command=lambda u=username: self.start_single_process(u),
                                    fg_color="green", hover_color="darkgreen",
                                    font=ctk.CTkFont(family=FONT_FAMILY, size=12))
            run_btn.grid(row=0, column=3, padx=2, pady=5)

            # ブラウザ起動ボタン (v1.1)
            browser_btn = ctk.CTkButton(row_frame, text="ブラウザ", width=70, 
                                        command=lambda u=username: self.open_manual_browser(u),
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=12))
            browser_btn.grid(row=0, column=4, padx=2, pady=5)

            # ペルソナ設定ボタン (v1.5)
            persona_btn = ctk.CTkButton(row_frame, text="設定", width=60,
                                        command=lambda u=username: self.open_persona_settings(u),
                                        fg_color="purple", hover_color="#500050",
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=12))
            persona_btn.grid(row=0, column=5, padx=2, pady=5)
            
            self.account_labels[username] = status_label

    def update_account_status(self, username, status, color=None, **kwargs):
        """特定のアカウントのステータス表示を更新"""
        if username in self.account_labels:
            label = self.account_labels[username]
            
            def _update():
                label.configure(text=status)
                if color:
                    label.configure(text_color=color)
                else:
                    # デフォルト色に戻す処理が必要ならここ（テーマ依存なので難しいが、とりあえず指定なしはそのまま）
                    pass
            
            self.after(0, _update)
            
            # ステータス変更時に保存
            self.save_account_status(username, status, color, **kwargs)

    def save_account_status(self, username, status, color, **kwargs):
        """ステータスをJSONに保存"""
        STATUS_FILE = os.path.join(BASE_DIR, "status_cache.json")
        try:
            data = {}
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            if username not in data:
                data[username] = {}
                
            data[username]["status"] = status
            data[username]["color"] = color
            data[username]["timestamp"] = datetime.datetime.now().isoformat()
            
            # 追加情報（最終実行時刻、表示名など）の更新
            for key, value in kwargs.items():
                data[username][key] = value
            
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"ステータス保存エラー: {e}")

    def load_account_statuses(self):
        """保存されたステータスを読み込んで反映"""
        STATUS_FILE = os.path.join(BASE_DIR, "status_cache.json")
        if not os.path.exists(STATUS_FILE):
            return
            
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for username, info in data.items():
                if username in self.account_labels:
                    status = info.get("status", "待機中")
                    color = info.get("color", "gray")
                    # UI更新
                    self.account_labels[username].configure(text=status, text_color=color)
        except Exception as e:
            print(f"ステータス読み込みエラー: {e}")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def log(self, message):
        """ログエリアにメッセージを出力"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {message}\n"
        
        # コンソールへの出力 (ウィンドウモードでのクラッシュ防止)
        if sys.stdout:
            try:
                print(full_msg.strip())
            except Exception:
                pass # 出力に失敗しても無視する
        
        def _update():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", full_msg)
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        
        self.after(0, _update)

    def update_status(self, text):
        """ステータスラベルを更新"""
        self.after(0, lambda: self.status_label.configure(text=f"ステータス: {text}"))

    def start_setup(self):
        """初回ログイン設定（手動）"""
        if self.is_running: return
        self.is_running = True
        self.stop_event.clear()
        self.pause_event.set() # 再開状態にする
        self.update_ui_state(running=True)
        self.update_status("初回ログイン設定中...")
        self.log("--- 初回ログイン設定を開始します ---")
        
        # 設定値を使用（ヘッドレスは手動設定時は常にFalse）
        thread = threading.Thread(target=self.run_setup)
        thread.daemon = True
        thread.start()

    def start_single_process(self, target_username):
        """単一アカウントの実行"""
        if self.is_running: return
        
        self.is_running = True
        self.stop_event.clear()
        self.pause_event.set()
        self.update_ui_state(running=True)
        self.update_status(f"単体実行中: {target_username}")
        self.log(f"--- 単体実行を開始します: {target_username} ---")
        
        thread = threading.Thread(target=self.run_auto_post, args=(target_username,))
        thread.daemon = True
        thread.start()

    def start_process(self):
        """自動投稿開始 (一括)"""
        if self.is_running: return
        
        if not os.path.exists(ACCOUNTS_FILE):
            messagebox.showerror("エラー", f"{ACCOUNTS_FILE} が見つかりません。")
            return

        # 実行数の取得
        max_count = None
        count_str = self.max_count_combo.get().strip()
        if count_str and count_str.lower() != "all":
            try:
                max_count = int(count_str)
                if max_count <= 0: raise ValueError
            except:
                messagebox.showerror("エラー", "実行数には正の整数か 'All' を選択してください。")
                return

        self.is_running = True
        self.stop_event.clear()
        self.pause_event.set() # 再開状態にする
        self.update_ui_state(running=True)
        self.update_status("自動投稿実行中")
        self.log("--- 自動投稿処理を開始します ---")
        self.log(f"設定: ヘッドレス={self.settings['headless']}, 待機={self.settings['wait_min']}-{self.settings['wait_max']}秒, GIF確率={self.settings['gif_probability']}%, いいね={self.settings['auto_like']}")
        if max_count:
            self.log(f"実行上限: {max_count}件 (最終実行日時が古い順)")
        
        # リストをリセット
        self.refresh_account_list()

        thread = threading.Thread(target=self.run_auto_post, args=(None, max_count))
        thread.daemon = True
        thread.start()

    def open_manual_browser(self, username):
        """手動操作用ブラウザを起動"""
        if self.is_running:
            messagebox.showwarning("警告", "自動投稿実行中はブラウザを起動できません。")
            return
        
        # 既に起動中のブラウザがある場合、PCスペックへの配慮として警告を出すか、
        # あるいはプロファイルロックの観点から、同じアカウントの二重起動は絶対に防ぐ必要がある。
        if username in self.active_manual_users:
            messagebox.showwarning("警告", f"{username} のブラウザは既に起動中です。")
            return

        self.log(f"ブラウザ起動リクエスト: {username}")
        thread = threading.Thread(target=self.run_manual_browser_thread, args=(username,))
        thread.daemon = True
        thread.start()

    def run_manual_browser_thread(self, username):
        with self.manual_lock:
            self.manual_browsers += 1
            self.active_manual_users.add(username)
            self.update_ui_state_manual(active=True)
        
        self.update_account_status(username, "操作中...", "blue")
        
        base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        user_data_path = os.path.join(base_path, PROFILES_DIR, username)
        
        try:
            with sync_playwright() as p:
                context = p.firefox.launch_persistent_context(
                    user_data_dir=user_data_path,
                    headless=False,
                    viewport={"width": 1280, "height": 720},
                    locale="ja-JP",
                    timezone_id="Asia/Tokyo",
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
                    ignore_default_args=["--enable-automation"]
                )
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                """)
                
                page = context.pages[0]
                page.goto("https://x.com/home")
                
                self.log(f"ブラウザ起動中: {username}")
                
                self.log(f"ブラウザ起動中: {username}")
                
                # ブラウザが閉じられるまで待機
                # page.is_closed() だけでは検知できない場合があるため、evaluateで生存確認を行う
                while True:
                    try:
                        if page.is_closed():
                            break
                        # 軽い処理を実行して接続確認
                        page.evaluate("1")
                    except Exception:
                        # エラーが発生したらブラウザが閉じられた/切断されたとみなす
                        break
                    time.sleep(1)
                    
                self.log(f"ブラウザが閉じられました: {username}")
                
        except Exception as e:
            self.log(f"ブラウザ起動エラー ({username}): {e}")
            messagebox.showerror("エラー", f"ブラウザ起動に失敗しました。\n{e}")
        
        finally:
            self.update_account_status(username, "待機中", "gray")
            with self.manual_lock:
                self.manual_browsers -= 1
                if username in self.active_manual_users:
                    self.active_manual_users.remove(username)
                if self.manual_browsers == 0:
                    self.update_ui_state_manual(active=False)

    def update_ui_state_manual(self, active):
        """手動ブラウザ起動中のUI制御"""
        # 手動ブラウザが開いている間は、自動投稿開始ボタンを無効化する
        if active:
            self.start_button.configure(state="disabled")
            self.setup_btn.configure(state="disabled")
            self.update_status("手動操作中")
        else:
            # 他に何も動いていなければ有効化
            if not self.is_running:
                self.start_button.configure(state="normal")
                self.setup_btn.configure(state="normal")
                self.update_status("待機中")


    def start_target_process(self, urls, actions, texts):
        """拡散・交流アクション開始"""
        if self.is_running: return
        
        if not os.path.exists(ACCOUNTS_FILE):
            messagebox.showerror("エラー", f"{ACCOUNTS_FILE} が見つかりません。")
            return

        self.is_running = True
        self.stop_event.clear()
        self.pause_event.set()
        self.update_ui_state(running=True)
        self.update_status("拡散・交流アクション実行中")
        self.log("--- 拡散・交流アクションを開始します ---")
        self.log(f"対象URL数: {len(urls)}, アクション: {actions}")

        # リストをリセット
        self.refresh_account_list()

        thread = threading.Thread(target=self.run_target_automation, args=(urls, actions, texts))
        thread.daemon = True
        thread.start()

    def run_target_automation(self, urls, actions, texts):
        """拡散・交流の実行ループ"""
        accounts = self.get_accounts()
        if not accounts:
            self.after(0, self.finish_process)
            return

        with sync_playwright() as p:
            for i, account in enumerate(accounts):
                if self.stop_event.is_set():
                    self.log("中断します。")
                    break

                # 一時停止チェック
                if not self.pause_event.is_set():
                    self.log("一時停止中...")
                    self.pause_event.wait()
                    if self.stop_event.is_set(): break
                    self.log("再開します。")

                username = account['username'].strip()
                password = account.get('password', '').strip()
                
                self.log(f"--- アカウント処理中: {username} ({i+1}/{len(accounts)}) ---")
                self.update_status(f"処理中: {username}")
                self.update_account_status(username, "処理中...", "orange")
                
                base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                user_data_path = os.path.join(base_path, PROFILES_DIR, username)
                
                try:
                    context = p.firefox.launch_persistent_context(
                        user_data_dir=user_data_path,
                        headless=self.settings["headless"],
                        viewport={"width": 1280, "height": 720},
                        locale="ja-JP",
                        timezone_id="Asia/Tokyo",
                        # Windows ChromeのUAに偽装
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        ignore_default_args=["--enable-automation"],
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    """)
                    
                    page = context.pages[0]
                    
                    # 各URLに対してアクション実行
                    for url in urls:
                        if self.stop_event.is_set(): break
                        self.process_target_action(page, url, actions, texts)
                        time.sleep(2) # URL間の短い待機

                    context.close()
                    self.log(f"完了: {username}")
                    self.update_account_status(username, "完了", "green")

                except Exception as e:
                    self.log(f"エラー ({username}): {e}")
                    self.update_account_status(username, "エラー", "red")
                
                if i < len(accounts) - 1:
                    wait_time = random.randint(5, 15) # アクション間の待機は短めでOKとする（または設定を使う）
                    self.log(f"次のアカウントまで {wait_time}秒 待機します...")
                    time.sleep(wait_time)

        self.after(0, self.finish_process)

    def process_target_action(self, page, url, actions, texts):
        """単一URLに対するアクション実行"""
        self.log(f"URLへ移動: {url}")
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            # ログインチェック（簡易）
            if page.locator('[data-testid="login"]').is_visible():
                self.log("ログインが必要です。このアカウントはスキップします。")
                return

            # 1. いいね
            if actions["like"]:
                try:
                    like_btn = page.locator('[data-testid="like"]').first
                    unlike_btn = page.locator('[data-testid="unlike"]').first
                    
                    if unlike_btn.is_visible():
                        self.log("既にいいね済みです。")
                    elif like_btn.is_visible():
                        like_btn.click()
                        self.log("いいねしました。")
                        page.wait_for_timeout(1000)
                    else:
                        self.log("いいねボタンが見つかりません。")
                except Exception as e:
                    self.log(f"いいね失敗: {e}")

            # 2. リポスト / 引用RP
            if actions["repost"] or actions["quote"]:
                try:
                    retweet_btn = page.locator('[data-testid="retweet"]').first
                    unretweet_btn = page.locator('[data-testid="unretweet"]').first
                    
                    if unretweet_btn.is_visible():
                        self.log("既にリポスト済みです。")
                    elif retweet_btn.is_visible():
                        retweet_btn.click()
                        page.wait_for_timeout(1000)
                        
                        if actions["quote"]:
                            # 引用リポスト
                            quote_menu = page.get_by_role("menuitem", name="引用").or_(page.locator('[data-testid="retweetConfirm"]')) # 英語だと Quote? data-testidで探すのが確実
                            # data-testid="retweetConfirm" は通常のリポスト確認。引用は別。
                            # メニューが出る: [Retweet, Quote Tweet]
                            # data-testid="retweetMenuItemRetweet"
                            # data-testid="retweetMenuItemQuote"
                            
                            quote_btn = page.locator('[data-testid="retweetMenuItemQuote"]')
                            if quote_btn.is_visible():
                                quote_btn.click()
                                page.wait_for_timeout(1000)
                                
                                # テキスト入力
                                text = random.choice(texts)
                                self.log(f"引用テキスト: {text}")
                                
                                # 入力欄: [data-testid="tweetTextarea_0"]
                                input_area = page.locator('[data-testid="tweetTextarea_0"]')
                                if input_area.is_visible():
                                    self.safe_type(page, '[data-testid="tweetTextarea_0"]', text)
                                    page.wait_for_timeout(1000)
                                    
                                    # 投稿ボタン: [data-testid="tweetButton"]
                                    page.locator('[data-testid="tweetButton"]').click()
                                    self.log("引用リポストしました。")
                                    page.wait_for_timeout(3000)
                            else:
                                self.log("引用メニューが見つかりません。")
                                # メニューを閉じるためにどこか押すか、リロード
                                page.keyboard.press("Escape")

                        elif actions["repost"]:
                            # 通常リポスト
                            confirm_btn = page.locator('[data-testid="retweetConfirm"]')
                            if confirm_btn.is_visible():
                                confirm_btn.click()
                                self.log("リポストしました。")
                                page.wait_for_timeout(1000)
                            else:
                                # メニュー項目の方かも (data-testid="retweetMenuItemRetweet")
                                rt_menu_item = page.locator('[data-testid="retweetMenuItemRetweet"]')
                                if rt_menu_item.is_visible():
                                    rt_menu_item.click()
                                    self.log("リポストしました。")
                                    page.wait_for_timeout(1000)
                    else:
                        self.log("リポストボタンが見つかりません。")
                except Exception as e:
                    self.log(f"リポスト処理失敗: {e}")

            # 3. リプライ
            if actions["reply"]:
                try:
                    # リプライエリアは通常、投稿の下にあるが、詳細ページでは [data-testid="reply"] ボタンを押すか、下の入力欄を使う
                    # 詳細ページ(status/xxx)にいるはずなので、下の入力欄 [data-testid="tweetTextarea_0"] があるはず
                    # または [data-testid="reply"] ボタンを押してモーダルを出す
                    
                    # 確実なのは reply ボタンを押すこと
                    reply_btn = page.locator('[data-testid="reply"]').first
                    if reply_btn.is_visible():
                        reply_btn.click()
                        page.wait_for_timeout(1000)
                        
                        text = random.choice(texts)
                        self.log(f"リプライテキスト: {text}")
                        
                        input_area = page.locator('[data-testid="tweetTextarea_0"]')
                        if input_area.is_visible():
                            self.safe_type(page, '[data-testid="tweetTextarea_0"]', text)
                            page.wait_for_timeout(1000)
                            
                            page.locator('[data-testid="tweetButton"]').click()
                            self.log("リプライしました。")
                            page.wait_for_timeout(3000)
                    else:
                        self.log("リプライボタンが見つかりません。")
                except Exception as e:
                    self.log(f"リプライ処理失敗: {e}")

        except Exception as e:
            self.log(f"URL処理エラー: {e}")


    def stop_process(self):
        """停止処理（2段階: 停止リクエスト -> 強制終了）"""
        if not self.is_running: return

        if not self.stop_event.is_set():
            # 1回目: 停止リクエスト
            self.stop_event.set()
            self.pause_event.set() # 一時停止中なら解除してループを回す
            self.log("停止リクエストを受け付けました。現在のアカウント処理が完了次第停止します...")
            self.update_status("停止処理中...")
            
            # ボタンの表示を変更
            self.stop_button.configure(text="強制停止", fg_color="#D32F2F", hover_color="#B71C1C")
        else:
            # 2回目: 強制終了
            if messagebox.askyesno("強制終了", "プロセスを強制的に終了しますか？\nブラウザが正しく閉じられない可能性があります。"):
                self.log("ユーザーによる強制終了。")
                # 強制的にアプリを閉じる
                self.destroy()
                sys.exit(0)
            self.stop_event.set()
            self.pause_event.set() # 一時停止中なら解除して停止処理へ進める

    def toggle_pause(self):
        """一時停止/再開の切り替え"""
        if not self.is_running: return
        
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_button.configure(text="再開", fg_color="green", hover_color="darkgreen")
            self.update_status("一時停止中")
            self.log("一時停止しました。")
        else:
            self.pause_event.set()
            self.pause_button.configure(text="一時停止", fg_color="orange", hover_color="darkorange")
            self.update_status("自動投稿実行中")
            self.log("再開しました。")

    def update_ui_state(self, running):
        """UIの有効/無効状態を更新"""
        if running:
            self.start_button.configure(state="disabled")
            self.setup_btn.configure(state="disabled")
            self.settings_button.configure(state="disabled") # 実行中は設定不可
            self.stop_button.configure(state="normal")
            self.pause_button.configure(state="normal", text="一時停止", fg_color="orange")
        else:
            self.start_button.configure(state="normal")
            self.setup_btn.configure(state="normal")
            self.settings_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.pause_button.configure(state="disabled", text="一時停止", fg_color="gray")
            self.update_status("待機中")

    def finish_process(self):
        self.is_running = False
        self.update_ui_state(running=False)
        self.log("処理が終了しました。")
        self.update_status("完了")

    def get_accounts(self):
        accounts = []
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'username' in row:
                        accounts.append(row)
        except Exception as e:
            self.log(f"CSV読み込みエラー: {e}")
        return accounts

    def safe_type(self, page, selector, text):
        """クリップボード経由で安全に入力するヘルパー関数"""
        try:
            element = page.locator(selector).first
            element.click()
            page.wait_for_timeout(500)
            
            # クリップボードにセット (json.dumpsでエスケープ)
            page.evaluate(f"navigator.clipboard.writeText({json.dumps(text)})")
            
            if sys.platform == "darwin":
                page.keyboard.press("Meta+V")
            else:
                page.keyboard.press("Control+V")
            page.wait_for_timeout(500)
        except Exception as e:
            self.log(f"入力エラー（フォールバックします）: {e}")
            page.locator(selector).first.fill(text)

    def run_setup(self):
        """手動ログイン用ループ"""
        accounts = self.get_accounts()
        if not accounts:
            self.after(0, self.finish_process)
            return

        with sync_playwright() as p:
            for i, account in enumerate(accounts):
                if self.stop_event.is_set():
                    self.log("ユーザーによる停止操作のため中断します。")
                    break
                
                # 一時停止チェック
                if not self.pause_event.is_set():
                    self.log("一時停止中...")
                    self.pause_event.wait()
                    self.log("再開します。")

                username = account['username'].strip()
                self.log(f"設定中: {username}")
                self.update_status(f"設定中: {username}")
                self.update_account_status(username, "設定中...", "orange")
                
                base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                user_data_path = os.path.join(base_path, PROFILES_DIR, username)
                
                try:
                    context = p.firefox.launch_persistent_context(
                        user_data_dir=user_data_path,
                        headless=False, # 手動設定は常にFalse
                        viewport={"width": 1280, "height": 720},
                        locale="ja-JP",
                        timezone_id="Asia/Tokyo",
                        # Windows ChromeのUAに偽装
                        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        ignore_default_args=["--enable-automation"],
                        args=["--disable-blink-features=AutomationControlled"]
                    )
                    
                    # ステルス化
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    """)

                    page = context.pages[0]
                    page.goto("https://x.com/home")
                    
                    # ログイン確認
                    try:
                        page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
                        self.log(f"ログイン済みです: {username}")
                        self.update_account_status(username, "設定完了", "green")
                        page.wait_for_timeout(1000)
                    except:
                        self.log(f"ログインしてください: {username}")
                        self.log("ブラウザでログイン操作を行ってください。完了したらブラウザを閉じてください（または自動で検知して閉じます）。")
                        self.update_account_status(username, "ログイン待ち...", "blue")
                        
                        # ログイン完了を監視 (最大5分)
                        try:
                            # 停止フラグを見ながら待機するのは難しいので、ループで回す
                            for _ in range(300): # 300秒
                                if self.stop_event.is_set(): break
                                try:
                                    if page.locator('[data-testid="SideNav_NewTweet_Button"]').is_visible():
                                        self.log("ログイン成功を検知しました。保存して終了します。")
                                        self.update_account_status(username, "設定完了", "green")
                                        page.wait_for_timeout(3000)
                                        break
                                except:
                                    pass
                                page.wait_for_timeout(1000)
                        except:
                            self.log("タイムアウトまたはブラウザが閉じられました。")
                            self.update_account_status(username, "タイムアウト", "red")
                    
                    context.close()
                    
                except Exception as e:
                    self.log(f"エラー: {e}")
                    self.update_account_status(username, "エラー", "red")

        self.after(0, self.finish_process)

    def generate_post_content(self, username):
        """投稿内容を生成 (AI or 定型文)"""
        # AIモード判定
        if self.settings.get("ai_mode", False) and self.settings.get("gemini_api_key", ""):
            personas = PersonaManager.load()
            user_data = personas.get(username)
            
            if user_data and user_data.get("persona"):
                self.log(f"AIモードで投稿を生成中... ({username})")
                try:
                    client = GeminiClient(self.settings["gemini_api_key"])
                    if client.model:
                        tone = user_data.get("tone", "普通")
                        examples = "\n".join(user_data.get("example_posts", []))
                        content = client.generate_post(user_data["persona"], tone, examples)
                        if content:
                            return content
                except Exception as e:
                    import traceback
                    self.log(f"AI生成エラー（定型文に切り替えます）: {e}")
                    print(traceback.format_exc()) # コンソールにも詳細を表示

        # フォールバック: 定型文生成
        time_slot = "morning"
        hour = datetime.datetime.now().hour
        if 11 <= hour < 16:
            time_slot = "day"
        elif 16 <= hour < 24:
            time_slot = "night"
        
        templates = POST_PATTERNS[time_slot]
        base = random.choice(templates)
        emoji = random.choice(EMOJIS)
        action = random.choice(ACTIONS)
        
        return f"{base.format(emoji=emoji)} {action} {emoji}"

    def delete_frozen_accounts(self):
        """凍結ステータスのアカウントをCSVから削除"""
        if not messagebox.askyesno("確認", "ステータスが「凍結」のアカウントをCSVから削除しますか？\nこの操作は取り消せません。"):
            return

        current_accounts = self.get_accounts()
        new_accounts = []
        deleted_count = 0
        
        # 現在のステータスを確認してフィルタリング
        # 注意: ステータスはUI上のラベルで管理されているため、self.account_labelsを参照するか、
        # 簡易的に「凍結」とマークされたものを除外するロジックが必要。
        # ここでは、UIのラベル状態を見るのが確実。
        
        frozen_users = set()
        for username, widgets in self.account_labels.items():
            label = widgets["status_label"]
            if label.cget("text") == "凍結":
                frozen_users.add(username)
        
        if not frozen_users:
            messagebox.showinfo("情報", "「凍結」ステータスのアカウントはありません。")
            return

        for acc in current_accounts:
            if acc["username"] in frozen_users:
                deleted_count += 1
            else:
                new_accounts.append(acc)
        
        if deleted_count > 0:
            try:
                with open(ACCOUNTS_FILE, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['username', 'password']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(new_accounts)
                
                self.accounts = new_accounts
                self.refresh_account_list()
                messagebox.showinfo("完了", f"{deleted_count} 件のアカウントを削除しました。")
                self.log(f"{deleted_count} 件の凍結アカウントを削除しました。")
            except Exception as e:
                messagebox.showerror("エラー", f"削除中にエラーが発生しました: {e}")
        else:
            messagebox.showinfo("情報", "削除対象のアカウントはありませんでした。")

    def run_auto_post(self, target_username=None, max_count=None):
        all_accounts = self.get_accounts()
        if not all_accounts:
            self.after(0, self.finish_process)
            return

        accounts_to_run = []

        if target_username:
            # 単体実行
            accounts_to_run = [acc for acc in all_accounts if acc['username'] == target_username]
            if not accounts_to_run:
                self.log(f"アカウントが見つかりません: {target_username}")
                self.after(0, self.finish_process)
                return
        else:
            # 一括実行 (ソート & 制限)
            
            # キャッシュから最終実行日時を取得してソート
            # 未実行(None)が一番先頭に来るようにする -> 空文字""は文字列比較で小さいので工夫が必要
            # datetime.min を使う
            
            status_data = {}
            STATUS_FILE = os.path.join(BASE_DIR, "status_cache.json")
            if os.path.exists(STATUS_FILE):
                try:
                    with open(STATUS_FILE, "r", encoding="utf-8") as f:
                        status_data = json.load(f)
                except:
                    pass
            
            def get_last_run(acc):
                u = acc['username']
                if u in status_data and "last_run" in status_data[u]:
                    return status_data[u]["last_run"]
                return "0000-01-01T00:00:00" # 未実行は最古

            # 昇順ソート (古い順 = 実行すべき順)
            all_accounts.sort(key=get_last_run)
            
            if max_count:
                accounts_to_run = all_accounts[:max_count]
            else:
                accounts_to_run = all_accounts

        self.log(f"{len(accounts_to_run)}件のアカウントを処理します。")

        with sync_playwright() as p:
            for i, account in enumerate(accounts_to_run):
                if self.stop_event.is_set():
                    self.log("ユーザーによる停止操作のため中断します。")
                    break

                # 一時停止チェック
                if not self.pause_event.is_set():
                    self.log("一時停止中...")
                    self.pause_event.wait()
                    if self.stop_event.is_set(): break # 待機中に停止された場合
                    self.log("再開します。")

                username = account['username'].strip()
                password = account.get('password', '').strip()
                
                self.log(f"--- アカウント処理中: {username} ({i+1}/{len(accounts_to_run)}) ---")
                self.update_status(f"処理中: {username} ({i+1}/{len(accounts_to_run)})")
                self.update_account_status(username, "処理中...", "orange")
                
                base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                user_data_path = os.path.join(base_path, PROFILES_DIR, username)
                
                try:
                    context = p.firefox.launch_persistent_context(
                        user_data_dir=user_data_path,
                        headless=self.settings["headless"], # 設定値を使用
                        viewport={"width": 1280, "height": 720},
                        locale="ja-JP",
                        timezone_id="Asia/Tokyo",
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
                        ignore_default_args=["--enable-automation"]
                    )
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    """)
                    
                    page = context.pages[0]
                    self.process_account(page, username, password)
                    context.close()
                    self.log(f"完了: {username}")
                    self.update_account_status(username, "完了", "green", last_run=datetime.datetime.now().isoformat())

                except Exception as e:
                    self.log(f"エラー ({username}): {e}")
                    self.update_account_status(username, "エラー", "red")
                
                if i < len(accounts_to_run) - 1:
                    wait_time = random.randint(self.settings["wait_min"], self.settings["wait_max"]) # 設定値を使用
                    self.log(f"次のアカウントまで {wait_time}秒 待機します...")
                    self.update_status(f"待機中 ({wait_time}秒)...")
                    
                    # 待機中も停止/一時停止をチェックできるように小刻みに待つ
                    for _ in range(wait_time):
                        if self.stop_event.is_set(): break
                        while not self.pause_event.is_set():
                            time.sleep(1)
                            if self.stop_event.is_set(): break
                        time.sleep(1)

        self.after(0, self.finish_process)

    def process_account(self, page, username, password):
        """1アカウント分の処理フロー"""
        try:
            # Xホームへ
            self.log("ホーム画面へ移動中...")
            try:
                page.goto("https://x.com/home", timeout=60000, wait_until="domcontentloaded")
                # 完全に読み込まれるのを少し待つ（networkidleは厳しすぎるため避ける）
                page.wait_for_timeout(3000)
            except Exception as e:
                self.log(f"ページ移動でタイムアウトしましたが続行します: {e}")

            # ログイン判定
            is_logged_in = False
            try:
                # ログイン状態ならサイドバーのポストボタンなどが見えるはず
                # 複数の可能性を考慮
                page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=5000)
                is_logged_in = True
                self.log("ログイン済みを確認しました。")
            except:
                self.log("ログインしていないようです。ログイン処理を開始します。")

            if not is_logged_in:
                # ログインフロー
                if "login" not in page.url:
                    page.goto("https://x.com/i/flow/login", wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)

                # ユーザー名入力
                self.log("ユーザー名入力欄を探しています...")
                try:
                    username_input = page.locator('input[autocomplete="username"]').or_(page.locator('input[name="text"]'))
                    username_input.first.wait_for(state="visible", timeout=10000)
                    
                    # クリップボード入力を使用
                    self.safe_type(page, 'input[autocomplete="username"], input[name="text"]', username)
                    self.log("ユーザー名を入力しました。")
                    
                    # 次へ
                    next_btn = page.get_by_role("button", name="次へ").or_(page.get_by_role("button", name="Next"))
                    next_btn.click()
                except Exception as e:
                    raise Exception(f"ユーザー名入力でエラー: {e}")

                # パスワード入力
                page.wait_for_timeout(5000) # 待機時間を延長
                self.log("パスワード入力欄を探しています...")
                try:
                    password_input = page.locator('input[name="password"]')
                    password_input.wait_for(state="visible", timeout=10000)
                    
                    # クリップボード入力を使用
                    self.safe_type(page, 'input[name="password"]', password)
                    self.log("パスワードを入力しました。")
                    
                    # 入力後少し待機
                    page.wait_for_timeout(3000)
                    
                    # ログインボタン
                    # ボタンが有効になるのを待つ
                    login_btn = page.get_by_testid("LoginForm_Login_Button")
                    if not login_btn.is_visible():
                        login_btn = page.get_by_role("button", name="ログイン").or_(page.get_by_role("button", name="Log in"))
                    
                    login_btn.wait_for(state="visible", timeout=5000)
                    # login_btn.wait_for(state="enabled", timeout=5000) # enabled待ちも入れたいが、visibleで十分な場合も多い
                    login_btn.click()
                    
                except Exception as e:
                    # エラーの詳細を出力
                    self.log(f"ログイン処理中にエラー: {e}")
                    if page.locator('input[name="text"]').is_visible():
                         raise Exception("追加の認証情報（電話番号またはメールアドレス）を求められました。手動対応が必要です。")
                    
                    # パスワード欄が見つからなかったのか、ボタンなのかを判別するのは難しいが、
                    # 少なくとも「パスワード入力欄が見つかりません」と決めつけるのは避ける
                    raise Exception(f"ログイン処理に失敗しました: {e}")
                
                # ログイン完了待ち
                self.log("ログイン完了を待機中...")
                page.wait_for_selector('[data-testid="SideNav_NewTweet_Button"]', timeout=20000)
                self.log("ログイン成功。")

            # --- 表示名の取得と保存 ---
            try:
                # サイドバーの下部にあるアカウント情報を探す
                # data-testid="UserAvatar-Container-..." のようなものがあるが、
                # もっと確実なのは自分のプロフィールに行くか、サイドバーのテキストを取得すること
                # ここでは簡易的に、サイドバーのアカウントメニューボタンのaria-labelなどを活用するか、
                # あるいはプロフィールページに行かずに取得できる範囲で試みる。
                
                # アカウントメニューボタン (左下)
                account_menu = page.locator('[data-testid="SideNav_AccountSwitcher_Button"]')
                if account_menu.is_visible():
                    # テキストを取得 (例: "Yuta @yuta...")
                    text = account_menu.inner_text()
                    lines = text.split('\n')
                    if len(lines) >= 2:
                        display_name = lines[0]
                        # self.log(f"表示名を取得: {display_name}")
                        self.save_account_status(username, "処理中...", "orange", display_name=display_name)
            except Exception as e:
                # 表示名取得失敗は致命的ではない
                pass

            # --- 「いいね」処理 (投稿前のアクション) ---
            if self.settings["auto_like"]: # 設定値を使用
                self.log("タイムラインを巡回して「いいね」を試みます...")
                try:
                    # まずホームにいることを確実にする
                    if "home" not in page.url:
                        page.goto("https://x.com/home", wait_until="domcontentloaded")
                        page.wait_for_timeout(3000)

                    # タイムラインが表示されるのを待つ
                    page.locator('[data-testid="tweet"]').first.wait_for(timeout=10000)
                    
                    # いいねする回数を決定 (v1.6)
                    like_min = self.settings.get("like_min", 1)
                    like_max = self.settings.get("like_max", 5)
                    like_count = random.randint(like_min, like_max)
                    
                    self.log(f"今回は {like_count}件 の投稿にいいねします。")
                    
                    # 画面内のツイートを取得
                    tweets = page.locator('[data-testid="tweet"]').all()
                    
                    liked_count = 0
                    for tweet in tweets:
                        if liked_count >= like_count:
                            break
                            
                        try:
                            like_button = tweet.locator('[data-testid="like"]').first
                            if like_button.is_visible():
                                like_button.click()
                                liked_count += 1
                                page.wait_for_timeout(random.randint(1000, 3000)) # 人間らしい待機
                        except:
                            continue
                            
                    if liked_count > 0:
                        self.log(f"{liked_count}件の投稿に「いいね」しました。")
                    else:
                        self.log("「いいね」できる投稿が見つかりませんでした。")
                        
                except Exception as e:
                    self.log(f"いいね処理中にエラー（スキップします）: {e}")

            # --- 投稿フロー ---
            content = self.generate_post_content(username)
            self.log(f"投稿内容生成: {content.replace(chr(10), ' ')}...")

            # 投稿のために一番上に戻る、またはショートカットを使う
            # ここでは確実性を重視して再度ホームへ（リロード効果も兼ねる）
            if random.random() < 0.5: # 50%の確率でリロードして一番上に戻る
                page.goto("https://x.com/home", wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
            
            # 投稿方法: モーダル（サイドバーのボタン）経由を優先する
            self.log("投稿ウィンドウを開きます...")
            try:
                # サイドバーの「ポストする」ボタン (複数のセレクタで試行)
                tweet_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]').or_(page.locator('a[href="/compose/tweet"]'))
                tweet_btn.first.wait_for(state="visible", timeout=10000)
                tweet_btn.first.click()
                
                # モーダルが開くのを待つ
                page.wait_for_selector('[data-testid="tweetTextarea_0"]', state="visible", timeout=10000)
                self.log("投稿モーダルが開きました。")
            except:
                self.log("サイドバーからの投稿に失敗。インライン投稿を試みます。")
                # インライン投稿エリアをクリック
                try:
                    page.locator('[data-testid="tweetTextarea_0"]').first.click()
                except:
                    pass 

            # --- 画像/GIF画像の添付 (ランダム) ---
            if random.random() * 100 < self.settings["gif_probability"]:
                # まずローカル画像をチェック
                base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
                images_dir = os.path.join(base_path, "images")
                images = []
                if os.path.exists(images_dir):
                    images = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
                
                if images:
                    # 画像があればそれをアップロード
                    target_image = random.choice(images)
                    image_path = os.path.join(images_dir, target_image)
                    self.log(f"画像を添付します: {target_image}")
                    try:
                        # input[type="file"] を探してアップロード
                        # Xの投稿画面には隠しinputがある
                        file_input = page.locator('input[type="file"]').first
                        file_input.set_input_files(image_path)
                        page.wait_for_timeout(2000) # アップロード待ち
                    except Exception as e:
                        self.log(f"画像アップロード失敗: {e}")
                else:
                    # 画像がなければGIF
                    self.log("GIF画像を添付します...")
                    try:
                        # GIFボタンをクリック (再試行ロジック)
                        gif_btn = page.locator('[data-testid="gifSearchButton"]').first
                        gif_btn.wait_for(state="visible", timeout=3000)
                        
                        dialog_opened = False
                        for _ in range(3):
                            try:
                                self.log("GIFボタンをクリックします...")
                                gif_btn.click(force=True)
                                page.wait_for_timeout(1000)
                                
                                # ダイアログ確認 (複数ある場合は最後=最新のものを対象)
                                if page.locator('[role="dialog"]').last.is_visible():
                                    dialog_opened = True
                                    break
                            except Exception as e:
                                self.log(f"GIFボタンクリック再試行: {e}")
                                page.wait_for_timeout(1000)
                        
                        if not dialog_opened:
                            raise Exception("GIFダイアログが開きませんでした。")

                        # 検索ボックスを待機
                        # 最新のダイアログを対象にする
                        dialog = page.locator('[role="dialog"]').last
                        
                        # 複数の可能性を試す (テキスト入力、検索ラベル付きなど)
                        # type="file"は除外
                        search_input = dialog.locator('input[type="text"]').or_(dialog.locator('input[aria-label*="Search"]')).or_(dialog.locator('input[aria-label*="検索"]')).first
                        search_input.wait_for(state="visible", timeout=5000)
                        
                        # 検索ワードをランダムに選ぶ
                        gif_keywords = ["Happy", "Cat", "Dog", "Funny", "Work", "Coffee", "Success", "Good morning", "Hello", "Smile"]
                        keyword = random.choice(gif_keywords)
                        
                        # 検索語句を入力
                        search_input.click()
                        search_input.fill(keyword)
                        search_input.press("Enter")
                        
                        # 検索語句を入力
                        search_input.click()
                        search_input.fill(keyword)
                        search_input.press("Enter")
                        
                        # 結果が表示されるのを待つ (固定待機 + 緩い条件)
                        # ユーザー報告によると候補は出ているので、厳密なロール待機はやめて、少し待ってから要素を探す
                        page.wait_for_timeout(3000)
                        
                        # 画像を選択
                        # role="button" だけでなく、画像を含む要素などを広く探す
                        # ダイアログ内のすべてのボタンまたは画像を含むdivを取得
                        candidates = dialog.locator('[role="button"], div[role="button"]').all()
                        
                        target_gif = None
                        # 候補の中から、画像(img)を含んでいるものを優先的に探す
                        gif_candidates = []
                        for cand in candidates:
                            if cand.locator("img").count() > 0 or cand.locator("video").count() > 0:
                                gif_candidates.append(cand)
                        
                        if gif_candidates:
                            # 画像を含むボタンが見つかればそこから選ぶ
                            target_gif = random.choice(gif_candidates[:8])
                        elif candidates:
                            # 画像タグが見つからなくても、ボタンがあれば試す（検索バーの直後にあるボタンなど）
                            # ただし、最初の数個はカテゴリボタンの可能性があるので、少し後ろの方を狙うのも手だが、
                            # ここではランダムに選ぶ
                            target_gif = random.choice(candidates[:8])
                        
                        if target_gif:
                            try:
                                target_gif.click(timeout=3000)
                                self.log(f"GIF画像 ({keyword}) を選択しました。")
                                page.wait_for_timeout(2000)
                            except Exception as e:
                                self.log(f"GIFクリックでエラー: {e}")
                        else:
                            self.log("GIF候補が見つかりませんでした（要素特定失敗）。")
                            # ダイアログを閉じるためにEscapeではなく、閉じるボタンを探すか、外側をクリックする
                            # Escapeは「保存しますか？」を誘発するリスクがあるため慎重に
                            page.keyboard.press("Escape")
                            
                    except Exception as e:
                        self.log(f"GIF添付に失敗しました（投稿は続行します）: {e}")
                        page.keyboard.press("Escape")
                        page.wait_for_timeout(1000)

            # テキスト入力
            self.log("テキストを入力中...")
            try:
                # フォーカスしてから入力
                textarea = page.locator('[data-testid="tweetTextarea_0"]').first
                textarea.click()
                page.wait_for_timeout(500)
                
                # safe_typeを使用して入力 (クリップボード経由 + フォールバック)
                self.safe_type(page, '[data-testid="tweetTextarea_0"]', content)
                
                page.wait_for_timeout(1000)
                
                # 入力イベントを確実に発火させるために、スペース→バックスペースを入力
                page.keyboard.press("Space")
                page.wait_for_timeout(100)
                page.keyboard.press("Backspace")
                page.wait_for_timeout(500)

                # 投稿ボタン
                post_button = page.locator('[data-testid="tweetButton"]').or_(page.locator('[data-testid="tweetButtonInline"]'))
                
                # ボタンが有効になるまで待機
                try:
                    post_button.first.wait_for(state="enabled", timeout=5000)
                except:
                    self.log("投稿ボタンが有効になりません。再入力を試みます。")
                    textarea.fill(content) # fillで再試行
                    page.wait_for_timeout(1000)

                if post_button.first.is_enabled():
                    post_button.first.click()
                    self.log("投稿ボタンを押下しました。")
                    page.wait_for_timeout(5000) # 完了待ち
                    self.log("投稿処理完了（待機終了）。")
                else:
                    raise Exception("投稿ボタンが無効状態です。")

            except Exception as e:
                raise Exception(f"投稿処理中にエラーが発生しました: {e}")

        except Exception as e:
            raise e

if __name__ == "__main__":
    app = AutoPostApp()
    app.mainloop()
