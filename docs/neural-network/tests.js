/* Run with node --test docs/neural-network/tests.js */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { NeuralNetwork, generateDataset } = require('./neural-network.js');

test('seeded initialization gives repeatable results', () => {
  const a = new NeuralNetwork(8, 10), b = new NeuralNetwork(8, 10);
  assert.equal(a.predict(0.3, -0.2), b.predict(0.3, -0.2));
});

test('data generation is deterministic and both classes appear', () => {
  for (const type of ['xor', 'circle', 'wave']) {
    const a = generateDataset(type, 320, 5);
    const b = generateDataset(type, 320, 5);
    assert.deepEqual(a, b);
    assert.equal(a.train.length, 240);
    assert.equal(a.validation.length, 80);
    assert.equal(new Set(a.train.map(p => p.label)).size, 2);
  }
});

test('training reduces XOR loss and improves validation accuracy', () => {
  const model = new NeuralNetwork(12, 42);
  const { train, validation } = generateDataset('xor', 320, 73);
  const beginning = model.trainBatch(train.slice(0, 64), 0.023);
  let final = beginning;
  for (let i = 0; i < 280; i++) {
    const batch = Array.from({ length: 64 }, (_, k) => train[(i * 17 + k * 13) % train.length]);
    final = model.trainBatch(batch, 0.023);
  }
  assert.ok(final < beginning * 0.5, 'loss did not decrease');
  assert.ok(model.accuracy(validation) > 0.85, 'accuracy below expected threshold');
});

test('invalid training inputs are rejected', () => {
  const model = new NeuralNetwork();
  assert.throws(() => model.trainBatch([]));
  assert.throws(() => model.trainBatch([{ x: 0, y: 0, label: 0 }], 0));
});
