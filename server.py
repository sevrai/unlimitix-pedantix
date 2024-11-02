from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import argparse  
import uvicorn

from ConsolePedantix import ConsolePedantix  # Adjust the import according to your project structure

app = FastAPI()

allowed_origins = ["http://localhost:3000"]

pedantix_instance = None

parser = argparse.ArgumentParser(description="Run the FastAPI server with custom configuration.")
parser.add_argument("--page", type=str, help="Configuration value for ConsolePedantix")
args = parser.parse_args()

pedantix_instance = ConsolePedantix(args.page)
print(pedantix_instance.title)

@app.get("/api/game/{id}")
async def get_data():
    return pedantix_instance.to_json()

@app.get("/api/game/{id}/guess/{word}")
async def get_data(id: str, word: str):
    return pedantix_instance.guess_word(id, word)


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


if __name__ == "__main__":
    print(args.page)
    #run server
    uvicorn.run(app)
   


