# mT5 Bidirectional EN-TR Machine Translation (ONNX INT8 & ORT Mobile)

This project involves fine-tuning the `google/mt5-small` model for bidirectional English-Turkish Machine Translation (EN<->TR) using the 8-bit LoRA (Low-Rank Adaptation) technique, followed by optimizing and quantizing the model into ONNX INT8 format for efficient mobile deployment (e.g., in Flutter applications).

## Key Features & Workflow

1. **Bidirectional Translation**: The model is trained to translate symmetrically in both directions (English to Turkish and Turkish to English) dynamically.
2. **Model Fine-Tuning**: The `google/mt5-small` model was fine-tuned on a custom EN-TR dataset (Lainchan-HPLT). To optimize GPU memory (VRAM) usage during training, the model was loaded in 8-bit using `BitsAndBytes`, and the `PEFT` library was used to apply LoRA.

3. **Vocabulary Pruning**: The original mT5 vocabulary was aggressively pruned by analyzing the dataset tokens. The vocabulary size was reduced by 67%, significantly decreasing the embedding layer's size and making the model much lighter for edge devices.

4. **ONNX and INT8 Quantization**: After merging the trained LoRA weights with the base model, it was exported to ONNX format using the Hugging Face `optimum` library. For low-latency mobile inference and reduced storage footprint, the ONNX model was quantized to **INT8** and converted into the highly optimized ORT Mobile format.

5. **Performance Evaluation**: The final quantized ONNX model was evaluated on the validation set, achieving a solid METEOR score of `0.6245`.

## Technologies Used

- **Deep Learning Frameworks**: PyTorch, PyTorch Lightning, Transformers, PEFT (LoRA), BitsAndBytes
- **Optimization & Inference**: ONNX, ONNX Runtime, Hugging Face Optimum
- **Data Processing & Metrics**: Pandas, PyArrow, Evaluate (METEOR Score)
