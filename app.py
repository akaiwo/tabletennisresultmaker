from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os
import platform

app = Flask(__name__)

class TableTennisImageGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1080
        self.bg_color = (255, 255, 255)
        self.primary_color = (41, 128, 185)
        self.secondary_color = (52, 73, 94)
        self.accent_color = (231, 76, 60)
        
        # フォント設定を初期化
        self.setup_fonts()
    
    def setup_fonts(self):
        """OS別に最適なフォントを設定"""
        self.japanese_fonts = {}
        self.english_fonts = {}
        
        system = platform.system()
        print(f"Detected OS: {system}")
        
        if system == "Linux":  # Render環境
            self.setup_linux_fonts()
        elif system == "Windows":
            self.setup_windows_fonts()
        elif system == "Darwin":  # macOS
            self.setup_macos_fonts()
        else:
            self.setup_fallback_fonts()
    
    def setup_linux_fonts(self):
        """Linux環境（Render含む）用フォント設定"""

        # ✅ カスタムフォントを最優先で使用
        custom_path = os.path.join(os.path.dirname(__file__), "fonts/NotoSansCJKjp-Regular.otf")
        if os.path.exists(custom_path):
            self.japanese_fonts['regular'] = custom_path
            self.japanese_fonts['bold'] = custom_path
            self.japanese_fonts['italic'] = custom_path
            self.japanese_fonts['bold_italic'] = custom_path
            print(f"✓ Custom font loaded from: {custom_path}")
            # 英語フォントも同時に設定
            self.setup_english_fonts_linux()
            return

        # 日本語フォント候補（優先順）
        japanese_font_paths = [
            # Noto Fonts（最も信頼性が高い）
            "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            # DejaVu系（英数字でも使用可能）
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
            # Liberation系
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
            # Ubuntu系（GitHub Actionsでよく使用される）
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Italic.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-BoldItalic.ttf",
        ]
        
        self.load_font_variants(japanese_font_paths, self.japanese_fonts, "Japanese")
        # 英語フォントを別途設定
        self.setup_english_fonts_linux()
    
    def setup_english_fonts_linux(self):
        """Linux環境用英語フォント設定（日本語フォントとは別に）"""
        # 英数字専用フォント候補
        english_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-Italic.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-BoldItalic.ttf",
        ]
        
        self.load_font_variants(english_font_paths, self.english_fonts, "English")
    
    def setup_windows_fonts(self):
        """Windows環境用フォント設定"""
        # 日本語フォント
        japanese_font_paths = [
            "C:/Windows/Fonts/msgothic.ttc",      # MS Gothic
            "C:/Windows/Fonts/msmincho.ttc",      # MS Mincho
            "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",  # もしインストールされていれば
            "C:/Windows/Fonts/yugothm.ttc",       # Yu Gothic Medium
            "C:/Windows/Fonts/yugothb.ttc",       # Yu Gothic Bold
        ]
        
        # 英数字フォント
        english_font_paths = [
            "C:/Windows/Fonts/arial.ttf",         # Arial Regular
            "C:/Windows/Fonts/arialbd.ttf",       # Arial Bold  
            "C:/Windows/Fonts/ariali.ttf",        # Arial Italic
            "C:/Windows/Fonts/arialbi.ttf",       # Arial Bold Italic
            "C:/Windows/Fonts/calibri.ttf",       # Calibri Regular
            "C:/Windows/Fonts/calibrib.ttf",      # Calibri Bold
            "C:/Windows/Fonts/calibrii.ttf",      # Calibri Italic
            "C:/Windows/Fonts/calibriz.ttf",      # Calibri Bold Italic
        ]
        
        self.load_font_variants(japanese_font_paths, self.japanese_fonts, "Japanese")
        self.load_font_variants(english_font_paths, self.english_fonts, "English")
    
    def setup_macos_fonts(self):
        """macOS環境用フォント設定"""
        # 日本語フォント
        japanese_font_paths = [
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
            "/Library/Fonts/NotoSansCJK-Regular.ttc",
        ]
        
        # 英数字フォント
        english_font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Arial Italic.ttf",
            "/System/Library/Fonts/Arial Bold Italic.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Helvetica Neue.ttc",
        ]
        
        self.load_font_variants(japanese_font_paths, self.japanese_fonts, "Japanese")
        self.load_font_variants(english_font_paths, self.english_fonts, "English")
    
    def setup_fallback_fonts(self):
        """フォールバック設定（最終手段）"""
        print("Using fallback font configuration")
        try:
            default_font = ImageFont.load_default()
            self.japanese_fonts = {
                'regular': default_font,
                'bold': default_font,
                'italic': default_font,
                'bold_italic': default_font
            }
            self.english_fonts = {
                'regular': default_font,
                'bold': default_font,
                'italic': default_font,
                'bold_italic': default_font
            }
        except Exception as e:
            print(f"Even fallback fonts failed: {e}")
            self.japanese_fonts = self.english_fonts = {}
    
    def load_font_variants(self, font_paths, font_dict, font_type):
        """フォントのバリエーション（Regular, Bold, Italic, BoldItalic）を読み込み"""
        loaded_fonts = []
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    # フォントファイルをテスト読み込み
                    test_font = ImageFont.truetype(font_path, 20)
                    test_font.getbbox("Test日本語")  # 日本語テスト
                    loaded_fonts.append(font_path)
                    print(f"✓ {font_type} font loaded: {font_path}")
            except Exception as e:
                print(f"✗ {font_type} font failed: {font_path} - {e}")
                continue
        
        if loaded_fonts:
            # 最初に見つかったフォントを使用（通常はRegular）
            primary_font = loaded_fonts[0]
            
            # バリエーションを設定
            font_dict['regular'] = primary_font
            
            # Bold系フォントを探す
            bold_font = None
            for font_path in loaded_fonts:
                if any(keyword in font_path.lower() for keyword in ['bold', 'bd', 'b.ttf', 'w6', 'w7']):
                    bold_font = font_path
                    break
            font_dict['bold'] = bold_font or primary_font
            
            # Italic系フォントを探す
            italic_font = None
            for font_path in loaded_fonts:
                if any(keyword in font_path.lower() for keyword in ['italic', 'oblique', 'i.ttf']):
                    italic_font = font_path
                    break
            font_dict['italic'] = italic_font or primary_font
            
            # BoldItalic系フォントを探す
            bold_italic_font = None
            for font_path in loaded_fonts:
                if any(keyword in font_path.lower() for keyword in ['bolditalic', 'boldobl', 'bi.ttf', 'z.ttf']):
                    bold_italic_font = font_path
                    break
            font_dict['bold_italic'] = bold_italic_font or font_dict['bold']
            
            print(f"{font_type} font variants configured:")
            for variant, path in font_dict.items():
                print(f"  {variant}: {path}")
        else:
            print(f"No {font_type} fonts found, using default")
            try:
                default_font = ImageFont.load_default()
                font_dict.update({
                    'regular': default_font,
                    'bold': default_font,
                    'italic': default_font,
                    'bold_italic': default_font
                })
            except:
                font_dict.clear()
    
    def get_font(self, size, bold=False, italic=False, japanese=False):
        """
        フォントを取得
        Args:
            size: フォントサイズ
            bold: 太字フラグ
            italic: 斜体フラグ
            japanese: 日本語フラグ（TrueならjапaneseテキJavanesee用フォント使用）
        """
        # フォント辞書を選択
        font_dict = self.japanese_fonts if japanese else self.english_fonts
        
        # バリエーションを決定
        if bold and italic:
            variant = 'bold_italic'
        elif bold:
            variant = 'bold'
        elif italic:
            variant = 'italic'
        else:
            variant = 'regular'
        
        # フォントパスを取得
        font_path = font_dict.get(variant)
        if not font_path:
            print(f"Font variant {variant} not found, using regular")
            font_path = font_dict.get('regular')
        
        # フォントオブジェクトを作成
        if font_path and isinstance(font_path, str):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception as e:
                print(f"Error loading font {font_path}: {e}")
        
        # フォールバック
        if isinstance(font_path, ImageFont.ImageFont):
            return font_path
        
        # 最終フォールバック
        try:
            return ImageFont.load_default()
        except:
            return None
    
    def has_japanese_chars(self, text):
        """文字列に日本語文字が含まれているかチェック"""
        for char in text:
            if ord(char) > 127:  # 基本的なASCII範囲外
                if any([
                    0x3040 <= ord(char) <= 0x309F,  # ひらがな
                    0x30A0 <= ord(char) <= 0x30FF,  # カタカナ
                    0x4E00 <= ord(char) <= 0x9FAF,  # 漢字
                ]):
                    return True
        return False
    
    def draw_text_with_font_selection(self, draw, text, position, size, fill, bold=False, italic=False):
        """テキストの内容に応じて適切なフォントを選択して描画（プレイヤー名専用）"""
        try:
            # 日本語文字が含まれているかチェック
            use_japanese_font = self.has_japanese_chars(text)
            
            # フォントを取得
            font = self.get_font(size, bold=bold, italic=italic, japanese=use_japanese_font)
            
            if font:
                draw.text(position, text, fill=fill, font=font)
            else:
                # フォント取得に失敗した場合
                draw.text(position, text, fill=fill)
                
        except Exception as e:
            print(f"Text drawing failed: {e}")
            try:
                # 最終フォールバック
                draw.text(position, text, fill=fill)
            except Exception as e2:
                print(f"Final fallback also failed: {e2}")
    
    def draw_english_text(self, draw, text, position, size, fill, bold=False, italic=False):
        """英語テキスト専用描画メソッド（確実に英語フォントを使用）"""
        try:
            # 強制的に英語フォントを使用
            font = self.get_font(size, bold=bold, italic=italic, japanese=False)
            
            if font:
                draw.text(position, text, fill=fill, font=font)
            else:
                # フォント取得に失敗した場合
                draw.text(position, text, fill=fill)
                
        except Exception as e:
            print(f"English text drawing failed: {e}")
            try:
                # 最終フォールバック
                draw.text(position, text, fill=fill)
            except Exception as e2:
                print(f"Final fallback also failed: {e2}")
    
    def create_image(self, player1, player2, scores, match_type):
        # 画像とDrawオブジェクトを作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # タイトル（英語）- 斜体 ★英語フォント強制使用
        title_text = "Game Result"
        try:
            # テキスト幅を計算（フォント取得できない場合のフォールバック）
            title_font = self.get_font(80, bold=True, italic=True, japanese=False)
            if title_font:
                title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
                title_width = title_bbox[2] - title_bbox[0]
            else:
                title_width = len(title_text) * 40  # フォールバック計算
        except:
            title_width = len(title_text) * 40
        
        self.draw_english_text(draw, title_text, 
                             ((self.width - title_width) // 2, 80), 
                             80, self.primary_color, bold=True, italic=True)
        
        # 勝者を判定
        player1_wins = sum(1 for score in scores if score[0] > score[1])
        player2_wins = sum(1 for score in scores if score[1] > score[0])
        winner = player1 if player1_wins > player2_wins else player2
        
        # プレイヤー名と各セットのスコアを左右に配置
        left_x = 230
        right_x = self.width - 230
        score_left_x = 420
        score_right_x = self.width - 420
        
        # WIN表示 - 斜体 ★英語フォント強制使用
        win_text = "WIN"
        try:
            win_font = self.get_font(60, bold=True, italic=True, japanese=False)
            if win_font:
                win_bbox = draw.textbbox((0, 0), win_text, font=win_font)
                win_width = win_bbox[2] - win_bbox[0]
            else:
                win_width = len(win_text) * 30
        except:
            win_width = len(win_text) * 30
        
        if winner == player1:
            self.draw_english_text(draw, win_text, 
                                 (left_x - win_width // 2, 230), 
                                 60, self.accent_color, bold=True, italic=True)
        else:
            self.draw_english_text(draw, win_text, 
                                 (right_x - win_width // 2, 230), 
                                 60, self.accent_color, bold=True, italic=True)
        
        # プレイヤー名を配置 - タイトルと同じサイズ（80） ★プレイヤー名のみ自動判定フォント使用
        player_y = 300
        
        # プレイヤー1（左側）
        try:
            name_font = self.get_font(80, bold=True, japanese=self.has_japanese_chars(player1))
            if name_font:
                player1_bbox = draw.textbbox((0, 0), player1, font=name_font)
                player1_width = player1_bbox[2] - player1_bbox[0]
            else:
                player1_width = len(player1) * 40
        except:
            player1_width = len(player1) * 40
        
        self.draw_text_with_font_selection(draw, player1, 
                                         (left_x - player1_width // 2, player_y), 
                                         80, self.secondary_color, bold=True)
        
        # プレイヤー2（右側）
        try:
            name_font = self.get_font(80, bold=True, japanese=self.has_japanese_chars(player2))
            if name_font:
                player2_bbox = draw.textbbox((0, 0), player2, font=name_font)
                player2_width = player2_bbox[2] - player2_bbox[0]
            else:
                player2_width = len(player2) * 40
        except:
            player2_width = len(player2) * 40
        
        self.draw_text_with_font_selection(draw, player2, 
                                         (right_x - player2_width // 2, player_y), 
                                         80, self.secondary_color, bold=True)
        
        # 「vs」をプレイヤー名の間に配置 - 斜体 ★英語フォント強制使用
        vs_text = "vs"
        try:
            vs_font = self.get_font(50, italic=True, japanese=False)
            if vs_font:
                vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
                vs_width = vs_bbox[2] - vs_bbox[0]
            else:
                vs_width = len(vs_text) * 25
        except:
            vs_width = len(vs_text) * 25
        
        self.draw_english_text(draw, vs_text, 
                             ((self.width - vs_width) // 2, player_y + 30), 
                             50, self.accent_color, bold=True, italic=True)
        
        # 各セットのスコアの配置計算
        num_sets = len(scores)
        line_height = 50
        final_y = 540
        
        if num_sets == 1:
            center_set_index = 0
        elif num_sets <= 3:
            center_set_index = 1
        elif num_sets <= 5:
            center_set_index = 2
        else:
            center_set_index = 3
        
        score_start_y = final_y + 50 - (center_set_index * line_height)
        
        # 各セットのスコア表示 - 斜体 ★英語フォント強制使用
        for i, (score1, score2) in enumerate(scores):
            y_pos = score_start_y + i * line_height
            
            # 左側のスコア
            score1_text = str(score1)
            try:
                detail_font = self.get_font(35, italic=True, japanese=False)
                if detail_font:
                    score1_bbox = draw.textbbox((0, 0), score1_text, font=detail_font)
                    score1_width = score1_bbox[2] - score1_bbox[0]
                else:
                    score1_width = len(score1_text) * 20
            except:
                score1_width = len(score1_text) * 20
            
            self.draw_english_text(draw, score1_text, 
                                 (score_left_x - score1_width // 2, y_pos), 
                                 35, self.secondary_color, italic=True)
            
            # 右側のスコア
            score2_text = str(score2)
            try:
                detail_font = self.get_font(35, italic=True, japanese=False)
                if detail_font:
                    score2_bbox = draw.textbbox((0, 0), score2_text, font=detail_font)
                    score2_width = score2_bbox[2] - score2_bbox[0]
                else:
                    score2_width = len(score2_text) * 20
            except:
                score2_width = len(score2_text) * 20
            
            self.draw_english_text(draw, score2_text, 
                                 (score_right_x - score2_width // 2, y_pos), 
                                 35, self.secondary_color, italic=True)
            
            # 中央のハイフン
            dash_text = "-"
            try:
                detail_font = self.get_font(35, italic=True, japanese=False)
                if detail_font:
                    dash_bbox = draw.textbbox((0, 0), dash_text, font=detail_font)
                    dash_width = dash_bbox[2] - dash_bbox[0]
                else:
                    dash_width = 15
            except:
                dash_width = 15
            
            self.draw_english_text(draw, dash_text, 
                                 ((self.width - dash_width) // 2, y_pos), 
                                 35, self.secondary_color, italic=True)
        
        # 最終スコア（セット数）- 斜体 ★英語フォント強制使用
        final_score1 = str(player1_wins)
        try:
            score_font = self.get_font(120, bold=True, italic=True, japanese=False)
            if score_font:
                final_bbox1 = draw.textbbox((0, 0), final_score1, font=score_font)
                final_width1 = final_bbox1[2] - final_bbox1[0]
            else:
                final_width1 = len(final_score1) * 70
        except:
            final_width1 = len(final_score1) * 70
        
        self.draw_english_text(draw, final_score1, 
                             (left_x - final_width1 // 2, final_y), 
                             120, self.primary_color, bold=True, italic=True)
        
        final_score2 = str(player2_wins)
        try:
            score_font = self.get_font(120, bold=True, italic=True, japanese=False)
            if score_font:
                final_bbox2 = draw.textbbox((0, 0), final_score2, font=score_font)
                final_width2 = final_bbox2[2] - final_bbox2[0]
            else:
                final_width2 = len(final_score2) * 70
        except:
            final_width2 = len(final_score2) * 70
        
        self.draw_english_text(draw, final_score2, 
                             (right_x - final_width2 // 2, final_y), 
                             120, self.primary_color, bold=True, italic=True)
        
        # 装飾的な要素
        draw.rectangle([100, 180, self.width - 100, 185], fill=self.primary_color)
        draw.rectangle([100, self.height - 150, self.width - 100, self.height - 145], 
                      fill=self.primary_color)
        
        # フッターテキスト ★英語フォント強制使用
        footer_text = "Table Tennis Result Generator"
        try:
            footer_font = self.get_font(30, japanese=False)
            if footer_font:
                footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
                footer_width = footer_bbox[2] - footer_bbox[0]
            else:
                footer_width = len(footer_text) * 15
        except:
            footer_width = len(footer_text) * 15
        
        self.draw_english_text(draw, footer_text, 
                             ((self.width - footer_width) // 2, self.height - 90), 
                             30, self.secondary_color)
        
        return img

# グローバルインスタンス（エラーハンドリング付き）
try:
    generator = TableTennisImageGenerator()
    print("Table Tennis Image Generator initialized successfully")
except Exception as e:
    print(f"Critical Error: Generator initialization failed: {e}")
    # 完全なフォールバック
    class EmergencyGenerator:
        def create_image(self, player1, player2, scores, match_type):
            img = Image.new('RGB', (1080, 1080), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # 基本的なテキスト描画（フォント無し）
            draw.text((540, 200), "Game Result", fill=(0, 0, 0), anchor="mm")
            draw.text((270, 400), player1, fill=(0, 0, 0), anchor="mm")
            draw.text((810, 400), player2, fill=(0, 0, 0), anchor="mm")
            draw.text((540, 400), "vs", fill=(255, 0, 0), anchor="mm")
            
            player1_wins = sum(1 for score in scores if score[0] > score[1])
            player2_wins = sum(1 for score in scores if score[1] > score[0])
            
            draw.text((270, 600), str(player1_wins), fill=(0, 0, 0), anchor="mm")
            draw.text((810, 600), str(player2_wins), fill=(0, 0, 0), anchor="mm")
            
            return img
    
    generator = EmergencyGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        # フォームデータを取得
        player1 = request.form['player1']
        player2 = request.form['player2']
        match_type = request.form['match_type']
        
        # スコアを取得
        scores = []
        max_sets = int(match_type.replace('セットマッチ', ''))
        
        for i in range(max_sets):
            score1_key = f'set{i+1}_score1'
            score2_key = f'set{i+1}_score2'
            
            if score1_key in request.form and score2_key in request.form:
                score1 = request.form[score1_key]
                score2 = request.form[score2_key]
                
                if score1 and score2:
                    scores.append((int(score1), int(score2)))
        
        if not scores:
            return "エラー: 少なくとも1セットのスコアを入力してください。", 400
        
        # 画像を生成
        img = generator.create_image(player1, player2, scores, match_type)
        
        # メモリ内のバイトストリームに保存
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # ファイル名を英数字のみに変更
        safe_filename = f'GameResult_{player1}_vs_{player2}.png'
        
        return send_file(img_io, mimetype='image/png', 
                        as_attachment=True, 
                        download_name=safe_filename)
        
    except Exception as e:
        print(f"Error in generate_image: {e}")
        return f"エラーが発生しました: {str(e)}", 500

# Render用のポート設定
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)