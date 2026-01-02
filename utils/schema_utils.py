import json
import logging
from typing import Any, Dict, List, Type, Optional
from pydantic import create_model, Field, BaseModel, ConfigDict

logger = logging.getLogger(__name__)

class DynamicModelBuilder:
    """
    Utility to dynamically build Pydantic models from a JSON schema.
    Specifically optimized for OpenAI Structured Outputs.
    """
    
    @staticmethod
    def validate_model(model_class: Type[BaseModel]):
        """
        Validates the Pydantic model against OpenAI's Strict Mode requirements.
        Uses the internal validation logic from the OpenAI SDK.
        """
        try:
            from openai.lib._pydantic import to_strict_json_schema
            # This function will raise an error if the model is invalid for Structured Outputs
            to_strict_json_schema(model_class)
            logger.info("✅ Schema validation successful: Model is compatible with OpenAI Structured Outputs.")
        except ImportError:
            logger.warning("⚠️ Could not import openai.lib._pydantic.to_strict_json_schema. Skipping strict validation.")
        except Exception as e:
            logger.error(f"❌ Schema Validation Failed: {e}")
            raise ValueError(f"Invalid Schema for OpenAI Strict Mode: {e}") from e


    @classmethod
    def build_model_from_schema(cls, schema_path: str, model_name: str = "ContractModel") -> Type[BaseModel]:
        """
        Reads a JSON schema file and builds a Pydantic model.
        """
        try:
            from pathlib import Path
            import os
            
            # Normalize path separators for cross-platform compatibility
            # Convert Windows backslashes to forward slashes
            normalized_path = schema_path.replace('\\', '/')
            
            # Robust Path Handling
            path_obj = Path(normalized_path)
            
            # If path is not absolute, try to resolve it
            if not path_obj.is_absolute():
                # 1. Try relative to Current Working Directory (Project Root in Docker)
                cwd_path = Path.cwd() / path_obj
                
                # 2. Try relative to this file's directory (utils/../) as a fallback
                utils_dir = Path(__file__).parent
                project_root = utils_dir.parent
                relative_path = project_root / path_obj
                
                if cwd_path.exists():
                    final_path = cwd_path
                elif relative_path.exists():
                    final_path = relative_path
                else:
                    # Log helpful debugging info if not found
                    logger.error(f"❌ Schema file not found.")
                    logger.error(f"Searched CWD: {cwd_path}")
                    logger.error(f"Searched Relative: {relative_path}")
                    raise FileNotFoundError(f"Schema not found: {schema_path}")
            else:
                final_path = path_obj

            logger.info(f"Loading schema from: {final_path}")

            with open(final_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            
            properties = schema.get("properties", {})
            fields = {}

            for field_name, field_info in properties.items():
                field_type = cls._resolve_python_type(field_info, field_name.capitalize())
                description = field_info.get("description", "")
                
                # OpenAI Structured Outputs require all fields to be required.
                # In Pydantic, this means no default value.
                fields[field_name] = (field_type, Field(..., description=description))

            # OpenAI Structured Outputs require additionalProperties: false, 
            # which mapping to extra='forbid' in Pydantic.
            model = create_model(
                model_name, 
                __config__=ConfigDict(extra="forbid"), 
                **fields
            )
            return model

        except Exception as e:
            logger.error(f"Failed to build model from schema: {e}")
            raise

    @classmethod
    def _resolve_python_type(cls, field_info: Dict[str, Any], model_name_hint: str) -> Any:
        """
        Recursively resolve JSON schema types to Python/Pydantic types.
        """
        json_type = field_info.get("type", "string")

        if json_type == "array":
            items = field_info.get("items", {})
            # If items is empty/missing, default to string to satisfy OpenAI Structured Output requirements
            if not items:
                logger.warning(f"Array field '{model_name_hint}' is missing 'items' schema. Defaulting to list[str].")
                return List[str]
            
            inner_type = cls._resolve_python_type(items, f"{model_name_hint}Item")
            return List[inner_type]

        if json_type == "object":
            nested_properties = field_info.get("properties", {})
            if not nested_properties:
                return Dict[str, Any]
            
            nested_fields = {}
            for n_name, n_info in nested_properties.items():
                n_type = cls._resolve_python_type(n_info, f"{model_name_hint}_{n_name.capitalize()}")
                n_desc = n_info.get("description", "")
                nested_fields[n_name] = (n_type, Field(..., description=n_desc))
            
            return create_model(
                model_name_hint, 
                __config__=ConfigDict(extra="forbid"), 
                **nested_fields
            )

        # Base types mapping
        mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
        }
        return mapping.get(json_type, Any)

if __name__ == "__main__":
    # Test loading the local schema
    try:
        model = DynamicModelBuilder.build_model_from_schema("contract_model.schema.json")
        print(f"Successfully built model: {model}")
        print(f"Model keys: {model.model_fields.keys()}")
    except Exception as e:
        print(f"Test failed: {e}")
