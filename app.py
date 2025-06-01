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
        
    def get_font(self, size, bold=False, italic=False):
        """OSに応じて適切な日本語フォントを取得"""
        system = platform.system()
        
        # フォントファイルのパスリスト（優先順）
        font_paths = []
        
        if system == "Windows":
            if bold and italic:
                font_paths = [
                    "C:/Windows/Fonts/arialbi.ttf",  # Arial Bold Italic
                    "C:/Windows/Fonts/NotoSansCJK-Bold.ttc",
                    "C:/Windows/Fonts/meiryob.ttc",
                    "C:/Windows/Fonts/arial.ttf"
                ]
            elif bold:
                font_paths = [
                    "C:/Windows/Fonts/arialbd.ttf",  # Arial Bold
                    "C:/Windows/Fonts/NotoSansCJK-Bold.ttc",
                    "C:/Windows/Fonts/meiryob.ttc",
                    "C:/Windows/Fonts/arial.ttf"
                ]
            elif italic:
                font_paths = [
                    "C:/Windows/Fonts/ariali.ttf",  # Arial Italic
                    "C:/Windows/Fonts/arial.ttf"
                ]
            else:
                font_paths = [
                    "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
                    "C:/Windows/Fonts/meiryo.ttc",
                    "C:/Windows/Fonts/msgothic.ttc",
                    "C:/Windows/Fonts/arial.ttf"
                ]
        elif system == "Darwin":  # macOS
            if bold and italic:
                font_paths = [
                    "/System/Library/Fonts/Arial Bold Italic.ttf",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                    "/System/Library/Fonts/Arial.ttf"
                ]
            elif bold:
                font_paths = [
                    "/System/Library/Fonts/Arial Bold.ttf",
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                    "/System/Library/Fonts/Arial.ttf"
                ]
            elif italic:
                font_paths = [
                    "/System/Library/Fonts/Arial Italic.ttf",
                    "/System/Library/Fonts/Arial.ttf"
                ]
            else:
                font_paths = [
                    "/System/Library/Fonts/Hiragino Sans GB.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                    "/Library/Fonts/Arial Unicode MS.ttf",
                    "/System/Library/Fonts/Arial.ttf"
                ]
        else:  # Linux
            if bold and italic:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                ]
            elif bold:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                ]
            elif italic:
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                ]
            else:
                font_paths = [
                    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/TTF/DejaVuSans.ttf"
                ]
        
        # フォントファイルを順番に試す
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
            except:
                continue
        
        # すべて失敗した場合はデフォルトフォントを使用
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def create_image(self, player1, player2, scores, match_type):
        # 画像とDrawオブジェクトを作成
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # フォントを設定
        title_font = self.get_font(80, bold=True, italic=True)
        name_font = self.get_font(45)  # プレイヤー名は通常フォント
        score_font = self.get_font(120, bold=True, italic=True)  # 最終スコアを斜体に
        detail_font = self.get_font(35, italic=True)  # セットスコアを斜体に
        win_font = self.get_font(60, bold=True, italic=True)
        vs_font = self.get_font(50, bold=True, italic=True)  # vsフォントを追加
        
        # タイトル
        title_text = "Game Result"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((self.width - title_width) // 2, 80), title_text, 
                 fill=self.primary_color, font=title_font)
        
        # 勝者を判定
        player1_wins = sum(1 for score in scores if score[0] > score[1])
        player2_wins = sum(1 for score in scores if score[1] > score[0])
        winner = player1 if player1_wins > player2_wins else player2
        
        # プレイヤー名と各セットのスコアを左右に配置（セットスコアをより中央寄りに）
        left_x = 230  # 左側の基準位置（プレイヤー名用）
        right_x = self.width - 230  # 右側の基準位置（プレイヤー名用）
        
        # セットスコア用の位置（より中央寄り）
        score_left_x = 420  # 左側セットスコアの位置
        score_right_x = self.width - 420  # 右側セットスコアの位置
        
        # WIN表示（勝利したプレイヤーの上に配置）
        win_text = "WIN"
        win_bbox = draw.textbbox((0, 0), win_text, font=win_font)
        win_width = win_bbox[2] - win_bbox[0]
        
        if winner == player1:
            # プレイヤー1の上にWIN表示
            draw.text((left_x - win_width // 2, 230), win_text, 
                     fill=self.accent_color, font=win_font)
        else:
            # プレイヤー2の上にWIN表示
            draw.text((right_x - win_width // 2, 230), win_text, 
                     fill=self.accent_color, font=win_font)
        
        # プレイヤー名を配置
        player_y = 300
        
        # プレイヤー1（左側）
        player1_bbox = draw.textbbox((0, 0), player1, font=name_font)
        player1_width = player1_bbox[2] - player1_bbox[0]
        draw.text((left_x - player1_width // 2, player_y), player1, 
                 fill=self.secondary_color, font=name_font)
        
        # プレイヤー2（右側）
        player2_bbox = draw.textbbox((0, 0), player2, font=name_font)
        player2_width = player2_bbox[2] - player2_bbox[0]
        draw.text((right_x - player2_width // 2, player_y), player2, 
                 fill=self.secondary_color, font=name_font)
        
        # 「vs」をプレイヤー名の間に配置（WINと同じカラー）
        vs_text = "vs"
        vs_bbox = draw.textbbox((0, 0), vs_text, font=vs_font)
        vs_width = vs_bbox[2] - vs_bbox[0]
        draw.text(((self.width - vs_width) // 2, player_y + 5), vs_text, 
                 fill=self.accent_color, font=vs_font)
        
        # 各セットのスコアを縦に並べて表示（より中央寄りの位置）
        # マッチタイプに応じて中央セットの位置を調整
        num_sets = len(scores)
        line_height = 50
        
        # 最終スコアのy座標
        final_y = 540
        
        # 中央セットのインデックスを計算（0から始まる）
        if num_sets == 1:
            center_set_index = 0  # 第1セット
        elif num_sets <= 3:
            center_set_index = 1  # 第2セット
        elif num_sets <= 5:
            center_set_index = 2  # 第3セット
        else:  # 7セットマッチ
            center_set_index = 3  # 第4セット
        
        # 中央セットが最終スコア+50と同じy座標になるように開始位置を計算
        score_start_y = final_y + 50 - (center_set_index * line_height)
        
        for i, (score1, score2) in enumerate(scores):
            y_pos = score_start_y + i * line_height
            
            # 左側のスコア（プレイヤー1）- より中央寄り
            score1_text = str(score1)
            score1_bbox = draw.textbbox((0, 0), score1_text, font=detail_font)
            score1_width = score1_bbox[2] - score1_bbox[0]
            draw.text((score_left_x - score1_width // 2, y_pos), score1_text, 
                     fill=self.secondary_color, font=detail_font)
            
            # 右側のスコア（プレイヤー2）- より中央寄り
            score2_text = str(score2)
            score2_bbox = draw.textbbox((0, 0), score2_text, font=detail_font)
            score2_width = score2_bbox[2] - score2_bbox[0]
            draw.text((score_right_x - score2_width // 2, y_pos), score2_text, 
                     fill=self.secondary_color, font=detail_font)
            
            # 中央のハイフン
            dash_text = "-"
            dash_bbox = draw.textbbox((0, 0), dash_text, font=detail_font)
            dash_width = dash_bbox[2] - dash_bbox[0]
            draw.text(((self.width - dash_width) // 2, y_pos), dash_text, 
                     fill=self.secondary_color, font=detail_font)
        
        # 最終スコア（セット数）の位置
        
        # 左側の最終スコア
        final_score1 = str(player1_wins)
        final_bbox1 = draw.textbbox((0, 0), final_score1, font=score_font)
        final_width1 = final_bbox1[2] - final_bbox1[0]
        draw.text((left_x - final_width1 // 2, final_y), final_score1, 
                 fill=self.primary_color, font=score_font)
        
        # 右側の最終スコア
        final_score2 = str(player2_wins)
        final_bbox2 = draw.textbbox((0, 0), final_score2, font=score_font)
        final_width2 = final_bbox2[2] - final_bbox2[0]
        draw.text((right_x - final_width2 // 2, final_y), final_score2, 
                 fill=self.primary_color, font=score_font)
        
        
        # 装飾的な要素を追加
        # 上部の線
        draw.rectangle([100, 180, self.width - 100, 185], fill=self.primary_color)
        # 下部の線
        draw.rectangle([100, self.height - 150, self.width - 100, self.height - 145], 
                      fill=self.primary_color)
        
        # 下部の線の下にフッターテキストを追加
        footer_font = self.get_font(30, italic=True)
        footer_text = "Table Tennis Result Generator"
        footer_bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((self.width - footer_width) // 2, self.height - 90), footer_text, 
                 fill=self.secondary_color, font=footer_font)
        
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
                
                if score1 and score2:  # 空でない場合のみ追加
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