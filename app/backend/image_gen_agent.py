from agno.agent import Agent  
from agno.models.google import Gemini  
from pathlib import Path  
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create images directory if it doesn't exist  
images_dir = Path("images")  
images_dir.mkdir(exist_ok=True)  
  
agent = Agent(  
    model=Gemini(  
        id="gemini-2.0-flash-exp-image-generation",  
        response_modalities=["Text", "Image"],  
        api_key=os.getenv("GOOGLE_API_KEY"),
    ),  
    create_default_system_message=False,  
    system_message=None,  
)  
  
# Generate an image  
agent.run("give me image of only one Winner of 2025 IPL if the match is mumbai indians vs RCB")  
  
# Get and save the generated images  
images = agent.get_images()  
if images:  
    for i, image in enumerate(images):  
        if image.content:  
            # Save image to the images directory  
            image_path = images_dir / f"generated_image_{i}.png"  
            with open(image_path, "wb") as f:  
                f.write(image.content)  
            print(f"Image saved to: {image_path}")