from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Initialize the router
router = APIRouter()

logger = logging.getLogger(__name__)

# Request/Response models
class HFInferenceRequest(BaseModel):
    model_name: str
    inputs: str
    parameters: Optional[Dict[str, Any]] = None

class HFInferenceResponse(BaseModel):
    generated_text: str
    model_used: str

# Placeholder for model cache
model_cache = {}

@router.post("/hf/inference", response_model=HFInferenceResponse)
async def hf_inference(request: HFInferenceRequest):
    """
    Generic Hugging Face model inference endpoint
    """
    try:
        # Import transformers inside the function to avoid heavy imports on startup
        from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
        import torch

        # Check if model is cached
        if request.model_name not in model_cache:
            logger.info(f"Loading model {request.model_name}")

            # Determine the task based on model type
            if "text-classification" in request.model_name.lower() or "sentiment" in request.model_name.lower():
                model_cache[request.model_name] = pipeline(
                    "text-classification",
                    model=request.model_name,
                    tokenizer=request.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )
            elif "text-generation" in request.model_name.lower() or "gpt" in request.model_name.lower():
                tokenizer = AutoTokenizer.from_pretrained(request.model_name)
                model = AutoModelForSequenceClassification.from_pretrained(request.model_name)

                # Add padding token if not present
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token

                model_cache[request.model_name] = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    device=0 if torch.cuda.is_available() else -1
                )
            else:
                # Default to text generation
                model_cache[request.model_name] = pipeline(
                    "text-generation",
                    model=request.model_name,
                    tokenizer=request.model_name,
                    device=0 if torch.cuda.is_available() else -1
                )

        # Run inference
        model_pipeline = model_cache[request.model_name]

        # Prepare parameters for the pipeline
        pipeline_params = request.parameters or {}

        if hasattr(model_pipeline, 'task') and 'text-generation' in model_pipeline.task:
            # For text generation models
            result = model_pipeline(
                request.inputs,
                pad_token_id=50256,  # Common for GPT models, adjust as needed
                **pipeline_params
            )
        else:
            # For other models
            result = model_pipeline(request.inputs, **pipeline_params)

        # Format the response
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], dict) and 'generated_text' in result[0]:
                generated_text = result[0]['generated_text']
            elif isinstance(result[0], dict) and 'label' in result[0]:
                generated_text = f"{result[0]['label']}: {result[0]['score']}"
            else:
                generated_text = str(result[0])
        else:
            generated_text = str(result)

        return HFInferenceResponse(
            generated_text=generated_text,
            model_used=request.model_name
        )

    except Exception as e:
        logger.error(f"Hugging Face inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.get("/hf/models")
async def list_models():
    """
    List currently loaded models
    """
    return {"loaded_models": list(model_cache.keys())}

@router.delete("/hf/models/{model_name}")
async def unload_model(model_name: str):
    """
    Unload a model from memory
    """
    if model_name in model_cache:
        del model_cache[model_name]
        return {"message": f"Model {model_name} unloaded successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found in cache")