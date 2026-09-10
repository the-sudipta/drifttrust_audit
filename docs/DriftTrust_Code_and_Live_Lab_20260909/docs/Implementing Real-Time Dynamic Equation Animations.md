# Instructions for CODEX: Implementing Real-Time Dynamic Equation Animations in lab.html

## Objective
Update the front-end UI and JavaScript logic of the `lab.html` page (and its associated JS modules) in the DriftTrust-Audit project. The goal is to visually showcase the real-time learning and mathematical value-updates of the Machine Learning model (12-24-1 MLP), making it highly educational and transparent.

## Reference Materials
1. **Video Reference:** Emulate the dynamic, real-time visual decision-making animation style seen in this short: https://www.youtube.com/shorts/jqPj-zyD8-I
2. **Image References (Crucial):** You must refer to the provided design concepts in the files named verbatim as "image_b76446.png" and "image_b76448.png". These images show a dynamic equation layout (e.g., `y = m * x + c`) where the values inside the boxes (Weight `m`, Input `x`, Bias `c`, Output `y`) update dynamically as the model learns.

## Required Features & Updates

### 1. Dynamic Equation Visualization Panel
*   Create a new animated section in `lab.html` (e.g., under the "Score and model-update state" section) dedicated to showing the live mathematical equations.
*   **MLP Layer Visuals:** Visually represent the core equation of the neural network: `Output = activation( (Weight * Input) + Bias )`. 
*   **Live Value Binding:** When the background Web Worker runs a forward pass (inference) or a backward pass (SGD/learning), the exact numerical values for the weights, biases, and inputs must flow into the UI in real-time. 
*   **Transition Effects:** When the model updates (e.g., the transition from state in `image_b76446.png` to `image_b76448.png`), the numbers inside the UI boxes should animate (e.g., a rolling number effect, color flash, or smooth transition) to visually prove that the model has "learned" and changed its internal parameters.

### 2. Trust Score Equation Animation
*   The system uses the formula: `Trust = 100 × (1 - Attack Score)`.
*   Build a dedicated, large-font animated equation block for this specific formula. 
*   Whenever the `Attack Score` changes due to the model adapting to a new network flow, the `Trust` calculation must animate live on the screen, showing the exact subtraction and multiplication happening step-by-step.

### 3. Data Flow & Network Animation (Video Inspiration)
*   Take inspiration from the provided YouTube link. When a user inputs a single flow or processes a replay, visualize the data packet (feature vector) entering the model.
*   Highlight the pathway: `Input Features -> Hidden Neurons (tanh) -> Output Score -> Trust Score`.
*   Show a visual trigger (like a pulse or a checkmark/cross) when the model decides to "Accept" or "Reject" an update based on the DriftTrust policy gate.

### 4. Technical Constraints (DO NOT BREAK EXISTING LOGIC)
*   **No Backend Frameworks:** The entire update must be implemented using pure HTML, CSS (for animations), and JavaScript. You cannot introduce Python backends or external database dependencies.
*   **Preserve IndexedDB:** The application currently relies on IndexedDB for storing model sessions and AJRs (Adaptation Justification Records). Your UI updates must read from these existing states without breaking the storage mechanism.
*   **Web Worker Integration:** The heavy mathematical lifting (matrix multiplication, SGD) is done in a background JS Worker. You must update the message-passing interface (`postMessage`) between the Worker and the main DOM thread to send the updated weights/biases back to the UI for the animation to render.

## Output Request for CODEX
Please provide the updated HTML structure, the CSS needed for the bounding boxes and animations (matching the style of `image_b76446.png`), and the modified JavaScript code required to fetch and animate these live values from the model engine.