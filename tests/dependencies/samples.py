from pydantic import BaseModel


class DocumentCreateDTO(BaseModel):
    name: str
    content: str


class DocumentService:
    async def create(self, dto: DocumentCreateDTO) -> DocumentCreateDTO:
        if isinstance(dto, dict):
            doc = DocumentCreateDTO(**dto)
        else:
            doc = DocumentCreateDTO(**dto.model_dump())
        return doc
