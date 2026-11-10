/* Neural Network Playground — a tiny, dependency-free multilayer perceptron.
   Architecture: 2 inputs -> N tanh units -> N tanh units -> 1 sigmoid output.
   Trained with mini-batch backpropagation and the Adam optimizer. */
(function (root) {
  "use strict";

  function randomGenerator(seed) {
    let state = seed >>> 0;
    return function () {
      state += 0x6D2B79F5;
      let z = state;
      z = Math.imul(z ^ (z >>> 15), z | 1);
      z ^= z + Math.imul(z ^ (z >>> 7), z | 61);
      return ((z ^ (z >>> 14)) >>> 0) / 4294967296;
    };
  }

  function sigmoid(value) {
    if (value >= 0) return 1 / (1 + Math.exp(-value));
    const e = Math.exp(value);
    return e / (1 + e);
  }

  function generateDataset(kind = "xor", count = 320, seed = 73) {
    if (!["xor", "circle", "wave"].includes(kind)) throw new Error("Unknown dataset");
    const rand = randomGenerator(seed);
    const points = [];
    for (let i = 0; i < count; i++) {
      const x = rand() * 2 - 1;
      const y = rand() * 2 - 1;
      let label;
      if (kind === "xor") label = x * y >= 0 ? 1 : 0;
      else if (kind === "circle") label = x * x + y * y < 0.38 ? 1 : 0;
      else label = y > 0.35 * Math.sin(4 * x) ? 1 : 0;
      points.push({ x, y, label });
    }
    return { train: points.slice(0, Math.floor(count * 0.75)),
             validation: points.slice(Math.floor(count * 0.75)) };
  }

  class NeuralNetwork {
    constructor(width = 12, seed = 42) {
      if (!Number.isInteger(width) || width < 2 || width > 32) throw new Error("Invalid hidden width");
      this.layers = [2, width, width, 1];
      this.rand = randomGenerator(seed);
      this.weights = [];
      this.biases = [];
      this.mw = [];
      this.vw = [];
      this.mb = [];
      this.vb = [];
      this.steps = 0;
      for (let l = 1; l < this.layers.length; l++) {
        const prev = this.layers[l - 1];
        const size = this.layers[l];
        const scale = Math.sqrt(6 / (prev + size));
        const layerW = Array.from({ length: size }, () =>
          Array.from({ length: prev }, () => (this.rand() * 2 - 1) * scale));
        this.weights.push(layerW);
        this.biases.push(Array(size).fill(0));
        this.mw.push(layerW.map(row => row.map(() => 0)));
        this.vw.push(layerW.map(row => row.map(() => 0)));
        this.mb.push(Array(size).fill(0));
        this.vb.push(Array(size).fill(0));
      }
    }

    forward(x, y) {
      const activations = [[x, y]];
      for (let l = 0; l < this.weights.length; l++) {
        const next = this.weights[l].map((row, i) => {
          let z = this.biases[l][i];
          for (let j = 0; j < row.length; j++) z += row[j] * activations[l][j];
          return l === this.weights.length - 1 ? sigmoid(z) : Math.tanh(z);
        });
        activations.push(next);
      }
      return activations;
    }

    predict(x, y) { return this.forward(x, y).at(-1)[0]; }

    accuracy(points) {
      if (!points.length) return 0;
      let correct = 0;
      for (const p of points) correct += Number((this.predict(p.x, p.y) >= 0.5) === Boolean(p.label));
      return correct / points.length;
    }

    trainBatch(points, learningRate = 0.023) {
      if (!points.length) throw new Error("Batch cannot be empty");
      if (!Number.isFinite(learningRate) || learningRate <= 0) throw new Error("Invalid learning rate");
      const gw = this.weights.map(layer => layer.map(row => row.map(() => 0)));
      const gb = this.biases.map(layer => layer.map(() => 0));
      let loss = 0;

      for (const point of points) {
        const a = this.forward(point.x, point.y);
        const p = a.at(-1)[0];
        loss -= point.label * Math.log(Math.max(p, 1e-12)) +
                (1 - point.label) * Math.log(Math.max(1 - p, 1e-12));
        const delta = this.biases.map(layer => layer.map(() => 0));
        delta.at(-1)[0] = p - point.label; // BCE + sigmoid derivative
        for (let l = delta.length - 2; l >= 0; l--) {
          for (let i = 0; i < delta[l].length; i++) {
            let effect = 0;
            for (let j = 0; j < delta[l + 1].length; j++) {
              effect += this.weights[l + 1][j][i] * delta[l + 1][j];
            }
            delta[l][i] = effect * (1 - a[l + 1][i] ** 2); // tanh derivative
          }
        }
        for (let l = 0; l < gw.length; l++) {
          for (let i = 0; i < gw[l].length; i++) {
            gb[l][i] += delta[l][i];
            for (let j = 0; j < gw[l][i].length; j++) gw[l][i][j] += delta[l][i] * a[l][j];
          }
        }
      }

      // Adam: adaptive first- and second-moment estimates.
      this.steps++;
      const b1 = 0.9, b2 = 0.999, eps = 1e-8;
      const correction1 = 1 - b1 ** this.steps;
      const correction2 = 1 - b2 ** this.steps;
      for (let l = 0; l < this.weights.length; l++) {
        for (let i = 0; i < this.weights[l].length; i++) {
          const gBias = gb[l][i] / points.length;
          this.mb[l][i] = b1 * this.mb[l][i] + (1 - b1) * gBias;
          this.vb[l][i] = b2 * this.vb[l][i] + (1 - b2) * gBias * gBias;
          this.biases[l][i] -= learningRate * (this.mb[l][i] / correction1) /
                               (Math.sqrt(this.vb[l][i] / correction2) + eps);
          for (let j = 0; j < this.weights[l][i].length; j++) {
            const g = gw[l][i][j] / points.length;
            this.mw[l][i][j] = b1 * this.mw[l][i][j] + (1 - b1) * g;
            this.vw[l][i][j] = b2 * this.vw[l][i][j] + (1 - b2) * g * g;
            this.weights[l][i][j] -= learningRate * (this.mw[l][i][j] / correction1) /
                                      (Math.sqrt(this.vw[l][i][j] / correction2) + eps);
          }
        }
      }
      return loss / points.length;
    }
  }

  const api = { NeuralNetwork, generateDataset, randomGenerator };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.NeuralNet = api;
})(typeof window !== "undefined" ? window : undefined);
