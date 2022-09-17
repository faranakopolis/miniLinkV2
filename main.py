from fastapi import FastAPI

from docs.responses import SUCCESS_GENERATE_SHORT_URL, SUCCESS_DELETE_SHORT_URL, SUCCESS_GET_URL_INFO

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/url/",
          tags=["generate_short_url"],
          responses={
              200: {
                  'content': {'application/json': {'example': SUCCESS_GENERATE_SHORT_URL}},
                  'description': 'The shorter url generated and returned to user successfully.'
              },
              500: {
                  'description': 'Server failed to return the generated url.'
              }
          }
          )
async def generate_short_url():
    return {"message": "Hello World"}


@app.delete("/url/",
            tags=["delete_short_url"],
            responses={
                200: {
                    'content': {'application/json': {'example': SUCCESS_DELETE_SHORT_URL}},
                    'description': 'The shorter url deleted successfully.'
                },
                500: {
                    'description': 'Server failed to delete the url.'
                }
            }
            )
async def delete_short_url(hashed_url: str):
    return {"message": "Hello World"}


@app.get("/url/",
         tags=["get_url(s)_info"],
         responses={
             200: {
                 'content': {'application/json': {'example': SUCCESS_GET_URL_INFO}},
                 'description': 'The url(s) info retrieved and returned to user successfully.'
             },
             500: {
                 'description': 'Server failed to get the url(s) info.'
             }
         }
         )
async def get_url_info(hashed_url: str = None):
    return {"message": "Hello World"}
