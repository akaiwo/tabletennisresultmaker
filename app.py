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
        
        # フォントファイルをダウンロードして準備
        self.setup_fonts()
        
    def download_font_if_needed(self, url, filename):
        """必要に応じてフォントファイルをダウンロード"""
        font_path = os.path.join('fonts', filename)
        
        # fontsディレクトリを作成
        os.makedirs('fonts', exist_ok=True)
        
        # ファイルが存在しない場合のみダウンロード
        if not os.path.exists(font_path):
            try:
                print(f"Downloading font: {filename}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                print(f"Font downloaded: {filename}")
                
            except Exception as e:
                print(f"Failed to download font {filename}: {e}")
                return None
                
        return font_path if os.path.exists(font_path) else None
    
    def setup_fonts(self):
        """フォントをセットアップ"""
        # Google Fontsから日本語対応フォントをダウンロード
        font_urls = {
            'NotoSansJP-Regular.ttf': 'https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf',
            'NotoSansJP-Bold.ttf': 'https://fonts.gstatic.com/s/notosansjp/v52/NotoSansJP-Bold.ttf',
        }
        
        self.font_paths = {}
        
        # 各フォントをダウンロード
        for filename, url in font_urls.items():
            try:
                # まず簡単なURL（直接ダウンロード可能）を試す
                if 'gstatic' in url:
                    font_path = self.download_font_if_needed(url, filename)
                    if font_path:
                        self.font_paths[filename] = font_path
                        continue
                
                # Google Fonts APIを使用してダウンロード
                # より確実な方法として、代替のCDNを使用
                alt_urls = {
                    'NotoSansJP-Regular.ttf': 'https://fonts.gstatic.com/s/notosansjp/v52/NotoSansJP-Regular.ttf',
                    'NotoSansJP-Bold.ttf': 'https://fonts.gstatic.com/s/notosansjp/v52/NotoSansJP-Bold.ttf',
                }
                
                if filename in alt_urls:
                    font_path = self.download_font_if_needed(alt_urls[filename], filename)
                    if font_path:
                        self.font_paths[filename] = font_path
                        
            except Exception as e:
                print(f"Error setting up font {filename}: {e}")
    
    def get_font(self, size, bold=False, italic=False):
        """フォントを取得（クラウド環境対応版）"""
        # まずダウンロードしたフォントを試す
        try:
            if bold and 'NotoSansJP-Bold.ttf' in self.font_paths:
                return ImageFont.truetype(self.font_paths['NotoSansJP-Bold.ttf'], size)
            elif 'NotoSansJP-Regular.ttf' in self.font_paths:
                return ImageFont.truetype(self.font_paths['NotoSansJP-Regular.ttf'], size)
        except Exception as e:
            print(f"Error loading downloaded font: {e}")
        
        # システムフォントを試す（ローカル環境用）
        system = platform.system()
        font_paths = []
        
        if system == "Windows":
            if bold:
                font_paths = [
                    "C:/Windows/Fonts/arialbd.ttf",
                    "C:/Windows/Fonts/NotoSansCJK-Bold.ttc",
                    "C:/Windows/Fonts/meiryob.ttc",
                ]
            else:
                font_paths = [
                    "C:/Windows/Fonts/arial.ttf",
                    "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
                    "C:/Windows/Fonts/meiryo.ttc",
                ]
        elif system == "Darwin":  # macOS
            if bold:
                font_paths = [
                    "/System/Library/Fonts/Arial Bold.ttf",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                ]
            else:
                font_paths = [
                    "/System/Library/Fonts/Arial.ttf",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                ]
        else:  # Linux (クラウド環境)
            if bold:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                ]
            else:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]
        
        # システムフォントを順番に試す
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except Exception as e:
                continue
        
        # すべて失敗した場合はデフォルトフォント
        print("Warning: Using default font. Text may not display correctly.")
        try:
            return ImageFont.load_default()
        except:
            # 最終手段として小さなデフォルトフォントを作成
            return ImageFont.load_default()
    
    def draw_text_with_fallback(self, draw, text, position, font, fill):
        """フォールバック付きテキスト描画"""
        try:
            # まず指定されたフォントで描画を試す
            draw.text(position, text, fill=fill, font=font)
        except Exception as e:
            # 失敗した場合はデフォルトフォントで描画
            print(f"Font rendering failed, using fallback: {e}")
            default_font = ImageFont.load_default()
            draw.text(position, text, fill=fill, font=default_font)
    
    def create_image(self, player1, player2, scores, match_type):
        # 画像とDrawオブジェクトを作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # フォントを設定
        title_font = self.get_font(80, bold=True)
        name_font = self.get_font(45)
        score_font = self.get_font(120, bold=True)
        detail_font = self.get_font(35)
        win_font = self.get_font(60, bold=True)
        vs_font = self.get_font(50, bold=True)
        footer_font = self.get_font(30)
        
        # タイトル
        title_text = "Game Result"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
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
        win_bbox = draw.textbbox((0, 0), win_text, font=win_font)
        win_width = win_bbox[2] - win_bbox[0]
        
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
        player1_bbox = draw.textbbox((0, 0), player1, font=name_font)
        player1_width = player1_bbox[2] - player1_bbox[0]
        self.draw_text_with_fallback(draw, player1, 
                                   (left_x - player1_width // 2, player_y), 
                                   name_font, self.secondary_color)
        
        # プレイヤー2（右側）
        player2_bbox = draw.textbbox((0, 0), player2, font=name_font)
        player2_width = player2_bbox[2] - player2_bbox[0]
        self.draw_text_with_fallback(draw, player2, 
                                   (right_x - player2_width // 2, player_y), 
                                   name_font, self.secondary_color)
        
        # 「vs」をプレイヤー名の間に配置
        vs_text = "vs"
        vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
        vs_width = vs_bbox[2] - vs_bbox[0]
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
            score1_bbox = draw.textbbox((0, 0), score1_text, font=detail_font)
            score1_width = score1_bbox[2] - score1_bbox[0]
            self.draw_text_with_fallback(draw, score1_text, 
                                       (score_left_x - score1_width // 2, y_pos), 
                                       detail_font, self.secondary_color)
            
            # 右側のスコア
            score2_text = str(score2)
            score2_bbox = draw.textbbox((0, 0), score2_text, font=detail_font)
            score2_width = score2_bbox[2] - score2_bbox[0]
            self.draw_text_with_fallback(draw, score2_text, 
                                       (score_right_x - score2_width // 2, y_pos), 
                                       detail_font, self.secondary_color)
            
            # 中央のハイフン
            dash_text = "-"
            dash_bbox = draw.textbbox((0, 0), dash_text, font=detail_font)
            dash_width = dash_bbox[2] - dash_bbox[0]
            self.draw_text_with_fallback(draw, dash_text, 
                                       ((self.width - dash_width) // 2, y_pos), 
                                       detail_font, self.secondary_color)
        
        # 最終スコア（セット数）
        final_score1 = str(player1_wins)
        final_bbox1 = draw.textbbox((0, 0), final_score1, font=score_font)
        final_width1 = final_bbox1[2] - final_bbox1[0]
        self.draw_text_with_fallback(draw, final_score1, 
                                   (left_x - final_width1 // 2, final_y), 
                                   score_font, self.primary_color)
        
        final_score2 = str(player2_wins)
        final_bbox2 = draw.textbbox((0, 0), final_score2, font=score_font)
        final_width2 = final_bbox2[2] - final_bbox2[0]
        self.draw_text_with_fallback(draw, final_score2, 
                                   (right_x - final_width2 // 2, final_y), 
                                   score_font, self.primary_color)
        
        # 装飾的な要素
        draw.rectangle([100, 180, self.width - 100, 185], fill=self.primary_color)
        draw.rectangle([100, self.height - 150, self.width - 100, self.height - 145], 
                      fill=self.primary_color)
        
        # フッターテキスト
        footer_text = "Table Tennis Result Generator"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
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
        
        return send_file(img_io, mimetype='image/png', 
                        as_attachment=True, 
                        download_name=f'卓球結果_{player1}_vs_{player2}.png')
        
    except Exception as e:
        return f"エラーが発生しました: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)