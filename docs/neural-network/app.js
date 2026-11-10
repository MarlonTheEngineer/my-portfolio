/* Interactive, locally trained neural-network visualization. No API or telemetry. */
(() => {
  "use strict";
  const { NeuralNetwork, generateDataset, randomGenerator } = window.NeuralNet;
  const $ = id => document.getElementById(id);
  const canvas = $('decision-canvas');
  const chart = $('loss-canvas');
  const choice = $('dataset');
  const slider = $('rate');
  const rateOutput = $('rate-value');
  const trainButton = $('train-button');
  const resetButton = $('reset-button');
  const epochText = $('epoch-value');
  const accuracyText = $('accuracy-value');
  const lossText = $('loss-value');
  const statusText = $('status');
  const sampleText = $('sample-status');
  const progress = $('progress');
  const progressFill = $('progress-fill');
  const MAX_STEPS = 720;
  const BATCH = 64;
  let model, data, random, losses, epochs, running, frameToken, selectedPoint;

  function setupCanvas(el) {
    const box = el.getBoundingClientRect();
    const size = Math.max(160, Math.round(box.width || 460));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    el.width = Math.round(size * dpr);
    el.height = Math.round(size * dpr);
    return { ctx: el.getContext('2d'), size, scale: dpr };
  }

  function renderDecision() {
    const { ctx, size, scale } = setupCanvas(canvas);
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    const cells = 44;
    const step = size / cells;
    for (let iy = 0; iy < cells; iy++) {
      for (let ix = 0; ix < cells; ix++) {
        const x = -1 + 2 * (ix + 0.5) / cells;
        const y = 1 - 2 * (iy + 0.5) / cells;
        const probability = model.predict(x, y);
        const alpha = 0.13 + 0.7 * Math.abs(probability - 0.5) * 2;
        ctx.fillStyle = probability > 0.5
          ? 'rgba(93, 230, 204, ' + alpha + ')'
          : 'rgba(173, 141, 255, ' + alpha + ')';
        ctx.fillRect(ix * step, iy * step, step + 1, step + 1);
      }
    }
    ctx.strokeStyle = 'rgba(255,255,255,.14)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(size / 2, 0); ctx.lineTo(size / 2, size);
    ctx.moveTo(0, size / 2); ctx.lineTo(size, size / 2);
    ctx.stroke();
    for (const point of data.train) {
      const px = (point.x + 1) * size / 2;
      const py = (1 - point.y) * size / 2;
      ctx.beginPath();
      ctx.arc(px, py, Math.max(2.8, size / 145), 0, Math.PI * 2);
      ctx.fillStyle = point.label === 1 ? '#5de6cc' : '#bca2ff';
      ctx.fill();
      ctx.lineWidth = 1.3;
      ctx.strokeStyle = '#11162b';
      ctx.stroke();
    }
    if (selectedPoint) {
      const px = (selectedPoint.x + 1) * size / 2;
      const py = (1 - selectedPoint.y) * size / 2;
      ctx.beginPath();
      ctx.arc(px, py, 10, 0, 2 * Math.PI);
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(px - 16, py); ctx.lineTo(px + 16, py);
      ctx.moveTo(px, py - 16); ctx.lineTo(px, py + 16);
      ctx.lineWidth = 1.4; ctx.stroke();
    }
  }

  function renderLoss() {
    const { ctx, size, scale } = setupCanvas(chart);
    const height = Math.round(size * 0.37);
    chart.height = Math.round(height * scale);
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, size, height);
    const left = 12, right = size - 12, top = 12, bottom = height - 17;
    ctx.strokeStyle = 'rgba(255,255,255,.12)';
    ctx.beginPath();
    ctx.moveTo(left, top); ctx.lineTo(left, bottom); ctx.lineTo(right, bottom); ctx.stroke();
    if (!losses.length) return;
    const maximum = Math.max(.8, ...losses);
    ctx.lineWidth = 2.5;
    ctx.strokeStyle = '#5de6cc';
    ctx.beginPath();
    losses.forEach((value, index) => {
      const x = left + (right - left) * index / Math.max(1, losses.length - 1);
      const y = bottom - (value / maximum) * (bottom - top);
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  function updateMetrics() {
    epochText.textContent = epochs.toLocaleString();
    accuracyText.textContent = (100 * model.accuracy(data.validation)).toFixed(1) + '%';
    lossText.textContent = losses.length ? losses.at(-1).toFixed(3) : '—';
    progressFill.style.width = Math.min(100, 100 * epochs / MAX_STEPS) + '%';
    progress.setAttribute('aria-valuenow', String(Math.floor(epochs / MAX_STEPS * 100)));
    if (selectedPoint) {
      const prob = model.predict(selectedPoint.x, selectedPoint.y);
      const label = prob >= 0.5 ? 'Mint' : 'Violet';
      const confidence = (Math.max(prob, 1 - prob) * 100).toFixed(1);
      sampleText.textContent = 'Selected point: ' + label + ' · ' + confidence + '% confidence';
    }
  }

  function setRunning(on) {
    running = on;
    trainButton.textContent = on ? 'Pause training' : epochs >= MAX_STEPS ? 'Training complete' : 'Train network';
    trainButton.disabled = epochs >= MAX_STEPS;
    statusText.textContent = on ? 'Training on local data…' : epochs === 0 ? 'Ready to learn' : epochs >= MAX_STEPS ? 'Training complete' : 'Paused';
  }

  function resetModel() {
    frameToken++;
    data = generateDataset(choice.value, 320, 73);
    model = new NeuralNetwork(12, 42);
    random = randomGenerator(2026);
    epochs = 0;
    setRunning(false);
    losses = [];
    selectedPoint = null;
    sampleText.textContent = 'Click the map to inspect a prediction.';
    updateMetrics();
    renderDecision();
    renderLoss();
  }

  function loop(token) {
    if (!running || token !== frameToken) return;
    for (let step = 0; step < 8 && epochs < MAX_STEPS; step++) {
      const batch = Array.from({ length: BATCH }, () =>
        data.train[Math.floor(random() * data.train.length)]);
      const loss = model.trainBatch(batch, Number(slider.value));
      epochs++;
      if (epochs === 1 || epochs % 8 === 0 || epochs === MAX_STEPS) losses.push(loss);
    }
    updateMetrics();
    renderLoss();
    if (epochs % 24 === 0 || epochs === MAX_STEPS) renderDecision();
    if (epochs >= MAX_STEPS) {
      setRunning(false);
      renderDecision();
      return;
    }
    window.requestAnimationFrame(() => loop(token));
  }

  trainButton.addEventListener('click', () => {
    if (running) { setRunning(false); frameToken++; return; }
    setRunning(true);
    const token = ++frameToken;
    window.requestAnimationFrame(() => loop(token));
  });
  resetButton.addEventListener('click', resetModel);
  choice.addEventListener('change', resetModel);
  slider.addEventListener('input', () => { rateOutput.textContent = Number(slider.value).toFixed(3); });
  canvas.addEventListener('click', event => {
    const rect = canvas.getBoundingClientRect();
    selectedPoint = {
      x: Math.max(-1, Math.min(1, (event.clientX - rect.left) / rect.width * 2 - 1)),
      y: Math.max(-1, Math.min(1, 1 - (event.clientY - rect.top) / rect.height * 2))
    };
    updateMetrics(); renderDecision();
  });
  window.addEventListener('resize', () => { renderDecision(); renderLoss(); });
  rateOutput.textContent = Number(slider.value).toFixed(3);
  frameToken = 0;
  resetModel();
})();
