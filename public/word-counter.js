(function(){
  const inputEl = document.getElementById('word-text');
  const wordCountEl = document.getElementById('word-count');
  const sentenceCountEl = document.getElementById('sentence-count');
  const paragraphCountEl = document.getElementById('paragraph-count');

  function countWords(text) {
    return text.trim().split(/\s+/).filter(Boolean).length;
  }

  function countSentences(text) {
    return text.split(/[.!?]+/).map(part => part.trim()).filter(Boolean).length;
  }

  function countParagraphs(text) {
    return text.split(/\n{2,}/).map(part => part.trim()).filter(Boolean).length;
  }

  function updateCounts() {
    const text = inputEl.value;
    wordCountEl.textContent = countWords(text);
    sentenceCountEl.textContent = countSentences(text);
    paragraphCountEl.textContent = countParagraphs(text);
  }

  inputEl.addEventListener('input', updateCounts);
  updateCounts();
})();