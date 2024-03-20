import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import aspose.words as aw

client = OpenAI()
app = FastAPI()

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Assuming your audio files are stored in 'audio_files' directory under the current working directory
app.mount("/audio_files", StaticFiles(directory="audio_files"), name="audio_files")

@app.post("/create-audio/")
def create_audio(text: str):
    try:
        file_name = 'tmp_sentence'
        file_path = f"audio_files/{file_name}.mp3"
        # Assuming you're running the server on localhost:8001
        # Adjust the host and port as necessary
        file_url = f"http://localhost:8001/audio_files/{file_name}.mp3"

        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text,
        )
        response.stream_to_file(file_path)
        # Return with a json response containing the URL to access the file
        return JSONResponse(status_code=200, content={"file_url": file_url})
    except Exception as e:
        logging.exception(text)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/document-to-html/")
def document_to_html(input_file_name: str, output_folder_path: str = 'data'):
    """
    Convert PDF to HTML
    :param input_file_name: The path to the source PDF file.
    """
    try:
        doc = aw.Document('pdfs/'+input_file_name)
        # Output file path
        output_file = input_file_name.replace('.pdf', '.html')

        # Get folder name
        output_file_path = f"{output_folder_path}/{output_file}"

        doc.save(output_file_path)
        # Remove watermark
        with open(output_file_path, "r") as file:
            data = file.read()
            data = data.replace(
                '<span style="font-weight:bold; color:#ff0000">Created with an evaluation copy of Aspose.Words. To discover the full versions of our APIs please visit: https://products.aspose.com/words/</span>',
                "",
            )
            # Add the folder name to the image src
            data = data.replace('img src="', f'img src="{output_folder_path}/')

        with open(output_file_path, "w") as file:
            file.write(data)
        return JSONResponse(status_code=200, content={"output_file_path": output_file_path})
    except Exception as e:
        logging.exception(input_file_name)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)
