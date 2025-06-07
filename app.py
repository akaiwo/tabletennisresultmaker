from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io
import os
import platform
import requests
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
        
        # フォントキャッシュディレクトリを設定
        self.font_cache_dir = os.path.join(os.path.dirname(__file__), 'font_cache')
        os.makedirs(self.font_cache_dir, exist_ok=True)
        
        # フォントを初期化
        self.setup_font()
    
    def get_google_fonts_url(self, font_family, weight='400'):
        """Google Fonts APIを使用してフォントURLを取得"""
        try:
            api_url = f"https://fonts.googleapis.com/css2?family={font_family}:wght@{weight}&display=swap"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            # CSSからフォントURLを抽出
            css_content = response.text
            import re
            url_match = re.search(r'url\((https://[^)]+\.ttf)\)', css_content)
            if url_match:
                return url_match.group(1)
        except Exception as e:
            print(f"Failed to get Google Fonts URL: {e}")
        return None

    def download_font(self, font_url, font_filename):
        """フォントをダウンロード"""
        font_path = os.path.join(self.font_cache_dir, font_filename)
        
        # 既にダウンロード済みの場合はそのまま使用
        if os.path.exists(font_path):
            return font_path
        
        try:
            print(f"Downloading font: {font_filename}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(font_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            with open(font_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Font downloaded successfully: {font_filename}")
            return font_path
        except Exception as e:
            print(f"Failed to download font {font_filename}: {e}")
            return None
    
    def setup_font(self):
        """汎用的なフォントをセットアップ"""
        self.font_paths = {}
        
        # Google Fonts API経由でNoto Sans JPのURLを取得してダウンロード
        noto_urls = {
            'regular': self.get_google_fonts_url('Noto+Sans+JP', '400'),
            'bold': self.get_google_fonts_url('Noto+Sans+JP', '700')
        }
        
        for weight, url in noto_urls.items():
            if url:
                font_path = self.download_font(url, f'NotoSansJP-{weight.title()}.ttf')
                if font_path:
                    self.font_paths[weight] = font_path
        
        # 複数のフォールバックソースを用意
        fallback_sources = [
            # GitHub経由のDejaVu Sans
            {
                'regular': 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf',
                'bold': 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf'
            },
            # jsDelivr経由の別のフォント
            {
                'regular': 'https://cdn.jsdelivr.net/gh/googlefonts/roboto@main/src/hinted/Roboto-Regular.ttf',
                'bold': 'https://cdn.jsdelivr.net/gh/googlefonts/roboto@main/src/hinted/Roboto-Bold.ttf'
            }
        ]
        
        # フォールバックフォントをダウンロード
        for i, source in enumerate(fallback_sources):
            for weight, url in source.items():
                font_path = self.download_font(url, f'Fallback{i+1}-{weight.title()}.ttf')
                if font_path:
                    self.font_paths[f'fallback{i+1}_{weight}'] = font_path
                    if f'fallback_{weight}' not in self.font_paths:
                        self.font_paths[f'fallback_{weight}'] = font_path
    
    def get_font(self, size, bold=False):
        """フォントを取得（太字対応）"""
        weight = 'bold' if bold else 'regular'
        
        # 複数のフォントソースを順番に試す
        font_candidates = [
            # 1. Noto Sans JP（最優先）
            weight,
            # 2. フォールバックフォント
            f'fallback_{weight}',
            f'fallback1_{weight}',
            f'fallback2_{weight}',
        ]
        
        for candidate in font_candidates:
            if candidate in self.font_paths:
                try:
                    font_path = self.font_paths[candidate]
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, size)
                        # フォントが正しく読み込めるかテスト
                        font.getbbox("Test")
                        return font
                except Exception as e:
                    print(f"Error loading font {candidate}: {e}")
                    continue
        
        # システムフォントを試す
        system_font = self.get_system_font(size, bold)
        if system_font:
            return system_font
        
        # 最終手段：デフォルトフォント
        print(f"Warning: Using default font for size {size}")
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def get_system_font(self, size, bold=False):
        """システムフォントを取得"""
        system = platform.system()
        system_font_paths = []
        
        if system == "Windows":
            if bold:
                system_font_paths = [
                    "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic (日本語対応)
                    "C:/Windows/Fonts/arialbd.ttf",
                    "C:/Windows/Fonts/calibrib.ttf",
                ]
            else:
                system_font_paths = [
                    "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic (日本語対応)
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/calibri.ttf",
                ]
        elif system == "Darwin":  # macOS
            if bold:
                system_font_paths = [
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 日本語対応
                    "/System/Library/Fonts/Arial Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
            else:
                system_font_paths = [
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 日本語対応
                    "/System/Library/Fonts/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                ]
        else:  # Linux (Render環境も含む)
            if bold:
                system_font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                ]
            else:
                system_font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                ]
        
        # システムフォントを試す
        for font_path in system_font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        return None
    
    def draw_text_with_fallback(self, draw, text, position, font, fill):
        """フォールバック付きテキスト描画"""
        try:
            draw.text(position, text, fill=fill, font=font)
        except Exception as e:
            print(f"Font rendering failed, using fallback: {e}")
            try:
                default_font = ImageFont.load_default()
                draw.text(position, text, fill=fill, font=default_font)
            except Exception as e2:
                print(f"Default font also failed: {e2}")
                draw.text(position, text, fill=fill)
    
    def create_image(self, player1, player2, scores, match_type):
        # 画像とDrawオブジェクトを作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # フォントを設定（太字対応）
        try:
            title_font = self.get_font(80, bold=True)
            name_font = self.get_font(45, bold=True)
            score_font = self.get_font(120, bold=True)
            detail_font = self.get_font(35, bold=False)
            win_font = self.get_font(60, bold=True)
            vs_font = self.get_font(50, bold=False)
            footer_font = self.get_font(30, bold=False)
        except Exception as e:
            print(f"Error setting up fonts: {e}")
            # フォント作成に失敗した場合のフォールバック
            default_font = ImageFont.load_default()
            title_font = name_font = score_font = detail_font = win_font = vs_font = footer_font = default_font
        
        # タイトル（英語）
        title_text = "Game Result"
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

# グローバルインスタンス（エラーハンドリング付き）
try:
    generator = TableTennisImageGenerator()
    print("Font system initialized successfully")
except Exception as e:
    print(f"Warning: Font system initialization failed: {e}")
    # フォールバック用の簡易ジェネレータを作成
    class FallbackGenerator:
        def create_image(self, player1, player2, scores, match_type):
            # 基本的な画像生成（システムフォントのみ使用）
            img = Image.new('RGB', (1080, 1080), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # 基本的なテキスト描画
            draw.text((540, 200), "Game Result", fill=(0, 0, 0), font=font, anchor="mm")
            draw.text((270, 400), player1, fill=(0, 0, 0), font=font, anchor="mm")
            draw.text((810, 400), player2, fill=(0, 0, 0), font=font, anchor="mm")
            draw.text((540, 400), "vs", fill=(255, 0, 0), font=font, anchor="mm")
            
            # 簡易スコア表示
            player1_wins = sum(1 for score in scores if score[0] > score[1])
            player2_wins = sum(1 for score in scores if score[1] > score[0])
            
            draw.text((270, 600), str(player1_wins), fill=(0, 0, 0), font=font, anchor="mm")
            draw.text((810, 600), str(player2_wins), fill=(0, 0, 0), font=font, anchor="mm")
            
            return img
    
    generator = FallbackGenerator()

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