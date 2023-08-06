__all__ = ['DetaConfig', 'config']

import os
import secrets
from typing import Union, Mapping, Optional
from pathlib import Path
from starlette.config import Config
from starlette.requests import Request
from starlette.datastructures import URL


class DetaConfig(Config):
    """
    Init accepts:
    - env_file: Union[str, Path, None]
    - environ: Mapping[str, str]
    - env_prefix: str = ""
    
    # ENV FILE (.env)
    Expected keys for .env file:
    - DETABASE_PROJECT_KEY
    - DETA_AUTH_TOKEN
    - SESSION_SECRET
    - LOGO_PATH
    
    # PRE-SET VARIABLES
    The following environment variables will be set in all Micros, accessible on the server side.
    Those names are private ENV variables of Deta and only can be set at Spacefile:
    - DETA_PROJECT_KEY: deta project key
    - DETA_SPACE_APP: will be set to “true”
    - DETA_SPACE_APP_VERSION: the app version
    - DETA_SPACE_APP_HOSTNAME: will be set to the primary hostname
    - DETA_SPACE_APP_MICRO_NAME: micro’s name
    - DETA_SPACE_APP_MICRO_TYPE: will be set to "primary" if primary otherwise “normal”
    
    # API KEYS
    If you want users of your app to be able to access their app instance programmatically you can enable the api_keys
    preset for Micros in your app:

    micros:
      - name: api
        src: ./api/
        engine: python3.9
        presets:
          api_keys: true
          
    If enabled, users of your app will be able to generate API keys in their app instance settings and use them to
    authenticate requests made to otherwise private routes of a Micro.

    Generated keys need to be provided in the HTTP header X-Space-App-Key and only work with Micros that have the
    preset api_keys enabled. Public routes have a higher preference than API keys, if there are public routes specified
    these will always be public.

    Note: If you enable API keys you should show clearly in the app that API keys can be used and ideally have clear
    documentation on which endpoints of your app work with API key auth.
    
    # CUSTOM VARIABLES
    Use the env preset if you need to set custom environment variables for your Micros. This can also be used to let
    users of your app specify things like external secrets or API Keys or Data Keys of different app instances.

    micros:
      - name: api
        src: ./api/
        engine: python3.9
        presets:
          env:
            - name: SECRET_MESSAGE
              description: Secret message only available to this Micro
              default: "deta is cool"
              
    name : environment variable name or key
    description : human friendly description (optional)
    default : default value for the variable (optional)
    
    The user of the app will be shown a UI in the App’s Settings where they can set the values for the specified
    environment variables. They will be exposed to the Micro’s environment under the specified name.
    """
    def __init__(self,
                 env_file: Union[str, Path, None] = '.env',
                 environ: Mapping[str, str] = os.environ,
                 env_prefix: str = ""
                 ):
        super().__init__(env_file=os.path.join(os.getcwd(), env_file), environ=environ, env_prefix=env_prefix)
        
    @property
    def detabase_project_key(self) -> Optional[str]:
        return self.get('DETABASE_PROJECT_KEY', cast=str, default=self.deta_project_key)
    
    @property
    def deta_project_key(self) -> Optional[str]:
        return self.get('DETA_PROJECT_KEY', cast=str,  default=None)
    
    @property
    def deta_auth_token(self) -> Optional[str]:
        return self.get('DETA_AUTH_TOKEN', default=None)
    
    @property
    def deta_space_app(self):
        return self.get('DETA_SPACE_APP', cast=bool)
    
    @property
    def deta_space_app_version(self):
        return self.get('DETA_SPACE_APP_VERSION', cast=str)
    
    @property
    def deta_space_app_hostname(self):
        return self.get('DETA_SPACE_APP_HOSTNAME', cast=str)

    @property
    def deta_space_app_micro_name(self):
        return self.get('DETA_SPACE_APP_MICRO_NAME', cast=str)
    
    @property
    def deta_space_app_micro_type(self):
        return self.get('DETA_SPACE_APP_MICRO_TYPE', cast=str)
    
    @property
    def session_secret(self) -> str:
        return self.get('SESSION_SECRET', default=secrets.token_hex())
    
    @property
    def static_base_url(self) -> Union[os.PathLike, str]:
        return os.path.join(os.getcwd(), 'static')
    
    @property
    def templates_base_url(self) -> Union[os.PathLike, str]:
        return os.path.join(os.getcwd(), 'templates')
    
    @property
    def logo_path(self) -> str:
        return self.get('LOGO_PATH', cast=str, default='img/logo.png')
        
    @property
    def footer_address(self) -> str:
        return self.get('FOOTER_ADDRESS', cast=str)
    
    @property
    def footer_phone(self) -> str:
        return self.get('FOOTER_PHONE', cast=str)
    
    @property
    def footer_email(self) -> str:
        return self.get('FOOTER_EMAIL', cast=str)
    
    @classmethod
    def url_for(cls, request: Request, __name: str, **path_params) -> URL:
        return request.url_for(__name, **path_params)



config = DetaConfig()