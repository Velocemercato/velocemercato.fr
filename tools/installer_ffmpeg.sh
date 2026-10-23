#!/usr/bin/env bash
# Installation ciblée : ne pas bloquer la vidéo sur un dépôt APT tiers.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
  echo '::notice::FFmpeg et FFprobe déjà disponibles.'
  exit 0
fi

vm_apt_flags=(-o Acquire::ForceIPv4=true -o Acquire::Retries=1
  -o Acquire::http::Timeout=20 -o Acquire::https::Timeout=20
  -o DPkg::Lock::Timeout=30)

if [[ -s /etc/apt/sources.list.d/ubuntu.sources ]]; then
  vm_source_input=/etc/apt/sources.list.d/ubuntu.sources
  vm_source_suffix=.sources
elif [[ -s /etc/apt/sources.list ]]; then
  vm_source_input=/etc/apt/sources.list
  vm_source_suffix=.list
else
  echo '::error::Sources Ubuntu absentes : installation FFmpeg interrompue.'
  exit 1
fi

vm_apt_source=$(mktemp --suffix="$vm_source_suffix")
trap 'rm -f "$vm_apt_source"' EXIT
# Les index de l'image pointent parfois vers un miroir HTTP inaccessible.
# Conserver suites et clés Ubuntu, passer les archives ET la sécurité en HTTPS,
# et ignorer les dépôts tiers sans rapport avec la vidéo.
sed -E 's@https?://[^ /]*archive\.ubuntu\.com/ubuntu/?@https://archive.ubuntu.com/ubuntu/@g; s@http://security\.ubuntu\.com/@https://security.ubuntu.com/@g' \
  "$vm_source_input" > "$vm_apt_source"
vm_apt_flags+=(-o "Dir::Etc::sourcelist=$vm_apt_source" -o Dir::Etc::sourceparts=-)
echo '::notice::Installation depuis les seules sources Ubuntu signées en HTTPS.'
timeout 90 sudo -E apt-get "${vm_apt_flags[@]}" -o APT::Update::Error-Mode=any update -qq
timeout 180 sudo -E apt-get "${vm_apt_flags[@]}" install -y -qq --no-install-recommends ffmpeg
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null
echo '::notice::FFmpeg et FFprobe installés.'
