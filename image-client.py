import os
import json
import base64
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI

# Load environment variables
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT")

# Create images folder if it doesn't exist
if not os.path.exists("images"):
    os.makedirs("images")

# Authenticate with Azure
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(
        exclude_environment_credential=True,
        exclude_managed_identity_credential=True
    ),
    "https://cognitiveservices.azure.com/.default"
)

# Initialize client
client = OpenAI(
    base_url=endpoint,
    api_key=token_provider(),
)

def save_image(image_bytes, filename):
    with open(filename, "wb") as f:
        f.write(image_bytes)

def main():
    print("=== AI Image Generator ===")
    print("Type 'quit' to exit\n")

    count = 1

    while True:
        prompt = input("Enter prompt: ")

        if prompt.lower() == "quit":
            print("Exiting...")
            break

        try:
            # Generate image
            response = client.images.generate(
                model=model_deployment,
                prompt=prompt,
                n=1
            )

            # Extract base64 image
            json_response = json.loads(response.model_dump_json())
            image_base64 = json_response["data"][0]["b64_json"]

            # Decode image
            image_bytes = base64.b64decode(image_base64)

            # Save image
            filename = f"images/image_{count}.png"
            save_image(image_bytes, filename)

            print(f"✅ Image saved: {filename}\n")

            count += 1

        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    main()