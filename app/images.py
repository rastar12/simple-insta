from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    private_key=os.getenv("IMAGE_KIT_PRIVATE_KEY")
)

IMAGE_KIT_PUBLIC_KEY = os.getenv("IMAGE_KIT_PUBLIC_KEY")
IMAGE_KIT_URL_ENDPOINT = os.getenv("IMAGE_KIT_URL")
