(function(){
  const convertBtn = document.getElementById('convert');
  const copyBtn = document.getElementById('copy');
  const clearBtn = document.getElementById('clear');
  const inputEl = document.getElementById('input');
  const outputEl = document.getElementById('output');

  function updateButtons(){
    const hasInput = inputEl.value.trim().length > 0;
    convertBtn.disabled = !hasInput;
    copyBtn.disabled = outputEl.value.trim().length === 0;
    clearBtn.disabled = !hasInput && outputEl.value.trim().length === 0;
  }

  function parseCsv(csvText){
    const rows = [];
    let row = [];
    let cell = '';
    let inQuotes = false;

    for (let i = 0; i < csvText.length; i++) {
      const char = csvText[i];
      const next = csvText[i + 1];

      if (inQuotes) {
        if (char === '"') {
          if (next === '"') {
            cell += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          cell += char;
        }
        continue;
      }

      if (char === '"') {
        inQuotes = true;
        continue;
      }

      if (char === ',') {
        row.push(cell);
        cell = '';
        continue;
      }

      if (char === '\n' || char === '\r') {
        if (char === '\r' && next === '\n') {
          i++;
        }
        row.push(cell);
        rows.push(row);
        row = [];
        cell = '';
        continue;
      }

      cell += char;
    }

    if (cell.length > 0 || row.length > 0) {
      row.push(cell);
      rows.push(row);
    }

    return rows;
  }

  function convert(){
    const raw = inputEl.value.trim();
    if(!raw){
      outputEl.value = '';
      return;
    }

    try {
      const rows = parseCsv(raw);
      if (rows.length === 0) {
        outputEl.value = '[]';
      } else {
        const headers = rows[0].map(header => String(header || '').trim());
        const data = rows.slice(1).map(row => {
          const item = {};
          headers.forEach((header, index) => {
            item[header || `column_${index + 1}`] = row[index] ?? '';
          });
          return item;
        });
        outputEl.value = JSON.stringify(data, null, 2);
      }
    } catch (error) {
      outputEl.value = 'Error: Invalid CSV data.';
    }

    updateButtons();
  }

  convertBtn.addEventListener('click', convert);

  copyBtn.addEventListener('click', () => {
    if (!outputEl.value) return;
    navigator.clipboard.writeText(outputEl.value).catch(() => {
      outputEl.select();
      document.execCommand('copy');
    });
  });

  clearBtn.addEventListener('click', () => {
    inputEl.value = '';
    outputEl.value = '';
    updateButtons();
  });

  inputEl.addEventListener('input', updateButtons);

  updateButtons();
})();
