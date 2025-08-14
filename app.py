# app.py
import os
import subprocess
from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

# ダウンロード先のディレクトリを作成
DOWNLOAD_DIR = 'downloads'
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        file_format = data.get('format', 'mp4')

        if not url:
            return jsonify({'success': False, 'error': 'URLが指定されていません。'})

        # yt-dlpのオプションを設定
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', # mp4形式でダウンロード
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4'
        }

        if file_format == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
            })

        # yt-dlpを実行
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # 拡張子が正しいことを確認
            base, ext = os.path.splitext(filename)
            if file_format == 'mp3' and ext != '.mp3':
                # mp3に変換されたファイル名を取得
                filename = base + '.mp3'

        # ダウンロードしたファイルへのパスを返す
        return jsonify({'success': True, 'file_path': f'/files/{os.path.basename(filename)}'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/files/<path:filename>')
def serve_file(filename):
    # ダウンロードしたファイルをユーザーに提供
    return send_file(os.path.join(DOWNLOAD_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
