import os

import torch
from diffusers import FluxPipeline
from huggingface_hub import login
from transformers import GenerationMixin, AutoTokenizer, AutoModelForCausalLM

login(token=os.environ.get("OPENAI_KEY"))


def setup_kobold():
    # Load model directly
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tokenizer = AutoTokenizer.from_pretrained("KoboldAI/OPT-30B-Erebus")
    model: AutoModelForCausalLM = AutoModelForCausalLM.from_pretrained("KoboldAI/OPT-30B-Erebus")
    return model, tokenizer


def setup_nsfw_detector():
    # Load model directly
    from transformers import AutoImageProcessor, AutoModelForImageClassification

    processor = AutoImageProcessor.from_pretrained("Falconsai/nsfw_image_detection")
    model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
    return model, processor


def setup_fast_model():
    model_name = "distilgpt2"  # A smaller, faster model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Quantize the model to INT8
    model = torch.quantization.quantize_dynamic(
        model, {torch.nn.Linear}, dtype=torch.qint8
    )

    # Move to GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    return model, tokenizer



def generate_text_fast(prompt, max_length=50):
    tokenizer, model = setup_fast_model()
    model.to('cpu')

    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    input_ids = input_ids.to('cpu')


    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
        )

    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text


def prompt(q, model):
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    inputs = tokenizer.encode(q, return_tensors="pt")
    outputs = model.generate(inputs, max_length=50, do_sample=True, temperature=0.7)
    return tokenizer.decode(outputs[0])
