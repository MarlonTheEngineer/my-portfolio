# Neural Network Playground

**[Launch the interactive demo](https://marlontheengineer.github.io/my-portfolio/neural-network/)**

A small neural network implemented **from scratch in JavaScript** and hosted on GitHub Pages. The model trains directly in the browser: it does not use a pretrained model, TensorFlow, external APIs, or a paid server.

## What the demo does

- Train a binary classifier on three synthetic 2D pattern datasets: **XOR, circle, wave**.
- See the probability-based decision boundary update while the network learns.
- Watch the training loss, validation accuracy, and training-step counter.
- Change the learning rate, pause training, reset the model, or click the plot for a prediction.
- Run everything offline once the page's files are loaded (no network required for training).

## Architecture

2 inputs (x, y) → 12 tanh units → 12 tanh units → 1 sigmoid output.

The output is a probability between 0 and 1. Binary cross-entropy measures prediction error, and backpropagation calculates weight gradients. Adam updates the weights using mini-batches of 64 synthetic points.

The dataset is divided into **240 training points and 80 held-out validation points**. The displayed accuracy is on validation data; the mini-batch loss is on training data.

## Results

In one deterministic local run using a 0.023 learning rate and 720 training steps:

| Synthetic pattern | Validation accuracy |
| --- | ---: |
| XOR | 98.8% |
| Circle | 95.0% |
| Wave | 96.3% |

These are educational results on simple constructed datasets, not guarantees for other runs or real-world AI benchmarks.

## Files

- [Neural network implementation](../../docs/neural-network/neural-network.js)
- [Interactive training and visualization](../../docs/neural-network/app.js)
- [Demo HTML](../../docs/neural-network/index.html)
- [Demo styles](../../docs/neural-network/styles.css)
- [Automated tests](../../docs/neural-network/tests.js)

## Run locally

From the repository root:

    python -m http.server 8000 --directory docs

Open http://localhost:8000/neural-network/ and click **Train network**.

To run automated unit tests (Node.js 20+):

    node --test docs/neural-network/tests.js

No npm installation is required.

## Next improvements

1. Create a network architecture diagram that displays each neuron and learned weight.
2. Add user-drawn points and retrain on custom labels.
3. Export and import trained weights.
4. Train on a small real dataset and compare training versus test performance.
5. Add a mathematical gradient-check unit test.

## Learning checkpoints

**Input layer:** what x and y represent.

**Forward propagation:** how each neuron combines weights and activations.

**Loss:** why wrong predictions are penalized.

**Backpropagation:** how gradients flow from output to earlier layers.

**Validation:** why testing on held-out examples matters.

This is a portfolio learning project, not a production classifier. Its code is inspectable and intended for further development.
