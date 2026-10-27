"""Monte un reportage animé : voix off Piper (si disponible), scènes canvas (anim.html) filmées
image par image avec Playwright, sous-titres synchronisés, puis MP4 vertical + affiche.
Usage : python tools/reportage/render.py tools/reportage/alexia.json [--sans-voix] [--apercu 3,10,40]"""
import argparse
import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPS = 24
WPS = 2.6  # mots par seconde pour estimer une durée sans voix


def wav_len(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def voice_model(name, quality):
    """Même source et même cache que les voix des JT (~/.cache/vm-voices)."""
    import os
    import urllib.request
    folder = Path(os.getenv('VM_VOICES', str(Path.home() / '.cache' / 'vm-voices')))
    folder.mkdir(parents=True, exist_ok=True)
    base = f'https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/{name}/{quality}/fr_FR-{name}-{quality}'
    for ext in ('.onnx', '.onnx.json'):
        target = folder / f'fr_FR-{name}-{quality}{ext}'
        if not target.exists():
            urllib.request.urlretrieve(base + ext, target)
    return folder / f'fr_FR-{name}-{quality}.onnx'


def voix(phrases, out, name, quality):
    model = voice_model(name, quality)
    subprocess.run([sys.executable, '-m', 'piper', '--model', str(model), '--output_file', str(out),
                    '--length-scale', '0.95', '--sentence-silence', '0.35'],
                   input=' '.join(phrases).encode('utf-8'), check=True, capture_output=True, timeout=300)
    return wav_len(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--sans-voix', action='store_true')
    ap.add_argument('--apercu', default='')
    args = ap.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding='utf-8'))
    out = ROOT / cfg['sortie']
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        timeline, pistes = [], []
        for i, sc in enumerate(cfg['scenes']):
            words = sum(len(p.split()) for p in sc['vo'])
            if args.sans_voix:
                spoken = words / WPS
            else:
                spoken = voix(sc['vo'], tmp / f'v{i}.wav', *cfg['voix'])
            lead = 0.6  # la voix démarre après le fondu
            dur = max(sc.get('min', 4), lead + spoken + 0.9)
            subs, t = [], lead
            for p in sc['vo']:  # sous-titres au prorata des mots
                d = spoken * len(p.split()) / words
                subs.append([round(t, 2), round(t + d, 2), p])
                t += d
            timeline.append({'id': sc['id'], 'dur': round(dur, 2), 'sub': subs})
            pistes.append((tmp / f'v{i}.wav', lead, dur))
        total = sum(s['dur'] for s in timeline)
        print(f'Durée : {total:.1f} s', flush=True)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            page = b.new_page(viewport={'width': 1080, 'height': 1920})
            page.goto((Path(__file__).parent / 'anim.html').as_uri())
            page.evaluate('t => { window.TIMELINE = t; return window.ready }', timeline)
            if args.apercu:
                for s in args.apercu.split(','):
                    page.evaluate(f'renderAt({float(s)})')
                    page.locator('canvas').screenshot(path=str(out.parent / f'apercu-{s}.png'))
                b.close()
                return
            n = int(total * FPS)
            enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-',
                                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p',
                                    str(tmp / 'video.mp4')], stdin=subprocess.PIPE)
            for f in range(n):
                page.evaluate(f'renderAt({f / FPS})')
                enc.stdin.write(page.locator('canvas').screenshot(type='jpeg', quality=88))
                if f == int(4.5 * FPS):
                    page.locator('canvas').screenshot(path=str(out) + '-vertical.jpg', type='jpeg', quality=86)
                if f % (FPS * 20) == 0:
                    print(f'{f / FPS:.0f}/{total:.0f} s', flush=True)
            enc.stdin.close()
            enc.wait()
            b.close()
        # Piste audio : chaque voix posée au début de sa scène, silence ailleurs (aucune musique).
        if args.sans_voix:
            audio = ['-f', 'lavfi', '-t', f'{total:.2f}', '-i', 'anullsrc=r=48000:cl=stereo']
            fil = []
        else:
            inputs, delays, start = [], [], 0.0
            for k, (wav, lead, dur) in enumerate(pistes):
                inputs += ['-i', str(wav)]
                ms = int((start + lead) * 1000)
                delays.append(f'[{k + 1}:a]aresample=48000,adelay={ms}|{ms},apad[a{k}]')
                start += dur
            mix = ''.join(f'[a{k}]' for k in range(len(pistes)))
            audio = inputs
            fil = ['-filter_complex', ';'.join(delays) + f';{mix}amix=inputs={len(pistes)}:normalize=0,'
                   f'atrim=0:{total:.2f},highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=9,aformat=channel_layouts=stereo[a]']
        cmd = ['ffmpeg', '-v', 'error', '-y', '-i', str(tmp / 'video.mp4'), *audio, *fil,
               '-map', '0:v', '-map', '[a]' if fil else '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
               '-shortest', '-movflags', '+faststart', str(out) + '-vertical.mp4']
        subprocess.run(cmd, check=True)
        print('ok', str(out) + '-vertical.mp4', flush=True)


if __name__ == '__main__':
    main()
