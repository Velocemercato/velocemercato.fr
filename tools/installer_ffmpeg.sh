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

# Les index de l'image peuvent déjà suffire. Éviter alors apt-get update,
# qui contacte également les dépôts tiers sans rapport avec cette vidéo.
echo '::notice::Installation ciblée de FFmpeg depuis les index existants.'
if timeout 120 sudo -E apt-get "${vm_apt_flags[@]}" install -y -qq --no-install-recommends ffmpeg; then
  command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null
  exit 0
fi

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
# Conserver suites et clés de signature, avec le miroir Ubuntu principal.
sed -E 's@https?://[^ /]*archive\.ubuntu\.com/ubuntu/?@http://archive.ubuntu.com/ubuntu/@g' \
  "$vm_source_input" > "$vm_apt_source"
vm_apt_flags+=(-o "Dir::Etc::sourcelist=$vm_apt_source" -o Dir::Etc::sourceparts=-)
echo '::notice::Actualisation limitée aux sources Ubuntu officielles.'
timeout 120 sudo -E apt-get "${vm_apt_flags[@]}" update -qq
timeout 120 sudo -E apt-get "${vm_apt_flags[@]}" install -y -qq --no-install-recommends ffmpeg
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null
echo '::notice::FFmpeg et FFprobe installés.'
