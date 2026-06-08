(function(){
  const urlInput = document.getElementById('youtube-url');
  const audioBtn = document.getElementById('download-audio');
  const videoBtn = document.getElementById('download-video');
  const clearBtn = document.getElementById('clear');
  const statusEl = document.getElementById('status');
  const downloadLink = document.getElementById('download-link');

  function setStatus(message) {
    statusEl.textContent = message;
  }

  function clearResult() {
    downloadLink.style.display = 'none';
    downloadLink.href = '#';
  }

  function updateLink(type) {
    const url = urlInput.value.trim();
    if (!url) {
      setStatus('Please enter a YouTube URL.');
      return;
    }
    const href = '/api/youtube?url=' + encodeURIComponent(url) + '&type=' + type;
    downloadLink.href = href;
    downloadLink.textContent = type === 'audio' ? 'Download audio file' : 'Download video file';
    downloadLink.style.display = 'inline-block';
    setStatus('Click the download link below after it appears.');
  }

  audioBtn.addEventListener('click', () => updateLink('audio'));
  videoBtn.addEventListener('click', () => updateLink('video'));
  clearBtn.addEventListener('click', () => {
    urlInput.value = '';
    clearResult();
    setStatus('Enter a YouTube URL first.');
  });
})();