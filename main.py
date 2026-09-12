#!/usr/bin/env python3
"""
Finance Shorts Generator
Gerador automático de vídeos sobre finanças para YouTube Shorts
"""

import json
import os
import sys
import argparse
import random
from datetime import datetime
from pathlib import Path

try:
    from moviepy.editor import (
        TextClip, ColorClip, CompositeVideoClip, 
        AudioFileClip, concatenate_videoclips
    )
    import pyttsx3
except ImportError:
    print("❌ Erro: Instale as dependências com: pip install -r requirements.txt")
    sys.exit(1)


class FinanceShortsGenerator:
    """Gerador de vídeos sobre finanças para YouTube Shorts"""
    
    def __init__(self, config_path="config.json", scripts_path="content/scripts.json"):
        """Inicializa o gerador"""
        self.config = self.load_json(config_path)
        self.scripts = self.load_json(scripts_path)
        self.output_dir = Path(self.config['output_path'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    @staticmethod
    def load_json(path):
        """Carrega arquivo JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_audio(self, text, filename):
        """Gera áudio com TTS"""
        print(f"🎙️ Gerando áudio para: {filename}")
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Velocidade
            engine.setProperty('volume', 0.9)  # Volume
            
            # Definir idioma português brasileiro
            engine.setProperty('voice', 1)  # Segunda voz disponível
            
            audio_path = self.output_dir / f"{filename}.mp3"
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
            
            return str(audio_path)
        except Exception as e:
            print(f"⚠️ Erro ao gerar áudio: {e}")
            return None
    
    def create_video_from_script(self, script, video_num):
        """Cria um vídeo a partir de um script"""
        print(f"\n📹 Criando vídeo {video_num}: {script['title']}")
        
        config = self.config['video_settings']
        text_cfg = self.config['text_settings']
        monetization = self.config['monetization']
        
        width = config['width']
        height = config['height']
        duration = config['duration']
        
        # Criar fundo colorido
        bg_color = self.config['colors']['background']
        background = ColorClip(
            size=(width, height),
            color=hex_to_rgb(bg_color),
            duration=duration
        )
        
        # Criar texto principal
        text_clip = TextClip(
            txt=script['script'],
            fontsize=text_cfg['font_size'],
            color=text_cfg['font_color'],
            font=text_cfg['font_family'],
            method='caption',
            size=(width - 100, height - 200),
            align='center'
        ).set_duration(duration).set_position('center')
        
        # Criar título
        title_clip = TextClip(
            txt=f"💰 {script['title']}",
            fontsize=50,
            color=hex_to_rgb(self.config['colors']['secondary']),
            font='Arial-Bold',
        ).set_duration(2).set_position(('center', 100))
        
        # Compor vídeo
        video = CompositeVideoClip([
            background,
            text_clip.set_position(('center', 'center')),
            title_clip.set_position(('center', 100))
        ])
        
        # Gerar áudio
        audio_file = self.generate_audio(
            script['script'], 
            f"audio_{video_num}"
        )
        
        # Adicionar áudio
        if audio_file and os.path.exists(audio_file):
            audio = AudioFileClip(audio_file)
            video = video.set_audio(audio)
        
        # Salvar vídeo
        output_path = self.output_dir / f"finance_short_{video_num:03d}.mp4"
        print(f"💾 Salvando em: {output_path}")
        
        video.write_videofile(
            str(output_path),
            fps=config['fps'],
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        return str(output_path)
    
    def generate_videos(self, count=5, category=None, random_select=True):
        """Gera múltiplos vídeos"""
        print(f"\n🎬 Gerando {count} vídeos...")
        
        # Selecionar scripts
        available_scripts = self.scripts['scripts']
        
        if category:
            available_scripts = [
                s for s in available_scripts 
                if s['category'].lower() == category.lower()
            ]
        
        if not available_scripts:
            print("❌ Nenhum script encontrado!")
            return
        
        if random_select:
            selected_scripts = random.choices(available_scripts, k=min(count, len(available_scripts)))
        else:
            selected_scripts = available_scripts[:count]
        
        generated_videos = []
        
        for i, script in enumerate(selected_scripts, 1):
            try:
                video_path = self.create_video_from_script(script, i)
                generated_videos.append(video_path)
                print(f"✅ Vídeo {i}/{count} criado com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao criar vídeo {i}: {e}")
        
        print(f"\n✅ {len(generated_videos)}/{count} vídeos gerados com sucesso!")
        print(f"📂 Salvos em: {self.output_dir}")
        
        return generated_videos


def hex_to_rgb(hex_color):
    """Converte hex para RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="Gerador de vídeos sobre finanças para YouTube Shorts"
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=5,
        help='Número de vídeos a gerar (padrão: 5)'
    )
    parser.add_argument(
        '--category',
        type=str,
        default=None,
        help='Categoria específica (investimento, economia, cripto, etc)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='Listar todos os scripts disponíveis'
    )
    
    args = parser.parse_args()
    
    generator = FinanceShortsGenerator()
    
    if args.list:
        print("\n📋 Scripts Disponíveis:\n")
        for script in generator.scripts['scripts']:
            print(f"• {script['title']} ({script['category']})")
        return
    
    generator.generate_videos(count=args.count, category=args.category)


if __name__ == '__main__':
    main()
