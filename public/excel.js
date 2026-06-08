const fileInput = document.getElementById('excel-file');
const outputFormat = document.getElementById('output-format');
const convertButton = document.getElementById('convert');
const downloadButton = document.getElementById('download-result');
const clearButton = document.getElementById('clear');
const status = document.getElementById('status');
const outputArea = document.getElementById('output');
let currentResult = '';
let currentFilename = 'excel-export';

function setControls(enabled) {
  convertButton.disabled = !enabled;
  downloadButton.disabled = !enabled || !currentResult;
}

function normalizeFilename(name) {
  return name.replace(/[^a-zA-Z0-9-_]/g, '_').toLowerCase();
}

function loadFile(file) {
  if (!file) {
    status.textContent = 'Select an Excel file first.';
    setControls(false);
    return;
  }

  status.textContent = `Ready to convert ${file.name}.`;
  currentFilename = normalizeFilename(file.name.replace(/\.[^.]+$/, '')) || 'excel-export';
  setControls(true);
}

function downloadText(filename, content, type = 'text/plain') {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function parseWorkbook(file) {
  const reader = new FileReader();
  reader.onload = event => {
    try {
      const data = new Uint8Array(event.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      const sheets = workbook.SheetNames;
      if (!sheets.length) {
        throw new Error('No sheets found in this workbook.');
      }

      if (outputFormat.value === 'csv') {
        const csv = XLSX.utils.sheet_to_csv(workbook.Sheets[sheets[0]]);
        currentResult = csv;
        outputArea.value = csv || 'No data found in the first sheet.';
        downloadButton.textContent = 'Download CSV';
        status.textContent = `Converted ${sheets[0]} to CSV.`;
      } else {
        const json = {};
        sheets.forEach(name => {
          const sheet = workbook.Sheets[name];
          json[name] = XLSX.utils.sheet_to_json(sheet, { defval: '' });
        });
        currentResult = JSON.stringify(json, null, 2);
        outputArea.value = currentResult;
        downloadButton.textContent = 'Download JSON';
        status.textContent = `Converted ${sheets.length} sheet${sheets.length === 1 ? '' : 's'} to JSON.`;
      }
      setControls(true);
    } catch (error) {
      status.textContent = `Conversion failed: ${error.message}`;
      outputArea.value = '';
      currentResult = '';
      setControls(false);
    }
  };
  reader.onerror = () => {
    status.textContent = 'Unable to read the file. Please try again.';
    outputArea.value = '';
    currentResult = '';
    setControls(false);
  };
  reader.readAsArrayBuffer(file);
}

fileInput.addEventListener('change', event => {
  const file = event.target.files[0];
  loadFile(file);
});

convertButton.addEventListener('click', () => {
  const file = fileInput.files[0];
  if (!file) {
    status.textContent = 'Please choose an Excel file to convert.';
    return;
  }
  status.textContent = 'Converting...';
  parseWorkbook(file);
});

downloadButton.addEventListener('click', () => {
  if (!currentResult) return;
  const extension = outputFormat.value === 'csv' ? 'csv' : 'json';
  const mime = outputFormat.value === 'csv' ? 'text/csv' : 'application/json';
  downloadText(`${currentFilename}.${extension}`, currentResult, mime);
});

clearButton.addEventListener('click', () => {
  fileInput.value = '';
  outputArea.value = '';
  status.textContent = 'Select an Excel file and click Convert.';
  currentResult = '';
  setControls(false);
});

setControls(false);
