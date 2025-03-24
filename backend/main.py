from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

app = FastAPI()
