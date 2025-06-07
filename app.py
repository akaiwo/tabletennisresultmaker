from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os
import platform
from datetime import datetime

app = Flask(__name__)

class TableTennisImageGenerator:
    def __init__(self):
        self.width = 1080
        self.height = 1080
        self.bg_color = (255, 255, 255)
        self.primary_color = (41, 128, 185)
        self.secondary_color = (52, 73, 94)
        self.accent_color = (231, 76, 60)
        
        # 事前配置されたフォントファイルを準備
        self.setup_fonts()
    
    def setup_fonts(self):
        """事前配置されたフォントをセットアップ"""
        self.font_paths = {}
        
        # 事前に配置されたフォントファイルのリスト（優先度順）
        font_candidates = [
            # 日本語対応フォント（Noto Sans JP）
            ('NotoSansJP-Regular.ttf', 'regular'),
            ('NotoSansJP-Bold.ttf', 'bold'),
            ('NotoSansJP-Medium.ttf', 'medium'),
            ('NotoSansJP-SemiBold.ttf', 'semibold'),
            ('NotoSansJP-Light.ttf', 'light'),
            ('NotoSansJP-ExtraBold.ttf', 'extrabold'),
            ('NotoSansJP-Black.ttf', 'black'),
            ('NotoSansJP-Thin.ttf', 'thin'),
            ('NotoSansJP-ExtraLight.ttf', 'extralight'),
            # バックアップ用（英語フォント）
            ('DejaVuSans.ttf', 'fallback_regular'),
            ('DejaVuSans-Bold.ttf', 'fallback_bold'),
        ]
        
        # fontsディレクトリ内のフォントファイルを検索
        fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        if os.path.exists(fonts_dir):
            for filename, font_type in font_candidates:
                font_path = os.path.join(fonts_dir, filename)
                if os.path.exists(font_path):
                    try:
                        # フォントが正常に読み込めるかテスト
                        test_font = ImageFont.truetype(font_path, 20)
                        self.font_paths[font_type] = font_path
                        print(f"Font loaded successfully: {filename} as {font_type}")
                    except Exception as e:
                        print(f"Warning: Could not load font {filename}: {e}")
                        continue
        
        # 利用可能なフォントを確認
        if self.font_paths:
            print(f"Available fonts: {list(self.font_paths.keys())}")
        else:
            print("Warning: No custom fonts loaded, will use system defaults")
    
    def get_font(self, size, bold=False, weight='regular'):
        """フォントを取得（事前配置フォント対応版）"""
        # 重み指定を正規化
        if bold:
            weight = 'bold'
        
        # 優先度順でフォントを選択
        font_priority = []
        
        if weight == 'bold':
            font_priority = ['bold', 'semibold', 'extrabold', 'black', 'medium', 'regular']
        elif weight == 'medium':
            font_priority = ['medium', 'semibold', 'regular', 'bold']
        elif weight == 'light':
            font_priority = ['light', 'extralight', 'thin', 'regular']
        else:  # regular
            font_priority = ['regular', 'medium', 'light', 'bold']
        
        # 事前配置されたフォントを優先度順に試す
        for font_type in font_priority:
            if font_type in self.font_paths:
                try:
                    font_path = self.font_paths[font_type]
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"Error loading font {font_type}: {e}")
                    continue
        
        # フォールバック用フォントを試す
        fallback_priority = ['fallback_regular', 'fallback_bold'] if not bold else ['fallback_bold', 'fallback_regular']
        for font_type in fallback_priority:
            if font_type in self.font_paths:
                try:
                    font_path = self.font_paths[font_type]
                    if os.path.exists(font_path):
                        return ImageFont.truetype(font_path, size)
                except Exception as e:
                    print(f"Error loading fallback font {font_type}: {e}")
                    continue
        
        # システムフォントをバックアップとして使用
        system = platform.system()
        system_font_paths = []
        
        if system == "Windows":
            if bold:
                system_font_paths = [
                    "C:/Windows/Fonts/arialbd.ttf",
                    "C:/Windows/Fonts/calibrib.ttf",
                    "C:/Windows/Fonts/tahomabd.ttf",
                ]
            else:
                system_font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf",
                    "C:/Windows/Fonts/tahoma.ttf",
                ]
        elif system == "Darwin":  # macOS
            if bold:
                system_font_paths = [
                    "/System/Library/Fonts/Arial Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
            else:
                system_font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
        else:  # Linux
            if bold:
                system_font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                ]
            else:
                system_font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]
        
        # システムフォントを試す
        for font_path in system_font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # 最終手段：デフォルトフォント
        print(f"Warning: Using default font for size {size}. Custom fonts may not be available.")
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def draw_text_with_fallback(self, draw, text, position, font, fill):
        """フォールバック付きテキスト描画"""
        try:
            # まず指定されたフォントで描画を試す
            draw.text(position, text, fill=fill, font=font)
        except Exception as e:
            # 失敗した場合はデフォルトフォントで描画
            print(f"Font rendering failed, using fallback: {e}")
            try:
                default_font = ImageFont.load_default()
                draw.text(position, text, fill=fill, font=default_font)
            except Exception as e2:
                # 最終手段: フォントなしで描画
                print(f"Default font also failed: {e2}")
                draw.text(position, text, fill=fill)
    
    def create_image(self, player1, player2, scores, match_type):
        # 画像とDrawオブジェクトを作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            # フォントを設定（日本語対応）
            title_font = self.get_font(80, bold=True)
            name_font = self.get_font(45, weight='medium')
            score_font = self.get_font(120, bold=True)
            detail_font = self.get_font(35, weight='regular')
            win_font = self.get_font(60, bold=True)
            vs_font = self.get_font(50, bold=True)
            footer_font = self.get_font(30, weight='regular')
        except Exception as e:
            print(f"Error setting up fonts: {e}")
            # フォント作成に失敗した場合のフォールバック
            default_font = ImageFont.load_default()
            title_font = name_font = score_font = detail_font = win_font = vs_font = footer_font = default_font
        
        # タイトル（英語）
        title_text = "Table Tennis Result"
        try:
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
        except:
            title_width = len(title_text) * 30  # フォールバック計算
        
        self.draw_text_with_fallback(draw, title_text, 
                                   ((self.width - title_width) // 2, 80), 
                                   title_font, self.primary_color)
        
        # 勝者を判定
        player1_wins = sum(1 for score in scores if score[0] > score[1])
        player2_wins = sum(1 for score in scores if score[1] > score[0])
        winner = player1 if player1_wins > player2_wins else player2
        
        # プレイヤー名と各セットのスコアを左右に配置
        left_x = 230
        right_x = self.width - 230
        score_left_x = 420
        score_right_x = self.width - 420
        
        # WIN表示
        win_text = "WIN"
        try:
            win_bbox = draw.textbbox((0, 0), win_text, font=win_font)
            win_width = win_bbox[2] - win_bbox[0]
        except:
            win_width = len(win_text) * 25
        
        if winner == player1:
            self.draw_text_with_fallback(draw, win_text, 
                                       (left_x - win_width // 2, 230), 
                                       win_font, self.accent_color)
        else:
            self.draw_text_with_fallback(draw, win_text, 
                                       (right_x - win_width // 2, 230), 
                                       win_font, self.accent_color)
        
        # プレイヤー名を配置
        player_y = 300
        
        # プレイヤー1（左側）
        try:
            player1_bbox = draw.textbbox((0, 0), player1, font=name_font)
            player1_width = player1_bbox[2] - player1_bbox[0]
        except:
            player1_width = len(player1) * 20
        
        self.draw_text_with_fallback(draw, player1, 
                                   (left_x - player1_width // 2, player_y), 
                                   name_font, self.secondary_color)
        
        # プレイヤー2（右側）
        try:
            player2_bbox = draw.textbbox((0, 0), player2, font=name_font)
            player2_width = player2_bbox[2] - player2_bbox[0]
        except:
            player2_width = len(player2) * 20
        
        self.draw_text_with_fallback(draw, player2, 
                                   (right_x - player2_width // 2, player_y), 
                                   name_font, self.secondary_color)
        
        # 「vs」をプレイヤー名の間に配置
        vs_text = "vs"
        try:
            vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
            vs_width = vs_bbox[2] - vs_bbox[0]
        except:
            vs_width = len(vs_text) * 20
        
        self.draw_text_with_fallback(draw, vs_text, 
                                   ((self.width - vs_width) // 2, player_y + 5), 
                                   vs_font, self.accent_color)
        
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
        
        # 各セットのスコア表示
        for i, (score1, score2) in enumerate(scores):
            y_pos = score_start_y + i * line_height
            
            # 左側のスコア
            score1_text = str(score1)
            try:
                score1_bbox = draw.textbbox((0, 0), score1_text, font=detail_font)
                score1_width = score1_bbox[2] - score1_bbox[0]
            except:
                score1_width = len(score1_text) * 15
            
            self.draw_text_with_fallback(draw, score1_text, 
                                       (score_left_x - score1_width // 2, y_pos), 
                                       detail_font, self.secondary_color)
            
            # 右側のスコア
            score2_text = str(score2)
            try:
                score2_bbox = draw.textbbox((0, 0), score2_text, font=detail_font)
                score2_width = score2_bbox[2] - score2_bbox[0]
            except:
                score2_width = len(score2_text) * 15
            
            self.draw_text_with_fallback(draw, score2_text, 
                                       (score_right_x - score2_width // 2, y_pos), 
                                       detail_font, self.secondary_color)
            
            # 中央のハイフン
            dash_text = "-"
            try:
                dash_bbox = draw.textbbox((0, 0), dash_text, font=detail_font)
                dash_width = dash_bbox[2] - dash_bbox[0]
            except:
                dash_width = 10
            
            self.draw_text_with_fallback(draw, dash_text, 
                                       ((self.width - dash_width) // 2, y_pos), 
                                       detail_font, self.secondary_color)
        
        # 最終スコア（セット数）
        final_score1 = str(player1_wins)
        try:
            final_bbox1 = draw.textbbox((0, 0), final_score1, font=score_font)
            final_width1 = final_bbox1[2] - final_bbox1[0]
        except:
            final_width1 = len(final_score1) * 50
        
        self.draw_text_with_fallback(draw, final_score1, 
                                   (left_x - final_width1 // 2, final_y), 
                                   score_font, self.primary_color)
        
        final_score2 = str(player2_wins)
        try:
            final_bbox2 = draw.textbbox((0, 0), final_score2, font=score_font)
            final_width2 = final_bbox2[2] - final_bbox2[0]
        except:
            final_width2 = len(final_score2) * 50
        
        self.draw_text_with_fallback(draw, final_score2, 
                                   (right_x - final_width2 // 2, final_y), 
                                   score_font, self.primary_color)
        
        # 装飾的な要素
        draw.rectangle([100, 180, self.width - 100, 185], fill=self.primary_color)
        draw.rectangle([100, self.height - 150, self.width - 100, self.height - 145], 
                      fill=self.primary_color)
        
        # フッターテキスト
        footer_text = "Table Tennis Result Generator"
        try:
            footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
        except:
            footer_width = len(footer_text) * 12
        
        self.draw_text_with_fallback(draw, footer_text, 
                                   ((self.width - footer_width) // 2, self.height - 90), 
                                   footer_font, self.secondary_color)
        
        return img

# グローバルインスタンス
generator = TableTennisImageGenerator()

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
        
        # ファイル名を英数字のみに変更（日本語文字が問題を起こす可能性を回避）
        safe_filename = f'table_tennis_result_{len(player1)}vs{len(player2)}.png'
        
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