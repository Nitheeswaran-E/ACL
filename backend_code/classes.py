from imports import *
class AuthConfig(BaseModel):
    client_id: str
    client_secret: str
    username: str
    password: str
    grant_type: str = "password"
    instance_url: str

    @field_validator('instance_url')
    def validate_instance_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('instance_url must start with http:// or https://')
        return v.rstrip('/')

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    created_at: float
 
class Query(BaseModel):
    question: str
    format_response: bool = True  # New field to control response formatting

    @field_validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('question cannot be empty')
        return v.strip()

class AuthManager:
    def __init__(self, auth_config: AuthConfig):
        self.auth_config = auth_config
        self.token_info: Optional[TokenInfo] = None
        
    def _request_token(self) -> TokenInfo:
        """Request a new token from ServiceNow"""
        oauth_url = f"{self.auth_config.instance_url}/oauth_token.do"
        auth_data = {
            "client_id": self.auth_config.client_id,
            "client_secret": self.auth_config.client_secret,
            "username": self.auth_config.username,
            "password": self.auth_config.password,
            "grant_type": self.auth_config.grant_type
        }
        
        try:
            response = requests.post(oauth_url, data=auth_data)
            response.raise_for_status()
            token_data = response.json()
            
            return TokenInfo(
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_in=token_data["expires_in"],
                token_type=token_data["token_type"],
                created_at=time.time()
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to obtain access token: {str(e)}"
            )

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired"""
        if not self.token_info:
            return True
        
        current_time = time.time()
        expiration_time = self.token_info.created_at + self.token_info.expires_in - 60
        return current_time >= expiration_time
    
    def get_valid_token(self) -> str:
        """Get a valid access token, requesting a new one if necessary"""
        if self._is_token_expired():
            self.token_info = self._request_token()
        
        return self.token_info.access_token

    def _get_headers(self) -> Dict[str, str]:
        """Get current headers with valid access token"""
        access_token = self.get_valid_token()
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }