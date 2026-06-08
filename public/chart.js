const dataInput = document.getElementById('data-input');
const dataFormat = document.getElementById('data-format');
const chartType = document.getElementById('chart-type');
const xField = document.getElementById('x-field');
const yField = document.getElementById('y-field');
const renderButton = document.getElementById('render-chart');
const clearButton = document.getElementById('clear-chart');
const status = document.getElementById('status');
const ctx = document.getElementById('chart-canvas').getContext('2d');
let chart = null;

function parseCsv(text) {
  const rows = text.trim().split(/\r?\n/).filter(Boolean).map(line => line.split(/,(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)/g).map(cell => cell.trim().replace(/^"|"$/g, '')));
  if (rows.length < 2) throw new Error('CSV must contain a header row and at least one data row.');
  const headers = rows[0];
  return rows.slice(1).map(row => headers.reduce((obj, header, index) => {
    obj[header] = row[index] ?? '';
    return obj;
  }, {}));
}

function parseJson(text) {
  const data = JSON.parse(text);
  if (!Array.isArray(data)) throw new Error('JSON input must be an array of objects.');
  return data;
}

function getFieldOptions(records) {
  const fields = records.reduce((set, row) => {
    Object.keys(row).forEach(key => set.add(key));
    return set;
  }, new Set());
  return Array.from(fields);
}

function detectNumericFields(records, fields) {
  return fields.reduce((map, field) => {
    const values = records.map(row => String(row[field] ?? '').trim()).filter(value => value !== '');
    const numeric = values.length > 0 && values.every(value => !Number.isNaN(Number(value)));
    map[field] = numeric;
    return map;
  }, {});
}

function chooseDefaultFields(records, fields) {
  const numericMap = detectNumericFields(records, fields);
  const stringFields = fields.filter(field => !numericMap[field]);
  const numericFields = fields.filter(field => numericMap[field]);

  const x = stringFields[0] || fields[0];
  const y = numericFields[0] || fields[1] || fields[0];
  return { x, y };
}

function populateFieldSelectors(fields, defaultSelection = {}) {
  xField.innerHTML = '';
  yField.innerHTML = '';
  fields.forEach(field => {
    const optionA = document.createElement('option');
    optionA.value = field;
    optionA.textContent = field;
    xField.appendChild(optionA);

    const optionB = document.createElement('option');
    optionB.value = field;
    optionB.textContent = field;
    yField.appendChild(optionB);
  });
  if (fields.length) {
    xField.value = defaultSelection.x || fields[0];
    yField.value = defaultSelection.y || fields[1] || fields[0];
  }
}

function toNumber(value) {
  const num = Number(String(value).trim());
  return Number.isFinite(num) ? num : NaN;
}

function renderChart(data, labels, datasetLabel, type) {
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type,
    data: {
      labels,
      datasets: [{
        label: datasetLabel,
        data,
        backgroundColor: labels.map((_, index) => `hsl(${(index * 40) % 360}, 70%, 55%)`),
        borderColor: labels.map((_, index) => `hsl(${(index * 40) % 360}, 70%, 35%)`),
        borderWidth: 2,
        fill: false  // FIX: was `type !== 'pie'`, which incorrectly filled line charts as area charts
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: type === 'pie' ? {} : {
        x: { title: { display: true, text: xField.value } },
        y: { title: { display: true, text: yField.value } }
      },
      plugins: {
        legend: { display: type !== 'pie' ? false : true }
      }
    }
  });
}

function updateStatus(message, isError = false) {
  status.textContent = message;
  status.classList.toggle('text-rose-600', isError);
  status.classList.toggle('text-slate-600', !isError);
}

function parseData() {
  const raw = dataInput.value.trim();
  if (!raw) throw new Error('Please paste CSV or JSON data.');

  if (dataFormat.value === 'csv') {
    return parseCsv(raw);
  }
  return parseJson(raw);
}

function updateFieldsFromData() {
  try {
    const records = parseData();
    const fields = getFieldOptions(records);
    if (!fields.length) throw new Error('No fields were found in the data.');
    const defaults = chooseDefaultFields(records, fields);
    populateFieldSelectors(fields, defaults);
    updateStatus(`Field selectors updated. Defaulting to x='${defaults.x}' and y='${defaults.y}'.`);
    return records;
  } catch (error) {
    updateStatus(error.message, true);
    throw error;
  }
}

function buildChartData(records) {
  const xKey = xField.value;
  const yKey = yField.value;
  const labels = records.map(row => String(row[xKey] ?? ''));
  const values = records.map(row => toNumber(row[yKey]));
  const invalidRows = values.reduce((count, value) => count + (Number.isNaN(value) ? 1 : 0), 0);
  if (invalidRows > 0) {
    throw new Error(`Field '${yKey}' must contain numeric values. ${invalidRows} row(s) contained non-numeric data.`);
  }
  return { labels, values };
}

renderButton.addEventListener('click', () => {
  try {
    const records = updateFieldsFromData();
    const { labels, values } = buildChartData(records);
    renderChart(values, labels, `${yField.value} vs ${xField.value}`, chartType.value);
    updateStatus('Chart rendered successfully.');
  } catch (error) {
    updateStatus(error.message, true);
  }
});

clearButton.addEventListener('click', () => {
  dataInput.value = '';
  xField.innerHTML = '';
  yField.innerHTML = '';
  if (chart) {
    chart.destroy();
    chart = null;
  }
  updateStatus('Paste your data and choose fields to preview a chart.');
});

[dataInput, dataFormat].forEach(element => {
  element.addEventListener('change', () => {
    try {
      updateFieldsFromData();
    } catch (err) {
      // ignore until render is clicked
    }
  });
});