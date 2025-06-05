from imports import *
from fields import *
from classes import *
from servicenow import *


load_dotenv()

app = FastAPI(title="ServiceNow Natural Language API")
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

def get_llm_model():
    """Initialize Azure ChatOpenAI model"""
    return AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_OPENAI_ENGINE"),
        model_name=os.getenv("AZURE_OPENAI_MODEL"),
        temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.0")),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

auth_config = AuthConfig(
    client_id="",
    client_secret="",
    username="",
    password="",
    instance_url=""
)

llm_model = get_llm_model()
auth_manager = AuthManager(auth_config)
servicenow_api = ServiceNowAPI(auth_manager, llm_model)

@app.post("/query")
async def process_query(query: Query):
    """Process natural language query and return ServiceNow data in human-readable format"""
    try:
        result = servicenow_api.process_query(query.question, query.format_response)
        return result
    except HTTPException as e:
        raise e

@app.post("/query/raw")
async def process_query_raw(query: Query):
    """Process natural language query and return raw ServiceNow data (JSON format)"""
    try:
        result = servicenow_api.process_query(query.question, format_response=False)
        return result
    except HTTPException as e:
        raise e
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "7000"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,

    )