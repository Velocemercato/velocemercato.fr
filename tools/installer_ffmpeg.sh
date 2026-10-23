#!/usr/bin/env bash
# Outils autonomes : ne pas dépendre des centaines de paquets des miroirs APT.
set -euo pipefail

if [[ ${1:-} != --standalone ]] && command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null \
    && ffmpeg -hide_banner -encoders 2>/dev/null | awk '$2 == "libx264" {found=1} END {exit !found}'; then
  echo '::notice::FFmpeg et FFprobe déjà disponibles.'
  exit 0
fi
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || {
  echo '::error::Cette distribution FFmpeg nécessite Linux x86_64.'; exit 1;
}
vm_ffmpeg_dir=${VM_FFMPEG_DIR:-${RUNNER_TEMP:-${TMPDIR:-/tmp}}/vm-ffmpeg-8.1-gpl}
vm_bin_dir="$vm_ffmpeg_dir/bin"
mkdir -p "$vm_bin_dir"
if [[ ! -x "$vm_bin_dir/ffmpeg" || ! -x "$vm_bin_dir/ffprobe" ]]; then
  vm_download_dir=$(mktemp -d)
  trap 'rm -rf "$vm_download_dir"' EXIT
  vm_archive=ffmpeg-n8.1-latest-linux64-gpl-8.1.tar.xz
  vm_release=https://github.com/BtbN/FFmpeg-Builds/releases/download/latest
  echo '::notice::Téléchargement des outils FFmpeg 8.1 autonomes et de leurs empreintes publiées.'
  curl --fail --location --silent --show-error --retry 2 --connect-timeout 15 --max-time 60 \
    "$vm_release/checksums.sha256" -o "$vm_download_dir/checksums.sha256"
  vm_expected=$(awk -v name="$vm_archive" '$2 == name {print $1}' "$vm_download_dir/checksums.sha256")
  [[ $vm_expected =~ ^[a-f0-9]{64}$ ]] || { echo '::error::Empreinte FFmpeg absente ou invalide.'; exit 1; }
  curl --fail --location --silent --show-error --retry 2 --connect-timeout 15 --max-time 180 \
    "$vm_release/$vm_archive" -o "$vm_download_dir/$vm_archive"
  printf '%s  %s\n' "$vm_expected" "$vm_download_dir/$vm_archive" | sha256sum --check --status
  vm_archive_root=${vm_archive%.tar.xz}
  # Extraire seulement les deux outils attendus, aucun autre chemin de l'archive.
  tar -xJf "$vm_download_dir/$vm_archive" -C "$vm_bin_dir" --strip-components=2 \
    "$vm_archive_root/bin/ffmpeg" "$vm_archive_root/bin/ffprobe"
  chmod +x "$vm_bin_dir/ffmpeg" "$vm_bin_dir/ffprobe"
fi
"$vm_bin_dir/ffmpeg" -version >/dev/null
"$vm_bin_dir/ffprobe" -version >/dev/null
"$vm_bin_dir/ffmpeg" -hide_banner -encoders 2>/dev/null | awk '$2 == "libx264" {found=1} END {exit !found}'
if [[ -n ${GITHUB_PATH:-} ]]; then printf '%s\n' "$vm_bin_dir" >> "$GITHUB_PATH"; fi
echo '::notice::FFmpeg et FFprobe 8.1 vérifiés, prêts sans installation APT.'
