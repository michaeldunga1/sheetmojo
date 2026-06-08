(function(){
  const urlInput = document.getElementById('page-url');
  const convertBtn = document.getElementById('convert');
  const clearBtn = document.getElementById('clear');
  const statusEl = document.getElementById('status');
  const downloadLink = document.getElementById('download-link');
  let objectUrl = null;

  function setStatus(message) {
    statusEl.textContent = message;
  }

  function clearResult() {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
    downloadLink.style.display = 'none';
    downloadLink.href = '#';
  }

  async function generatePdf() {
    const url = urlInput.value.trim();
    if (!url) {
      setStatus('Please enter a valid web page URL.');
      return;
    }

    clearResult();
    setStatus('Generating PDF...');

    try {
      const response = await fetch('/api/page-to-pdf?url=' + encodeURIComponent(url));
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        setStatus(errorBody?.error || 'PDF generation failed.');
        return;
      }

      const blob = await response.blob();
      objectUrl = URL.createObjectURL(blob);
      downloadLink.href = objectUrl;
      downloadLink.download = 'page.pdf';
      downloadLink.style.display = 'inline-block';
      setStatus('PDF is ready. Click the link to download.');
    } catch (error) {
      setStatus('Error: ' + error.message);
    }
  }

  convertBtn.addEventListener('click', generatePdf);
  clearBtn.addEventListener('click', () => {
    urlInput.value = '';
    clearResult();
    setStatus('Enter a URL and click Generate PDF.');
  });
})();