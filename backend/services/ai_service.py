from config import get_settings
import base64, httpx


async def generate_tags_from_image(image_bytes: bytes) -> list[str]:    
    settings = get_settings() 
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"https://vision.googleapis.com/v1/images:annotate?key={settings.GOOGLE_VISION_API_KEY}",
            json={
                "requests": [
                    {
                        "image": {"content": image_base64},
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 10},
                            {"type": "IMAGE_PROPERTIES", "maxResults": 5}
                        ]
                    }
                ]
            }
        )
        
        if response.status_code != 200:
            raise ValueError(f"AI service returned error: {response.text}")
        
        result = response.json()
        labels = result["responses"][0]["labelAnnotations"]
        
        tags = [
            label["description"].lower().replace(" ", "-")
            for label in labels
            if label["score"] > settings.MIN_CONFIDENCE
        ]
        
        return tags[:settings.MAX_TAGS_PER_POST]