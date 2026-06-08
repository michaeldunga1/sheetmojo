(function(){
  const inputEl = document.getElementById('text-input');
  const totalCharsEl = document.getElementById('total-chars');
  const charsNoSpacesEl = document.getElementById('chars-no-spaces');
  const lineCountEl = document.getElementById('line-count');

  function updateCounts() {
    const text = inputEl.value;
    totalCharsEl.textContent = text.length;
    charsNoSpacesEl.textContent = text.replace(/\s+/g, '').length;
    lineCountEl.textContent = text.split(/\r?\n/).length;
  }

  inputEl.addEventListener('input', updateCounts);
  updateCounts();
})();